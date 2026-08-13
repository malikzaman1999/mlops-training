# MLOps Mastery Guide

This guide is the long-form version of my MLOps study notes. It is written to
answer three questions:

- What is MLOps?
- How do the pieces work together?
- Why does each piece matter in production?

It also includes practical exercises with answer keys so the material can be
used as a study plan, interview prep sheet, or project checklist.

## 1. What MLOps Is

MLOps is the discipline of building, shipping, and operating machine learning
systems with the same rigor that software engineering applies to production
applications.

The important difference from standard software engineering is that ML systems
change not only when code changes, but also when data changes, labels change,
feature distributions change, and model behavior drifts over time.

That means an ML system must handle:

- code
- data
- features
- training
- evaluation
- deployment
- monitoring
- retraining
- governance

If any of these parts are weak, the model may work in a notebook and fail in
production.

## 2. Why MLOps Exists

MLOps exists because machine learning is not a one-time build.

In production, ML teams need to answer questions like:

- Which code trained this model?
- Which data was used?
- What version of the model is live?
- How do we compare candidates?
- How do we roll back safely?
- How do we know the model is still healthy?
- How do we reproduce a result from last month?

Without MLOps, these questions are answered manually, slowly, and often
incompletely.

The goal is not just to train a good model. The goal is to repeatedly deliver a
reliable ML system as everything around it changes.

## 3. The ML Lifecycle

A practical ML lifecycle usually looks like this:

1. Define the business problem.
2. Collect and validate data.
3. Prepare features and labels.
4. Train candidate models.
5. Track experiments.
6. Evaluate and compare candidates.
7. Validate the chosen model.
8. Package the model.
9. Register and promote it.
10. Deploy it.
11. Monitor it.
12. Retrain or roll back when needed.

The most important idea is that the lifecycle is circular, not linear.
Monitoring feeds back into retraining and experimentation.

## 4. The Core MLOps Layers

### 4.1 Data

Data is the foundation.

What to learn:

- batch and streaming ingestion
- missing values
- outliers
- schema validation
- dataset versioning
- label quality
- feature leakage
- point-in-time correctness

Why it matters:

- Most model failures begin with data problems.
- If training data and serving data differ, you get skew.
- If labels are wrong, the model learns the wrong pattern.

### 4.2 Training

Training is the process of turning data into a model.

What to learn:

- model selection
- hyperparameters
- cross-validation
- seeds and determinism
- training pipelines
- reproducible environments

Why it matters:

- Training must be repeatable.
- A successful training run should be traceable and comparable.

### 4.3 Experiment Tracking

Experiment tracking records what happened in each training run.

You want to capture:

- parameters
- metrics
- tags
- artifacts
- code versions
- dataset references

Why it matters:

- It makes comparison possible.
- It reduces guesswork.
- It creates a history of what was tried.

MLflow Tracking is a common solution here. It provides an API and UI for
logging parameters, metrics, code versions, and output files. It also supports
Python, REST, R, and Java APIs. See the official docs:

- [MLflow Tracking](https://mlflow.org/docs/latest/ml/tracking/)
- [MLflow Tracking Quickstart](https://mlflow.org/docs/latest/ml/getting-started/quickstart/)

### 4.4 Model Packaging

Packaging turns a trained model into something portable.

What to learn:

- serialization
- model signatures
- input examples
- dependency capture
- flavors

Why it matters:

- A model should load reliably in another environment.
- The serving contract should be explicit.
- Dependencies should be reproducible.

MLflow Models use a standard package format with an `MLmodel` file and
dependency metadata. The model signature defines the expected format for
inputs, outputs, and parameters.

Useful docs:

- [MLflow Models](https://mlflow.org/docs/latest/ml/model/index.html)
- [Model Signatures and Input Examples](https://mlflow.org/docs/latest/ml/model/signatures/)

### 4.5 Model Registry

The registry is the governance layer.

What to learn:

- registering versions
- aliases
- tags
- promotion workflows
- rollback strategy
- approval gates

Why it matters:

- Teams need one source of truth for production models.
- Registry-based workflows reduce deployment chaos.

Useful docs:

- [Model Registry Workflows](https://www.mlflow.org/docs/latest/ml/model-registry/workflow/)

### 4.6 Serving

Serving exposes the model to users or downstream systems.

What to learn:

- REST inference APIs
- batch inference
- containers
- canary deploys
- shadow deploys
- A/B testing
- rollback

Why it matters:

- Training is not production.
- Real systems need latency, scale, and reliability.

MLflow can serve models locally through a standard inference server.

Useful docs:

- [Deploy MLflow Model as a Local Inference Server](https://mlflow.org/docs/latest/ml/deployment/deploy-model-locally)

### 4.7 Monitoring

Monitoring checks whether the model and service are still healthy.

What to learn:

- latency
- throughput
- error rates
- input drift
- concept drift
- output drift
- business KPI monitoring
- alerting

Why it matters:

- A model can degrade without any code change.
- Production quality is not the same as offline evaluation quality.

### 4.8 Retraining

Retraining refreshes the model using new data or new labels.

What to learn:

- retraining triggers
- scheduled retraining
- drift-triggered retraining
- baseline comparison
- validation gates

Why it matters:

- The world changes.
- A model must adapt or it becomes stale.

## 5. What MLflow Is and Why It Matters

MLflow is a platform for managing the ML lifecycle.

It is useful because it gives you:

- experiment tracking
- model packaging
- model registry
- model serving
- evaluation support
- project reproducibility

In short:

- `Tracking` tells you what happened.
- `Projects` tell you how to rerun it.
- `Models` package the output.
- `Registry` manages versions and promotion.
- `Serving` exposes the model.
- `Evaluation` tells you whether it is good enough.

MLflow documentation is organized for both traditional ML and LLM/agent
workflows:

- [MLflow Documentation](https://www.mlflow.org/docs/latest/)

## 6. How MLflow Works

### 6.1 Tracking

Tracking is the logging layer.

You start a run, log parameters and metrics, then save artifacts like model
files or plots.

This creates a reproducible record for later comparison.

Typical things to log:

- hyperparameters
- training loss
- validation metrics
- feature schema
- data sample references
- model checkpoints
- plots
- environment files

### 6.2 Runs and Experiments

- A `run` is one execution of training or evaluation.
- An `experiment` groups related runs together.

This makes it easier to compare trials and find the best candidate.

### 6.3 Autologging

Autologging reduces manual logging by capturing metrics, parameters, and model
artifacts automatically for supported libraries.

Why it matters:

- less boilerplate
- fewer missing logs
- faster experimentation

### 6.4 Backend Store

The backend store holds metadata such as:

- run ID
- model ID
- tags
- metrics
- parameters
- timestamps

MLflow supports relational database-backed stores such as PostgreSQL, MySQL,
SQLite, and MSSQL. The docs recommend a database backend for better performance
and reliability.

Useful docs:

- [Backend Stores](https://mlflow.org/docs/latest/self-hosting/architecture/backend-store/)

### 6.5 Artifact Store

The artifact store holds larger files such as:

- model weights
- images
- parquet files
- dataset samples

This is separate from metadata because the storage patterns are different.

Useful docs:

- [Artifact Stores](https://mlflow.org/docs/latest/self-hosting/architecture/artifact-store/)

### 6.6 Model Signatures

The model signature is the contract between training and serving.

It describes:

- input schema
- output schema
- parameter schema

Why it matters:

- It prevents serving-time mismatches.
- It documents how to call the model.
- It catches bad requests earlier.

### 6.7 Registry Workflow

The registry workflow is:

1. log a model
2. register it
3. assign versions or aliases
4. promote it after validation
5. roll back if needed

This gives teams a controlled promotion path instead of ad hoc deployment.

### 6.8 Serving Workflow

The serving workflow is:

1. load the logged model
2. create a serving environment
3. expose an inference endpoint
4. send requests to the model
5. monitor performance and correctness

MLflow's local serving flow is useful for testing before production.

## 7. MLOps Maturity Levels

### Level 0: Manual Process

Characteristics:

- notebooks or scripts
- manual training
- manual validation
- manual deployment
- weak reproducibility
- limited automation

Why teams start here:

- it is fast to prototype
- it works for small, low-risk systems

Main risks:

- lost lineage
- hard rollback
- hidden notebook logic
- inconsistent environments
- model drift with weak monitoring

### Level 1: ML Pipeline Automation

Characteristics:

- modular training pipeline
- repeatable execution
- automated validation
- metadata logging
- consistent environments
- candidate model registration

Why it matters:

- training becomes reproducible
- retraining can be automated
- validation is no longer manual every time

### Level 2: CI/CD for ML Pipelines

Characteristics:

- automated testing of pipeline code
- build and deploy of pipeline implementations
- separate pipeline CD and model CD
- stronger governance
- safer production releases

Why it matters:

- teams can evolve pipeline code safely
- model delivery and pipeline delivery are both controlled

## 8. What You Should Learn First

If you want to become an MLOps engineer, learn in this order:

1. Python, pandas, scikit-learn
2. SQL and data validation
3. Git and code review
4. Docker and Linux
5. MLflow tracking and registry
6. Model packaging and serving
7. CI/CD
8. Orchestration
9. Monitoring and alerting
10. Cloud infrastructure
11. Kubernetes
12. Security and governance
13. LLMOps and GenAI evaluation

## 9. Kubernetes Basics

Kubernetes shows up everywhere in MLOps, so it is worth learning the basic
building blocks clearly.

### 9.1 Cluster vs Node vs Pod

- `Cluster` = the whole Kubernetes environment.
- `Node` = one machine in that cluster, usually a VM or server.
- `Pod` = the smallest deployable unit, running on a node.

How they relate:

- A `cluster` contains many `nodes`.
- A `node` can run many `pods`.
- A `pod` runs on exactly one node at a time.

Why it matters:

- The cluster is the platform.
- The node is the compute host.
- The pod is the unit Kubernetes schedules and replaces.

### 9.2 Pod vs Container

- `Container` = one packaged process with code, runtime, and dependencies.
- `Pod` = a wrapper around one or more containers that share networking and
  storage.

Key difference:

- A container is the runtime unit.
- A pod is the Kubernetes scheduling unit.

Why pods exist:

- Kubernetes manages pods, not raw containers.
- A pod lets multiple tightly coupled containers run together, like an app
  container plus a sidecar.

### 9.3 Deployment vs ReplicaSet vs Pod

- `Pod` = the actual running instance of your app.
- `ReplicaSet` = keeps the desired number of pod replicas running.
- `Deployment` = manages ReplicaSets and handles rollout updates.

How they work together:

- You define a `Deployment`.
- The Deployment creates and manages a `ReplicaSet`.
- The ReplicaSet creates and maintains the `Pods`.

Why it matters:

- `Pod`: runs the app.
- `ReplicaSet`: ensures availability and scaling.
- `Deployment`: handles versioned updates, rollback, and rollout strategy.

### 9.4 Instance vs Pod

- `Instance` usually means one compute machine, like one VM or cloud server.
- In Kubernetes, an instance often refers to the machine that hosts one or more
  pods.
- It is not a Kubernetes object by itself.

Important distinction:

- A single `instance` can run many `pods`.
- A single `pod` runs on only one `node` at a time.
- A `cluster` contains many `nodes` and many `pods`.

## 10. What to Practice

### Practice Area 1: Reproducibility

Goal:

- reproduce a training run exactly.

What to do:

- pin dependencies
- fix random seeds
- log the dataset version
- log the commit SHA
- log metrics and artifacts

Why:

- if you cannot reproduce it, you cannot trust it.

### Practice Area 2: Experiment Tracking

Goal:

- compare 10 runs and pick the best model.

What to do:

- vary one hyperparameter at a time
- log every run
- compare on a consistent validation set

Why:

- makes tradeoffs visible.

### Practice Area 3: Validation Gates

Goal:

- block bad models from reaching production.

What to do:

- define minimum metric thresholds
- require schema validation
- compare against a baseline model

Why:

- production safety.

### Practice Area 4: Serving

Goal:

- deploy a model behind an API.

What to do:

- serve locally first
- test the inference endpoint
- measure latency
- use a container

Why:

- a model is only useful if it can answer requests reliably.

### Practice Area 5: Monitoring

Goal:

- detect when model performance changes.

What to do:

- track input drift
- track prediction drift
- track latency and error rates
- track downstream business metrics

Why:

- production data changes continuously.

## 11. Exercises With Answers

### Exercise 1

**Task:** Train a classification model and log parameters, metrics, and the
model.

**Answer:** Use a tracking run, log parameters and metrics, then save the model
as an artifact. In MLflow, that typically means `mlflow.start_run()`,
`mlflow.log_param()`, `mlflow.log_metric()`, and a flavor-specific
`log_model()` call.

### Exercise 2

**Task:** Make a training run reproducible.

**Answer:** Pin dependencies, use a fixed random seed, version the dataset,
record the code commit, and log the full environment. Reproducibility comes
from controlling inputs and environment, not just from saving the model file.

### Exercise 3

**Task:** Prevent a bad input from reaching a model in serving.

**Answer:** Define a model signature and input example, then validate requests
against that schema before inference. The signature acts like a contract.

### Exercise 4

**Task:** Compare many runs and choose the best one.

**Answer:** Group the runs in one experiment, log the same validation metric for
each, sort by the metric that matters most, and keep the winner and runner-up
for comparison. Never compare runs that were evaluated on different data splits
without noting it.

### Exercise 5

**Task:** Promote a candidate model safely.

**Answer:** Register the model, assign an alias or tag, validate it against
release criteria, deploy it to staging, then promote to production only after
the checks pass.

### Exercise 6

**Task:** Deploy a model locally and test it.

**Answer:** Use the local serving command, then call the `/invocations`
endpoint with a valid payload. If the request fails, first check the input
schema and the content type.

### Exercise 7

**Task:** Build a quality gate for training.

**Answer:** Add a pipeline step that fails if the candidate model does not beat
the baseline or does not meet a threshold for the chosen metric. Include slice
checks if specific user groups matter.

### Exercise 8

**Task:** Detect drift.

**Answer:** Compare the live input distribution to the training distribution.
If the change exceeds an agreed threshold, alert the team and investigate.

### Exercise 9

**Task:** Explain why metadata and artifacts should be stored separately.

**Answer:** Metadata is small and query-heavy, while artifacts are large and
storage-heavy. Separate stores scale better and are easier to manage.

### Exercise 10

**Task:** Design an LLM evaluation plan.

**Answer:** Track prompts, outputs, human reviews, and rubric scores. Compare
model versions using consistent tasks and scoring rules, and keep the feedback
loop visible in the evaluation system.

## 12. Mini Project Ideas

### Project 1: Binary Classifier with Full Tracking

Build a classification model with:

- tracked experiments
- logged metrics
- model signature
- registered version
- local serving
- basic monitoring

### Project 2: Batch Forecasting Pipeline

Build a scheduled pipeline that:

- loads data
- validates schema
- trains a model
- logs results
- saves the model
- compares against a baseline

### Project 3: Drift Monitor

Build a service that:

- captures incoming features
- compares them with training statistics
- flags drift
- generates an alert

### Project 4: Registry-Based Deployment Workflow

Build a system where:

- candidates are registered
- aliases point to production
- rollbacks are one command
- model promotion requires passing tests

## 13. Common Failure Modes

### 12.1 Training-Serving Skew

Training uses different transformations or feature values than serving.

Fix:

- share code
- validate schemas
- test parity

### 12.2 Label Leakage

The model sees information that would not be available at prediction time.

Fix:

- use point-in-time-safe data
- review features carefully

### 12.3 Silent Data Drift

The model is still running but input distributions have changed.

Fix:

- monitor drift
- retrain or rollback when needed

### 12.4 Unreproducible Results

You cannot recreate a successful run later.

Fix:

- log code, data, environment, and parameters

### 12.5 Weak Validation

A model is deployed because it trained successfully, not because it is better.

Fix:

- enforce release gates
- compare against a baseline

## 14. How to Think About MLOps in One Sentence

MLOps is the system that makes machine learning repeatable, measurable,
deployable, and safe to evolve.

## 15. Suggested Weekly Study Cycle

Each week:

- learn one concept
- implement one small pipeline
- track one experiment
- add one validation rule
- deploy one model locally
- write one postmortem or learning note

That cycle is enough to build real skill.

## 16. Short Checklist

Before you call a model production-ready, ask:

- Can I reproduce the training run?
- Can I explain the metrics?
- Can I reload the model in another environment?
- Do I know the input schema?
- Can I register and promote versions safely?
- Can I roll back quickly?
- Can I observe latency and drift?
- Do I know when to retrain?

If the answer to any of these is no, the system is not fully production-ready
yet.
