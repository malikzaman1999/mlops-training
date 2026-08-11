# MLOps Interview Questions: Google Cloud Pipeline Architecture

Based on [Google Cloud's MLOps continuous delivery and automation pipeline article](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning).

Each question includes a complete sample answer. Practice giving the answer in
your own words, then connect it to a real project or production scenario.

## Fundamentals

### 1. What is MLOps?

**Answer:** MLOps is a culture and set of engineering practices for building,
deploying, and operating machine-learning systems reliably. It connects model
development with production operations and applies automation, testing,
versioning, monitoring, and governance throughout the ML lifecycle. Its goal is
to make changes to code, data, models, and infrastructure reproducible and safe.

### 2. Why is deploying a model file not the same as deploying an ML system?

**Answer:** A model file contains learned parameters, but it cannot collect and
validate inputs, reproduce preprocessing, expose predictions, handle failures,
or monitor itself. A production system also needs data pipelines,
configuration, feature transformations, serving infrastructure, metadata,
resource management, monitoring, security, feedback loops, and rollback. The
model is therefore one artifact inside a much larger operational system.

### 3. How does MLOps differ from DevOps?

**Answer:** MLOps uses the same foundations as DevOps—source control, automated
testing, CI/CD, infrastructure management, observability, and reliable
releases—but ML adds data and trained models as changing artifacts. It must also
support experimentation, validate data and model quality, reproduce training,
prevent training-serving skew, monitor drift, and decide when to retrain or
replace a model. Conventional application behavior mainly changes with code;
ML behavior can change when either code or data changes.

### 4. What makes ML development unusually experimental?

**Answer:** ML development involves testing many datasets, features,
algorithms, hyperparameters, and architectures because the best design is not
known in advance. The same code may also produce different results when its
data, random seed, or environment changes. Teams therefore need experiment
tracking, reusable components, versioned inputs, and recorded environments to
compare runs and reproduce both successful and failed approaches.

### 5. Why can an unchanged model degrade in production?

**Answer:** A model learns relationships from historical data, but the world
that generates production data can change. Input distributions, customer
behavior, products, policies, upstream schemas, or the relationship between
features and the target may shift. Data-quality failures and feedback from the
model's own decisions can also change performance. The code can remain
identical while the model becomes stale or harmful.

## CI, CD, and CT

### 6. What does continuous integration validate in an ML system?

**Answer:** ML CI should test ordinary code as well as ML-specific behavior. It
builds packages or images and checks feature transformations, schemas, sample
data, component contracts, training execution, finite numerical outputs,
expected artifacts, model-quality thresholds, and integration between pipeline
steps. These tests prevent invalid data or a broken training path from creating
a candidate model.

### 7. What does continuous delivery mean for ML?

**Answer:** Continuous delivery in ML means keeping validated changes ready for
safe release. One delivery path releases a new implementation of the training
pipeline; another promotes a validated model artifact to a batch or online
prediction service. These paths are related but distinct because pipeline code
usually changes after a code commit, while a new model can be produced from
unchanged code when new data arrives.

### 8. What is continuous training?

**Answer:** Continuous training automatically executes a reproducible training
pipeline in response to a trigger such as a schedule, new labeled data, drift,
or degraded performance. It produces a versioned candidate model with metrics
and lineage. The candidate still has to pass data checks, offline evaluation,
comparison with the current model, and any required online or human approval
before production promotion.

### 9. What is the difference between pipeline CD and model CD?

**Answer:** Pipeline CD deploys a new version of the code and components used to
produce models. Model CD deploys a trained artifact produced by that pipeline.
Pipeline CD is normally triggered by source changes and requires code,
component, and integration tests. Model CD may be triggered by new data or
performance signals and requires model-quality and serving checks. Rolling back
one restores pipeline code; rolling back the other restores a previous model.

### 10. Should every retrained model be deployed automatically?

**Answer:** No. Retraining should create a candidate rather than guarantee a
release. The candidate must use valid data, beat an agreed baseline or satisfy
business thresholds, avoid regressions on important slices, and remain
compatible with serving infrastructure. Higher-risk systems should also use a
shadow, canary, or A/B deployment and an approval gate before receiving all
traffic.

## ML lifecycle

### 11. Walk through the end-to-end ML lifecycle.

**Answer:** First define the business problem, prediction task, constraints, and
success criteria. Then extract and analyze data, prepare features and dataset
splits, train candidate models, evaluate them on independent data, and validate
the best candidate against technical and business release rules. Deploy it
through an appropriate serving pattern, monitor the service, data, predictions,
and outcomes, and feed those observations into investigation, retraining, or
new experimentation.

### 12. What is the difference between model evaluation and validation?

**Answer:** Evaluation measures a model, for example by calculating precision,
recall, RMSE, calibration, or business metrics on a holdout dataset. Validation
uses those results and additional constraints to decide whether the candidate
is safe to release. It compares the candidate with a baseline or production
model, checks important slices, verifies business thresholds, and confirms that
the artifact can run behind the serving contract.

### 13. What serving patterns should an ML engineer consider?

**Answer:** Common patterns are synchronous online APIs for low-latency
requests, batch inference for high-volume jobs that tolerate delay, streaming
or asynchronous inference for event-driven systems, and embedded or edge
inference when predictions must run near the device. The choice depends on
latency, throughput, freshness, availability, privacy, hardware, cost, and how
much operational complexity the team can support.

### 14. What is training-serving skew?

**Answer:** Training-serving skew occurs when production inference uses feature
values, transformations, or semantics that differ from those used during
training. Examples include different category encoding, a feature calculated
with future information during training, or stale online values. Reduce it with
shared transformation code, explicit schemas and contracts, point-in-time-
correct data, parity tests, monitoring, and a feature store when its benefits
justify the added infrastructure.

## Maturity levels

### 15. Describe MLOps level 0.

**Answer:** Level 0 is a manual, notebook- or script-driven ML process. People
manually move through analysis, preparation, training, validation, and
deployment, often handing a model artifact from data scientists to engineers.
Releases are infrequent, CI/CD for the ML workflow is limited, and production
model monitoring may be weak. The focus is usually deploying a prediction
service rather than operating a repeatable training system.

### 16. What are the biggest risks at level 0?

**Answer:** The largest risks are runs that cannot be reproduced, lost context
during hand-offs, training-serving skew, tests hidden inside notebooks, and
models remaining online after they become stale. Missing lineage makes it hard
to identify the exact code and data behind a model, while weak monitoring and
registry practices make incidents and rollbacks slower and less reliable.

### 17. When might level 0 still be reasonable?

**Answer:** Level 0 can be reasonable for a small number of rarely changing,
low-risk models when a larger platform would cost more than it saves. Manual
does not have to mean uncontrolled: the team should still version code and
data, document reproducible runs, validate candidates, record deployments,
monitor basic quality, and maintain a tested rollback procedure.

### 18. What changes at MLOps level 1?

**Answer:** Level 1 replaces repeated manual training steps with an orchestrated
pipeline of modular components. The pipeline can run from schedules, new data,
or performance signals and includes automated data and model validation. It
records metadata and lineage, uses consistent execution environments, registers
candidates, and can deliver validated models. This makes retraining faster and
more reproducible.

### 19. What is deployed at level 1 that was not deployed at level 0?

**Answer:** At level 1, the team deploys a reusable training pipeline that can
repeatedly prepare data, train, evaluate, validate, register, and possibly
deploy new model versions. Level 0 usually deploys only a model artifact and its
prediction service. Deploying the pipeline is what enables reliable continuous
training.

### 20. What limitation remains at level 1?

**Answer:** Level 1 automates execution of the current pipeline, but a new
version of the pipeline implementation may still require manual testing,
packaging, and deployment. That is manageable for a few stable pipelines but
becomes a bottleneck and source of inconsistency when many teams frequently
change features, algorithms, or components.

### 21. What changes at MLOps level 2?

**Answer:** Level 2 adds a complete CI/CD path for the ML pipeline itself. A code
change automatically builds, tests, and packages affected components and safely
deploys the validated pipeline to the target environment. The deployed pipeline
then participates in level-1 continuous training and model delivery. This
separates safe pipeline-code releases from safe model promotion while connecting
both workflows.

### 22. Name the main level-2 platform components.

**Answer:** A level-2 platform normally includes source control; automated test
and build services; artifact and container storage; deployment services; an ML
pipeline orchestrator; a metadata and lineage store; and a model registry. It
may also contain a feature store when multiple systems need shared, consistent
offline and online features. Monitoring and serving infrastructure complete the
operational feedback loop.

### 23. Walk through the six stages of the level-2 flow.

**Answer:** First, data scientists develop and experiment, then commit modular
pipeline code. Second, pipeline CI builds and tests the code and components.
Third, pipeline CD deploys the validated pipeline. Fourth, a production trigger
runs it and registers a candidate model. Fifth, model continuous delivery
promotes and serves an approved candidate. Sixth, monitoring produces feedback
for retraining, rollback, or a new experiment cycle.

## Validation, features, and metadata

### 24. What should data validation check before training?

**Answer:** Validate that required features exist, unexpected features are
handled, and types, ranges, categories, null rates, uniqueness, volume, and
freshness meet contracts. Check relationships such as label availability and
referential integrity, then compare relevant statistics with a reference
dataset. Separate breaking schema errors that should stop the pipeline from
distribution changes that may justify investigation or retraining.

### 25. How should a pipeline respond to schema skew?

**Answer:** A breaking schema change should normally fail closed before
training, preserve the anomaly report and input version, and alert the data and
ML owners. The team then decides whether the upstream producer violated its
contract or whether the change is intentional. The remedy is either to restore
the data contract or release and test a compatible pipeline version—not to
silently coerce unknown data.

### 26. How do you validate a candidate model offline?

**Answer:** Evaluate the candidate on an untouched, representative test set and
compare its technical and business metrics with the current production model or
an agreed baseline. Examine performance, calibration, and fairness on important
segments, run robustness checks, and verify that preprocessing and the model
artifact satisfy the serving schema and resource constraints. Record all
results as an auditable promotion decision.

### 27. Why examine segment-level metrics when the overall metric improved?

**Answer:** An aggregate metric weights groups according to their frequency and
can hide severe regressions in a smaller or strategically important segment. A
model might improve average accuracy while becoming unsafe for one region,
device type, customer class, or protected group. Slice checks expose these
failures and let the team enforce release criteria that reflect risk and
business priorities.

### 28. What is online model validation?

**Answer:** Online validation exposes a candidate to realistic production data
and infrastructure after it passes offline gates. Shadow mode compares outputs
without affecting users, a canary sends a small traffic percentage, and an A/B
test measures outcomes against the current model. The team monitors errors,
latency, prediction behavior, model metrics, and business results before
increasing traffic or rolling back.

### 29. What problem does a feature store solve?

**Answer:** A feature store centralizes feature definitions, metadata,
discovery, storage, and retrieval. It enables teams to reuse features, construct
point-in-time-correct training datasets from an offline store, and fetch fresh
values from an online store for low-latency inference. Consistent definitions
across both paths reduce duplicated work and training-serving skew.

### 30. When should you avoid introducing a feature store?

**Answer:** Avoid a feature store when one team has a few simple batch features,
features are not shared, and online low-latency lookup is unnecessary. A
versioned transformation pipeline or warehouse views may solve the problem with
far less operational cost. Add a feature store only when consistency, reuse,
point-in-time correctness, or online serving creates measurable value.

### 31. What metadata should be recorded for each pipeline run?

**Answer:** Record the pipeline and component versions, initiator, start and end
times, parameters, environment, source commit, and all input and output artifact
locations. Include dataset identifiers, validation anomalies, statistics,
feature definitions, evaluation metrics, registry entry, and the previous
production model. These links form lineage from a deployed prediction back to
the exact code and data that created it.

### 32. How does metadata support rollback and debugging?

**Answer:** Metadata lets engineers reconstruct the failing run and compare it
with the last successful one. They can identify which code, data, parameter,
environment, or component changed and inspect its artifacts and metrics. The
registry and lineage records identify a known-good previous model for rollback,
while persisted step outputs can allow an idempotent pipeline to resume without
repeating valid expensive work.

## Retraining and monitoring

### 33. What events can trigger a training pipeline?

**Answer:** A pipeline can run on demand, on a time schedule, when enough new
labeled data arrives, when monitored model quality falls below a threshold, or
when meaningful changes appear in input distributions. Code changes should
usually trigger the separate pipeline CI/CD process. Every trigger should have
deduplication, cost controls, and validation gates so it creates a candidate
rather than automatically replacing production.

### 34. How would you choose a retraining frequency?

**Answer:** Base retraining frequency on how quickly the environment changes,
how much new representative data arrives, when labels become available, and how
rapidly quality historically decays. Also consider seasonality, business risk,
training cost, model complexity, and the team's capacity to validate candidates.
A monitored event-based policy is often better than retraining frequently only
because a calendar says so.

### 35. What is the difference between data drift and concept drift?

**Answer:** Data drift means the distribution of input features or predictions
has changed from a reference period. Concept drift means the relationship
between inputs and the correct target has changed, so the old decision boundary
may no longer work. Data drift can be measured before labels arrive but does not
prove performance degradation. Confirm business impact with labels or reliable
outcome signals when possible.

### 36. What should an ML monitoring system observe?

**Answer:** Monitor service availability, errors, latency, throughput, resource
use, dependencies, and cost. Monitor data schemas, validity, missingness,
freshness, volume, and distributions. Monitor prediction distributions,
confidence, model age, quality and calibration when labels arrive, performance
on important slices, and business outcomes. Every alert should map to an owner
and a documented response.

### 37. What should happen after a drift alert?

**Answer:** First verify that the alert is genuine rather than a monitoring or
upstream-data failure. Identify affected features, traffic, and segments, and
compare prediction and labeled performance if available. Assess user and
business impact, then choose among continued observation, fixing data,
retraining a candidate, rolling back, or redesigning features or the model.
Document the decision and tune the alert only with evidence.

### 38. How do you monitor model quality when labels arrive weeks later?

**Answer:** Log a stable prediction identifier, timestamp, model version,
features or approved feature references, and prediction so outcomes can be
joined later. Immediately monitor service, input, and prediction behavior and
use proxy business signals only with known limitations. When labels arrive,
backfill true model metrics by time and segment, then use those results to
recalibrate alerts and retraining policies.

## Testing and delivery

### 39. Why test whether a model can overfit a tiny dataset?

**Answer:** A sufficiently expressive model should be able to memorize a tiny
sample. If it cannot, the training path may have broken labels, preprocessing,
loss calculation, gradients, parameter updates, or feature wiring. This is a
fast smoke test for implementation correctness, not evidence that the model
will generalize to unseen production data.

### 40. What causes NaN values during training, and how do you test for them?

**Answer:** NaNs can come from missing or invalid data, division by zero, logs or
square roots outside their domains, unstable normalization, numerical overflow,
or an excessive learning rate. Validate inputs and assert that transformed
features, loss, gradients, metrics, and parameters are finite. Add a small
training test that fails immediately and records the batch and component where
the invalid value first appeared.

### 41. What should be tested before deploying a prediction service?

**Answer:** Test that the service loads the correct model and dependencies,
enforces the input schema, reproduces preprocessing, returns the documented
output schema, and handles invalid requests safely. Verify CPU, memory, startup,
latency, throughput, concurrency, authentication, logging, health/readiness
checks, and dependency failures. Run tests in the release image and confirm a
known-good model and procedure are available for rollback.

### 42. Why use separate test, pre-production, and production environments?

**Answer:** Separate environments increase confidence progressively while
limiting the blast radius. Tests can run quickly with fixtures; pre-production
can verify integrations, permissions, representative data, load, and rollback
in an environment close to production; production then receives only approved
artifacts. Promotion should preserve the same immutable artifact rather than
rebuilding it differently in every environment.

## Scenario questions

### 43. A new model improves global accuracy by 3% but performs 15% worse for one region. What do you do?

**Answer:** I would block automatic promotion because an aggregate improvement
does not justify a serious regional regression. I would first verify the slice
size, label quality, and confidence intervals, then examine feature coverage,
distribution differences, thresholds, and business or fairness impact. I would
retrain or add an approved mitigation and define a region-level release gate.
Only after offline requirements pass would I consider a limited canary or A/B
test; otherwise I would keep the current production model.

### 44. Your inputs drifted substantially, but labeled performance has not changed. Should you retrain?

**Answer:** I would not retrain and deploy automatically. I would confirm that
the drift is real, identify which features and segments changed, and determine
whether those features strongly affect the model. I would account for label
delay and watch prediction and business proxies. It can be useful to train a
candidate on fresh data, but I would deploy it only if offline and, where
appropriate, online validation demonstrate an improvement.

### 45. A model works in the notebook but fails in the API container. Diagnose it.

**Answer:** I would reproduce the failure inside the exact release image and
inspect logs and the failing request. Then I would compare Python and library
versions, lockfiles, model serialization, preprocessing code, environment
variables, file paths, permissions, request schemas, and CPU/GPU assumptions
with the notebook environment. I would add an integration test that loads the
real artifact and calls the API in the container so the mismatch cannot recur.

### 46. A scheduled retraining pipeline fails after feature engineering. How should the system recover?

**Answer:** The pipeline should record the failed component, exact inputs,
versions, logs, and produced artifacts, then alert the responsible owner. I
would fix or retry only if the step is idempotent; otherwise I would clean up or
compensate for its side effects first. If upstream artifacts are immutable and
valid, the orchestrator can resume from the last successful checkpoint. The
current production model must continue serving because the failed run never
passed validation or promotion.

### 47. Design a safe automated retraining process.

**Answer:** I would start from an explicit schedule, new-data, drift, or
performance trigger with deduplication and cost controls. The pipeline would
version code, data, parameters, and environment; validate inputs; train
reproducibly; and record runs in an experiment tracker. A candidate must beat a
baseline, pass slice and compatibility checks, and enter a registry. I would
deploy it to staging, run API and load tests, then use a canary with monitored
promotion thresholds. Every decision and artifact would be auditable, and the
previous model would remain available for immediate rollback.

### 48. Your production model's latency doubled after a new release, but accuracy improved. Keep it?

**Answer:** I would compare the new latency with the product's service-level
objective and quantify whether the accuracy improvement creates enough business
value to justify slower and potentially more expensive predictions. I would
profile preprocessing, inference, serialization, network calls, and resource
use, then consider optimization, batching, caching, a smaller model, or
different hardware. If the release violates the SLO or harms users during the
canary, I would roll it back while optimizing it offline.

### 49. How would you migrate a level-0 team toward level 2?

**Answer:** I would migrate incrementally around the team's largest risks. First
make training reproducible with source, data, dependency, and model versioning.
Add automated code, data, and model tests, then experiment tracking, a registry,
basic serving observability, and rollback. Next modularize and orchestrate the
training workflow and introduce carefully gated continuous training. Finally
add CI/CD for pipeline implementations. I would introduce feature stores,
Kubernetes, or a larger platform only when scale or repeated bottlenecks justify
their operating cost.

### 50. Design MLOps for a model whose labels are never immediately available.

**Answer:** I would log traceable prediction records containing the model
version, time, input references, prediction, and a stable entity or event ID.
Before labels arrive, I would monitor service health, schemas, data quality,
feature and prediction distributions, and carefully selected proxy business
signals. I would build a delayed-label join and backfill true metrics by time
and segment as soon as outcomes become available. Because immediate quality is
uncertain, promotion would be conservative, canary exposure limited, rollback
fast, and ambiguous degradation reviewed by a human.

## Questions to ask the interviewer

- How many production models and teams does the platform support?
- Which parts of training and deployment are currently manual?
- How are datasets, features, experiments, and model lineage tracked?
- What gates must a candidate pass before production promotion?
- How quickly do labels become available for production monitoring?
- Who owns an incident caused by data quality or model degradation?
- What are the latency, availability, cost, and model-quality objectives?
- How are rollbacks, retraining, and model retirement handled?
- Where does the current platform create the most developer friction?
- Which platform complexity has the team deliberately chosen not to adopt?
