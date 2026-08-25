# MLflow in Action — Course Notes Context

## 1. What this folder is

This folder contains Obsidian "hover-notes" exported (twice, hence the duplicate
files — see §5) from the Udemy course **"MLflow in Action - Master the art of
MLOps using MLflow tool"**. The notes cover MLOps fundamentals and then walk
through every major MLflow subsystem — Tracking, Autologging, Tracking Server
architecture, Models, Model Registry, Model Evaluation, Projects, and an
end-to-end AWS SageMaker deployment — using a running example: training an
**ElasticNet / Ridge / Lasso regression model to predict wine quality** on the
red wine quality dataset, and later a **house price prediction** regression
project deployed via AWS CodeCommit → SageMaker → MLflow Tracking Server on
EC2. This CLAUDE.md distills the reusable, factual content (function
signatures, CLI flags, config tables, architecture diagrams-as-text) so a
future session doesn't need to re-read the raw notes.

## 2. Course topic map

1. **What is MLOps? / Why MLflow** (`Untitled.md`) — MLOps as "DevOps + ML",
   the ML lifecycle silo problem (data scientists vs. engineers), technical
   debt in ML systems, versioning/monitoring/CI-CD-CT concepts, and an intro
   to MLflow's four components (Tracking, Projects, Models, Model Registry),
   its Databricks origins, and language-agnostic REST/CLI design.
2. **Tracking fundamentals** (`Untitled 1.md`) — building a plain
   scikit-learn ElasticNet wine-quality regressor, then instrumenting it with
   `mlflow.start_run`, `log_param(s)`, `log_metric(s)`, `log_model`; the
   `mlruns` local directory layout (`meta.yaml`, `tags/`, `params/`,
   `metrics/`, `artifacts/`); the MLflow UI; and the full core tracking API
   (`set_tracking_uri`, `create_experiment`, `set_experiment`, `start_run`,
   `end_run`, `log_artifact(s)`, `get_artifact_uri`, tag functions).
3. **Tags, multi-run/multi-experiment patterns, autologging, and Tracking
   Server architecture** (`Mlfow-3.md`, long — ~2485 lines) — `set_tags`,
   system tags (`mlflow.runName`, `mlflow.source.*`, etc.), running many runs
   /experiments in one script (ElasticNet vs Ridge vs Lasso comparison),
   `mlflow.autolog()` / `mlflow.sklearn.autolog()` parameters, then a deep
   dive into Tracking Server storage (backend store vs artifact store) and
   six deployment scenarios (localhost, localhost+SQLite, localhost+server,
   remote server+remote storage, proxied artifact access, artifacts-only
   proxy mode). Also covers MLflow Models storage format (`MLmodel` file,
   flavors, conda/venv/requirements files) and model signatures/input
   examples/enforcement in detail.
4. **Model Registry** (`Model registry component.md`) — registry concepts
   (versioning, stages → aliases), registering via UI vs API
   (`log_model(registered_model_name=...)`, `mlflow.register_model()`),
   loading registered models (`models:/name/version`), and bringing
   externally-trained (non-MLflow) models into the registry.
5. **Model API** (`MLflow Model api.md`) — `mlflow.sklearn.save_model` /
   `log_model` / `load_model` signatures, model URI formats, and building
   fully custom Python models with `mlflow.pyfunc.PythonModel` (wrapper
   classes, `load_context`/`predict`, custom `conda_env`/`artifacts` dicts).
6. **Custom flavors & Model Evaluation** (`MLflow model evaluation.md`) —
   building a true custom MLflow flavor (e.g. `sktime`) with
   `save_model`/`log_model`/`load_model` functions and an `MLmodel` flavor
   entry, then the full `mlflow.evaluate()` API: parameters, custom metrics/
   artifacts, `validation_thresholds` + `MetricThreshold` baseline-model
   comparisons, and the MLflow UI's run-comparison plots (parallel
   coordinates, scatter, box, contour).
7. **MLflow Projects & MLflow Client** (`Ml flow projects 1.md`, ~1444
   lines) — the `MLproject` file format (name, environments: system/venv/
   conda/docker, entry points, parameter types), running projects via CLI
   (`mlflow run`) and API (`mlflow.projects.run`), and the low-level
   `MLflowClient` class for programmatic experiment/run/model management
   (create/get/rename/delete/restore/search for both experiments and runs).
8. **End-to-end AWS deployment, part 1** (`Mlflow E2E.md`, ~1211 lines) — a
   full MLOps pipeline: AWS CodeCommit repo, MLflow Tracking Server on EC2
   (backed by SQLite + S3 artifact store), a house-price-prediction project
   (`data.py`/`train.py`/`params.py`/`utils.py`), hyperparameter sweeps via
   `sklearn.model_selection.ParameterGrid` across ElasticNet/Ridge/XGBoost,
   running training via an `MLproject`/`run.py` pair, then moving
   experimentation into a SageMaker Notebook instance (IAM roles, Git
   integration), comparing runs, and registering best models with aliases.
9. **End-to-end AWS deployment, part 2** (`ML flow project.md`) — building
   and pushing a SageMaker-ready Docker image
   (`mlflow sagemaker build-and-push-container`), deploying a SageMaker
   endpoint via `mlflow.deployments.get_deploy_client("sagemaker")` +
   `create_deployment(...)`, and performing inference against the live
   endpoint with `boto3` (`invoke_endpoint`).

---

## 3. Key MLflow concepts & APIs (reference / cheat-sheet)

### 3.1 Tracking — core concepts

- **Experiment**: a high-level grouping containing N runs (one ML problem).
- **Run**: one execution; records code version, hyperparameters, metrics,
  tags, artifacts, and gets a unique `run_id`.
- Local storage: `mlruns/<experiment_id>/<run_id>/` containing
  `meta.yaml`, `params/`, `metrics/`, `tags/`, `artifacts/`.
- Experiment-level `meta.yaml`: `artifact_location`, `creation_time`,
  `experiment_id`, `last_updated_time`, `lifecycle_stage`, `name`.
- Run-level `meta.yaml`: `artifact_uri`, `experiment_id`, `run_id`,
  `run_name`, `start_time`/`end_time`, `status`, `tags`, `user_id`.
- Environment reproducibility files auto-generated per run/model:
  `conda.yaml` (conda env), `python_env.yaml` (pip venv), `requirements.txt`.

### 3.2 Tracking — Python API reference

```python
mlflow.set_tracking_uri(uri)     # "" -> ./mlruns ; "my_tracks" -> ./my_tracks
                                  # "file:/abs/path" (no drive letters, e.g. no D:)
                                  # "http://host:port" ; "databricks://profileName"
mlflow.get_tracking_uri()        # -> current uri (no args)

mlflow.create_experiment(name: str, artifact_location: Optional[str]=None,
                          tags: Optional[Dict[str,Any]]=None) -> experiment_id: str
mlflow.set_experiment(experiment_name: Optional[str]=None,
                       experiment_id: Optional[str]=None) -> mlflow.entities.Experiment
    # set_experiment(name=...) auto-creates if missing; set_experiment(id=...) throws if missing
mlflow.get_experiment(experiment_id) -> Experiment  # .name .experiment_id .artifact_location
                                                     # .tags .lifecycle_stage .creation_timestamp

mlflow.start_run(run_id: Optional[str]=None, experiment_id: Optional[str]=None,
                  run_name: Optional[str]=None, nested: bool=False,
                  tags: Optional[Dict[str,Any]]=None,
                  description: Optional[str]=None) -> mlflow.ActiveRun
    # experiment resolution precedence: set_experiment()/create_experiment() in code
    #   > MLFLOW_EXPERIMENT_NAME env var > MLFLOW_EXPERIMENT_ID env var > server default
mlflow.end_run(status='FINISHED')  # status: RUNNING|SCHEDULED|FAILED|FINISHED|KILLED
mlflow.active_run()          # current ActiveRun (use inside start_run/end_run block)
mlflow.last_active_run()     # most recently completed run

mlflow.log_param(key: str, value: Any) -> value
mlflow.log_params(params: Dict[str, Any]) -> None
mlflow.log_metric(key: str, value: float, step: Optional[int]=None) -> None
mlflow.log_metrics(metrics: Dict[str, float], step: Optional[int]=None) -> None
mlflow.log_artifact(local_path, artifact_path: Optional[str]=None) -> None
mlflow.log_artifacts(local_dir, artifact_path: Optional[str]=None) -> None
mlflow.get_artifact_uri(artifact_path: Optional[str]=None) -> str
    # no arg -> run's artifact root; with arg -> that artifact's absolute URI

mlflow.set_tag(key: str, value: Any) -> None      # key up to ~250 chars
mlflow.set_tags(tags: Dict[str, Any]) -> None     # only valid between start_run/end_run
```

- Special-value note: some backends (e.g. SQLAlchemy) clamp ±infinity to max
  float. All backend stores support metric/param string values up to length
  5000 (some support more).

### 3.3 System tags (auto-created every run, prefix `mlflow.`)

| Tag Key | Description |
| --- | --- |
| mlflow.logModel.history | Model registry / model version history |
| mlflow.runName | Name of the run |
| mlflow.source.name | Source file the run was generated from (e.g. main.py) |
| mlflow.source.type | Source execution type (local, cloud, etc.) |
| mlflow.user | User who ran the code |
| mlflow.note.content | Descriptive note (user-overridable) |
| mlflow.parentRunId | Parent run ID (for nested runs) |
| mlflow.source.git.commit | Git commit hash of executed code |
| mlflow.source.git.branch | Git branch of executed code |
| mlflow.source.git.repoURL | Git repo URL code was cloned from |
| mlflow.project.env | Runtime context used by MLflow project (docker/conda) |
| mlflow.docker.image.id | Docker image ID used for the run |

Note: the MLflow **UI hides system tags** by default — only user tags show;
the local `tags/` folder on disk contains both.

### 3.4 Multiple runs / multiple experiments

- Use multiple runs in one experiment for: incremental training, model
  checkpointing, hyperparameter tuning, multi-dataset evaluation, feature
  engineering comparisons, cross-validation folds.
- Use **separate experiments** when moving to a genuinely different
  algorithm/hyperparameter family (e.g. ElasticNet vs Ridge vs Lasso), one
  experiment when just varying values of the same algorithm's hyperparams.
- Course example compared: ElasticNet (`alpha`+`l1_ratio`), Ridge (`alpha`
  = L2 penalty only), Lasso (`alpha` = L1 penalty only) — three experiments
  `exp_multi_EL`, `exp_multi_Ridge`, `exp_multi_Lasso`, three runs each.

### 3.5 Autologging

```python
mlflow.autolog(log_models=True, log_input_examples=False,
                log_model_signatures=True, log_datasets=True,
                disable=False, exclusive=False,
                disable_for_unsupported_versions=False, silent=False)
```
- Must be called **before** training (`.fit()`) — it instruments library
  internals; calling after training captures nothing.
- `log_input_examples` and `log_model_signatures` only take effect if
  `log_models=True`.
- `exclusive=True` → autologged content is NOT attached to user-created
  fluent runs; `exclusive=False` (typical) → attached to the active run.
- `disable_for_unsupported_versions=True` avoids logging on
  untested/incompatible library versions.
- Supported libraries: scikit-learn, Keras, Gluon, XGBoost, LightGBM,
  Statsmodels, Spark, Fastai, PyTorch.
- Input datasets themselves are **not** captured by autolog — still need
  manual `mlflow.log_artifact()` for the raw data file.
- Autolog struggles with customized/non-standard models — fall back to
  explicit `mlflow.sklearn.log_model()` in that case.

```python
mlflow.sklearn.autolog(...)   # inherits all mlflow.autolog() params, plus:
    max_tuning_runs=...              # cap child runs for GridSearch/RandomizedSearch etc.
    log_post_training_metrics=True   # logs MAE/RMSE/R2 etc. post-fit
    serialization_format=...         # mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE
                                      # or SERIALIZATION_FORMAT_CLOUDPICKLE
    registered_model_name=...        # auto-registers a new version on every training run
    pos_label=...                    # binary classification only; ignored for regression;
                                      # breaks multi-class metric computation if misused
```

### 3.6 Tracking Server & Storage architecture

- **Backend Store**: metadata (experiment/run names/IDs, params, metrics,
  tags). Options: File Store, or DB Store (SQLite / MySQL / PostgreSQL via
  SQLAlchemy).
- **Artifact Store**: actual files (models, plots, datasets). Options: local
  filesystem, or cloud object storage (S3, Azure Blob, GCS).
- **Networking**: REST API (HTTP) or RPC (gRPC).
- Server start command:
  ```bash
  mlflow server --backend-store-uri sqlite:///mlflow.db \
                 --default-artifact-root ./mlflow-artifacts \
                 --host 127.0.0.1 --port 5000
  ```
  - `--backend-store-uri`: `sqlite:///mlflow.db`, `mysql://<db>`, etc.
  - `--default-artifact-root`: only affects experiments created *after* the
    flag is set — does not retroactively migrate old experiments.
  - If `--serve-artifact` disabled and no root given → defaults to `./mlruns`.
- Point client code at the server:
  ```python
  mlflow.set_tracking_uri("http://127.0.0.1:5000")
  ```
- Artifact proxying: the tracking server can act as an **HTTP artifact
  proxy** so clients never need direct S3/GCS/HDFS credentials — useful for
  restricted-network or security-sensitive orgs. Exclusive proxy mode:
  ```bash
  mlflow server --artifacts-destination s3://bucket_name --artifacts-only --host remote_host
  ```
  (disables all metadata/run functionality — artifacts only.)

**Six standard deployment scenarios** (official MLflow docs, covered in
`Mlfow-3.md`):

| # | Scenario | Backend store | Artifact store | Notes |
| --- | --- | --- | --- | --- |
| 1 | Localhost | `./mlruns` (FileStore) | `./mlruns` | zero setup, `pip install mlflow` default |
| 2 | Localhost + SQLite | SQLite via SQLAlchemyStore | `./mlruns` | `mlflow.set_tracking_uri("sqlite:///mlflow.db")` |
| 3 | Localhost + Tracking Server | FileStore or DB (`--backend-store-uri`) | local dir | server as separate local process, REST on port 5000 |
| 4 | Remote backend + remote artifacts | remote DB (e.g. Postgres) | remote object store (e.g. S3 via `boto3`/`S3ArtifactRepository`) | production-grade, multi-data-scientist |
| 5 | Remote server, proxied artifact access | remote DB | remote object store, but client never touches it directly | tracking server does assumed-role auth to S3, proxies via `HttpArtifactRepository` |
| 6 | Tracking server as artifacts-only proxy | none (disabled) | remote object store only | `--artifacts-only --artifacts-destination s3://...` |

Scenario 4 launch example:
```bash
mlflow server --backend-store-uri postgresql://user:password@postgres:5432/mlflowdb \
               --default-artifact-root s3://bucket_name --host remote_host --no-serve-artifacts
```

> Security note (from notes): when using the artifact proxy, end users
> effectively inherit the tracking server's assumed-role permissions — scope
> that role tightly.

### 3.7 MLflow Models — storage format

Default "directory of files" layout (~6-7 files) produced by `log_model`/
`save_model`:
- `MLmodel` — the master YAML config; most important file. Lists each
  **flavor** (e.g. `python_function`, `sklearn`) with its own config block
  (`loader_module`, `model_path`/`pickled_model`, `predict_fn`,
  `serialization_format`, `sklearn_version`, `code`, etc.), plus top-level
  `mlflow_version`, `mlflow_uid` (registry id), `run_id`,
  `saved_input_example_info` (`artifact_path`, `pandas_orient`, `type`), and
  `signature`.
- `model.pkl` — the serialized model (pickle/cloudpickle).
- `input_example.json` — optional, `{"columns": [...], "data": [...]}` for
  tabular data (≥10 rows typically).
- `conda.yaml` / `python_env.yaml` / `requirements.txt` — three equivalent
  ways to reproduce the training environment (conda, pip-venv,
  install-into-existing-env respectively). Default channel is
  `conda-forge` (older MLflow used `defaults`, deprecated due to Anaconda
  licensing changes).

Other supported storage formats besides directory-of-files: single file,
Python function, container image (Docker).

### 3.8 Model Signatures & Input Examples

- **Signature**: input/output schema (types + shapes). Two kinds:
  - **Column-based** — named columns with MLflow types (`double`,
    `integer`, `string`, ...); supported by all flavors.
  - **Tensor-based** — `dtype` (NumPy dtype), `shape` (`-1` = variable batch
    dim), optional `name`; only supported by deep-learning flavors
    (TensorFlow, Keras, PyTorch, ONNX, Gluon).
- **Input Example**: a literal sample of expected input data — separate
  concept from the signature (signature = schema, input example = data).
- Autologging logs signature by default (`log_model_signatures=True`); input
  examples only if `log_input_examples=True` explicitly set.
- Manual construction:
  ```python
  from mlflow.models.signature import ModelSignature
  from mlflow.types.schema import ColSpec, Schema

  input_schema = Schema([ColSpec(col["type"], col["name"]) for col in input_data])
  output_schema = Schema([ColSpec(col["type"]) for col in output_data])
  signature = ModelSignature(inputs=input_schema, outputs=output_schema)

  mlflow.sklearn.log_model(sk_model=lr, artifact_path="model", signature=signature,
                            input_example=input_example)  # input_example: dict of column->np.array,
                                                           # OR {"columns": np.array(...), "data": np.array(...)}
  ```
- Auto-inference (preferred over manual typing):
  ```python
  from mlflow.models import infer_signature
  signature = infer_signature(X_test, predicted_qualities)  # y optional -> input-only schema
  ```

**Signature enforcement** (applied by MLflow deployment tools / `pyfunc`
loading, NOT applied to natively-loaded models):
- *Signature/schema enforcement*: raises if inputs don't match schema,
  checked before the model implementation runs.
- *Name-ordering enforcement*: if schema has names, matches by name and
  reorders; missing input → exception; extra input → ignored. If schema has
  no names, matches by position (count only).
- *Input-type enforcement*: column-based signatures allow lossless
  conversions (`int`→`long`, `int`→`double`) but not lossy ones
  (`long`→`double` fails); tensor-based signatures are strict, no
  conversion at all.

### 3.9 Model Registry

- Requires a **database backend store** (registry metadata needs a DB, not
  just a file store).
- Register during logging:
  ```python
  mlflow.sklearn.log_model(lr, "model", registered_model_name="ElasticNet_API")
  # new name -> Version 1; existing name -> next version auto-incremented
  ```
- Register after the fact:
  ```python
  mlflow.register_model(model_uri, name, await_registration_for=300, *, tags=None)
  # model_uri: "runs:/<run_id>/<artifact_path>" (models:/ URIs NOT supported here)
  # await_registration_for: seconds to wait for READY status; 0/None = skip wait
  # tags: dict -> converted to ModelVersionTag objects
  ```
- Load a registered model:
  ```python
  mlflow.set_tracking_uri("http://127.0.0.1:5000")   # must match server that holds the model
  model = mlflow.pyfunc.load_model(model_uri="models:/elastic-api-2/1")  # models:/<name>/<version>
  # also supports models:/<name>/<stage> (legacy) and models:/<name>@<alias> (current)
  ```
- Registering an **external** (non-MLflow-trained) model: load the pickle,
  then `mlflow.sklearn.log_model(loaded_model, artifact_path="model",
  serialization_format="cloudpickle", registered_model_name="...")` inside a
  run pointed at the tracking server.
- **Stages → Aliases**: legacy fixed stages were `Staging` / `Production` /
  `Archive` (a version in Staging/Production cannot be deleted until moved
  to Archive). Newer MLflow replaces this with flexible, arbitrary
  **Aliases** (e.g. `@Champion`, `@Challenger`) — unlimited custom names,
  can still reuse the old stage names as aliases if desired.
- Metadata can be set at **model level** (applies to all versions — e.g.
  overall description) or **version level** (applies to one version — e.g.
  hyperparameters used for that specific training run).
- `MLflowClient` (low-level, REST-backed) complements the high-level
  `mlflow.*` functions — same capabilities, more granular control, used for
  scripted/programmatic registry & experiment/run management (see §3.11).

### 3.10 Model API — save / log / load (`mlflow.sklearn` as example)

```python
mlflow.sklearn.save_model(
    sk_model, path,                       # local path, NOT run-relative
    conda_env=None,                       # dict or path to .yaml; else inferred
    code_paths=None,                      # list of local file deps (e.g. training code)
    mlflow_model=None,                    # mlflow.models.Model flavor object
    serialization_format="cloudpickle",   # or "pickle"
    signature=None, input_example=None,
    pip_requirements=None,                # REPLACES inferred requirements (can't combine w/ extra_pip_requirements)
    extra_pip_requirements=None,          # APPENDS to inferred requirements
    pyfunc_predict_fn="predict",          # e.g. "predict_proba"
    metadata=None,                        # experimental
)
# produces flavors: mlflow.sklearn + mlflow.pyfunc

mlflow.sklearn.log_model(
    sk_model, artifact_path,              # run-relative, not local path
    registered_model_name=None,           # auto-registers if provided
    await_registration_for=300,           # seconds; 0/None = skip
    ... # (shares remaining params with save_model)
)

mlflow.sklearn.load_model(model_uri, dst_path=None)
```

Model URI formats:

| Type | Example |
| --- | --- |
| Local path | `/Users/me/path/to/local/model` |
| Relative path | `relative/path/to/local/model` |
| S3 bucket | `s3://my_bucket/path/to/model` |
| MLflow run | `runs:/<run_id>/run-relative/path/to/model` |
| Registry (version) | `models:/<model_name>/<model_version>` |
| Registry (stage/alias) | `models:/<model_name>/<stage>` |

- Key distinction: `log_model` → visible in MLflow UI (run artifact);
  `save_model` → local dir only, run's Artifacts section stays empty.

### 3.11 MLflowClient (low-level API)

```python
from mlflow.client import MLflowClient   # or mlflow.MlflowClient
mlflow.set_tracking_uri("http://127.0.0.1:5000")
client = MLflowClient()
```

Experiment management:
```python
client.create_experiment(name, tags={...}) -> experiment_id
client.set_experiment_tag(experiment_id, key, value)   # one tag per call
client.get_experiment(experiment_id) -> Experiment
client.get_experiment_by_name(name) -> Experiment | None
client.rename_experiment(experiment_id, new_name)      # no return value
client.delete_experiment(experiment_id)
client.restore_experiment(experiment_id)
client.search_experiments(view_type=ViewType.ACTIVE_ONLY|DELETED_ONLY|ALL,
                           max_results=..., filter_string="...",
                           order_by="...", page_token=...) -> PagedList[Experiment]
    # filter_string identifiers: name, creation_time, last_update_time, tags.<key>
    # comparators: string/tag ==, !=, LIKE, ILIKE ; numeric ==, !=, <, <=, >, >=
    # combine with AND
```

Run management:
```python
run = client.create_run(experiment_id, tags={...}, run_name=..., start_time=...)
    # creates run WITHOUT active-run context; must pass run_id explicitly to all logging calls
run = client.get_run(run_id)
    # run.data.tags / run.info.experiment_id / run.info.run_id / run.info.run_name
    # run.info.lifecycle_stage / run.info.status

client.log_param(run_id, key, value)
client.log_metric(run_id, key, value)
client.log_artifact(run_id, local_path)

client.set_terminated(run_id, status="FINISHED")   # default status FINISHED; can set FAILED etc.
client.update_run(run_id, status="FINISHED", run_name="...")  # can change status AND name

client.get_metric_history(run_id, metric_key) -> list of {step, timestamp, value}
    # esp. useful for per-epoch metrics in deep learning
client.list_artifacts(run_id, path=None) -> list of {path, file_size}
client.delete_run(run_id)     # lifecycle_stage: active -> deleted
client.restore_run(run_id)    # lifecycle_stage: deleted -> active
client.search_runs(...)       # same filtering semantics as search_experiments
```

- `mlflow.start_run()` (fluent API) sets an **active run context** — logging
  calls need no `run_id`. `client.create_run()` does **not** set an active
  context — every logging call must pass `run_id` explicitly.

### 3.12 Model Evaluation — `mlflow.evaluate()`

```python
mlflow.evaluate(
    model,                     # pyfunc instance or model URI; only pyfunc flavor supported
    data,                      # np array/list (features only), Pandas/Spark DF (features+labels;
                                #   Spark capped at first 10,000 rows), or mlflow.data.dataset.Dataset
    *, model_type,             # "regressor" | "classifier" | "question-answering" | "text-summarization"
    targets=None,               # np array/list, DF column name, or omitted if Dataset provides it
    dataset_path=None,          # for lineage tracking; logged to mlflow.datasets tag; no double-quotes
    feature_names: Optional[list] = None,
    evaluators=None,             # list of evaluator names; default: mlflow.models.list_evaluators()
    evaluator_config=None,       # dict, or nested dict per-evaluator if multiple evaluators
    custom_metrics=None,         # list of EvaluationMetric via mlflow.models.make_metric
    custom_artifacts=None,       # list of functions producing custom artifacts (.json/.csv/etc.)
    validation_thresholds=None,  # dict[metric_name] -> MetricThreshold
    baseline_model=None,         # URI of baseline model for comparison
    env_manager='local',
)
```

- **Metrics logged**: classification → accuracy, precision, recall, F1,
  AUC-ROC; regression → MSE, MAE (RMSE/R2 also commonly seen in examples).
- **Plots**: confusion matrix, precision-recall curve, ROC curve.
- **Explainability**: SHAP-based by default (`pip install shap` required);
  `evaluator_config` options include `log_model_explainability` (bool,
  default True), `explainability_samples` (default 2000),
  `explainability_algorithm` (`exact`/`partition`/`kernel`/auto),
  `explainability_kernel` (`identity`/`logit`),
  `max_classes_for_multiclass_roc`, `metric_prefix`,
  `log_metrics_with_dataset_info` (default True), `pos_label`, `average`
  (default `"weighted"`), `sample_weights`.
- Custom metric example:
  ```python
  def root_mean_squared_error(eval_df, builtin_metrics):
      return np.sqrt(np.abs(eval_df["prediction"] - eval_df["target"]) ** 2).mean()
  rmse_metric = mlflow.models.make_metric(eval_fn=root_mean_squared_error, greater_is_better=False)
  ```
- **Baseline / threshold validation**:
  ```python
  from mlflow.models import MetricThreshold
  thresholds = {
      "mean_squared_error": MetricThreshold(
          threshold=0.6,             # absolute pass/fail bound
          min_relative_change=0.05,  # min % improvement required vs baseline
          # mean_absolute_change also available (absolute improvement vs baseline)
          greater_is_better=False,   # aka higher_is_better; interchangeable
      )
  }
  mlflow.evaluate(model_uri, data, targets="quality", model_type="regressor",
                   evaluators=["default"], validation_thresholds=thresholds,
                   baseline_model=baseline_model_uri)
  # raises ModelValidationError if criteria not met
  ```
- Comparison UI: select ≥2 runs → **Compare** → Parallel Coordinates Plot,
  Scatter Plot, Box Plot, Contour Plot, plus side-by-side Params/Metrics/Tags
  tables and Run Details.

### 3.13 Custom Python Models & Custom Flavors

- **Custom Python Model** (for libraries without a built-in flavor, or
  custom inference logic) — still saved as `python_function` flavor:
  ```python
  class SklearnWrapper(mlflow.pyfunc.PythonModel):
      def load_context(self, context):
          self.sklearn_model = joblib.load(context.artifacts['sklearn_model'])
      def predict(self, context, model_input):
          return self.sklearn_model.predict(model_input)

  mlflow.pyfunc.log_model(
      artifact_path="sklearn_wrapper",
      python_model=SklearnWrapper(),        # instance of PythonModel subclass, cloudpickled
      artifacts={"sklearn_model": sklearn_model_path},  # name -> file path map
      code_path=["main.py"],                # code dependencies to package
      conda_env=conda_env,                  # dict: channels/dependencies/pip/name
  )
  model = mlflow.pyfunc.load_model(f"runs:/{run.info.run_id}/{artifact_path}")
  predictions = model.predict(data)
  ```
- **Custom Flavor** (full custom serialization, e.g. a hypothetical
  `sktime` flavor) — heavier-weight than a custom pyfunc model, rarely
  needed in practice:
  1. Implement serialize/deserialize logic.
  2. Build flavor directory structure (`save_model`/`log_model`/
     `load_model` functions; `get_default_pip_requirements`,
     `get_default_conda_env`).
  3. Register flavor (own subdirectory under `mlflow/models/`).
  4. Optional flavor-specific tools/wrapper class exposing `predict(self,
     dataframe, params=None) -> pd.DataFrame` for `python_function`
     compatibility.
  - The `MLmodel` file ends up describing multiple flavors simultaneously
    (e.g. `python_function` + the custom flavor).

### 3.14 MLflow Projects (`MLproject` file)

- File must be named exactly `MLproject`, no extension, YAML format.
- Three core sections: `name`, environment, `entry_points`.
- **Environments** (choose one):
  ```yaml
  python_env: files/config/python_env.yml   # virtualenv/pyenv-based
  conda_env: conda.yaml                      # conda (can export via
                                              # `conda env export --name <env> > conda.yml`)
  docker_env:
    image: mlflow-docker-example-environment          # local Docker Hub lookup
    # or a full registry path, e.g. ECR:
    # image: 012345678910.dkr.ecr.us-west-2.amazonaws.com/my-image:7.0
    volumes: ["/host/path:/container/path"]
    environment: [["NEW_VAR", "value"], "VAR_COPIED_FROM_HOST"]
  # system environment = no entry at all (uses host OS's Python)
  ```
  Build a new image from a base with `mlflow run ... --build-image`.
- **Entry points**:
  ```yaml
  entry_points:
    ElasticNet:
      command: "python main.py --alpha ${alpha} --l1_ratio ${l1_ratio}"
      parameters:
        alpha:
          type: float      # string | float | path | uri
          default: 0.4
        l1_ratio:
          type: float
          default: 0.4
  ```
  - Command placeholders `${name}` are auto-escaped via `shlex.quote`.
  - Parameter types: `string`, `float` (validated numeric), `path` (relative
    → absolute conversion, downloads distributed URIs locally), `uri`
    (for distributed storage-aware code, e.g. Spark).
  - Undeclared params used in `command` default to `string` type.
  - Each entry point = exactly one command (multiple params OK).

**Running projects**:
```bash
mlflow run [OPTIONS] URI
  -e/--entry-point NAME          # default "main"
  -v/--version VERSION           # git ref, for git-hosted projects
  -P/--param-list NAME=VALUE     # repeatable
  -A/--docker-args NAME=VALUE    # passed to `docker run`
  --experiment-name / --experiment-id
  -b/--backend local|databricks|kubernetes(experimental)   # default local
  -c/--backend-config FILE       # JSON file/string, backend-specific
  --env-manager local|virtualenv|conda
  --storage-dir DIR              # local backend only
  --run-id RUN_ID                # internal use
  --run-name NAME
  --build-image                  # Docker projects only
```
Environment variable defaults: `MLFLOW_EXPERIMENT_NAME`,
`MLFLOW_EXPERIMENT_ID`, `MLFLOW_TMP_DIR` (maps to `--storage-dir`),
`MLFLOW_TRACKING_URI`.

Example:
```bash
export MLFLOW_TRACKING_URI=http://127.0.0.1:5000
mlflow run . --entry-point elastic_net -p alpha 0.5 -p l1_ratio 0.5 --experiment-name "Project exp 1"
```

**API equivalent**:
```python
mlflow.projects.run(uri=".", entry_point="Training", experiment_name="Elasticset",
                     conda_env="conda", synchronous=True)  # synchronous default True;
                                                            # False = fire-and-forget/async
```
- `mlflow doctor` CLI command diagnoses local MLflow installation/config
  issues.

### 3.15 Deployment / End-to-End (AWS SageMaker path)

Architecture: local repo → AWS CodeCommit → EC2 (hosts MLflow Tracking
Server, backed by SQLite + S3 artifact root) → SageMaker (training +
endpoint) → S3 (artifacts) → SageMaker Endpoint → inference results.

**EC2 Tracking Server bootstrap**:
```bash
sudo apt update
pip install pipenv virtualenv
mkdir mlflow && cd mlflow
pipenv install mlflow awscli boto3 setuptools
pipenv shell
aws configure          # Access Key ID / Secret / region (us-east-1) / output format
mlflow server --host 0.0.0.0 --backend-store-uri sqlite:///mlflow.db \
               --default-artifact-root s3://<bucket-name>
```
- Open inbound TCP port 5000 in the EC2 security group to reach the UI/API.
- Tracking URI from clients: `http://<public-ipv4-dns>:5000`.

**IAM role for SageMaker notebook** needs: `AmazonSageMakerFullAccess`,
`AmazonS3FullAccess`, `AWSCodeCommitFullAccess`,
`AmazonEC2ContainerRegistryFullAccess`.

**Hyperparameter sweep pattern** (`train.py`):
```python
from sklearn.model_selection import ParameterGrid
for params in ParameterGrid(elasticnet_params_grid):
    with mlflow.start_run():
        tr = ElasticNet(**params); tr.fit(X_train, y_train)
        y_pred = tr.predict(X_val)
        metrics = eval_metrics(y_val, y_pred)   # MSE, MAPE, R2 in this project
        mlflow.log_input(mlflow.data.from_numpy(X_train.toarray()), context="training dataset")
        mlflow.log_input(mlflow.data.from_numpy(X_val.toarray()), context="validation dataset")
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.sklearn.log_model(sk_model=tr, artifact_path="model",
                                  input_example=X_train.toarray(),
                                  registered_model_name="ElasticNet")
```

**Build & push a SageMaker container**:
```bash
mlflow sagemaker build-and-push-container --container-name xgb --env-manager conda
# container-name must be lowercase; env-manager defaults to virtualenv
```

**Deploy a SageMaker endpoint** (`deploy.py`):
```python
from mlflow.deployments import get_deploy_client
config = {
    "execution_role_arn": "...",           # IAM role ARN with SageMaker perms
    "bucket_name": "mlflow-project-artifacts",
    "image_uri": "...",                    # from ECR
    "region": "us-east-1",
    "instance_type": "ml.m5.xlarge",       # avoid t2.medium-class instances — too slow/fails
    "instance_count": 1,
    "synchronous": True,
}
client = get_deploy_client("sagemaker")
client.create_deployment(name="prod-endpoint", model_uri=model_uri,
                          flavor="python_function", config=config)
```

**Inference against the endpoint**:
```python
import boto3, json
smrt = boto3.client("runtime.sagemaker", region_name="us-east-1")
test_data = json.dumps(test_dataset[:10].toarray().tolist(), default=str)
resp = smrt.invoke_endpoint(EndpointName="prod-endpoint",
                             ContentType="application/json", Body=test_data)
prediction = resp["Body"].read().decode("ascii")
```

**Model comparison strategy at scale**: find the best run per experiment
first (ElasticNet best, Ridge best, XGBoost best), then compare only those
top runs against each other before registering; automate the
register-if-better-than-baseline decision using `validation_thresholds` +
`baseline_model` in `mlflow.evaluate()` rather than eyeballing the UI.

---

## 4. Project artifacts in this folder

- **`red-wine-quality.csv`** — the primary dataset used throughout the
  Tracking/Autologging/Model API/Evaluation sections (`Untitled.md` through
  `MLflow model evaluation.md`). 11 physicochemical features (acidity,
  sugar, chlorides, etc.) + `quality` label. Used to train and compare
  **ElasticNet / Ridge / Lasso** regression models across many runs and
  experiments, tuning `alpha` and `l1_ratio`, and to demonstrate every
  logging pattern (manual, autolog, custom pyfunc, evaluation, registry).
- **`wine-dataset/`** — a separate, self-contained (has its own `.git/`)
  companion project directory holding `winequality.csv`,
  `basic+ML+code.py`, and a `Readme.md`. Appears to be a supplementary/
  reference copy of the same wine-quality regression example rather than
  course-note content itself.
- **`hover-notes-images/`** — three PNG screenshots referenced inline by the
  hover-notes via Obsidian-style embeds (e.g.
  `screenshot-01M0FS8E2EJQ5B6V53XNCNG3T8.png`), illustrating specific UI
  moments (multi-experiment setup, autolog config, MLflow Projects API
  section) called out in `Mlfow-3.md` and `Ml flow projects 1.md`.

The later course sections (`Mlflow E2E.md`, `ML flow project.md`) pivot to a
**separate house-price-prediction dataset** (`train.csv`/`test.csv`, not
present in this folder — that project lived in a separate AWS CodeCommit
repo per the notes) to demonstrate the full AWS SageMaker deployment
pipeline; no corresponding CSVs are stored here.

---

## 5. Notes on file organization (duplicates)

This directory contains an Obsidian hover-notes export that ran twice,
producing byte-for-byte content duplicates that differ only in their
`hovernotes-id` frontmatter field. Confirmed duplicate pairs (same file
size, same content):

| Canonical file (read for this summary) | Duplicate (skip) |
| --- | --- |
| `Mlfow-3.md` | `Untitled 2.md` |
| `MLflow model evaluation.md` | `Untitled 3.md` |
| `ML flow project.md` | `Untitled 4.md` |
| `Model registry component.md` | `Model registry component 1.md` |
| `Ml flow projects 1.md` | `Ml flow projects 1 1.md` |

Additionally, `Ml flow projects.md` is a **shorter/earlier duplicate
lecture pass** covering similar Projects/Client content to
`Ml flow projects 1.md` — treat `Ml flow projects 1.md` as canonical for
that topic.

Files actually read to build this document (in course order): `Untitled.md`,
`Untitled 1.md`, `Mlfow-3.md`, `Model registry component.md`,
`MLflow Model api.md`, `MLflow model evaluation.md`,
`Ml flow projects 1.md`, `Mlflow E2E.md`, `ML flow project.md`.

Non-note files in this directory: `-hovernotes.base`,
`-video-screenshots.base`, `-video-screenshots-without-notes.base` are
Obsidian "Bases" config files (not prose content) associated with this
export and were not read for this summary.
