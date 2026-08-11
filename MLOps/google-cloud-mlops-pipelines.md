# Google Cloud MLOps Pipelines: Detailed Study Guide

Source: [MLOps—Continuous delivery and automation pipelines in machine learning](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)

Source status when reviewed: Google Cloud marks the article as last reviewed on
2024-08-28. It primarily discusses predictive ML systems.

This file is an original study summary of the source, organized for revision and
interview preparation. It is not a copy of the article.

## 1. Purpose of the article

The article explains how CI, CD, and continuous training apply to ML systems. It
is written for data scientists and ML engineers who want to apply DevOps ideas
to the complete ML lifecycle.

Its central argument is that producing an accurate model on an offline test set
is only the beginning. The hard part is integrating that model into a system,
operating it continuously, and responding safely when code, data, models, user
behavior, or infrastructure changes.

## 2. Definition of MLOps

MLOps is both a culture and a collection of engineering practices that connect
ML development with ML operations. It promotes automation and monitoring across:

- integration
- testing
- release and deployment
- infrastructure management
- data and model validation
- production serving
- ongoing model operation and retraining

MLOps is not one product. Tools support the practice, but reliable processes,
clear ownership, validation gates, and feedback loops are the real system.

## 3. Why the model is only a small part of the system

A real ML product surrounds its model code with many other components:

- configuration
- automation and orchestration
- data collection
- data verification
- testing and debugging
- compute and resource management
- model analysis
- process and metadata management
- serving infrastructure
- monitoring and alerting

This is why a notebook that trains a good model is not equivalent to a
production ML system.

## 4. DevOps versus MLOps

Both aim for short development cycles, repeatable delivery, reliability, and
safe change. ML adds complications that conventional software does not fully
address.

| Area | Conventional software | ML system |
|---|---|---|
| Primary changing artifact | Code and configuration | Code, configuration, data, features, and models |
| Development style | Usually requirements-driven | Highly experimental and iterative |
| Reproducibility | Rebuild from source and dependencies | Reproduce code, data, features, parameters, environment, and randomness |
| Testing | Unit, integration, security, and performance tests | All software tests plus data, schema, feature, training, and model-quality tests |
| Deployment | Deploy an application or package | Deploy serving code and often a complete retraining pipeline |
| Production failure | Bugs, dependencies, capacity, or infrastructure | Those failures plus skew, drift, stale models, and feedback-loop problems |
| Team composition | Primarily software and operations roles | Data scientists, researchers, data engineers, ML engineers, and operations roles |

Important consequences:

- Experiments must be tracked so successful and failed approaches are
  reproducible and comparable.
- Training logic should move from interactive notebooks into reusable,
  testable pipeline components.
- Production monitoring must cover input data and model behavior in addition to
  normal service health.
- Deploying only the prediction API leaves retraining and validation as fragile
  manual work.

## 5. CI, CD, and CT in ML

### Continuous integration (CI)

ML CI validates more than code. It can build packages and container images and
test:

- feature-engineering functions
- model implementation functions
- data and schemas
- whether training converges on a small sample
- whether training creates NaN or invalid values
- whether components produce expected artifacts
- whether pipeline components integrate correctly
- whether the model meets a minimum quality threshold

### Continuous delivery (CD)

ML CD can deliver two connected things:

1. A new implementation of the training pipeline.
2. A validated model produced by that pipeline and deployed to a prediction
   service.

This distinction matters: changing pipeline code is different from retraining
unchanged pipeline code on new data.

### Continuous training (CT)

CT automatically retrains a model in response to an approved trigger and makes
the resulting candidate available for evaluation and possible deployment.

CT should include data and model validation. Automatic training must not mean
automatic promotion of every candidate model.

## 6. End-to-end data science and ML lifecycle

The source describes eight steps after defining the business problem and success
criteria.

### 1. Data extraction

Select and combine the data sources relevant to the prediction task. Record the
source, extraction time, query/version, access rules, and ownership.

### 2. Data analysis

Use exploratory analysis to understand schemas, distributions, relationships,
missingness, anomalies, leakage risks, and label quality. This step informs data
preparation and feature engineering.

### 3. Data preparation

Clean and transform data, create features, and produce training, validation, and
test splits. The transformations must eventually be consistent between training
and serving.

### 4. Model training

Train candidate algorithms and tune hyperparameters. The output is a model
artifact tied to its code, data, features, parameters, and environment.

### 5. Model evaluation

Evaluate against a holdout test set and produce metrics that reflect the use
case—not only a convenient generic metric.

### 6. Model validation

Decide whether the candidate is deployable. Compare it with a baseline or the
current production model, verify requirements across important data segments,
and check serving compatibility.

### 7. Model serving

Deploy a validated model through one of several patterns:

- an online prediction service such as a REST API
- an embedded model on an edge or mobile device
- a batch prediction system

Streaming and asynchronous patterns are additional practical variants.

### 8. Model monitoring

Observe the model and its environment after deployment. Monitoring creates the
feedback that starts investigation, experimentation, rollback, or retraining.

The automation level across these steps determines MLOps maturity.

## 7. MLOps maturity overview

| Level | Main idea | What is deployed | Main trigger | Primary weakness |
|---|---|---|---|---|
| 0 | Manual ML process | Usually one trained model/prediction service | Human actions | Slow, fragile, poorly monitored, difficult to reproduce |
| 1 | Automated ML training pipeline | A repeatable pipeline that creates and deploys models | New data, schedule, drift, degradation, or demand | Pipeline code changes may still be manually tested and deployed |
| 2 | Automated pipeline CI/CD | Tested pipeline components plus continuously trained models | Code events and operational/data events | Highest platform and governance complexity |

Maturity is not a competition. A low-change, low-risk system might not justify
every level-2 component. Automation should be introduced where it reduces real
risk or lead time.

## 8. Level 0: manual process

### Characteristics

- Data analysis, preparation, training, and validation are manual.
- Work is often driven by interactive notebooks and scripts.
- Transitions between lifecycle steps require a person.
- Data scientists build the model and hand an artifact to engineers.
- ML development and production operations are separated.
- Models change infrequently, perhaps only a few times per year.
- There is no meaningful CI for the ML pipeline.
- There is no automated delivery of model versions.
- Deployment focuses on the prediction service rather than the whole ML
  system.
- Prediction and outcome logs may be insufficient for active model-quality
  monitoring.

### Major risks

- Hand-offs lose context and are difficult to reproduce.
- Training features can differ from serving features, causing training-serving
  skew.
- A stale model can remain online after the real-world distribution changes.
- Testing may be hidden inside notebooks instead of enforced before release.
- Retraining and deployment are slow and error-prone.
- Model lineage and rollback information may be incomplete.

### When level 0 can be acceptable

It can be a rational starting point when there are very few models, changes are
rare, risk is low, and manual processes are documented and controlled. It
should still include source control, reproducibility, validation, and basic
monitoring.

### How to improve it

- actively monitor production model quality and staleness
- retrain when changing data or business behavior justifies it
- continue experimentation with features, algorithms, and hyperparameters
- convert repeated manual steps into an automated training pipeline

## 9. Level 1: ML pipeline automation

Level 1 automates the training pipeline to support continuous training and the
delivery of new validated model versions.

### Characteristics

- Experiment steps are orchestrated, reducing manual transitions.
- Fresh production data can trigger retraining.
- The same pipeline implementation is used across development,
  pre-production, and production as far as practical.
- Components are modular, reusable, composable, and independently testable.
- Components can be containerized to isolate dependencies and make environments
  reproducible.
- Model deployment is part of the pipeline.
- The team deploys a recurring training pipeline, not merely one model file.

Notebooks can remain useful for exploration, but production components should
be modular source code.

## 10. Required level-1 components

### Data validation

Run it before training to decide whether the pipeline can continue.

Schema problems include:

- missing expected features
- unexpected new features
- incompatible data types
- unexpected or invalid values

A breaking schema problem should usually stop the pipeline and create an alert
for investigation.

Statistical data changes can indicate that patterns have moved enough to justify
retraining. Not every distribution change is harmful; the team needs thresholds
and business context.

### Offline model validation

After training, the candidate model should be checked by:

- calculating predictive metrics on an independent test dataset
- comparing the candidate against the current production model, a baseline, or
  explicit business requirements
- checking important slices such as regions, device types, or customer groups
- verifying that the artifact is compatible with the serving infrastructure
  and API contract

### Online model validation

Even after offline validation, use controlled exposure such as a canary release
or A/B test before serving all traffic. Check both model and service metrics.

### Feature store

A feature store is an optional centralized system for defining, storing,
discovering, and serving features to training and inference workloads.

Potential benefits:

- reuse rather than repeated feature implementation
- consistent definitions and metadata
- current feature values for online prediction
- batch access for training
- reduced training-serving skew because both paths use consistent feature logic

A feature store should support both high-throughput offline/batch use and
low-latency online retrieval when the use case needs both. It adds operational
cost, so a small system should not adopt one without a clear need.

### Metadata management

Each pipeline execution should record enough information for lineage,
reproducibility, comparison, debugging, resumption, and rollback:

- pipeline and component versions
- start time, end time, and duration for steps
- the user or service that initiated the run
- parameters supplied to the pipeline
- locations of prepared data and intermediate artifacts
- validation anomalies and computed statistics
- vocabularies or other preprocessing artifacts
- the previous production model or rollback target
- training and test evaluation metrics

Persisting intermediate outputs can allow a failed run to resume without
repeating successful expensive steps, provided the steps are safe and their
inputs have not changed.

### Pipeline triggers

Possible triggers include:

- an on-demand manual request
- a daily, weekly, monthly, or other schedule
- arrival of sufficient new labeled training data
- measured production model-quality degradation
- a meaningful change in feature or data distributions

Select triggers using label availability, rate of environmental change,
training cost, risk, and business urgency. A trigger starts evaluation; it does
not guarantee deployment.

### Level-1 limitation

The data-to-model flow is automated, but a new implementation of the pipeline
may still be tested and deployed manually. That can be acceptable for a few
stable pipelines. Frequent algorithm or pipeline-code changes create the need
for level 2.

## 11. Level 2: CI/CD pipeline automation

Level 2 adds automated build, test, and delivery for changes to the pipeline
implementation itself. This supports rapid experimentation while protecting the
production system with repeatable controls.

### Architecture components

- source control
- test and build services
- deployment services
- model registry
- feature store when justified
- ML metadata store
- pipeline orchestrator

### Six-stage flow

1. **Development and experimentation:** explore algorithms, features, and
   hyperparameters through orchestrated experiments; commit production pipeline
   code to source control.
2. **Pipeline CI:** build and test code, packages, images, components, and their
   integrations.
3. **Pipeline CD:** deploy the validated pipeline implementation to its target
   environment.
4. **Automated triggering:** execute the deployed training pipeline from an
   approved event or schedule and register the resulting candidate model.
5. **Model continuous delivery:** promote and serve a validated candidate model
   through a prediction service.
6. **Monitoring:** collect live service, data, and model statistics; create a
   feedback signal for retraining or new experimentation.

Data analysis and model analysis still require human judgment in important
places. Level 2 automates repeatable work; it does not eliminate scientific or
business decisions.

## 12. CI tests highlighted by the architecture

### Code and feature tests

- feature transformations produce correct values for normal and edge cases
- encoding logic handles known, unknown, missing, and invalid categories
- no leakage uses future or target information

### Training smoke tests

- training runs on a small fixture dataset
- loss moves in the expected direction
- the model can intentionally overfit a tiny sample, demonstrating that the
  training path is capable of learning
- numerical operations do not create NaN or infinite values

### Component contract tests

- each component emits the expected artifact type, schema, and metadata
- downstream components can read upstream outputs
- pipeline retries do not corrupt data or duplicate side effects

### Integration tests

- the pipeline runs end to end in a small test environment
- model packaging, registry operations, and serving interfaces are compatible

## 13. Continuous-delivery checks

Before a release or promotion, verify:

- model dependencies match the serving environment
- sufficient CPU, memory, storage, or accelerators are available
- the prediction API accepts expected input and returns the correct schema
- latency and throughput meet service targets under load
- retraining or batch-prediction data passes validation
- predictive metrics meet deployment thresholds
- rollback targets and procedures are available

A practical environment policy can be:

- automatically deploy a new pipeline build to a test environment after CI
- deploy to pre-production after review and a merge to the protected main branch
- require successful pre-production runs and explicit approval for production

Automation depth should reflect risk. Fully automatic production promotion is
not always the safest or most valuable design.

## 14. Monitoring as the feedback loop

Monitoring should cover multiple layers:

### System and service

- uptime and errors
- latency and throughput
- resource saturation
- dependency failures
- infrastructure cost

### Data

- schema violations
- missingness and invalid values
- category and range changes
- feature distribution changes
- freshness and volume

### Model

- prediction distributions and confidence
- quality metrics when labels arrive
- segment-level performance
- calibration, fairness, and business outcomes where applicable
- model age and staleness

Monitoring must connect to an action: investigate, alert, roll back, retrain,
change a threshold, collect labels, or start a new experiment.

## 15. Essential distinctions for interviews

### Data drift versus concept drift

- Data drift: the distribution of model inputs changes.
- Concept drift: the relationship between inputs and the target changes.

Input drift is measurable without immediate labels, but it does not prove that
model performance fell. Concept drift is ultimately about the prediction
relationship and often requires labels or business outcome signals.

### Model retraining versus model redeployment

- Retraining runs the same or changed training logic to produce a new model.
- Redeployment changes what model or serving implementation handles traffic.

Either can happen without the other.

### Pipeline CD versus model CD

- Pipeline CD releases a new implementation of how models are produced.
- Model CD promotes a model artifact produced by an existing pipeline.

They require different triggers, tests, and rollback plans.

### Training-serving skew

Skew occurs when features, transformations, or data semantics differ between
training and production inference. Shared transformation code, strong contracts,
feature stores where justified, and monitoring reduce the risk.

## 16. Progressive adoption plan

The article explicitly supports gradual improvement rather than an immediate
jump to maximum automation.

1. Put code in version control and make training reproducible.
2. Add data and model validation.
3. Add experiment tracking, a registry, and basic production monitoring.
4. Modularize and orchestrate the training pipeline.
5. Add safe CT triggers and model-promotion gates.
6. Add CI/CD for pipeline implementations.
7. Add advanced infrastructure only when scale, risk, or team needs justify it.

## 17. One-minute summary

MLOps extends DevOps to a system whose behavior depends on code, data, and
trained artifacts. Level 0 manually produces and deploys models. Level 1 deploys
an automated training pipeline with validation, metadata, triggers, and model
delivery. Level 2 also automates the build, testing, and deployment of new
pipeline implementations. Across all levels, the goal is safe, reproducible,
observable change—not automation for its own sake.
