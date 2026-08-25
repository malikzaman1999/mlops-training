---
title: "Course: MLflow in Action - Master the art of MLOps using MLflow tool | Udemy Business"
description: A master guide to unleash the full potential of MLflow to optimize MLOps. Streamline MLOps workflows using MLflow tool
author: Udemy Business
source: https://10pearls.udemy.com/course/mlflow-course/learn/lecture/40364830#overview
created: "2026-08-20"
tags:
  - hover-notes
  - udemy
hovernotes-id: doc_82cbd4a0-b644-4c97-a4f3-1a219c92447d
---

### MLflow `set_tags()`

- Used to set multiple tags under the current run
- **Parameters**:
    - `tags`: A dictionary where the key is the `tag_name` (String) and the value is the tag value (Any type)
- **Return**:
    - `None`
- **Usage Constraints**:
    - These logging functions can only be specified during an active run
    - They must be called between the `start_run()` and `end_run()` functions

### Practical Implementation of Tags

- **Programmatic Tagging Example**:
    - Tags can be added within the `start_run()` block using `mlflow.set_tag(key, value)`
    - Example code:

```python
mlflow.set_tag("release.version", 0)
```

- **Managing Tags via MLflow UI**
    - Tags are not limited to code; they can be added or edited through the MLflow interface
    - Methods include:
            - Editing tags associated with a specific experiment
            - Clicking on a specific run and adding tags directly
- **Verifying Results**
    - After running the code, tags appear in the MLflow directory
    - In the MLflow UI, a dedicated "Tags" section is created for the run, often containing both user-defined tags and default system tags

### MLflow Tag Storage Mechanism

- **File-based storage in the MLflow directory**
    - Within the specific run folder, tags are stored inside the `tags` subdirectory
    - Each tag is represented by its own file:
        - **Filename**: The name of the tag (e.g., `release.version`)
        - **File Content**: The value assigned to that tag (e.g., `0`)

```text

# Example of how a tag appears in the file system
File Name: release.version
Content: 0
```

### MLflow System Tags

- Automatically created by MLflow every time a new run is launched
- Reserved for internal use and assigned by MLflow to provide metadata about the run
- All system tags follow a specific naming convention, starting with `mlflow.`

#### Common System Tags

| Tag Key | Description |
| --- | --- |
| mlflow.logModel.history | Related to the model registry and the version of the model |
| mlflow.runName | Stores the name of the run |
| mlflow.source.name | Contains the name of the file from which the run was generated (e.g., main.py) |
| mlflow.source.type | Specifies the type of source where the execution occurred (e.g., local or cloud) |
| mlflow.user | The name of the user running the code |

- **Other notable system tags include**:
    - `mlflow.note.content`: A descriptive note about the run (can be overridden by the user)
    - `mlflow.parentRunId`: The ID of the parent run, if this is a nested run
    - `mlflow.source.git.commit`: The commit hash of the executed code, if in a git repository
    - `mlflow.source.git.branch`: The name of the branch of the executed code
    - `mlflow.source.git.repoURL`: The URL that the executed code was cloned from
    - `mlflow.project.env`: The runtime context used by the MLflow project (e.g., `docker` or `conda`)
    - `mlflow.docker.image.id`: The ID of the Docker image used to execute the run

### Batch Tagging with `set_tags()`

- Use `mlflow.set_tags()` to assign multiple tags in a single call
    - This function accepts a dictionary where keys are the tag names and values are the tag content
    - Custom tags do not require a specific prefix (e.g., they do not need to start with `release.`)

```python

# Example of setting multiple tags using a dictionary
tags = {
    "name": "my_run_name",
    "release.version": "1.0"
}
mlflow.set_tags(tags)
```

### MLflow UI Tag Visibility

- **Filtering of System Tags**
    - The MLflow UI does not display default system tags
    - The UI primarily shows only the tags provided by the user
    - This differs from the local file system, where both user and system tags are present in the `tags` directory

### Multiple Runs per Experiment

- While a single program often performs one run, several use cases require multiple runs within a single execution:
    - **Incremental Training**
        - Training a model incrementally by adding new data over time
        - Running multiple training sessions with different data slices to monitor performance changes
    - **Model Checkpointing**
        - Saving the state of a model at different stages during long training processes
        - Each checkpoint can be recorded as a separate run within the same MLflow experiment to track progress
- **Implementing Multiple Runs**
    - To execute multiple runs, repeat the logic block bounded by the start and end functions
    - Each repeated block must be provided with a unique run name

```python

# Logic for a single run block
mlflow.start_run()

tags = {
    "engineering": "RL platform",
    "release.candidate": "RC1",
    "release.version": "2.0"
}
mlflow.set_tags(tags)

# ... training and evaluation logic ...

mlflow.log_params(params)
mlflow.log_metrics(metrics)

mlflow.end_run()
```

### Implementing Multiple Runs

- To execute multiple runs within a single script, duplicate the logic block bounded by `start_run` and `end_run` functions
    - Each block must be assigned a unique run name to distinguish them in the MLflow UI
- **[Tip]** Commenting out excessive print statements can help keep the terminal output clean when running multiple iterations

### Accessing Run Metadata

- **`mlflow.active_run()`**
    - Used inside the `start_run` and `end_run` block to access the current active run
    - Can be used to retrieve the current `run_id` and `run_name` for logging or printing
- **`mlflow.last_active_run()`**
    - Used after a run has completed to retrieve the most recently active run
    - Useful for accessing metadata from the run that just finished

```python

# Example of a single run block designed for duplication
mlflow.start_run(run_name=run_name)

tags = {
    "engineering": "RL platform",
    "release.candidate": "RC1",
    "release.version": "2.0"
}
mlflow.set_tags(tags)

# Accessing current run info
current_run = mlflow.active_run()
print(f"Current Active run id is: {format(current_run.info.run_id)}")
print(f"Current Active run name is: {format(current_run.info.run_name)}")

# ... training and evaluation logic ...

mlflow.log_params(params)
mlflow.log_metrics(metrics)

mlflow.end_run()

# Accessing the run that just completed
run = mlflow.last_active_run()
print(f"Recent Active run id is: {format(run.info.run_id)}")
print(f"Recent Active run name is: {format(run.info.run_name)}")
```

### Verifying Multiple Run Execution

- **Terminal Output Analysis**
    - When executing a script with multiple runs, the terminal displays metadata for each run sequentially
    - Each block includes the run's specific metadata (e.g., run ID and run name)
- **Filesystem and UI Organization**
    - MLflow creates individual folders for each run within the experiment directory (e.g., `mlruns/experiment_5/`)
    - These folders can be accessed via the local directory or visualized through the MLflow UI
- **Confirming the Last Active Run**
    - In a sequence of multiple runs, `mlflow.last_active_run()` returns the metadata for the very last run that completed
    - In the demonstration, where three runs were executed, the function returned the details for the third run

### Use Cases for Multiple Runs

- **Hyperparameter Tuning**
    - Allows finding optimal hyperparameters by creating multiple runs in one program
    - Each run can be assigned different hyperparameter values
    - Enables comparison of model performance across runs to identify the best configuration
- **Multiple Dataset Evaluation**
    - Useful when you want to test your model or process against several different datasets within a single execution

### Additional Use Cases for Multiple Runs

- **Incremental Training and Model Checkpointing**
    - Previously mentioned as ways to manage training progress and state within a single program
- **Feature Engineering**
    - Allows tracking and comparing the impact of different feature transformations on model performance
    - Each run can represent a different set of transformations or varied features
- **Cross Validation**
    - Used to evaluate model robustness
    - Multiple runs can be created for each fold or combination of data, allowing for the averaging of performance metrics

### Managing Hyperparameters Across Runs

- **Providing Varied Values**
    - Since a single run might use default values (e.g., `alpha=0.7`, `l1_ratio=0.7`), multiple runs require a way to inject different hyperparameters into each execution
- **Implementation Approach**
    - For learning purposes, different values can be provided by hard-coding them within each run block in the script

### Hard-coding Hyperparameters for Multiple Runs

- To test different configurations, unique values can be provided to each run block
- **[Implementation Note]** It is critical to update values in two places to avoid mismatches:
    - The actual model training/logic
    - The `mlflow.log_params` call used to record the metadata

#### Example Implementation Pattern

```python

# Run 1.1: Using default parameters
with mlflow.start_run(run_name="run 1.1") as run:

# ... (using default alpha=0.7, l1_ratio=0.7)
    mlflow.log_params({"alpha": 0.7, "l1_ratio": 0.7})

# Run 2.1: Hard-coded different values
with mlflow.start_run(run_name="2.1") as run:
    alpha = 0.9
    l1_ratio = 0.7

# ... (training with new alpha)
    mlflow.log_params({"alpha": alpha, "l1_ratio": l1_ratio})

# Run 3.1: Hard-coded different values
with mlflow.start_run(run_name="3.1") as run:
    alpha = 0.4
    l1_ratio = 0.4

# ... (training with new values)
    mlflow.log_params({"alpha": alpha, "l1_ratio": l1_ratio})
```

### Analyzing Hyperparameter Impact

- The experiment compared three sets of parameters to observe the effect on model performance:
    - **Run 1.1 (Default)**: `alpha=0.7`, `l1_ratio=0.7` $\rightarrow$ RMSE: 0.83, MAE: 0.66
    - **Run 2.1 (Increased)**: `alpha=0.9`, `l1_ratio=0.7` $\rightarrow$ RMSE: \~0.83, MAE: \~0.66 (similar to default)
    - **Run 3.1 (Decreased)**: `alpha=0.4`, `l1_ratio=0.4` $\rightarrow$ RMSE: 0.76, MAE: 0.59
- **[Conclusion]** Decreasing the hyperparameter values yielded better performance in this specific case, suggesting further runs with even lower values might optimize the model further.

### Multiple Experiments per Program

- It is possible to have multiple distinct experiments within a single program, similar to how multiple runs can be managed within one experiment.
- It is possible to run multiple distinct experiments within a single program
- **[Organizational Principle]** MLflow is designed for proper management; therefore, it is recommended to "club interrelated things properly"
    - **One Experiment**: Use this to test different values for a specific set of hyperparameters or to test variations of the same algorithm
    - **Multiple Experiments**: Use these when you want to move to a totally different set of hyperparameters or a different algorithm entirely
- This ensures that the tracking remains organized and meaningful rather than cluttered with unrelated data

![00:00:48](hover-notes-images/screenshot-01M0FS8E2EJQ5B6V53XNCNG3T8.png)
[00:00:48](https://10pearls.udemy.com/course/mlflow-course/learn/lecture/40370726#overview)

### Comparing Regression Models

- The current approach uses **ElasticNet** regression, which combines both L1 and L2 regularization penalties using two hyperparameters: `alpha` and `l1_ratio`.
- To optimize performance, it is necessary to test individual regularization methods:
    - **Ridge Regression**: Uses only the L2 penalty.
    - **Lasso Regression**: Uses only the L1 penalty.
- **[Hypothesis]** Using a single type of regularization (either L1 or L2 alone) might yield better results than the combined ElasticNet approach.

### Implementation Plan

- Create two new distinct experiments: one for Ridge and one for Lasso.
- Within each experiment, test various hyperparameter values to find the optimal configuration.
- **[Code Preparation]** To implement this, `Ridge` and `Lasso` must be imported from `sklearn`:

```python
from sklearn.linear_model import ElasticNet, Ridge, Lasso
```

### Implementing Ridge and Lasso Experiments

- To implement the new models, the existing ElasticNet experiment block is copied and modified
    - **[Code Organization]** While duplicating code works for quick implementation, a more scalable approach is to define separate functions for each experiment in different files and call them from `main.py` to prevent the main script from becoming too lengthy
- **Experiment Differentiation**
    - A `print` statement is added to the terminal to clearly distinguish which experiment is currently running
    - The experiment name is updated using `mlflow.set_experiment(experiment_name=...)`
- **Run Name Management**
    - Because these are entirely new experiments, it is acceptable to reuse the same `run_name` used in previous experiments

### Code Structure for New Experiments

- The core logic for both Ridge and Lasso is nearly identical to ElasticNet, requiring only minor changes to the model parameters
- Example of updating the experiment name and parameters:

```python

# For the second experiment (e.g., Ridge)
exp = mlflow.set_experiment(experiment_name="exp_ridge")

# ... (other setup code) ...

# Updating parameters for the specific model
params = {
    "alpha": 0.4,
    "l1_ratio": 0.0  # Set to 0 for Ridge (L2 only)
}

# Training the model
lr = Ridge(alpha=params["alpha"], l2_ratio=params["l2_ratio"])

# Note: The transcript/visuals suggest adjusting the specific hyperparameter relevant to the model
```

### Implementing Ridge Experiment

- Replaced the ElasticNet model with Ridge to focus solely on the L2 penalty
    - Removed the `l1_ratio` parameter from the code as Ridge only requires `alpha`
    - Kept `random_state=42` for consistency across experiments

```python

# Second experiment: Ridge
exp = mlflow.start_run(run_name="run1")

# ... (tags and other setup) ...

# Ridge uses only the alpha parameter (L2 penalty)
lr = Ridge(alpha=params["alpha"], random_state=42)
lr.fit(train_x, train_y)

predicted_qualities = lr.predict(test_x)
rmse, mse, r2 = eval_metrics(test_y, predicted_qualities)

print(f"Ridge (alpha={params['alpha']})")
print(f"RMSE: {rmse} & MSE: {mse}")
print(f"R2: {r2} & MSE: {mse}")

# log parameters
params = {
    "alpha": 0.4
}

# ... (logging metrics and artifacts) ...

mlflow.end_run()
```

### Implementing Lasso Experiment

- The Ridge experiment block is copied and pasted to serve as the template for the third experiment (Lasso)
- Replaced the Ridge experiment code to implement Lasso regression
- **[Hyperparameter Note]** While the parameter name remains `alpha`, its meaning changes based on the model type:
    - In **Ridge**: `alpha` represents the **L2 penalty**
    - In **Lasso**: `alpha` represents the **L1 penalty**
    - In **ElasticNet**: The model combines both L1 and L2

```python

# Third experiment: Lasso
exp = mlflow.start_run(run_name="run1")

# ... (tags and other setup) ...

# Lasso uses only the alpha parameter (L1 penalty)
lr = Lasso(alpha=params["alpha"], random_state=42)
lr.fit(train_x, train_y)

predicted_qualities = lr.predict(test_x)
rmse, mse, r2 = eval_metrics(test_y, predicted_qualities)

print(f"Lasso (alpha={params['alpha']})")
print(f"RMSE: {rmse} & MSE: {mse}")
print(f"R2: {r2} & MSE: {mse}")

# log parameters
params = {
    "alpha": 0.4
}

# ... (logging metrics and artifacts) ...

mlflow.end_run()
```

### Summary of Regression Experiments

- The setup creates three distinct experiments to compare regularization methods:

| Experiment | Model | Regularization Type |
| --- | --- | --- |
| 1 | ElasticNet | Combined L1 and L2 |
| 2 | Ridge | L2 penalty only |
| 3 | Lasso | L1 penalty only |

- **Code Organization Tip**: For larger projects, instead of having one lengthy `main.py`, it is better practice to define individual experiments as separate functions in different files and call them from the main script.

### Evaluating Experiment Results

- The performance metrics (RMSE, MSE, R2) for Ridge and Lasso did not show significant improvements over the ElasticNet baseline
    - In this specific case, reducing the L2 penalty (Ridge) or applying L1 (Lasso) didn't drastically change model performance
- **[Key Insight]** The primary goal of this setup was not metric optimization, but demonstrating the technical capability to orchestrate multiple runs and experiments within a single script

### MLflow Experimentation Workflow

- The MLflow UI successfully organized the work into three distinct experiments, each containing three separate runs:
    - `exp_multi_EL` (ElasticNet)
    - `exp_multi_Ridge` (Ridge)
    - `exp_multi_Lasso` (Lasso)
- **[Efficiency for Data Scientists]** This approach allows for rapid testing of various:
    - Models
    - Features
    - Datasets
    - Hyperparameters
- **[The Trade-off: Sequential vs. Parallel Execution]**
    - **Current Approach (Sequential)**:
        - Pros: Simple to implement in a single script
        - Cons: Time-consuming, as each experiment must finish before the next begins
    - **Professional Approach (Parallel)**:
        - Pros: Significantly reduces total model creation time by running experiments simultaneously
        - Cons: Requires more complex orchestration

```mermaid
flowchart TD
    A[Single Program Script] --> B{Execution Mode}
    B -->|Sequential| C[Run Exp 1] --> D[Run Exp 2] --> E[Run Exp 3]
    B -->|Parallel| F[Run Exp 1 & 2 & 3 Simultaneously]
    C & D & E --> G[Total Time: Sum of all runs]
    F --> H[Total Time: Duration of longest run]
```

### MLflow Automatic Logging

- Previously, all logging was performed manually using specific functions:
    - `log_params`: To log hyperparameters
    - `log_metrics`: To log performance metrics
    - `log_artifacts`: To log files or other external entities
- **[The Problem with Manual Logging]** As the number of parameters and metrics to track increases, manual logging becomes:
    - Extremely difficult to manage one by one
    - Result in significantly more lengthy and complex code
- **[The Solution: Auto-logging]** MLflow provides an automatic logging feature designed to reduce manual effort and streamline the experimentation process.

### MLflow Autologging Mechanics

- A feature that allows automatic logging of parameters, metrics, artifacts, etc., without requiring explicit code instrumentation
- **[How it works]** It captures information directly from the runtime environment and the code itself
    - Automatically captures model metrics and parameters
    - Records the framework used to build the model
    - Captures the version of the code and the git commit hash
    - Logs the timestamp of the experiment

### Methods for Implementing Autologging

- **General Autologging**
    - Uses `mlflow.autolog()`
    - Enables autologging for every supported library that is currently installed and being used in the code
- **Library-Specific Autologging**
    - Uses `mlflow.<lib>.autolog()`
    - Logs entities only for specific, designated libraries

#### Supported Libraries

- Scikit-learn
- Keras
- Gluon
- XGBoost
- LightGBM
- Statsmodels
- Spark
- Fastai
- Pytorch

### Choosing an Autologging Method

- **`mlflow.autolog()`**
    - Calls logging for all supported libraries simultaneously
    - **[When to use]** Use this if you are working with multiple MLflow-supported libraries and want to log items for all of them in a single shot
- **Library-specific autologging**
    - Only calls logs for the specified libraries
    - **[When to use]** Use this if you want to avoid logging for all libraries and only want to capture data for specific ones

### Parameters of `mlflow.autolog()`

- The function accepts 8 parameters, most of which are Boolean values used to determine whether or not to log a specific entity
- The available parameters are:
    - `< log_models: bool = True, log_input_examples: bool = False, log_model_signatures: bool = True, log_datasets: bool = True, disable: bool = False, exclusive: bool = False, disable_for_unsupported_versions: bool = False, silent: bool = False >`
- **`log_models`**
    - A Boolean field used to specify whether or not to log the output model to MLflow tracking
- **`log_input_examples`**
    - A Boolean parameter
    - If set to `True`, input examples from training datasets are collected and logged along with the model artifacts during training

### `log_input_examples` Dependency

- Input examples are considered MLflow model attributes
- **[Requirement]** They are only collected if the `log_models` parameter is also set to `True`

#### `log_model_signatures` parameter

- Specifies whether to log the model signatures
- **[What are model signatures?]** They define the schema for a model's inputs and outputs
    - They specify the format and data types of the input data the model can accept
    - They specify the format and data types of the outputs the model produces

![00:00:00](hover-notes-images/screenshot-01M0FXPB9J0GK0NSXRC028AJ1V.png)
[00:00:00](https://10pearls.udemy.com/course/mlflow-course/learn/lecture/40381468#overview)

#### `log_model_signatures` parameter dependency

- Like input examples, model signatures are also model attributes
    - **[Requirement]** They are only collected if `log_models` is set to `True`

#### `log_datasets` parameter

- A Boolean parameter used to log dataset information to MLflow tracking
- **[What is logged]** If set to `True`, both the training and evaluation datasets are logged

#### `disable` parameter

- A Boolean parameter used to turn off all automatic logging
- Set to `True` to disable autologging entirely

#### `exclusive` parameter

- Determines how autologged content is associated with runs
- **If&#32;`True`**: Autologged content is *not* logged to user-created fluent runs
- **If&#32;`False`**: Autologged content is logged to the active fluent run (which may be user-created)
    - **[Note]** This is usually set to `False` so logs are stored within a specified run

#### `disable_for_unsupported_versions` parameter

- A Boolean parameter to prevent compatibility issues
- **[What it does]** If `True`, automatic logging is disabled for integrated library versions that have not been tested against or are incompatible with the current MLflow client version

#### `silent` parameter

- Controls the verbosity of the logging process
- **If&#32;`True`**: Suppresses all event logs and warnings from MLflow during autologging setup and training execution
- **If&#32;`False`**: Shows all events and warnings during the process

### Transitioning to `mlflow.autolog()`

- Replacing manual logging functions with autologging to reduce boilerplate
    - Instead of calling `log_params` or `log_metrics` manually, `mlflow.autolog()` captures these automatically during training
    - Explicit calls to `log_model` can often be removed if using standard supported frameworks
- **[Manual Logging Requirement]** Input datasets are not automatically logged by the autolog function
    - To keep the original input dataset in the run, you must still use `mlflow.log_artifact()`
- **[The Custom Model Catch]** Autologging has limitations with custom model implementations
    - Autologging works seamlessly with standard, supported models
    - If you customize a model or change how it performs logging, `mlflow.autolog()` may fail to capture it, requiring you to use explicit `mlflow.sklearn.log_model()` calls

```python

# Example of manual artifact logging alongside autologging
mlflow.autolog()

# ... training code ...

# Manually logging the input data as it is not covered by autolog
mlflow.log_artifact("red-wine-quality.csv")

# Manually logging a custom model if autologging doesn't catch it
mlflow.sklearn.log_model(lr, "red-wine-quality.csv")
```

### Choosing between Autologging and Manual Logging

- **[When to use Autologging]** Best choice when using standard, supported models (e.g., standard scikit-learn packages)
- **[When to use Manual Logging]** Recommended for advanced machine learning problems involving customization
    - Custom models may include custom metrics and loss functions that autologging cannot automatically detect
    - In these cases, using `mlflow.log_*` functions individually is more reliable

### Proper Placement of `mlflow.autolog()`

- The function must be called **before** the model training process starts
    - **[Why?]** MLflow autologging works by instrumenting specific functions and methods within supported libraries to capture data during execution
    - If called after the training step (e.g., after `.fit()`), the instrumentation will not be in place to capture the relevant parameters and metrics, resulting in no logs being recorded

```python

# Correct placement: call autolog before training
mlflow.autolog()

# The training process (e.g., .fit()) will now be instrumented
tr.fit(train_x, train_y)
```

### Configuring `mlflow.autolog()`

- **[Default Behavior]** Several parameters are set to `True` by default, so they do not need to be explicitly mentioned:
    - `log_model_signatures`
    - `log_model_params`
- **[Logging Input Examples]** The `log_input_examples` parameter can be enabled
    - **[Note]** Setting this to `True` does **not** log the entire input dataset; it only logs a few examples from the data to provide context
    - Full input datasets still require manual logging via `mlflow.log_artifact()` if they are needed

```python

# Configuring autologging with specific parameters
mlflow.autolog(log_input_examples=True)

# The training process will now capture parameters and examples
lr.fit(train_x, train_y)
```

### Verifying Autologging in the MLflow UI

- Once the code runs, the MLflow UI confirms successful autologging (e.g., "Autologging successfully enabled for scikit-learn")
- **[What is captured automatically?]** For a standard model like `ElasticNet`, the UI will display:
    - **Datasets**: Automatically logs the training and evaluation datasets used
    - **Parameters**: Captures all available parameters for the specific model (e.g., 11 parameters for scikit-learn's `ElasticNet`)
    - **Model Signatures**: Captures the input and output schema of the model

### Detailed Breakdown of Autologged Data

- **Parameters**
    - Automatically logs all available parameters for the model, not just the ones explicitly defined in code
    - **[Example]** For `ElasticNet`, even if only `alpha`, `l1_ratio`, and `random_state` are provided, MLflow logs all 11 parameters with their default values
- **Metrics**
    - Captures all relevant metrics available for the specific model (e.g., 5 metrics for `ElasticNet`)
- **Tags**
    - Combines user-defined tags with automatically generated metadata
    - **[Automatic Tags]** Includes `estimator_class` and `estimator_name` (e.g., identifying the model as `scikit-learn`'s `ElasticNet`)
- **Artifacts**
    - Stores model files and supplementary data
    - **[Input Examples]** If `log_input_examples=True` is set, an `input_examples.json` file is created containing a few rows from the input data for context
- **Model Signatures**
    - Because `log_model_signatures` is `True` by default, MLflow logs the model's input and output schemas
    - This defines the expected data types and structures for making future predictions

### Library-Specific Autologging

- While `mlflow.autolog()` is a general-purpose function for most logging requirements, MLflow also supports library-specific functions
    - These functions are designed to log only entities relevant to a specific library
- **`sklearn.autolog`**
    - A library-specific function for scikit-learn
    - It inherits all parameters from the generic `mlflow.autolog()`
    - It includes additional parameters specifically tailored for scikit-learn needs
- **Specialized Parameters in&#32;`sklearn.autolog`**
    - `max_tuning_runs`: Sets the maximum number of child MLflow runs created for hyperparameter search estimators
        - This is useful when using algorithms like Grid Search or Random Forest to prevent an excessive number of runs from being logged

### Additional `sklearn.autolog` Parameters

- **`log_post_training_metrics`**
    - When set to `True`, it logs several metrics after the model has been trained
    - **[Example Metrics]** Includes MAE, RMSE, and R2 score
    - The exact set of metrics logged depends on the specific estimator used and the installed version of scikit-learn
- **`serialization_format`**
    - Specifies the format used for model artifacts when the trained model is saved
    - The choice of format affects the performance and portability of the model
        - Some formats may be more efficient or faster to load
        - Others may offer better portability across different platforms and environments
    - **[Available Formats for scikit-learn]**
        - `mlflow.sklearn.SERIALIZATION_FORMAT_PICKLE`
        - `mlflow.sklearn.SERIALIZATION_FORMAT_CLOUDPICKLE`

### Specialized `sklearn.autolog` Parameters

- **`registered_model_name`**
    - Specifies the name of the model to be registered in the MLflow Model Registry
    - If this parameter is provided, every time a model is trained, it is registered as a new version of the model with this name
    - If the registered model does not already exist, MLflow will create it
- **`pos_label`**
    - Used exclusively for **binary classification** models to specify the positive class label
    - In binary classification, targets are typically encoded as 0 (negative) and 1 (positive)
    - **[Usage Note]** While 1 is the default, this parameter should be used if your dataset uses 0 or arbitrary values (like -1) to represent the positive class
    - **[Constraints]**
        - Must only be set for binary classification models
        - If used for multi-level classification, the training metrics calculation will fail and metrics won't be logged
        - If used for regression models, the parameter is simply ignored

### Using `mlflow.sklearn.autolog()` in Practice

- To capture training metrics, you can call the function without any arguments
    - This works because `log_post_training_metrics` is set to `True` by default
- **[Implementation Example]**

```python
mlflow.sklearn.autolog()
```

- Running the training script with autologging enabled automatically populates the MLflow tracking server with detailed metadata

### MLflow UI Observations

- After a run is completed, the MLflow UI displays a comprehensive breakdown of the experiment
- **[Logged Components]**
    - **Datasets**: The specific data used for training
    - **Parameters**: The hyperparameters used in the model (e.g., 11 parameters in the example)
    - **Metrics**: Performance measurements, including post-training metrics (e.g., 5 metrics)
    - **Tags**: Metadata associated with the run
- The metrics captured via library-specific autologging (like `sklearn.autolog`) are consistent with manual logging but are handled automatically by the framework.

## Tracking Server

- A centralized repository responsible for storing metadata and artifacts generated during the training of machine learning models
- **[Why use it?]** Because logging to a local system is not ideal for production and is not scalable; a dedicated server allows for enterprise-level requests and sharing results with team members at scale
- **[Core Components]**
    - **Storage**: The component responsible for holding the data
    - **Networking/Communication**: The component that allows clients to interact with the server via requests (e.g., sending data to store or sending retrieval requests)

```mermaid
flowchart TD
    Client[Client] <-->|Requests/Responses| Server[MLflow Tracking Server]
    subgraph ServerComponents [Tracking Server Components]
        direction TB
        Storage[Storage]
        Networking[Networking/Communication]
    end
    Server --- Storage
    Server --- Networking
```

### Tracking Server Components

- **Storage**
    - Responsible for storing artifacts (e.g., model checkpoints, trained models) and execution metadata (e.g., experiment and run details)
- **Networking**
    - Allows interaction with the tracking server using REST API or RPC calls

### Storage Options

- MLflow categorizes storage into two distinct types:
    - **Backend Store**
        - Stores metadata related to experiments and runs
        - Examples of metadata: experiment name, ID, run name, run ID, parameters, metrics, and tags
    - **Artifact Store**
        - Stores the actual files generated during training

```mermaid
flowchart TD
    Storage[Storage] --> Backend[Backend Store]
    Storage --> Artifact[Artifact Store]

    subgraph BackendDetails [Backend Store Types]
        direction TB
        DB[DB Store]
        File[File Store]
    end

    Backend --> DB
    Backend --> File
```

#### Backend Store Implementation

- **Database (DB) Store**
    - Uses relational databases to manage metadata
    - Supported databases include:
        - SQLite
        - MySQL
        - PostgreSQL
- **File Store**
    - Stores metadata in a file-based format

#### Artifact Store Implementation

- Can be stored in the local file system or via cloud storage
    - Amazon S3
    - Azure Blob Storage
    - Google Cloud Storage (GCS)
- **[What is stored?]** Artifacts such as trained models, input data, output files, or visuals

#### Networking Component

- Establishes communication between the client and the tracking server
- Supports two modes of communication:
    - **REST API**
        - Provides a simple and flexible interface
        - Accesses the tracking server over HTTP
    - **RPC**
        - Uses gRPC
        - A high-performance open-source framework
        - Provides bidirectional, faster, and more efficient communication channels

```mermaid
flowchart TD
    Network[Network]
    Network --> REST["REST API (over HTTP)"]
    Network --> RPC["RPC (using gRPC)"]
```

### Artifact Proxy Access

- The tracking server can act as a proxy for artifact storage
    - Useful when there are security concerns regarding direct access to artifacts
    - Helpful when data must be accessed from locations where direct access is restricted (e.g., accessing Amazon S3 or Azure Blob Storage)
- **[How it works]** The tracking server can be utilized as a proxy server for artifact operations
    - This allows users to authenticate and access data from a centralized location, regardless of physical storage location
- **[Security Strategy]** Organizations with strict requirements can create a separate MLflow tracking server instance exclusively for handling sensitive artifact storage/retrieval, then connect it to the main tracking server via proxying

### Client Interaction and Experiment Management

- Client applications communicate with the tracking server to log experiment data and store artifacts
- **APIs and SDKs** are provided for various programming languages and ML libraries:
        - **Languages**:
                - Python
                - Java
                - R
        - **Machine Learning Libraries**:
                - TensorFlow
                - PyTorch
                - Scikit-learn
- **[Capabilities]** These tools allow users to:
        - Log experiment data
        - Query runs and experiments
        - Manage experiments

### Benefits of a Centralized Tracking Server

- **[Why use it?]** Because it provides a single source of truth for the entire team
    - **Compare results**: Easily evaluate different experiments against one another
    - **Track performance**: Monitor how model performance evolves over time
    - **Collaboration**: Enables team members to work together using the same centralized data

### Environment Setup

- Activating the project environment in the terminal:
    - Command used: `conda activate mlflow_demo1`

### MLflow Server Configuration

- **Backend Store URI**
    - Specifies the database used to store experiment metadata
    - **[Supported Databases]** MLflow currently supports:
        - SQLite (easiest to work with)
        - MySQL
        - PostgreSQL
    - **[Syntax Examples]**
        - For SQLite: `sqlite:///mlflow.db`
        - For MySQL: `mysql://<database_name>`
- **Artifact URI**
    - Specifies the location where experiment artifacts (files, models, etc.) are stored
    - By default, this is set using the `--default-artifact-root` flag
    - Defines the directory where all new experiment artifacts will be saved

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-uri <path_to_directory>
```

### Starting the MLflow Tracking Server

- **[Workflow]** To initialize the server, follow these steps in the terminal:

    1. Activate the project environment (e.g., `conda activate mlflow_demo1`)
    2. Execute the `mlflow server` command with required configuration flags

- **[Command Syntax]** Using specific URIs to direct where data is stored:
    - `--backend-store-uri`: Defines where metadata files/database entries are kept
    - `--default-artifact-uri`: Defines the directory for experiment artifacts

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-uri ./mlflow-artifacts
```

- **[Configuration Impact]**
    - Setting a custom `--default-artifact-uri` only affects new experiments created after the flag is enabled
    - It does not retroactively impact experiments created under previous server configurations

### MLflow Artifact Storage Details

- **[Scope of Configuration]** The `--default-artifact-uri` flag only impacts experiments created *after* the flag is enabled
    - It does not affect experiments that were already created under previous server configurations
- **[Default Storage Behavior]**
    - If the `--serve-artifact` option is enabled in the command, data is logged to the specified MLflow artifacts URI
    - If no custom path is specified, the default location for logging is `./mlruns`
- **[Customizing Paths]**
    - You can specify any local folder or a remote storage path as the artifact URI

### MLflow Server Configuration Details

- **[Customizing Artifact Storage]**
    - You can specify a custom local directory for artifacts (e.g., `./mlflow-artifacts`) using the `--default-artifact-uri` flag
- **[Server Host Configuration]**
    - The server can be configured to run on a specific host, such as `127.0.0.1`
- **[Storage Logic Summary]**

| Condition | Resulting Storage Location |
| --- | --- |
| --serve-artifact is enabled | Data is logged to the specified --default-artifact-uri |
| --serve-artifact is NOT enabled | Data is logged to the default ./mlruns directory |

### MLflow Server Host and Port Configuration

- **[Specifying Network Settings]** The tracking server can be bound to a specific network interface and port:
    - `--host`: Defines the host address (e.g., `127.0.0.1` for localhost)
    - `--port`: Defines the port number (e.g., `5000`)

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-uri ./mlflow-artifacts --host 127.0.0.1 --port 5000
```

- **[Command Components]**
    - The command creates a tracking server running at the specified address and port
    - Further parameters are available in the official MLflow documentation

### Running the MLflow Server

- **[Execution Steps]**

    1. Activate the target environment (e.g., `conda activate mlflow_demo1`)
    2. Execute the `mlflow server` command with all necessary configuration flags

- **[Troubleshooting Environment Issues]**
    - If the environment is not properly activated, the system may return errors like `EnvironmentNameNotFound` or fail to recognize the `mlflow` command
    - **Error Example:**

```text
EnvironmentNameNotFound: Could not find conda environment: mlflow_demo1
      You can list all discoverable environments with `conda info --envs`
```

    - **Command Not Found Error:**

```text
'mlflow' is not recognized as an internal or external command, operable program or batch file.
```

### Verifying the MLflow Tracking Server

- **[Accessing the UI]** Once the server is running, the MLflow UI can be accessed via the browser at the specified address (e.g., `http://127.0.0.1:5000`)
    - A newly started server will show an empty UI because no experiments or runs have been performed yet

### Logging Experiments to the Server

- **[Connecting Code to the Server]** To send experiment data to the tracking server, the tracking URI in the Python script must be updated to match the server's address

```python
import mlflow

# Update this to point to your running MLflow server
mlflow.set_tracking_uri("http://127.0.0.1:5000")

# Define the experiment name
mlflow.set_experiment("my_experiment")

# Rest of the autologging/training code...
```

- **[Observing Results]** After running the updated code:
        - **Artifacts:** A new directory (e.g., `mlflow-artifacts`) is created locally to store only the artifacts (files, models, etc.) produced during the run
        - **Metadata:** The experiment metadata (parameters, metrics, etc.) is stored in the backend store (e.g., the SQLite database) rather than the artifact folder
        - **UI Update:** Refreshing the MLflow UI will show the newly created experiment and its associated runs

### Tracking Server Storage Architecture

- **[Separation of Concerns]** When using a tracking server, the storage of experiment data is split into two distinct components:
    - **Metadata**: Experiment details, run parameters, metrics, and tags are stored in the **backend store** (e.g., a SQLite database).
    - **Artifacts**: Files like models, plots, and datasets are stored in the **artifact URI** location (e.g., a local folder).
- **[Comparison with Default Setup]**
    - **Standard/Default Setup**: Both metadata and artifacts are stored together in the same `./mlruns` directory.
    - **Tracking Server Setup**: Metadata is centralized in a database, while artifacts are kept in a separate, dedicated directory.

```mermaid
flowchart TD
    Client["MLflow Client/Python Script"] -->|Logs Metadata| DB[("Backend Store: SQLite/MySQL")]
    Client -->|Logs Artifacts| Folder["Artifact Directory: ./mlflow-artifacts"]
    DB -.->|UI Displays| UI["MLflow Web UI"]
    Folder -.->|UI Displays| UI
```

## Tracking Server Configurations

- **[Configuration Flexibility]** The MLflow client can interface with a variety of different backend and artifact storage configurations. According to official documentation, there are six common configuration scenarios.

### Scenario 1: MLflow on localhost

- **[Local Setup]** This is the most common setup for learners, where MLflow is installed and run entirely on a local machine.
- **[Unified Storage]** In this scenario, both the backend store and the artifact store share a common directory on the local file system, specifically the `./mlruns` directory.
    - This directory contains all artifacts, metrics, hyperparameters, and tags.

```mermaid
flowchart TD
    subgraph localhost
        UserCode["User ML code + MLflowClient APIs"]
        FileStore["FileStore (./mlruns)"]
        UserCode --> FileStore
    end
```

### MLflow on localhost Details

- **[Interface Mechanics]** The MLflow client uses two distinct local interfaces to record data:
    - **Local Artifact Repository**: Used specifically to store artifacts (e.g., model files, plots)
    - **File Store**: Used to record run metadata, including hyperparameters, metrics, and tags
- **[Setup and Automation]** This configuration requires no manual setup
    - It is automatically configured when installing MLflow via `pip install mlflow` on a local system
    - The `./mlruns` directory and required folder structures are created automatically when the first experiment run is performed
- **[Use Cases]** Because of its simplicity, this scenario is best suited for:
    - Small-scale projects
    - Development and testing purposes

### MLflow on localhost with SQLite

- In this configuration, SQLite is utilized on the local machine to serve as the backend store.
- **[Decoupled Storage]** In this setup, metadata and artifacts are handled by different storage mechanisms on the same local machine:
    - **Backend Store**: Uses a local SQL database (via `SQLAlchemyStore`) to store run metadata like parameters and metrics.
    - **Artifact Store**: Continues to use the local file system (e.g., the `./mlruns` directory) to store generated artifacts.
- **[Setup]** Requires explicitly setting the tracking URI in the code to point to the local SQLite database.

```python
mlflow.set_tracking_uri("sqlite:///mlflow.db")
```

```mermaid
flowchart TD
    subgraph localhost
        UserCode["User ML code + MLflowClient APIs"]
        UserCode -->|SQLAlchemyStore| SQLDB[("mlruns.db")]
        UserCode -->|LocalArtifactRepository| FileStore["mlruns/0/..."]
    end
```

### MLflow on localhost with Tracking Server

- **[Dedicated Unit]** Similar to the basic localhost setup, but instead of the client interfacing directly with a file store, a dedicated tracking server is launched on the local machine.
- **[Communication]** The client communicates with this server via REST requests, typically over port 5000.
- **[Server Configuration]** The tracking server itself can be configured to use different backend stores:
    - **Default**: A local file store.
    - **Database**: Can be switched to a database by passing the `--backend-store-uri` parameter during the `mlflow server` command.

```bash
--backend-store-uri sqlite:///mlflow.db
```

```mermaid
flowchart TD
    subgraph localhost
        UserCode["User ML code + MLflowClient APIs"]

        subgraph TrackingServerUnit [Tracking Server]
            TS[TrackingServer]
            FS[FileStore]
            TS --- FS
        end

        UserCode -->|"REST (Port 5000)"| TS
        UserCode -->|LocalArtifactRepository| Artifacts["mlruns/0/..."]
    end
```

### MLflow on localhost with a dedicated tracking server

- **[Core Difference]** Unlike Scenario 1, a dedicated tracking server is launched as a separate unit on the localhost to handle requests, though it still interacts with local storage.
- **[Setup Command]** This configuration is initiated using the `mlflow server` command:

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlflow_artifacts --host 127.0.0.1 --port 5000
```

- **[Operational Workflow]** The interaction between the MLflow client and the tracking server follows a specific two-part process:

#### 1. Logging Metadata (Entities)

- The MLflow client creates a REST store instance and sends a REST API request to log entities (e.g., parameters, metrics) to the server.
- The tracking server receives the request and uses its own store instance (File Store or SQLite) to write the metadata directly to the local `./mlruns` directory or database.

#### 2. Storing Artifacts

- The MLflow client sends a REST request to the tracking server to fetch the artifact store's URI location.
- The tracking server responds with the specific URI.
- The MLflow client then uses a local artifact repository instance to save the actual files directly to the local filesystem at that specified location.

```mermaid
flowchart TD
    subgraph localhost
        subgraph Client["User ML code + MLflowClient APIs"]
            REST["REST store"]
            LocalArt["LocalArtifactRepository"]
        end

        subgraph Server["TrackingServer"]
            FileStore["FileStore"]
        end

        Storage[("Local Storage\n./mlruns/")]

        %% Metadata Flow
        Client -->|"1a: REST API Request"| Server
        Server -->|"1d: Write Metadata"| Storage

        %% Artifact Flow
        Client -->|"2a: Fetch URI"| Server
        Server -->|"2b: Return URI"| Client
        Client -->|"2c: Save Artifacts"| Storage
    end
```

## MLflow with remote Tracking Server and Storage

### Scenario 4: Remote Backend and Artifact Stores

- **[Core Concept]** Both the backend store (metadata) and the artifact store (files) are located on remote hosts, and the client interacts with them via the tracking server and direct connections.
- **[Workflow]**
    - The client sends a REST request to the tracking server to fetch the artifact store's URI (e.g., an S3 bucket location).
    - The tracking server responds with this URI.
    - The client then uses a remote artifact repository instance (e.g., an S3 repository using the `boto3` client) to upload artifacts directly to the remote storage.
- **[Setup Command]** A typical command to launch a tracking server in this configuration:

```bash
mlflow server --backend-store-uri postgresql://user:password@postgres:5432/mlflowdb --default-artifact-root s3://bucket_name --host remote_host --no-serve-artifacts
```

- **[Use Case]** This setup is widely used in real-world projects because it allows MLflow tracking to scale and supports collaboration among multiple data scientists.

```mermaid
flowchart TD
    subgraph localhost
        subgraph Client["User ML code + MLflowClient APIs"]
            REST["REST store"]
            S3Art["S3ArtifactRepository client"]
        end
    end

    subgraph RemoteHost["Remote host"]
        Server["TrackingServer\n(SQLAlchemy/FileStore)"]
    end

    subgraph S3RemoteHost["S3 remote host"]
        S3Bucket[("s3://bucket_name")]
    end

    subgraph PostgresRemoteHost["Remote host"]
        Postgres[("PostgreSQL")]
    end

    %% Metadata Flow
    Client -->|"1a: REST API Request"| Server
    Server -->|"1b: Write Metadata"| Postgres

    %% Artifact Flow
    Client -->|"2a: Fetch URI"| Server
    Server -->|"2b: Return URI"| Client
    Client -->|"2c: Upload Artifacts"| S3Bucket
```

### Scenario 5: MLflow remote Tracking Server with Proxied access

- **[Proxy Functionality]** The MLflow tracking server can be configured to act as an **artifact HTTP proxy**.
- **[Benefit]** This allows the server to handle artifact requests, passing them through to the underlying storage. This enables the client to store and retrieve artifacts through the tracking server without needing to interact directly with the underlying object storage.

### MLflow remote Tracking Server with Proxied access

- **[Use Case]** This configuration is ideal when users have restricted network access to the remote backend store or object store
    - It is particularly useful for organizations with critical data where direct access to remote objects must be limited
- **[Mechanism]** The tracking server is configured as an artifact HTTP proxy
    - The server routes requests for operations like saving, loading, or listing artifacts (models, images, documents, etc.) through itself
    - This eliminates the need for end users to have direct access to remote object stores like S3, GCS, or HDFS
    - **[Security Benefit]** Users do not need to provide or manage individual access credentials for the underlying object store

```mermaid
flowchart TD
    subgraph localhost
        subgraph Client["User ML code + MLflowClient APIs"]
            REST["REST store"]
            LocalArt["wbg ArtifactRepository"]
        end
    end

    subgraph RemoteHost1["Remote Host"]
        Server["Tracking Server<br/>(with artifact proxy)"]
        DB[("PostgreSQL")]
    end

    subgraph RemoteHost2["Remote Host"]
        Storage["s3://bucket_name<br/>(models, images, configs, etc.)"]
    end

    %% Metadata Flow
    Client -->|"1a, 1b"| Server
    Server -->|"1c"| DB

    %% Proxy Artifact Flow
    Client -->|"2a, 2b"| Server
    Server -->|"2c"| Storage
    Storage -.->|"2d"| Client
```

#### Metadata Logging Workflow

- **[Initial Step]** To store runs and experiment metadata, the MLflow client utilizes a REST store to send REST API requests to the tracking server.

#### Metadata and Artifact Workflow Details

- **[Metadata Flow]** The tracking server manages metadata using a SQLAlchemy Store
    - The server creates a SQLAlchemy Store instance to connect to the remote host
    - It performs operations like inserting and retrieving metrics, parameters, and tags into the database
    - Client retrieval requests pull this information from the configured SQLAlchemy Store tables
- **[Artifact Flow]** The tracking server acts as an HTTP artifact repository to proxy file operations
    - **Logging:** The MLflow client sends logging events via the HTTP artifact repository to the tracking server, which then writes the files to the object store (e.g., S3) using assumed role authentication
    - **Retrieval:** When a client requests an artifact, the tracking server retrieves it from the object store using the same server-side authorized authentication configured at startup

```mermaid
flowchart TD
    subgraph localhost
        subgraph Client["User ML code + MLflowClient APIs"]
            REST["RestStore"]
            LocalArt["wbg ArtifactRepository"]
        end
    end

    subgraph RemoteHost1["Remote Host"]
        Server["Tracking Server<br/>(with artifact proxy)"]
        DB[("PostgreSQL")]
        SQL["SQLAlchemy / FileStore"]
    end

    subgraph RemoteHost2["Remote Host"]
        Storage["s3://bucket_name<br/>(models, images, configs, etc.)"]
    end

    %% Metadata Flow
    Client -->|"1a, 1b"| Server
    Server -->|"1c"| DB
    Server -->|"1d"| Client

    %% Proxy Artifact Flow
    Client -->|"2a, 2b"| Server
    Server -->|"2c"| Storage
    Storage -.->|"2d"| Client
```

## MLflow Remote Tracking Server Configurations

- Remote tracking servers can be configured with various storage setups to manage metadata and artifacts independently of the client environment.

### Distributed Architecture Deployment Patterns

- **[Deployment Environment]** In large-scale production environments, the tracking server, backend store, and artifact store are often decoupled and hosted on separate, specialized cloud services (e.g., AWS, Azure, or GCP) to ensure high availability and scalability.
- **[Component Roles]**
    - **Tracking Server**: Acts as the central orchestration point for all client requests.
    - **Backend Store**: A managed database service (like Amazon RDS or Google Cloud SQL) used for persistent entity storage.
    - **Artifact Store**: A managed object storage service (like Amazon S3 or Google Cloud Storage) used for large file persistence.

#### Workflow Summary for Distributed Components

| Phase | Action | Component Involved |
| --- | --- | --- |
| Metadata Logging | Client sends REST API requests to the server; Server uses SQLAlchemyStore to write to the remote database. | RestStore \rightarrow Tracking Server \rightarrow SQLAlchemyStore \rightarrow Remote DB |
| Artifact Discovery | Client requests the artifact URI via REST; Server returns the remote storage location (e.g., S3 URI). | RestStore \rightarrow Tracking Server \rightarrow Client |

#### Detailed Artifact Upload Mechanism (Scenario 4)

- **[Step 2c: Direct Upload]** Once the client receives the S3 URI from the server, it performs the following:
    - Creates an instance of an `S3ArtifactRepository`.
    - Establishes a connection to the remote AWS host using `boto3` client libraries.
    - Uploads the artifacts directly to the specified S3 bucket location.
- **[Configuration Breakdown]** When launching the server for this specific remote setup, the following flags are critical:
    - `--backend-store-uri`: Points to the remote database (e.g., `postgresql://user:password@host:port/db`).
    - `--default-artifact-root`: Defines the remote object storage path (e.g., `s3://bucket_name`).
    - `--host`: Specifies the remote network address where the tracking server is reachable.
- **[Key Advantage]** This architecture is the standard for production-grade collaboration, as it decouples storage from the local environment, allowing multiple data scientists to scale their tracking capabilities independently.
- The tracking server can be configured to act as an HTTP proxy for artifact operations
    - Artifact requests are passed through the tracking server to store and retrieve data
    - **[Benefit]** This removes the need for the client to interact directly with the underlying object storage service

```mermaid
flowchart TD
    subgraph localhost
        A["User ML code + MLflow Client APIs"]
        B["HttpArtifactRepository"]
    end

    subgraph "Remote Host (Tracking Server)"
        C["Tracking Server (with artifact proxy)"]
        D["SQLAlchemy / Reflect"]
    end

    subgraph "Remote Host (Backend Store)"
        E["PostgreSQL"]
    end

    subgraph "Remote Host (Artifact Store)"
        F["s3://bucket_name\n(models, images, configs)"]
    end

    A -->|"1a"| C
    C -->|"1b"| D
    D -->|"1c"| E
    B -->|"2a"| C
    C -->|"2b"| F
    C -->|"2c"| B
    C -->|"2d"| D
```

### MLflow Tracking Server with Proxied Artifact Storage Access

- **[The Problem]** Users may have restricted network access to the backend store or remote object stores (e.g., S3, GCS, HDFS)
- **[The Solution]** Use the tracking server as a proxy for artifact operations
    - The tracking server is configured to route requests to the backend store
    - It handles operations like saving, loading, or listing model artifacts, images, documents, and files
- **[Key Advantages]**
    - **Security**: Eliminates the need to grant end users direct access to remote object stores
    - **Credential Management**: Users do not need to provide their own access credentials to interact with the underlying storage service

```mermaid
flowchart TD
    subgraph localhost
        A["User ML code +
MLFlowClient APIs"]
        B["HttpArtifactRepository"]
    end

    subgraph "Remote Host (Tracking Server)"
        C["Tracking Server
(with artifact proxy)"]
        D["SQLAlchemy / Reflect"]
    end

    subgraph "Remote Host (Backend Store)"
        E["PostgreSQL
(runs metrics,
params, tags)"]
    end

    subgraph "Remote Host (Artifact Store)"
        F["s3://bucket_name
(models, images,
configs)"]
    end

    A -->|"1a"| C
    C -->|"1b"| D
    D -->|"1c"| E
    B -->|"2a"| C
    C -->|"2b"| F
    C -->|"2c"| B
    C -->|"2d"| D
```

### MLflow Remote Tracking Server Inner Workings

The proxied access architecture follows two distinct communication paths for metadata and artifacts:

#### 1. Metadata Logging and Retrieval (Runs, Experiments, Metrics)

- The MLflow client communicates with the tracking server using REST API requests to log entities
- The tracking server uses an instance of SQLAlchemy to connect to the remote backend store (e.g., PostgreSQL)
- This process handles the insertion and retrieval of:
    - Metrics
    - Parameters
    - Tags

#### 2. Artifact Logging and Retrieval (Models, Images, Configs)

- Artifact operations are routed through the tracking server acting as an HTTP proxy
- This allows the client to store and retrieve large files without direct access to the underlying object store

#### Artifact Logging and Retrieval Process (Proxied Access)

- **Logging Artifacts (Writing)**
    - The MLflow client initiates logging events via an `HttpArtifactRepository` to send files to the tracking server (Step 2a)
    - The tracking server then writes these files to the configured object store (e.g., S3) using **assumed role authentication** (Step 2b)
- **Retrieving Artifacts (Reading)**
    - Retrieval requests are handled by the tracking server using the same authorized authentication configured at its startup (Step 2c)
    - Artifacts are passed back to the end user through the tracking server via the `HttpArtifactRepository` interface (Step 2d)

> [!CAUTION] **Security Warning for Administrators**
> Because the artifact proxy service allows users to access files through the tracking server, users effectively gain the same level of access as the tracking server's assumed role. Administrators must ensure the tracking server's permissions are strictly limited to only what is necessary for artifact operations to prevent unauthorized access to the entire object store.

### MLflow Tracking Server as Exclusive Artifact Proxy

In this configuration, the MLflow Tracking Server is restricted to serving only artifact-related API requests. It acts solely as a proxy to the underlying object store.

- **Functional Restrictions**
    - All metadata-related functionalities are disabled
    - Users cannot create runs, log metrics, log parameters, or access experiment attributes
    - The setup results in a system that manages artifacts but contains no backend metadata (no runs or experiments)
- **Artifact Workflow (Artifacts-Only Mode)**

```mermaid
sequenceDiagram
    participant Client as localhost (User Code + MLflowClient)
    participant Server as Remote Host (Tracking Server: artifacts-only mode)
    participant Store as Remote Host (Object Store: models, images, configs)

    Note over Client, Server: 1a: Interaction via HttpArtifactRepository
    Client->>Server: API calls (save, load, list artifacts)

    Note over Server, Store: 1d: Writing artifacts
    Server->>Store: Write artifact files using server credentials

    Note over Store, Server: 1c: Listing artifacts
    Store-->>Server: Return list of artifact files
    Server-->>Client: Pass list response to client

    Note over Server, Store: 1d: Loading artifacts
    Server->>Store: Acquire files using server credentials
    Store-->>Server: Return files
    Server-->>Client: Pass files to client
```

- **Deployment Command**
    - To enable this mode, the server is started with the `--artifacts-only` flag:

```bash
mlflow server --artifacts-destination s3://bucket_name --artifacts-only --host remote_host
```

### Summary of MLflow Tracking Scenarios

- Local configurations are appropriate for:
    - Individual use
    - Small-scale projects
- Enterprise-level projects require remote tracking server configurations to manage scale and security requirements.
- **Key Flag for Artifact Proxying**
    - The `--artifacts-only` flag is used to restrict the server instance to serving only artifact-related API requests by proxying to an underlying object store.

## MLflow Models

- A standard format used to package machine learning models in a reusable way
- **[Why use it?]** Because this packaging allows models to be easily deployable to various environments," such as:
    - Production servers
    - Cloud-based platforms
    - Docker
    - Kubernetes

### Challenges of Conventional Model Deployment

- The traditional process involves manual packaging of the model and its dependencies
- **[Why is this a problem?]** Because manual processes are error-prone and lead to several key issues:
    - **Reproducibility**
        - It is difficult to recreate the exact environment used to train the model
        - Inconsistent dependency versions or environmental changes cause deployment failures
    - **Collaboration**
        - It creates friction and difficulty when working between data scientists and engineers

### Additional Challenges in Traditional Deployment

- **Communication Gaps**
    - Lack of coordination between data scientists and engineering teams can cause discrepancies between development and production models
- **Lack of Transparency**
    - It is difficult to understand a model's lineage
    - Engineering teams often lack access to the model's source code or training details, making debugging and improvement difficult
- **Flexibility Issues**
    - Deploying to different environments is difficult
    - Different deployment types have varying requirements:
        - Real-time inference
        - Batch inference
        - Edge deployment
- **The Deployment Bottleneck**
    - There is often a massive time gap in the machine learning lifecycle
    - A working model might be built in two weeks, but deploying it to production can take months

### The Goal of MLflow Models

- **[Purpose]** To provide a solution where models are packaged in a way that is universally usable
    - Enables anyone to use the model
    - Allows deployment to any environment
    - Simplifies the management of the entire machine learning lifecycle, from experimentation to production

### How MLflow Models Solve Deployment Challenges

MLflow models address traditional issues through three primary mechanisms:

- **Standard format** for packaging models
- **Central repository** for managing models
- **API** for deploying models to various environments

#### Solving Reproducibility

- The MLflow models component packages the model in a **standard format** along with its dependencies
    - **[Why?]** This ensures the exact environment used to train the model is reproducible

#### Enhancing Collaboration

- Provides a **user-friendly interface** for team coordination
    - Allows users to track model versions
    - Enables sharing models and code with other team members
    - Facilitates the promotion of models to production
- **[Transparency]** Supports tracking **model lineage**
    - Allows users to track back the history of a model
    - Provides understanding of how a model was created

#### Increasing Flexibility

- The **MLflow Model Serving** component supports multiple deployment types:
        - Real-time inference
        - Batch inference
        - Edge deployment
- Provides an API for managing models across different environments
    - **[Benefit]** Makes it easier for other developers to use a model in their applications without needing to train the models themselves

## Components of MLflow Models

The MLflow model component is comprised of three main parts:

- Storage format
- Model signature
- Model API

### Storage Format

- **[Definition]** Specifies how the model is packaged and saved
- **[Contents]** A standard packaging format that includes:
    - The model itself
    - Model metadata (e.g., input/output schema)
    - Hyperparameters used during training
    - The model's version
- **Supported Formats**
    - Directory of files: Model artifacts are saved in an easy-to-manage directory structure
    - Single file format: Useful for specific use cases where the model is contained in one file
    - Python functions
    - Container images (e.g., Docker)

### Model Signature

- **[Definition]** Specifies the input and output data types and shapes that the model expects and returns
    - Can range from simple types (integers, strings) to complex types (NumPy arrays, Python lists)
- **[Importance]** Ensures the model is deployed correctly and performs as expected
    - This information is used by MLflow to automatically generate a REST API for the model to facilitate inference
- **Implementation Details**
    - Defined using Python function annotation syntax
    - Stored as part of the MLflow model so it can be accessed by other components of the platform
- **Input Examples**
    - Data used for training and testing that is also stored as an artifact
    - **[Why use them?]** To ensure live production data is formatted correctly to match the data the model was trained on

### Model API

- **[Definition]** A standardized REST API that provides a consistent interface for interacting with the model
- **Generation**
    - Can be easily generated based on the defined model signatures using tools like Flask, FastAPI, or other Python frameworks
- **Capabilities**
    - Supports both synchronous and asynchronous requests
    - Suitable for both real-time inference and batch processing
- **Deployment**
    - Can be deployed to various environments, including:
        - Cloud platforms
        - Edge devices
        - On-premises servers

#### Model API Capabilities

- **[Versioning]** The API is versioned and can be updated alongside model artifacts
    - This occurs when retraining or modifying the model
- **[Summary]** Provides a consistent interface for working with different model types by providing tools to load, evaluate, and deploy them

### Flavor

- **[Definition]** A specific way of serializing and storing a machine learning model
- **[Relationship to Frameworks]** Each flavor is associated with the specific framework or library used during training
- **[Supported Frameworks]** MLflow integrates with a wide variety of libraries, each having its own associated flavor:
    - TensorFlow
    - PyTorch
    - Scikit-Learn
    - XGBoost

### Benefits of Standardized Model Packaging

- **[Interoperability]** Allows developers to easily switch between different frameworks or libraries
- **[Deployment]** Simplifies the process of deploying models to various environments
- **[Consistency]** Provides a standard way to package and load models, including their dependencies, for consistent usage

### Types of MLflow Flavors

- **Built-in Flavors**
    - Associated with major frameworks and libraries integrated directly into MLflow
- **Community-driven Flavors**
    - Created by the open MLflow community
    - Designed to quickly package and deploy models trained with specific, community-supported frameworks
- **Custom Model Flavors**
    - User-defined flavors that can be introduced for specific, unique model requirements

### Selecting an MLflow Flavor

- **[Decision Logic]** Choose a flavor based on the specific libraries and tools used during the training process:
    - **Standard ML Libraries** (e.g., TensorFlow, PyTorch, Scikit-Learn) $\rightarrow$ Use **Built-in Flavors**
    - **Niche/Specific Requirements** $\rightarrow$ Check for **Community-driven Flavors**
    - **Unique Tools or Custom Libraries** $\rightarrow$ Create a **Custom Model Flavor**
- **[Customization]** Custom flavors allow for specialized model packaging processes, such as utilizing Docker for specific deployment needs.

### Miscellaneous MLflow Model Functionalities

#### Model Evaluation

- Provides functionality to evaluate models using specific metrics
    - **[Common Metrics]**
        - Accuracy
        - Precision
        - Recall
        - F1 score
    - **[Regression Metrics]** (as seen in practical examples)
        - RMSE (Root Mean Square Error)
        - MAE (Mean Absolute Error)
        - R2 score
- **[Purpose]** To compare different trained models and ensure only the best, most suitable one is selected for deployment

#### Deployment Platforms

- MLflow provides tools to deploy models to a variety of environments:
    - Docker containers
    - REST APIs
    - TensorFlow Serving
    - AWS SageMaker
- **[Custom Deployment Targets]**
    - Users can set up custom targets by specifying the necessary code
    - **[Use Case]** Essential for large corporations (e.g., petroleum companies) that utilize private clouds or on-premise data centers instead of public clouds for security or data volume reasons

## MLflow Model Storage Format

- Defines how a model is packaged and saved
- **[Contents]** Includes the model itself and various metadata:
    - Input and output schemes
    - Model dependencies
    - Model version and hyperparameters
- **[Supported Formats]**
    - Directory of files (Default)
    - Single file format
    - Python functions
    - Container images (e.g., Docker)

### Default Storage: Directory of Files

- Because it is the default, most standard MLflow runs automatically use this format
- The model directory acts as an artifact folder containing all necessary files for versioning and deployment
- **[Structure]** Typically contains 6 to 7 specific files required to reconstruct the model environment

### Contents of the Model Directory

#### input\_example.json

- **[Definition]** An optional file that serves as a representative example of the data the model expects during inference or prediction
- **[Purpose]** Defines the input format and data structure that the model should handle
- **[Structure for Tabular Data]** Contains two key-value pairs:
    - `columns`: A list of column names
    - `data`: A list of data points (typically containing at least 10 data points per column)
- **[Note]** The structure may differ if the model is designed for non-tabular data like images, video, or audio

#### model.pickle

- **[Definition]** A binary file containing the actual model in pickle format
- **[Contents]** This file packages and saves the model along with its metadata, including:
    - The model itself
    - Input and output schemes
    - Model dependencies
    - Model version and other relevant metadata

#### Environment Reproducibility Files

When a model is logged, MLflow automatically provides specific files to assist in setting up a consistent environment. These files ensure the Python environment used during training is reproducible, which is essential for reliable deployment across different environments.

- **Logged Environment Files**
    - `conda.env.yml`
    - `python_env.yml`
    - `requirements.txt`

### Environment Setup Options

- The three logged files allow for three distinct ways to set up the model's environment:
    - `conda.env.yml`: Used to configure a full Conda environment
    - `python_env.yml`: Used to set up a pip virtual environment
    - `requirements.txt`: Used when an environment is already prepared and only specific necessary packages need to be installed

### Detailed View: `conda.env.yml`

- **[Structure]** Contains the following key sections:
    - `channels`: A list of remote locations (Anaconda channels) where Python packages are hosted and from which they are downloaded and installed
    - `dependencies`: The list of specific packages required for the environment
    - `name`: The name of the Conda environment
- **[Channels and Licensing]**
    - The default channel logged is `conda-forge`
    - **[Historical Note]** Older versions of MLflow might have pointed to `defaults`
    - **[Why the change?]** Anaconda changed its software licensing, requiring MLflow to align with the `conda-forge` channel
    - **[Recommendation]** Use the latest version of MLflow to ensure compatibility with current channel naming standards

```yaml
channels:
  - conda-forge
dependencies:
  - python=3.9.12
  - pip=23.1.2
  - mlflow=2.5.0
  - cloudpickle=2.2.1
  - rampy=1.25.1
  - scikit-learn=1.3.0
  - scikit-image=1.11.1
```

### Detailed View: `conda.env.yml` (continued)

- **[Dependencies]** This section lists all the specific packages and versions required to work with the MLflow model:
    - `python=3.10.12`
    - `pip=23.1.2`
    - `mlflow=2.5.0`
    - `cloudpickle=2.2.1`
    - `numpy=1.25.1`
    - `scikit-learn=1.3.0`
    - `scipy=1.11.1`
- **[Purpose]** This file allows for the creation of a new Conda environment on a different machine that is an exact replica of the training environment
    - **[Why it matters]** It helps eliminate environment reproducibility issues by ensuring all Python, pip, and library versions are identical

```yaml
channels:
  - conda-forge
dependencies:
  - python=3.10.12
  - pip=23.1.2
  - mlflow=2.5.0
  - cloudpickle=2.2.1
  - numpy=1.25.1
  - scikit-learn=1.3.0
  - scipy=1.11.1
name: mlflow-env
```

### Detailed View: `python_env.yml`

- **[Purpose]** Used to set up a pip virtual environment
- **[Structure]** Contains the following sections:
    - `python`: Specifies the Python version (e.g., `3.10.12`)
    - `build_dependencies`: Lists tools needed to build the environment, such as `pip`, `setuptools`, and `wheel`
    - `dependencies`: Points to the `requirements.txt` file to identify which packages to install

```yaml
python: 3.10.12
build_dependencies:
  pip=25.1.2
  setuptools=67.8.0
  wheel=0.38.4
dependencies:
  - requirements.txt
```

- **[Relationship with&#32;`requirements.txt`]** The two files work together to establish the environment:
    - `python_env.yml` guides the establishment of the Python and pip virtual environment itself
    - `requirements.txt` provides the specific list of packages to be installed into that environment

### `requirements.txt` and Environment Reproducibility

- **[Function]** Can be used to install necessary packages into any existing environment
- **[Content]** Contains the exact same packages required by the model as seen in the `conda.env.yml` file (e.g., `mlflow`, `cloudpickle`, `numpy`, etc.)
- **[Summary]** All these files (`conda.env.yml`, `python_env.yml`, and `requirements.txt`) serve to hassle-free reproduce the environments used to train the model

> **Note:** While these files are essential for reproducibility, the `MLmodel` file is the most important file in the directory.

### The `MLmodel` File

- **[Function]** A standardized configuration file in YAML format that describes a packaged machine learning model
    - It acts as a bridge that different tools and libraries can easily understand
    - It contains vital metadata, including model flavors, fields, and signatures
- **Model Flavors**
    - **[Definition]** Refers to the different ways a machine learning model can be represented and stored
    - Each flavor corresponds to a specific machine learning library, framework, or the specific conventions that library uses to store its models
    - The flavor section tells the system how the model can be interpreted and served
- **Example Flavors in&#32;`MLmodel`**
    - In the provided example, the model has two flavors:
        - `python_function`: Allows the model to be loaded and used as a generic Python function
            - To support this, it provides environment file names (like `conda.env.yml`) to recreate the necessary environment
        - `sklearn`: Allows the model to be loaded using specific scikit-learn functions (e.g., `load_model`)

```yaml
flavors:
  python_function:
    conda: conda.env.yml
    serialization:
      loader_module: mlflow.sklearn
      model_path: model.pkl
      predict_fn: predict
      python_version: 3.10.12
  sklearn:
    code: null
    pickled_model: model.pkl
    serialization_format: cloudpickle
    sklearn_version: 1.3.0
    mlflow_version: 2.5.0
```

### `python_function` Flavor Details

- **loader\_module**
    - Specifies the module used to load the model when it is deployed or served
    - In the example, it is set to `mlflow.sklearn`
    - This allows the model stored in `model.pkl` to be loaded for prediction and serving using the `predict` function
- **Environment Files**
    - Provides file names to recreate the necessary Python environment for the function
    - Examples include:
        - `conda.env.yml` (to create a Conda environment)
        - `python_env.yml` (to create a virtual environment)
- **predict\_fn**
    - Specifies a specific Python function that can be used to perform inference when the model is deployed or served

---

### `sklearn` Flavor Details

- **code**
    - Used to package the exact code and logic used to train the model
    - This ensures the specific environment and logic that generated the `model.pkl` file are captured for reproducibility
    - Can point to different locations:
        - A local directory
        - A Git repository
            - If using Git, a `version` field (representing a Git commit ID) is used to track back to the exact codebase used at the time the model was built

### `sklearn` Flavor: Code Reproducibility

- **code**
    - Captures the exact logic and environment used to generate the model, ensuring complete transparency and reproducibility
    - **[Options for locating code]**
        - **Git Repository**: Uses a `version` field to store the Git commit ID, allowing users to track back to the exact codebase used at the time of training
        - **Local Directory**: Uses a `path` field to specify the location of the code within the project or repository
            - This path can include essential elements like pre-processing, training, and evaluation code
    - **[Auto-logging limitation]**
        - Currently, MLflow's `auto-logging` functionality does not automatically log the code
        - **Workaround**: To manually log the code, use the `log_model` function and specify the appropriate files via the `code_paths` parameter

```yaml
flavors:
  sklearn:
    code: null
    pickled_model: model.pkl
    serialization_format: cloudpickle
    sklearn_version: 1.3.0
    mlflow_version: 2.5.0
```

### `sklearn` Flavor Details (continued)

- **pickled\_model**
    - The name of the pickle file containing the trained model (e.g., `model.pkl`)
- **serialization\_format**
    - The format used to serialize the model
    - Defaults to `cloudpickle` unless explicitly changed
- **sklearn\_version**
    - The specific version of scikit-learn used to train the model (e.g., `1.3.0`)

### Model Metadata and Configuration

- **General Metadata Fields**
    - `mlflow_version`: The version of MLflow used
    - `mlflow_uid`: A unique identifier assigned to the saved model for tracking in the MLflow Model Registry
    - `run_id`: The ID of the specific MLflow run that was used to save the model
    - `saved_input_example_info`: Contains information regarding the input examples saved during model logging

### The Concept of Flavors

- Flavors provide a standardized way to package models from different libraries, making it easier for diverse teams to interact with them
- **Example: TensorFlow Flavor**
    - Would consist of a set of binary files representing the trained weights
    - Uses its own set of configurations specific to the TensorFlow framework

```yaml
flavors:
  sklearn:
    code: null
    pickled_model: model.pkl
    serialization_format: cloudpickle
    sklearn_version: 1.3.0
  mlflow_version: 2.5.0
  mlflow_uid: 99490584...
  run_id: st8e3...
  saved_input_example_info:
    artifact_path: input_example.json
    pandas_orient: split
    type: dataframe
    signature:
      inputs: [{"type": "long", "name": "Unnamed: 0", "type": "double"}, ...]
```

### `saved_input_example_info` Details

- **artifact\_path**
    - Indicates the path to where the input example file is stored (e.g., `input_example.json`)
- **pandas\_orient**
    - Specifies the orientation of the input data if it is in a Pandas format
    - Helps the system interpret whether the data frame is structured as `split`, `records`, `index`, or `columns` format
    - In the current example, the type is `split`
- **type**
    - The format of the input data (e.g., `dataframe`)

### Model Signature

- **signature**
    - Defines the input and output schema of the model
    - Specifies the required format and structure for inputs the model expects
    - Specifies the format and structure of the outputs the model produces

```yaml
saved_input_example_info:
  artifact_path: input_example.json
  pandas_orient: split
  type: dataframe
signature:
  inputs: [{"type": "long", "name": "Unnamed: 0", "type": "double"}, ...]
```

- A way to describe the input and output data types and shapes that are expected as input and produced by a machine learning model
- **[Why it matters]** Clear understanding of inputs and outputs is necessary for integrating models into larger applications or systems
    - This ensures the model can interact correctly with other components that provide or consume data in specific formats
- **Downstream Tooling**
    - Signatures are typically included in model metadata
    - They allow tools like web applications or data pipelines to validate that incoming input data conforms to the expected format
- **Example Scenario**
    - An X-Y model might have a signature specifying an input of a 2D array of floating point values and an output of a single scalar value

### Model Input Examples

- A kind of sample input that is representative of the type of data that the model is designed to handle
- **[Why include them?]** Including input examples in the model metadata provides a concrete reference for the expected data format

### Benefits of Model Input Examples

- **[Why include them?]** They serve multiple purposes in the model lifecycle:
    - Generating documentation to explain how the model should be used
    - Providing test cases to validate the model during development and deployment

### Column-based Signatures

- Each column of the input data is treated as a separate feature or input variable
    - Each feature is assigned a unique name and a specific data type
    - Data types correspond to MLflow types, such as `double`, `integer`, or `string`
- Supported by all flavors of MLflow
- **Example: Iris Classification Model Signature**
    - The model expects four named input columns of type `double`:
        - `sepal length (cm)`
        - `sepal width (cm)`
        - `petal length (cm)`
        - `petal width (cm)`
    - The model outputs a single `integer` representing the predicted class

```python
signature:
  inputs: [{"name": "sepal length (cm)", "type": "double"}, {"name": "sepal width (cm)", "type": "double"}, {"name": "petal length (cm)", "type": "double"}, {"name": "petal width (cm)", "type": "double"}, {"name": "class", "type": "string", "optional": "true"}]
  outputs: [{"type": "integer"}]
```

### Tensor-based Signatures

- Refers to a specific way of representing input data for machine learning models
- Involves organizing the data as a multi-dimensional array or tensor
- Involves organizing input and output data as multi-dimensional arrays or tensors
- **[Supported Flavors]** Only supported by deep learning flavors of MLflow:
    - TensorFlow
    - Keras
    - PyTorch
    - ONNX
    - Gluon
- Each input and output is represented by:
    - A `dtype` corresponding to a NumPy data type (e.g., `numpy.float32` or `numpy.int64`)
    - A `shape`
    - An optional `name`

#### MNIST Classification Example

- The signature for a model trained on the MNIST dataset is represented as follows:

```python
signature:
  inputs: [{"name": "images", "dtype": "uint8", "shape": [-1, 28, 28, 1]}]
  outputs: [{"shape": [-1, 10], "dtype": "float32"}]
```

- **[Key Detail]** The first dimension of both input and output is set to `-1` to allow for variable batch sizes

### Including Model Signatures

- Including a signature in the `MLModel` file provides essential information for downstream tooling to perform validation and verification
- **[How to include them]**
    - **Autologging**: If using the `autolog` function, the model signature is logged automatically (the parameter is set to `true` by default)
    - **Manual logging**: If not using autologging, a signature object can be passed as an argument to the `log_model` function

### Signature Enforcement

- Simply defining a signature does not guarantee that a model will consistently receive the correct data
- **[The Solution]** MLflow provides **signature enforcement**, which actively checks whether incoming data matches the specified input and output schema

### Model Signature Enforcement

- The process of defining and validating the input and output schema for a machine learning model
- **[Purpose]** To ensure that data provided to a model matches the expected structure
    - Enhances consistency
    - Reduces potential errors during deployment or interaction
- **[Deployment Integration]** Recognized and enforced by standard MLflow deployment tools (e.g., `mlflow models serve`)
    - When deploying as a REST API, the tool validates inputs against the signature
    - Requests that do not adhere to the defined schema are rejected
- **[Enforcement Rules]** Rules can vary based on the specific use case:
        - **Strict enforcement**: Appropriate for production environments where consistency and accuracy are paramount
        - **Lenient enforcement**: May be appropriate for other scenarios

### MLflow Enforcement Types

- MLflow provides three distinct types of enforcement to maintain model integrity:
    - **Signature enforcement** (also known as schema enforcement)
    - **Name-ordering enforcement**
    - **Input-type enforcement**

### Signature Enforcement

- Also known as **schema enforcement**
- **[How it works]** It checks if the inputs provided to the model match the expected signature
    - If they do not match, an exception is raised
    - This check is applied **before** the underlying model implementation is called, ensuring the model only receives conforming data
- **[When it applies]**
    - Applied when using MLflow model deployment tools
    - Applied when loading models as a `python_function`
    - **[Note]** It is **not** applied to models loaded in their native format
- **[Use Case]** Especially important in production environments where consistency and accuracy are paramount

### Name-Ordering Enforcement

- Ensures that the input names provided to the model match the expected input names in the signature
- **[Handling Mismatches]**
    - **Missing inputs**: MLflow will raise an exception
    - **Extra inputs**: Any inputs not declared in the signature are ignored
- **[Reordering Logic]**
    - If the signature's input schema contains input names, matching is performed by name
    - The inputs are then **re-ordered** to match the order specified in the signature

### Name-Ordering Enforcement (Continued)

- **[Matching Logic]**
    - If the input schema **has** input names: matching is done by name, and inputs are re-ordered to match the signature
    - If the input schema **does not** have input names: matching is done by **position** (MLflow only checks the number of inputs)
- **[Importance]** Critical when models are used in complex workflows or pipelines where data order and names significantly impact downstream systems

### Input-Type Enforcement

- Ensures provided input types match the expected types in the signature
- **[Enforcement Behavior by Signature Type]**
    - **Column-based signatures** (e.g., data frame inputs):
        - **[Lenient enforcement]** MLflow can perform **safe type conversions** if they are guaranteed to be lossless
            - **Valid conversions**: `int` $\rightarrow$ `long` or `int` $\rightarrow$ `double`
            - **Invalid conversion**: `long` $\rightarrow$ `double` (not allowed)
            - If types cannot be made compatible, an error is raised
    - **Tensor-based signatures**:
        - **[Strict enforcement]** No conversions are performed
        - An exception is thrown immediately if the input type does not match the schema

### Manual Logging of Model Signatures and Input Examples

- While `mlflow.autolog()` automatically logs signatures and input examples by default, manual logging is necessary for custom project requirements
- **[Context]** Automatic logging occurs when using functions like `autolog` with `input_examples` and `log_model_signatures` set to `True`

### Granular Control and Manual Signature Creation

To achieve granular control over what is logged, you can disable specific automatic logging features while keeping others active.

- **[Configuring Autologging]**
    - Set `log_input_examples`, `log_model_signatures`, and `log_model` to `False` within the autologging configuration
    - This allows other entities like hyperparameters and metrics to continue logging automatically

```python
mlflow.sklearn.autolog(log_input_examples=False,
                       log_model_signatures=False,
                       log_model=False)
```

- **[Logging the Model Manually]**
    - Use the `mlflow.sklearn.log_model` function to manually include the signature
    - **[Creating the Signature Object]**
        - The signature object must contain the training data and the model's predictions on that dataset
        - It can be created in two ways:
            - **Manually**: By explicitly defining the schema
            - **Inference**: By automatically deriving it from the dataset

```python

# Example of manual model logging
mlflow.sklearn.log_model(sk_model=lr,
                         artifact_path="model",
                         signature=signature)
```

### Manual Implementation Workflow

To implement manual signature logging after configuring autologging, follow these steps:

1. **Import necessary packages**: Ensure required libraries (e.g., `mlflow`, `numpy`, `sklearn`) are imported.
2. **Configure autologging**: Disable specific model-related logging parameters to prevent duplication.
3. **Create the signature object**: Define the schema manually or derive it from the dataset.
4. **Log the model**: Use `mlflow.sklearn.log_model` to record the model alongside the manually created signature.

### Manual Creation of Column-Based Signatures

To manually define a column-based signature, you must specify the names and data types for both the input features and the model's output.

- **[Defining Data Structures]**
    - Create lists of dictionaries to represent the schema
    - Each dictionary contains the column name and its corresponding MLflow data type

```python
from mlflow.models.signature import ModelSignature
from mlflow.types.schema import ColSpec

# Define input features and their types
input_data = [
    {"name": "volatile acidity", "type": "double"},
    {"name": "citric acid", "type": "double"},
    {"name": "residual sugar", "type": "double"},
    {"name": "chlorides", "type": "double"},
    {"name": "free sulfur dioxide", "type": "double"},
    {"name": "total sulfur dioxide", "type": "double"},
    {"name": "density", "type": "double"},
    {"name": "pH", "type": "double"},
    {"name": "sulphates", "type": "double"},
    {"name": "alcohol", "type": "double"},
    {"name": "quality", "type": "double"}
]

# Define the output type
output_data = [{"type": "long"}]
```

- **[Constructing Schema Objects]**
    - Use list comprehension to iterate through the data lists and wrap each entry in a `ColSpec` object
    - This transforms the raw dictionaries into formal schema definitions required by MLflow

```python

# Convert input dictionaries to ColSpec objects
input_schema = [ColSpec(col["type"], col["name"]) for col in input_data]

# Convert output dictionaries to ColSpec objects
output_schema = [ColSpec(col["type"]) for col in output_data]

# Create the final ModelSignature object
signature = ModelSignature(inputs=input_schema, outputs=output_schema)
```

### Finalizing Manual Signature Logging

After defining the input and output schemas, the signature and the model can be logged together.

- **[Creating the Signature Object]**
    - Instantiate the `ModelSignature` class using the `input_schema` and `output_schema` created via list comprehension

```python
signature = ModelSignature(inputs=input_schema, outputs=output_schema)
```

- **[Logging the Model with Signature]**
    - Pass the `signature` object to the `signature` parameter within the `mlflow.sklearn.log_model` function

```python
mlflow.sklearn.log_model(
    skelarn_model,
    "model",
    signature=signature
)
```

### Logging Model Input Examples

- Input examples provide concrete data samples that the model expects
- **[Format Requirement]**
    - Must be provided as a dictionary
    - Keys represent the column names
    - Values represent the data (e.g., a NumPy array containing multiple records)

```python
input_example = {
    "fixed acidity": np.array([7.5, 7.5, 7.6, 7.6, 7.6]),
    "volatile acidity": np.array([0.35, 0.35, 0.35, 0.35, 0.35]),
    "citric acid": np.array([0.41, 0.50, 0.41, 0.50, 0.41]),
    "residual sugar": np.array([18.5, 18.5, 18.5, 18.5, 18.5]),
    "chlorides": np.array([0.045, 0.045, 0.045, 0.045, 0.045]),
    "free sulfur dioxide": np.array([25, 125, 135, 155, 115]),
    "total sulfur dioxide": np.array([45.95, 45.95, 45.95, 45.95, 45.95]),
    "density": np.array([0.99, 0.99, 0.99, 0.99, 0.99]),
    "pH": np.array([3.1, 3.1, 3.1, 3.1, 3.1]),
    "sulphates": np.array([0.45, 0.45, 0.45, 0.45, 0.45]),
    "alcohol": np.array([7, 7, 7, 7, 7]),
    "quality": np.array([5, 5, 5, 5, 5])
}
```

- **[Format for Multiple Samples]**
    - When storing multiple data points, pass them as NumPy arrays associated with their respective column names within a dictionary

```python
input_example = {
    "fixed acidity": np.array([7.5, 7.5, 7.6, 7.6, 7.6]),
    "volatile acidity": np.array([0.35, 0.35, 0.35, 0.35, 0.35]),
    "citric acid": np.array([0.41, 0.50, 0.41, 0.50, 0.41]),
    "residual sugar": np.array([18.5, 18.5, 18.5, 18.5, 18.5]),
    "chlorides": np.array([0.045, 0.045, 0.045, 0.045, 0.045]),
    "free sulfur dioxide": np.array([25, 125, 135, 155, 115]),
    "total sulfur dioxide": np.array([45.95, 45.95, 45.95, 45.95, 45.95]),
    "density": np.array([0.99, 0.99, 0.99, 0.99, 0.99]),
    "pH": np.array([3.1, 3.1, 3.1, 3.1, 3.1]),
    "sulphates": np.array([0.45, 0.45, 0.45, 0.45, 0.45]),
    "alcohol": np.array([7, 7, 7, 7, 7]),
    "quality": np.array([5, 5, 5, 5, 5])
}
```

- **[Logging Both Signature and Examples]**
    - Pass the `input_example` object to the `input_example` parameter in the `log_model` function to ensure both the signature and the examples are recorded in the run

```python
mlflow.sklearn.log_model(
    skelarn_model,
    "model",
    signature=signature,
    input_example=input_example
)
```

### Verifying Logged Artifacts in MLflow UI

After a successful run, the logged metadata can be inspected in the MLflow User Interface:

- **[MLmodel File]**
    - Contains the registered `signature` information
- **[Input Example Artifact]**
    - Appears as a separate artifact, allowing for verification of the sample data used during logging

### Inferring Model Signatures Automatically

- Manual definition can be tedious and complex
- An easier approach is to infer signatures and input examples directly from existing DataFrames

#### Using `infer_signature`

- MLflow provides the `infer_signature` function within the `mlflow.models.signature` module
- **[How it works]** It analyzes the shape and data types of provided example inputs and outputs to automatically determine the schema
- **[Usage]** Pass the input features (e.g., `X_test`) and the model's predictions (e.g., `predicted_qualities`) as arguments

```python
from mlflow.models.signature import infer_signature

# Automatically infer the schema from the data
signature = infer_signature(X_test, predicted_qualities)
```

### Manual Structure for Multiple Input Examples

- When providing multiple sample values instead of a single record, the `input_example` must be structured as a dictionary
    - **[Required Keys]**
        - `columns`: A NumPy array containing the column names from the input DataFrame
        - `data`: A NumPy array containing the actual values from the input DataFrame
- **[Why this structure?]** This is necessary because there is no other valid option for storing multiple data points in this format

```python

# Defining the input example dictionary for multiple samples
input_example = {
    "columns": np.array(testX.columns),
    "data": np.array(testX.values)
}

# Logging both the signature and the input examples
mlflow.sklearn.log_model(
    skelarn_model, "model",
    signature=signature,
    input_example=input_example
)
```

### Summary: Model Signatures vs. Input Examples

While both are important metadata stored with a model, they serve distinct purposes:

- **Model Signatures**
    - Defines the type, schema, and nature of the data
    - Specifies what data types are expected for inputs and what will be produced as outputs
- **Input Examples**
    - Provides a representation of the actual dataset used for predictions
    - Acts as a reference for the model's expected input format and values

---

### Manual Logging in Real-World Projects

In many professional environments, the `autolog` function may not be suitable or available. In these cases, developers must implement **manual logging** to ensure model metadata is captured according to specific project requirements.

### Configuring Autologging for Granular Control

In scenarios where you want to automate most of the logging but maintain control over specific metadata, you can configure `mlflow.sklearn.autolog()` to disable certain components.

- **[Configuration]** By setting specific parameters to `False`, you can prevent the automatic logging of the model, its signature, and its input examples, while still allowing other entities like hyperparameters and metrics to be logged automatically.

```python

# Example configuration to disable specific autologging components
mlflow.sklearn.autolog(
    log_model=False,
    log_input_examples=False,
    log_model_signatures=False
)
```

### Manual Creation of Model Signatures

Once autologging is configured to skip these components, you must manually create and log the signature object.

- **[Signature Object]** This object must contain two primary pieces of information:
    - The training data (input schema)
    - The model's predictions on that dataset (output schema)
- **[Two Approaches]**
    - **Manual Creation**: Typing out the schema definition explicitly.
    - **Inference**: Using a quick method to infer the schema directly from the dataset (e.g., using `infer_signature`).

### Manual Implementation of Model Signatures

When autologging is disabled, you can manually define the input and output schemas using the `models.signature` and `mlflow.types.schema` modules.

- **[Workflow]** Define the data structure, convert it to schema objects, and then instantiate the `ModelSignature` object.

#### 1. Defining Data Structures

- Create lists of dictionaries to represent the schema for both inputs and outputs.
- Each dictionary specifies the column name and its corresponding data type.

```python
input_data = [
    {"name": "fixed acidity", "type": "double"},
    {"name": "volatile acidity", "type": "double"},
    {"name": "citric acid", "type": "double"},
    {"name": "residual sugar", "type": "double"},
    {"name": "chlorides", "type": "double"},
    {"name": "free sulfur dioxide", "type": "double"},
    {"name": "total sulfur dioxide", "type": "double"},
    {"name": "density", "type": "double"},
    {"name": "pH", "type": "double"},
    {"name": "sulphates", "type": "double"},
    {"name": "alcohol", "type": "double"},
    {"name": "quality", "type": "double"}
]

output_data = [{"type": "long"}]
```

#### 2. Creating Schema Objects

- Use list comprehension to iterate through the data lists and convert them into `ColSpec` objects.
- The `Schema` object then wraps these `ColSpec` objects to form the complete input or output schema.

```python
from mlflow.types.schema import ColSpec
from mlflow.schema import Schema

# Convert input data to an input schema object
input_schema = Schema([ColSpec(type, name) for {"type": type, "name": name} in input_data])

# Convert output data to an output schema object
output_schema = Schema([ColSpec(type) for {"type": type} in output_data])
```

#### 3. Instantiating the Model Signature

- Combine the input and output schemas into a single `ModelSignature` object.

```python
from mlflow.models.signature import ModelSignature

signature = ModelSignature(inputs=input_schema, outputs=output_schema)
```

### Logging the Model with Signature and Input Examples

#### 1. Passing the Signature to `log_model`

- The `signature` object must be passed to the `signature` parameter within the `mlflow.sklearn.log_model` function to ensure the manual column-based signature is logged alongside the model.

```python
mlflow.sklearn.log_model(
    sk_model=model,
    artifact_path="model",
    signature=signature
)
```

#### 2. Defining Input Examples

- Input examples provide sample data points that help users understand the expected input format.
- **[Format]** Create a dictionary where keys are column names and values are data arrays.
    - You cannot pass a simple list for multiple records.
    - For a single record, use a scalar value.
    - For multiple records, use a NumPy array (`np.array`) to store multiple sample values per column.

```python
import numpy as np

input_example = {
    "fixed acidity": np.array([7.4, 7.8, 7.3, 7.8, 6.8]),
    "volatile acidity": np.array([0.25, 0.26, 0.28, 0.35, 0.27]),
    "citric acid": np.array([0.26, 0.28, 0.28, 0.28, 0.32]),
    "residual sugar": np.array([19.2, 18.6, 18.7, 18.6, 18.7]),
    "chlorides": np.array([0.079, 0.08, 0.08, 0.08, 0.08]),
    "free sulfur dioxide": np.array([11.2, 10.5, 15.6, 12.5, 11.5]),
    "total sulfur dioxide": np.array([34.0, 35.0, 35.0, 34.0, 35.0]),
    "density": np.array([0.997, 0.998, 0.998, 0.998, 0.998]),
    "pH": np.array([3.51, 3.48, 3.51, 3.51, 3.51]),
    "sulphates": np.array([0.56, 0.57, 0.57, 0.57, 0.57]),
    "alcohol": np.array([9.4, 9.4, 9.4, 9.4, 9.4]),
    "quality": np.array([5, 5, 5, 5, 5])
}
```

#### 3. Logging with Input Examples

- Pass the `input_example` dictionary to the `input_examples` parameter in the `log_model` function.

```python
mlflow.sklearn.log_model(
    sk_model=model,
    artifact_path="model",
    signature=signature,
    input_examples=input_example
)
```

- After running the logging code, the model signature and input examples can be verified within the MLflow experiment run artifacts.
- **[Verification Steps]**
    - Open the specific MLflow experiment and run.
    - Navigate to the `artifacts` section.
    - Locate the `MLmodel` file to confirm the `signature` is present.
    - Check for the `input_example.json` file to ensure the sample data was logged correctly.

### Automating Signature Generation

- Manually typing out column names and data types for signatures and input examples is tedious and error-prone.
- **[The Efficient Way]** Use MLflow's built-in utility to infer the signature directly from the data.
    - `mlflow.models.infer_signature` can automatically derive the schema from a DataFrame.
    - This eliminates the need for manual dictionary creation and ensures the signature matches the actual data structure.

### Using `infer_signature` for Automated Schema Generation

- `mlflow.models.infer_signature` is used to automatically infer the input and output schema of a machine learning model
    - It analyzes the shape and data type of provided example inputs and outputs
- **[Arguments]**
    - `X`: The input test data (e.g., `train_x`)
    - `y`: The output schema/predictions (e.g., `predicted_qualities`)
- **[Note on Output Schema]**
    - Providing output examples is optional
    - If the output schema is not provided, `infer_signature` will only infer the input schema

```python
from mlflow.models import infer_signature

signature = infer_signature(train_x, predicted_qualities)
```

### Creating Manual Input Examples from DataFrames

- To avoid manual typing, construct the `input_example` dictionary by extracting components directly from the testing DataFrame (`test_x`).
- **[Implementation Detail]** Because there is no single option to pass a DataFrame directly into the dictionary, the columns and data must be stored separately:
    - `"columns"`: The array of column names from `test_x.columns`.
    - `"data"`: The array of values from `test_x.values`.

```python
input_example = {
    "columns": np.array(test_x.columns),
    "data": np.array(test_x.values)
}
```

- After passing both the `signature` and `input_example` to `mlflow.sklearn.log_model`, the results can be verified in the MLflow UI.
- **[Verification in MLflow UI]**
    - The `MLmodel` file will show the schema was successfully `inferred` rather than manually defined.
    - The `input_example.json` artifact will be present, containing the sample data used for the model's input representation.

### Summary of Model Signatures and Input Examples

- **Model Signatures**
    - Specify the type, schema, and nature of the data that enters and exits the model
    - Defines the expected structure for both inputs and outputs
- **Input Examples**
    - Act as a representation of the dataset used for model predictions
    - Serve as a reference for how the dataset must be structured before being loaded into the model for inference

| Entity | Primary Purpose |
| --- | --- |
| Model Signature | Defines the schema, data types, and structure (input/output) |
| Input Example | Provides a practical reference/template of the input data format |

- **Key Concepts Covered**
    - Signature types: Column-based vs. Tensor-based
    - Signature enforcement techniques in MLflow
    - Manual logging of signatures and examples when auto-logging is unavailable