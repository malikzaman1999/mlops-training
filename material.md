# MLOps Learning Materials: Zero to Interview Ready

Last reviewed: 2026-08-11

This is an ordered curriculum, not a list to complete all at once. Learn the
core stack first, build one end-to-end project, and use the optional resources
only when the project creates a reason to learn them.

## Target outcome

By the end of this path, I should be able to:

- explain how MLOps differs from data science and DevOps
- turn notebook code into a tested, reproducible Python project
- track experiments, datasets, parameters, metrics, and model versions
- build an automated training pipeline with validation gates
- expose a model through online or batch inference
- package a service with Docker
- use CI/CD to test and deploy pipeline and serving changes
- monitor service health, data quality, drift, and model quality
- decide when to retrain, promote, roll back, or retire a model
- design and discuss an end-to-end ML platform in an interview

## Recommended core stack

Do not learn five competing tools at the beginning. Use this stack for the
first complete project:

| Concern | First tool |
|---|---|
| Language and packaging | Python, `uv` or `pip`, `pyproject.toml` |
| Modeling | scikit-learn |
| Testing | pytest |
| Code versioning | Git and GitHub |
| Experiment/model tracking | MLflow |
| Data and pipeline versioning | DVC |
| Prediction API | FastAPI |
| Containers | Docker and Docker Compose |
| CI/CD | GitHub Actions |
| Orchestration | Prefect first; Airflow or Kubeflow later |
| Data/model monitoring | Evidently plus service metrics |
| Metrics dashboards | Prometheus and Grafana |
| Cloud deployment | Google Cloud Run first; Vertex AI later |
| Infrastructure as code | Terraform after the first manual deployment |

## 16-week learning order

Adjust the pace, but preserve the order.

### Weeks 1-2: Prerequisites

Learn:

- Python functions, classes, typing, virtual environments, and packaging
- NumPy, pandas, and scikit-learn workflows
- Git commits, branches, pull requests, tags, and `.gitignore`
- shell navigation, files, processes, environment variables, and permissions
- basic SQL and HTTP/REST concepts
- train/validation/test splits, leakage, metrics, and baselines

Resources:

- [Python tutorial](https://docs.python.org/3/tutorial/)
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [Pro Git book](https://git-scm.com/book/en/v2)
- [The Missing Semester: shell tools](https://missing.csail.mit.edu/)
- [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html)
- [DataCamp Machine Learning Scientist in Python](https://www.datacamp.com/tracks/machine-learning-scientist-with-python)

Deliverable: a small model trained from a Python script, with a saved metric
and a reproducible environment.

### Week 3: MLOps concepts and lifecycle

Learn:

- why a model is only one component of a production ML system
- DevOps versus MLOps
- CI, CD, and continuous training (CT)
- the ML lifecycle from data extraction through monitoring
- MLOps maturity levels 0, 1, and 2
- training-serving skew, drift, lineage, reproducibility, and governance

Core reading:

- [Google Cloud: Continuous delivery and automation pipelines in ML](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Local detailed study guide](MLOps/google-cloud-mlops-pipelines.md)
- [Google Cloud Practitioners Guide to MLOps](https://cloud.google.com/resources/mlops-whitepaper)
- [Hidden Technical Debt in Machine Learning Systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf)

Deliverable: draw a system diagram for the model built in weeks 1-2 and label
the data, training, registry, serving, and monitoring paths.

### Week 4: Production-quality Python and testing

Learn:

- move notebook logic into importable modules
- configuration, logging, type hints, and dependency locking
- unit, integration, data, model, and API tests
- deterministic runs and reproducible seeds
- linting, formatting, and pre-commit hooks

Resources:

- [pytest getting started](https://docs.pytest.org/en/stable/getting-started.html)
- [Made With ML: testing code, data, and models](https://madewithml.com/courses/mlops/)
- [pre-commit documentation](https://pre-commit.com/)
- [Ruff documentation](https://docs.astral.sh/ruff/)

Deliverable: tests for feature transformations, schema assumptions, training,
model output shape, and minimum model quality.

### Week 5: Experiment tracking and model management

Learn:

- runs, experiments, parameters, metrics, tags, and artifacts
- comparing candidate models
- model signatures and input examples
- model registry, aliases/stages, promotion, and rollback
- the difference between code, data, experiment, and model versioning

Resources:

- [MLflow machine-learning quickstarts](https://mlflow.org/docs/latest/ml/getting-started/)
- [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/)
- [MLflow Model Registry](https://mlflow.org/docs/latest/ml/model-registry/)

Deliverable: track at least five experiments and register the best validated
model without selecting it by hand-written file names.

### Week 6: Data and pipeline versioning

Learn:

- data lineage and immutable dataset versions
- reproducible pipeline stages and dependency graphs
- parameters, metrics, artifacts, and remote storage
- schema validation, statistical checks, and data-quality gates

Resources:

- [DVC get started](https://dvc.org/doc/start)
- [DVC data pipelines](https://dvc.org/doc/user-guide/pipelines)
- [Great Expectations introduction](https://docs.greatexpectations.io/docs/core/introduction/)

Deliverable: reproduce a model from a Git commit and its corresponding data
version, then intentionally fail the pipeline with invalid input data.

### Week 7: Model serving

Learn:

- online, batch, streaming, edge, and asynchronous inference
- request/response schemas and model contracts
- preprocessing parity between training and serving
- latency, throughput, concurrency, timeouts, and error handling
- health, readiness, and model metadata endpoints

Resources:

- [FastAPI tutorial](https://fastapi.tiangolo.com/tutorial/)
- [FastAPI deployment concepts](https://fastapi.tiangolo.com/deployment/concepts/)
- [MLflow model deployment](https://mlflow.org/docs/latest/ml/deployment/)

Deliverable: an API with `/predict`, `/health`, and `/model-info` endpoints,
plus API integration tests.

### Week 8: Containers and local environments

Learn:

- images, containers, layers, registries, volumes, and networks
- writing a small, cache-efficient Dockerfile
- pinned dependencies, non-root users, and secret handling
- Docker Compose for the API, MLflow, database, and monitoring services

Resources:

- [Docker getting started](https://docs.docker.com/get-started/)
- [Dockerfile best practices](https://docs.docker.com/build/building/best-practices/)
- [Docker Compose quickstart](https://docs.docker.com/compose/gettingstarted/)

Deliverable: run the prediction API from a clean Docker image without relying
on files or packages installed only on the host machine.

### Week 9: Workflow orchestration

Learn:

- tasks, flows/DAGs, dependencies, retries, caching, schedules, and backfills
- idempotency and recovery from partial failures
- pipeline parameters, artifacts, metadata, and observability
- when a Python script is sufficient and when orchestration is justified

Resources:

- [Prefect documentation](https://docs.prefect.io/)
- [Apache Airflow tutorials](https://airflow.apache.org/docs/apache-airflow/stable/tutorial/)
- [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/)

Deliverable: an orchestrated extract, validate, transform, train, evaluate,
register pipeline that can resume safely after a failed step.

### Week 10: CI/CD and continuous training

Learn:

- CI checks for code, data transformations, models, and pipeline components
- building and scanning container images
- development, staging, and production environments
- approval gates, artifacts, release tags, and rollback
- triggers based on code, schedules, new data, drift, or model degradation
- why CT does not mean blindly deploying every newly trained model

Resources:

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [DVC CI/CD for machine learning](https://dvc.org/doc/use-cases/ci-cd-for-machine-learning)
- [Google Cloud MLOps architecture with pipelines and Cloud Build](https://docs.cloud.google.com/architecture/architecture-for-mlops-using-tfx-kubeflow-pipelines-and-cloud-build)

Deliverable: a pull request runs tests; a merge builds an image; a release
deploys to a test environment; model promotion requires validation gates.

### Week 11: Monitoring and drift

Learn:

- infrastructure and service metrics: availability, errors, latency, traffic,
  saturation, CPU, memory, and cost
- data-quality and schema monitoring
- feature drift, prediction drift, concept drift, and model-quality decay
- delayed labels and proxy metrics
- slices/segments, fairness, alert thresholds, and retraining policies
- dashboards, alerts, incident response, rollback, and postmortems

Resources:

- [Evidently documentation](https://docs.evidentlyai.com/)
- [Prometheus getting started](https://prometheus.io/docs/prometheus/latest/getting_started/)
- [Grafana fundamentals](https://grafana.com/tutorials/grafana-fundamentals/)
- [Google Cloud model monitoring overview](https://docs.cloud.google.com/vertex-ai/docs/model-monitoring/overview)

Deliverable: simulate drift, display it on a dashboard, trigger an alert, and
document whether the response should be investigation, rollback, or retraining.

### Week 12: Cloud deployment on Google Cloud

Learn:

- IAM and least privilege
- object storage, container registries, managed compute, logs, and secrets
- deploying a container to Cloud Run
- managed training, pipelines, model registry, endpoints, and monitoring in
  Vertex AI
- budgets, quotas, autoscaling, and cost controls

Resources:

- [Cloud Run quickstarts](https://docs.cloud.google.com/run/docs/quickstarts)
- [Vertex AI Pipelines introduction](https://docs.cloud.google.com/vertex-ai/docs/pipelines/introduction)
- [Vertex AI Model Registry introduction](https://docs.cloud.google.com/vertex-ai/docs/model-registry/introduction)
- [Secret Manager documentation](https://docs.cloud.google.com/secret-manager/docs)

Deliverable: deploy the containerized API to a test project, with secrets kept
outside the repository and logs visible in the cloud console.

### Weeks 13-14: Infrastructure and platform concepts

Learn:

- infrastructure as code and environment parity
- Kubernetes pods, deployments, services, config, secrets, probes, and scaling
- feature stores and point-in-time-correct training sets
- build-versus-buy decisions for an ML platform

Resources:

- [Terraform tutorials](https://developer.hashicorp.com/terraform/tutorials)
- [Kubernetes basics](https://kubernetes.io/docs/tutorials/kubernetes-basics/)
- [Feast quickstart](https://docs.feast.dev/getting-started/quickstart)
- [Kubeflow documentation](https://www.kubeflow.org/docs/)

Deliverable: provision one repeatable test environment with Terraform. Treat
Kubernetes as optional until a simpler deployment platform is insufficient.

### Weeks 15-16: Capstone and interview preparation

Build one complete system and be ready to explain every design decision.

Required capstone components:

1. A measurable business and ML objective.
2. Versioned source code, environment, data, and model artifacts.
3. Automated data validation and leakage checks.
4. Reproducible training with MLflow tracking.
5. A model-quality gate against a baseline or production model.
6. A model registry and documented promotion/rollback policy.
7. Batch or online serving with a documented schema.
8. Docker packaging and local Compose setup.
9. Unit, integration, pipeline, model, and API tests.
10. CI/CD workflow with protected production promotion.
11. Service, data, drift, and model-quality monitoring.
12. An architecture diagram, runbook, and cost/security notes.

Use [the interview question bank](MLOps/interview-questions.md) and answer each
question aloud in two minutes or less before attempting the scenario questions.

## Full courses

Take one primary course and use the others as references:

1. [DataCamp Machine Learning Engineer](https://www.datacamp.com/tracks/machine-learning-engineer) — structured introduction to MLOps, MLflow, DVC, Docker, CI/CD, data pipelines, and monitoring.
2. [MLOps Zoomcamp](https://github.com/DataTalksClub/mlops-zoomcamp) — free, project-oriented training covering tracking, orchestration, deployment, monitoring, testing, CI/CD, and infrastructure as code.
3. [Made With ML](https://madewithml.com/courses/mlops/) — production ML design, data, modeling, testing, reproducibility, serving, CI/CD, and monitoring.
4. [Full Stack Deep Learning](https://fullstackdeeplearning.com/) — systems thinking for ML products; use after the basic toolchain.

Recommended order for this repository: DataCamp for guided exercises, then
MLOps Zoomcamp or Made With ML for the main portfolio project.

## Books and deeper reading

- *Designing Machine Learning Systems* by Chip Huyen — system design,
  deployment, monitoring, data distribution shifts, and platform thinking.
- *Machine Learning Design Patterns* by Valliappa Lakshmanan, Sara Robinson,
  and Michael Munn — reusable solutions to data, training, serving, and
  reproducibility problems.
- *Practical MLOps* by Noah Gift and Alfredo Deza — automation, cloud, CI/CD,
  and operational workflows.
- [Rules of Machine Learning](https://developers.google.com/machine-learning/guides/rules-of-ml) — practical engineering guidance for production ML.
- [Machine Learning: The High Interest Credit Card of Technical Debt](https://research.google/pubs/machine-learning-the-high-interest-credit-card-of-technical-debt/) — why shortcuts in ML systems accumulate operational cost.
- [Hidden Technical Debt in Machine Learning Systems](https://papers.nips.cc/paper/5656-hidden-technical-debt-in-machine-learning-systems.pdf) — system-level failure modes beyond model code.

## Documentation habit

For every study session:

1. Add the date and source to `MLOps/notes.md`.
2. Write the concept in my own words.
3. Add one concrete example from my project.
4. Record one failure or confusing point and how I resolved it.
5. Create at least one interview question.
6. Commit the notes and code together when they represent one learning unit.

Do not save secrets, cloud credentials, private datasets, or large generated
models in Git. Store references and reproducible retrieval instructions instead.
