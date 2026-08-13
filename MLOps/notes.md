# MLOps Notes and Learning Log

Use this file as the index and chronological log for MLOps study sessions.

## Primary source currently being studied

- [Google Cloud: MLOps—Continuous delivery and automation pipelines in machine learning](https://docs.cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Detailed local study guide](google-cloud-mlops-pipelines.md)
- [Interview questions from the article](interview-questions.md)
- [MLOps mastery guide](mlops-mastery-guide.md)

## Initial mental model

MLOps applies software-engineering and operations practices to the complete ML
system. The goal is to make data preparation, training, validation, deployment,
monitoring, and retraining reproducible, testable, observable, and safe.

The shortest useful distinction is:

- Data science asks: can we build a model that performs well?
- Software engineering asks: can we build a reliable application?
- MLOps asks: can we repeatedly deliver and operate a reliable ML system as its
  code, data, models, and environment change?

## Study-session template

Copy this section for each session.

```markdown
## YYYY-MM-DD — Topic

Source:

### Concepts in my own words

### Commands or implementation notes

### What failed and why

### Connection to my capstone project

### Interview questions to revisit

### Next action
```

## Learning log

### 2026-08-11 — Google Cloud MLOps maturity model

Source: the Google Cloud architecture article linked above.

Key ideas captured:

- production ML consists of much more than the model code
- ML extends CI/CD with validation of data and models
- continuous training is a separate automation concern
- maturity progresses from manual work, to automated training pipelines, to
  automated CI/CD for pipeline implementations
- safe automation requires validation gates, metadata, lineage, monitoring,
  and rollback—not only scheduled retraining

Next action: explain levels 0, 1, and 2 without reading the study guide, then
implement the level-0 version of the first capstone project.
