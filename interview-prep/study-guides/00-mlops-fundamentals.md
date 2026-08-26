# MLOps Fundamentals - Interview Study Guide

## Table of Contents
1. [What is MLOps?](#what-is-mlops)
2. [Why MLOps Exists](#why-mlops-exists)
3. [The ML Lifecycle](#the-ml-lifecycle)
4. [MLOps vs DevOps](#mlops-vs-devops)
5. [MLOps Maturity Levels](#mlops-maturity-levels)
6. [Common Failure Modes](#common-failure-modes)
7. [Interview Questions & Answers](#interview-questions--answers)

---

## What is MLOps?

### Definition
**MLOps (Machine Learning Operations)** is the discipline of building, shipping, and operating machine learning systems with the same rigor that software engineering applies to production applications.

### Simple Explanation
Think of MLOps as **"DevOps for Machine Learning"**. While traditional software changes when code changes, ML systems change when:
- Code changes
- **Data changes**
- **Model behavior drifts over time**

### The 8 Core Responsibilities

| Responsibility | What It Means | Example |
|----------------|---------------|---------|
| **Code Versioning** | Track which code trained which model | Git commits, version tags |
| **Data Versioning** | Track which data was used for training | DVC, dataset snapshots |
| **Feature Engineering** | Reproducible transformations | Shared feature pipelines |
| **Training** | Repeatable model creation | Automated training pipelines |
| **Evaluation** | Systematic model validation | Offline metrics, A/B testing |
| **Deployment** | Safe model releases | Blue-green, canary deploys |
| **Monitoring** | Track model health in production | Drift detection, performance tracking |
| **Governance** | Audit trails and compliance | Model registry, lineage tracking |

---

## Why MLOps Exists

### The Production Reality Check

Without MLOps, teams cannot answer fundamental questions:

1. **"Which code trained this production model?"**
   - Problem: Lost lineage, can't reproduce
   - MLOps Solution: Automated tracking, git SHA logging

2. **"What data was used 3 months ago?"**
   - Problem: Data changes continuously
   - MLOps Solution: Data versioning, immutable datasets

3. **"How do I safely roll back this model?"**
   - Problem: No version control for models
   - MLOps Solution: Model registry with stages/aliases

4. **"Why is my model's accuracy dropping?"**
   - Problem: Silent degradation
   - MLOps Solution: Monitoring, drift detection, alerting

5. **"Can I reproduce last month's results?"**
   - Problem: Inconsistent environments
   - MLOps Solution: Containerization, environment specs

### The Hidden Technical Debt Problem

ML systems accumulate unique forms of technical debt:

```
Traditional Software Debt:
- Spaghetti code
- No tests
- Poor documentation

ML-Specific Debt:
- Training-serving skew (features computed differently)
- Label leakage (using future info)
- Data dependencies (upstream changes break models)
- Configuration hell (hyperparameter chaos)
- Glue code everywhere
- Pipeline jungles
```

**Key Insight:** Most ML failures in production aren't due to poor algorithms—they're due to poor operations.

---

## The ML Lifecycle

### The Circular Flow (NOT Linear!)

```
┌─────────────────────────────────────────────────────────────┐
│                    ML Lifecycle Loop                         │
└─────────────────────────────────────────────────────────────┘

1. Define Business Problem
   ↓
2. Collect & Validate Data ← Monitoring feeds back here!
   ↓
3. Prepare Features & Labels
   ↓
4. Train Candidate Models
   ↓
5. Track Experiments ← MLflow Tracking
   ↓
6. Evaluate & Compare Candidates
   ↓
7. Validate Best Model
   ↓
8. Package Model ← MLflow Models
   ↓
9. Register & Promote ← MLflow Registry
   ↓
10. Deploy (Online/Batch/Streaming)
   ↓
11. Monitor Performance & Drift
   ↓
12. Retrain or Roll Back
   └──────→ Back to Step 5 (Continuous Loop!)
```

### Critical Insight

**The most important idea:** The lifecycle is **circular, not linear**. Monitoring feeds back into retraining. Production is not the end—it's the beginning of the next iteration.

---

## MLOps vs DevOps

### What DevOps and MLOps Share

| Practice | Description |
|----------|-------------|
| **Version Control** | Git for code |
| **Automated Testing** | CI/CD pipelines |
| **Reproducible Builds** | Containers, environment specs |
| **Monitoring** | Logs, metrics, alerts |
| **Incremental Deployment** | Blue-green, canary releases |

### What Makes MLOps Unique

| Aspect | DevOps | MLOps |
|--------|--------|-------|
| **Primary Artifact** | Application code | Code + Data + Model |
| **Testing Focus** | Unit/integration tests | Data validation, model quality gates |
| **Behavior Changes When** | Code changes | Code OR data OR distribution changes |
| **Failure Modes** | Crashes, exceptions | Silent degradation, drift |
| **Monitoring** | Latency, errors, uptime | All that + prediction drift, data drift, model accuracy |
| **Reproducibility** | Same code = same behavior | Same code + same data + same seed = same model |
| **Experimentation** | Rare | Core activity (dozens/hundreds of runs) |

### Interview Answer Template

**Q: "How does MLOps differ from DevOps?"**

**Your Answer:**
> "MLOps builds on DevOps foundations—version control, CI/CD, monitoring—but adds ML-specific practices. The key difference is that ML systems have three moving parts (code, data, models) instead of one. Traditional apps change when code changes; ML behavior changes when code, data distributions, or model weights change. This means we need additional practices like experiment tracking to compare dozens of training runs, data versioning to ensure reproducibility, model registries for governance, and drift monitoring because models degrade even without code changes. DevOps asks 'is the service running?'—MLOps adds 'is the model still accurate?'"

---

## MLOps Maturity Levels

Based on Google's MLOps whitepaper. Understand where most companies are and where they're trying to get to.

### Level 0: Manual Process

**Characteristics:**
- Jupyter notebooks or ad-hoc scripts
- Manual training, validation, deployment
- No pipeline automation
- Weak reproducibility
- Limited monitoring

**When It's Acceptable:**
- Proof-of-concept projects
- One-off analyses
- Very low-risk models (e.g., internal recommendations)
- Small teams with infrequent updates

**Risks:**
- **Lost lineage:** Can't trace which code/data produced a model
- **Hard rollbacks:** No version control for models
- **Training-serving skew:** Different preprocessing in notebooks vs production
- **Hidden notebook logic:** Business logic trapped in notebooks
- **Silent drift:** Model degrades, no one notices

**Interview Red Flag:**
If a company is still at Level 0 for critical models, that's a warning sign.

---

### Level 1: ML Pipeline Automation

**Characteristics:**
- **Modular components** (data validation, preprocessing, training, evaluation)
- **Orchestrated pipeline** (Airflow, Prefect, Azure ML Pipelines)
- **Automated retraining** (triggered by schedule, new data, or drift)
- **Metadata logging** (experiments tracked in MLflow)
- **Consistent environments** (Docker, conda)
- **Model registration** (candidates saved in registry)

**What Changes from Level 0:**
- Training becomes **repeatable** (run pipeline = get model)
- Retraining can be **automated** (no manual notebook re-runs)
- Validation is **consistent** (not forgotten steps)

**What's Still Manual:**
- Deploying new pipeline code
- Testing pipeline changes
- Promoting models to production

**Target State for Most Teams:**
This is where you want to be as an MLOps engineer. It eliminates the worst operational pain while remaining practical.

---

### Level 2: CI/CD for ML Pipelines

**Characteristics:**
- **Pipeline code CI/CD:** Automated tests for data processing, model code
- **Model CI/CD:** Separate deployment for models
- **Infrastructure as Code:** Terraform, ARM templates
- **Automated validation gates:** Models must pass quality thresholds
- **A/B testing infrastructure:** Safe gradual rollouts

**Two Deployment Paths:**

```
Path 1: Pipeline CD (Less Frequent)
Code change → Tests → Build pipeline → Deploy pipeline to prod

Path 2: Model CD (More Frequent)
New data arrives → Pipeline runs → Candidate model → Validation →
   → Passes gates? → Deploy to staging → Monitor → Promote to prod
```

**Key Insight:**
Pipeline code and models have **different change cadences**. Pipelines change when you improve feature engineering or algorithms. Models change when you retrain on new data. Level 2 separates these concerns.

---

### Maturity Level Summary Table

| Level | Characteristics | Typical Use Case | Interview Answer |
|-------|----------------|------------------|-------------------|
| **0** | Manual notebooks, no automation | POCs, one-off analysis | "Not suitable for production-critical models" |
| **1** | Automated training pipelines | Most production ML systems | "Reliable retraining with reproducibility" |
| **2** | Full CI/CD for code and models | Large-scale ML platforms | "Complete automation with safety gates" |

---

## Common Failure Modes

### 1. Training-Serving Skew

**What It Is:**
Model training uses different feature computation than production serving.

**Example:**
```python
# Training (in notebook)
df['age_group'] = df['age'].apply(lambda x: 'young' if x < 30 else 'old')

# Serving (in API)
age_group = 'Young' if age < 25 else 'Old'  # Different threshold! Different case!
```

**Result:** Model performs well offline, fails in production.

**Solution:**
- Share transformation code between training and serving
- Use model signatures to enforce schemas
- Add integration tests for preprocessing parity

---

### 2. Label Leakage

**What It Is:**
Training uses information that wouldn't be available at prediction time.

**Example:**
```python
# WRONG: Using future information
features = ['purchase_amount', 'total_lifetime_value']  # ← Leak!
# total_lifetime_value includes future purchases after this transaction

# CORRECT: Point-in-time features only
features = ['purchase_amount', 'ltv_up_to_this_transaction']
```

**Result:** Amazing offline accuracy, terrible production performance.

**Solution:**
- Careful feature review
- Use point-in-time-correct data
- Test with temporal splits (train on past, validate on future)

---

### 3. Silent Data Drift

**What It Is:**
Input distribution changes, model keeps running but becomes less accurate.

**Example:**
- Model trained on summer data, now it's winter (different customer behavior)
- New product category launched (model never saw it)
- Upstream system changes how it encodes categories

**Result:** Model degrades gradually, no alerts.

**Solution:**
- Monitor input feature distributions
- Set drift detection alerts
- Have retraining policies

---

### 4. Unreproducible Results

**What It Is:**
Can't recreate a successful training run.

**Common Causes:**
- Random seed not fixed
- Data changed (no versioning)
- Dependency versions not pinned
- Environment differences

**Solution:**
```python
# Fix random seeds
np.random.seed(42)
tf.random.set_seed(42)

# Log everything
mlflow.log_param("random_seed", 42)
mlflow.log_param("git_commit", git_sha)
mlflow.log_param("dataset_version", "v1.2.3")
mlflow.log_artifact("conda.yaml")  # Exact environment
```

---

### 5. Weak Validation

**What It Is:**
Model deployed because it trained successfully, not because it's actually better.

**Example:**
- No baseline comparison
- No business metric validation
- No slice analysis (model might fail on important subgroups)

**Solution:**
```python
# Validation gates
if new_model.rmse < baseline_model.rmse * 0.95:  # Must be 5% better
    if new_model.passes_fairness_check():
        if new_model.meets_latency_requirement():
            register_model()
```

---

## Interview Questions & Answers

### Q1: "What is MLOps?"

**Good Answer:**
> "MLOps is the set of practices for building, deploying, and operating machine learning systems reliably. It combines software engineering best practices—version control, testing, CI/CD—with ML-specific needs like experiment tracking, data versioning, and model monitoring. The goal is to make ML repeatable, measurable, and safe to evolve as both code and data change."

**What NOT to Say:**
- "It's just DevOps for ML" (too simplistic, misses ML-specific challenges)
- "It's about automating everything" (automation is a means, not the goal)

---

### Q2: "Why can't we just use DevOps practices for ML?"

**Good Answer:**
> "DevOps is necessary but not sufficient. Traditional software changes when code changes—you update a function, you get different behavior. ML adds two more variables: data and learned parameters. The same training code with different data produces a different model. Models also degrade over time as real-world distributions drift, even with no code changes. This means we need additional practices: experiment tracking to compare dozens of training runs, data versioning to ensure reproducibility, model registries for governance, and drift monitoring to detect silent failures."

---

### Q3: "Walk me through a production ML lifecycle."

**Good Answer:**
> "It starts with defining a business problem and collecting validated data. We engineer features, train candidate models, and use experiment tracking to compare them. The best candidate goes through offline validation—does it beat our baseline? Does it meet performance requirements on important subgroups? We package it, register the version, and deploy to staging for integration tests. After monitoring shows stable behavior, we promote to production with gradual traffic ramping. Throughout, we monitor data drift, prediction drift, and actual model quality when labels arrive. If drift is detected or performance degrades, we trigger retraining or rollback. It's a continuous loop, not a one-way path."

---

### Q4: "What's the difference between Level 0, 1, and 2 MLOps maturity?"

**Good Answer:**
> "Level 0 is manual—notebooks, ad-hoc scripts, hand-offs between data scientists and engineers. It works for POCs but fails for production systems due to lost lineage and weak reproducibility. Level 1 introduces ML pipeline automation: modular components, orchestration, automated retraining, and experiment tracking. This is where most teams should aim—it makes training reproducible and enables continuous delivery. Level 2 adds CI/CD for the pipeline code itself: automated testing of transformations, infrastructure as code, and separate deployment paths for pipeline updates versus model updates. Level 2 is for larger platforms with frequent pipeline changes."

---

### Q5: "What causes training-serving skew and how do you prevent it?"

**Good Answer:**
> "Training-serving skew happens when feature computation differs between offline training and online serving. Common causes include: duplicated preprocessing logic that diverges over time, different library versions, or using training-time-only data features. I prevent it by sharing transformation code between training and serving—ideally through a feature store or at minimum a shared preprocessing module. I also define model signatures to enforce input schemas, add integration tests that compare offline and online preprocessing outputs on sample data, and monitor production inputs against training distributions to catch discrepancies early."

---

### Q6: "How do you know when to retrain a model?"

**Good Answer:**
> "I use a combination of signals. First, scheduled retraining based on how quickly the domain changes—daily for ad bidding, monthly for fraud detection. Second, performance-triggered retraining: when monitored metrics like AUC or RMSE degrade below thresholds, or when delayed labels show accuracy dropping. Third, drift-triggered retraining: when input distributions shift significantly according to statistical tests like KS test or PSI. Fourth, data-availability-driven: when enough new labeled data arrives to make retraining worthwhile. The key is that retraining should create a candidate, not auto-deploy—the new model still needs to pass validation gates against the current production model."

---

### Q7: "Describe a time when an ML model failed in production." (Scenario Question)

**Good Answer Framework:**
> "At [Company], we deployed a churn prediction model that performed well offline but failed in production. The issue was label leakage—we'd included 'customer_service_calls_last_30_days' as a feature, but in production we predicted churn at day 1, when we didn't yet have 30 days of calls. Our offline validation used time-agnostic splits, so it didn't catch this. We fixed it by implementing point-in-time-correct feature engineering, changing to temporal validation splits, and adding integration tests that simulate production conditions. This taught me the importance of validating not just model accuracy but also feature availability at inference time."

---

## Study Tips for Interviews

### Prepare These Stories

Have 2-3 real examples ready of:
1. A model that failed and how you debugged it
2. A successful MLOps improvement you implemented
3. A tradeoff you made between complexity and practicality

### Practice Out Loud

Read these answers out loud 3 times. Time yourself—aim for 60-90 seconds per answer.

### Connect to Your Project

For every concept here, think: "How does this apply to my housing-price-prediction project?"

### Next Steps

After mastering this guide, move to:
- **Study Guide 01:** MLflow Core Concepts
- **Code Example:** basic-mlflow-tracking/

---

## Summary: Key Takeaways

✅ **MLOps = reliable ML delivery** despite changing code, data, and environments

✅ **Lifecycle is circular:** monitoring → retraining → deployment → monitoring

✅ **Level 1 maturity** (automated ML pipelines) is the practical target for most teams

✅ **Common failures:** training-serving skew, label leakage, silent drift, weak validation

✅ **DevOps is necessary but insufficient** for ML systems

---

**Time to Complete This Guide:** 2-3 hours of focused study
**Next:** Study Guide 01 - MLflow Core Concepts
