---
title: "Course: MLflow in Action - Master the art of MLOps using MLflow tool | Udemy Business"
description: A master guide to unleash the full potential of MLflow to optimize MLOps. Streamline MLOps workflows using MLflow tool
author: Udemy Business
source: https://10pearls.udemy.com/course/mlflow-course/learn/lecture/40383726#overview
created: "2026-08-21"
tags:
  - hover-notes
  - udemy
hovernotes-id: doc_18e31d14-5728-4ba8-829e-f6b383c1001e
---

## Model API

- A set of functionalities and utilities used to simplify packaging, versioning, and deploying trained models
    - This abstraction works regardless of the underlying technology or framework used to train the model
    - Concepts like ML model files, flavors, and signatures are all components of the Model API
- **Integration with ML Libraries**
    - The API is integrated with popular libraries (flavors) such as:
        - scikit-learn
        - TensorFlow
        - PyTorch
    - While the core functionality remains consistent across these libraries, specific arguments in the functions may change depending on the library being used
- **Core Functions**
    - `save_model`: To save the model
    - `log_model`: To log the model
    - `load_model`: To load the model
- **Implementation Examples**
    - `mlflow.sklearn`: An implementation of the Model API specifically integrated with the scikit-learn library

### `mlflow.sklearn.save_model` function

- Saves a scikit-learn model to a path on the local file system
    - This persists the model to a local directory without necessarily logging it to an MLflow server
- **Produces a model containing two flavors:**
    - `mlflow.sklearn`
    - `mlflow.pyfunc`
- **Parameters:**
    - `sk_model`: The scikit-learn model object to be saved
    - `path`: The local path where the model will be stored
    - `conda_env`: Defines the environment for the model
        - Can be a dictionary of the Conda environment
        - Or the path to a Conda environment `.yaml` file
        - If not specified, defaults are inferred from `mlflow.models.infer_pip_requirements()`

#### `mlflow.sklearn.save_model` continued

- **Additional Parameters:**
    - `code_paths`:
        - A list of local filesystem paths to Python file dependencies
        - Useful for storing the specific training code used to create the model
    - `mlflow_model`:
        - The `mlflow.models.Model` flavor being added to the saved model
    - `serialization_format`:
        - The format used to serialize the model
        - Examples include `pickle` or `cloudpickle`
    - `signature`:
        - An instance of the `ModelSignature` class
        - Describes the model's input and output schema
        - Can be created manually or inferred from a DataFrame
    - `input_example`:
        - An instance representing a sample of the data used as input to the model
    - `pip_requirements`:
        - An iterable of pip requirement strings (e.g., `["scikit-learn", "-r requirements.txt"]`)
        - Or a path to a `requirements.txt` file on the local filesystem
        - **Note:** While you can specify this explicitly, MLflow typically infers the default list of requirements from the current software environment automatically.
- **`pip_requirements`**
    - Used to explicitly specify a list of pip requirements if they cannot be automatically inferred by MLflow
    - Can be an iterable list of strings (e.g., `["scikit-learn", "-r requirements.txt", "-c constraints.txt"]`)
    - Or a path to a specific requirements file on the local filesystem
    - **[Caution]** Using this parameter replaces the default list that MLflow automatically infers from the environment
- **`extra_pip_requirements`**
    - **[Why use it?]** To add specific additional dependencies while still keeping the default requirements inferred by MLflow
    - Unlike `pip_requirements`, this parameter appends the specified requirements to the automatically generated list
    - Can be provided as an iterable list of strings or a path to a file

### `save_model` continued

- **Constraint on requirements:**
    - `pip_requirements` and `extra_pip_requirements` cannot be used simultaneously
- **`pyfunc_predict_fn`**
    - Specifies the name of the function used for prediction within the PyFunc representation of the resulting MLflow model
    - Example: `"predict_proba"`
- **`metadata`**
    - **[Caution]** This parameter is experimental and may change or be removed in the future
    - Accepts a custom metadata dictionary to be stored in the `MLModel` file

---

### `log_model` function

- **Purpose:** Logs a scikit-learn model as an artifact to an MLflow tracking server, making it accessible via the MLflow UI or other interfaces
- **Comparison to&#32;`save_model`:**
    - Shares most parameters with `save_model` but has key distinctions regarding destination and registration
- **Key Parameters:**
    - `artifact_path`:
        - Unlike `path` (which points to a local filesystem), this accepts a path relative to the MLflow run
        - Can be any path, not just local
    - `registered_model_name`:
        - Used for model registry
        - Creates a model version under the specified name
        - If the model name does not already exist, MLflow will register it automatically

### `log_model` continued

- **`await_registration_for`**
    - Specifies the number of seconds to wait for the model version to finish being created and reach the `READY` status
    - Default value is 300 seconds (5 minutes)
    - Set to `0` or `None` to skip this waiting period

---

### `load_model` function

- **Purpose:** Loads a logged or saved model from a local file or an MLflow run to be used for prediction and inference
- **Parameters:**
    - **`model_uri`**: The location of the model in URI format
    - **`dst_path`**:
        - The local filesystem path where the model artifact will be downloaded
        - The specified directory must already exist
        - If left unspecified, a `local_output` path will be created automatically
- **Model URI Examples:**
    - Models can be located in local directories, on servers, or in the cloud

| URI Format Type | Example |
| --- | --- |
| Local Path | /Users/me/path/to/local/model |
| Relative Path | relative/path/to/local/model |
| S3 Bucket | s3://my_bucket/path/to/model |
| MLflow Run | runs:/<mlflow_run_id>/run-relative/path/to/model |
| Model Name & Version | models:/<model_name>/<model_version> |
| Model Name & Stage | models:/<model_name>/<stage> |

### `log_model` vs `save_model` demonstration

- **Key distinction in artifact storage**:
    - `log_model`: Logs the model artifact to the MLflow tracking server, making it visible in the MLflow UI.
    - `save_model`: Simply saves the model artifact to a local directory on the filesystem.
- **Observation from demonstration**:
    - When using `save_model`, the MLflow tracking server shows parameters, metrics, and tags, but the **Artifacts** section remains empty.
    - The actual model files are only found in the local directory specified in the code (e.g., a folder named `model`).

## Model Customization

### MLflow Flavors

- A standardized way of organizing and encapsulating a model and its associated metadata
    - This allows for easier interaction with models across different frameworks and tools
- **Types of Flavors**:
        - **Built-in flavors**: Included by default in MLflow; provide out-of-the-box functionality for tracking, packaging, and deploying models
                - Examples: `scikit-learn`, `tensorflow`, `pytorch`
                - Best for beginners or straightforward workflows
        - **Custom flavors**: Required when built-in utilities are insufficient
        - **Community flavors**: (Mentioned as a category)

### Scenarios Requiring Customization

- **Unsupported Libraries**: When you need to use a machine learning library that does not have an explicit built-in flavor in MLflow
- **Custom Inference Logic**: When the built-in utilities cannot sufficiently package your specific custom inference code into an MLflow model

### Model Customization Methods

- **Custom Python Models**
    - Empower data scientists to incorporate their own algorithms, custom logic, and external libraries directly into the model building process
    - Allows for defining custom model implementations using any Python library or framework of choice
    - Enables leveraging MLflow's tracking and deployment capabilities even when using libraries that do not have a built-in flavor
- **Custom Flavors**
    - Extends MLflow's capabilities beyond the standard built-in flavors
    - Allows for the creation of custom serialization and deserialization logic
    - **[Why use it?]** To ensure models with specific requirements or dependencies are properly packaged and can be deployed consistently across different environments

### Customization Implementation

- **Custom Python Models**
    - Empower data scientists to incorporate their own algorithms, custom logic, and external libraries seamlessly into the model building process
- **Custom Flavors**
    - Allow for the creation of custom serialization and deserialization logic for model packaging and deployment

### Using `mlflow.pyfunc` for Custom Models

- Used when a library is not natively supported by MLflow or when custom inference logic is required
- **[How it works]** By using the `mlflow.pyfunc` module, you can define your own Python code to specify model functionality
    - You can include specific artifact dependencies or other resources needed for inference
- **[The Benefit]** Custom models are packaged with a `PythonFunction` flavor
    - This is a built-in MLflow flavor that ensures compatibility across various production environments
    - Supports deployment to platforms like SageMaker, Azure ML, or local REST endpoints

```python
import warnings
import argparse
import logging
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.linear_model import ElasticNet
import mlflow
import mlflow.sklearn
import os

from mlflow.models.signature import ModelSignature, infer_signature
from mlflow.types.schema import Schema, ListType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get arguments from command
parser = argparse.ArgumentParser()
parser.add_argument('--alpha', type=float, required=False, default=0.1)
parser.add_argument('--l1_ratio', type=float, required=False, default=0.4)
args = parser.parse_args()

# Evaluation function
def eval_metrics(actual, pred):
    mse = np.sqrt(mean_squared_error(actual, pred))
    mae = mean_absolute_error(actual, pred)
    r2 = r2_score(actual, pred)
    return mse, mae, r2
```

### Implementing Custom Model Logging

- **Adapting Existing Scripts**
    - If a library like `scikit-learn` is assumed to be unsupported, native MLflow functions (such as `mlflow.sklearn.log_model`) must be removed
    - The core experiment setup and run logic remain identical; only the model saving/logging step changes
- **Using&#32;`mlflow.pyfunc.log_model`**
    - Used as the replacement for library-specific logging functions
    - **Parameters**
        - `artifact_path`: The first parameter, defining the directory/path where the packaged model will be stored within the MLflow run

```python

# Example of transitioning to pyfunc logging

# Instead of mlflow.sklearn.log_model(...)

mlflow.pyfunc.log_model(
    artifact_path="model",

# ... other parameters
)
```

### `mlflow.pyfunc.log_model` Parameters

- **`artifact_path`**
    - A run-relative path defining where the packaged model is stored
- **`python_model`**
    - Specifies the Python function-based model object to be logged
    - **Requirements**
        - Must be an instance of a class derived from `mlflow.pyfunc.PythonModel` (or a compatible implementation)
    - **Mechanism**
        - The object passed is serialized using the `cloudpickle` library
        - This is where the wrapper class name of the customized model is provided

```python
mlflow.pyfunc.log_model(
    artifact_path=mlflow.get_artifact_uri(),
    python_model=None,  # Placeholder for the custom model instance
    artifacts=None
)
```

### `mlflow.pyfunc.log_model` Parameters (cont.)

- **`artifacts`**
    - An artifact directory used to store additional files required by the model
- **`code_path`**
    - A list of files or directories to be logged as code dependencies
    - **Purpose**
        - Ensures custom functions, modules, or scripts required to reproduce the model are included in the package
    - **Example**
        - In this demonstration, only `main.py` is being saved
- **`conda_env`**
    - Specifies the Conda environment configuration for the model
    - **Format**
        - Accepts a dictionary containing the environment configuration

```python
mlflow.pyfunc.log_model(
    artifact_path="model",
    python_model=None, # Placeholder for custom model instance
    artifacts=None,
    code_path=["main.py"],
    conda_env=None
)
```

### MLflow Model Storage

- Models are treated as artifacts within MLflow
    - MLflow does not store models as standalone entities
    - Instead, it stores everything related to a machine learning project in a directory structure
    - This includes the model itself, supporting datasets, and any other necessary files
    - **[Purpose]** This organization ensures all ML components are neatly packaged, managed, and easily accessible via MLflow

### Manual Model Serialization with `joblib`

- `joblib` is a common package used to serialize machine learning models
- **`joblib.dump`&#32;parameters**
    - The trained model object
    - The full path of the directory where the model should be saved

```python

# Creating a pickle file of the model
import joblib

# Define the filename/path
sklearn_model_path = "sklearn_model.pickle"

# Serialize and save the model
joblib.dump(sklearn_model, sklearn_model_path)
```

### Custom Model Wrapper with `mlflow.pyfunc.PythonModel`

- A wrapper class is used to define custom Python models that are compatible with MLflow's APIs
    - **[Purpose]** It standardizes the model interface and ensures compatibility with MLflow's management functionalities
- The class must inherit from `mlflow.pyfunc.PythonModel`
- **Key Methods to Override**
        - `load_context(self, context)`
                - Called when the model is being loaded into a deployment context (e.g., during model serving)
                - Used to load necessary artifacts or dependencies required for inference
        - `predict(self, context, model_input)`
                - Defines the behavior of the model during inference
        - `serialize_model(self)`
                - Defines how the model is serialized

```python
class SklearnWrapper(mlflow.pyfunc.PythonModel):
    def load_context(self, context):

# Logic to load artifacts or dependencies
        pass

    def predict(self, context, model_input):

# Logic for model inference
        pass
```

### Implementing Wrapper Class Methods

#### `load_context` Method

- Used to handle model-specific loading logic
    - Takes two parameters: `self` and `context`
    - Uses `joblib.load` to deserialize the model from the `context.artifacts` dictionary

```python
def load_context(self, context):

# Logic specific to a model within this method.
    self.sklearn_model = joblib.load(context.artifacts['sklearn_model'])
```

#### `predict` Method

- Responsible for performing inference or predictions
- **Parameters**
        - `self`: The wrapper instance
        - `context`: Provides additional context information
        - `model_input`: The actual input data for which predictions are required

```python
def predict(self, context, model_input):

# Implement the prediction logic of your model within this method
    return self.sklearn_model.predict(model_input)
```

#### `predict` Method Implementation

- The method uses the loaded model to perform predictions based on the provided input

```python
def predict(self, context, model_input):
    return self.sklearn_model.predict(model_input)
```

### Benefits of Custom Python Models

- Provides full control over model behavior within MLflow
    - Achieved by overriding default methods
    - Allows for the creation of new methods if required

### Defining the Conda Environment

- For built-in supported libraries, MLflow automatically creates environment files (e.g., `conda.yaml`, `pipenv`, or `requirements.txt`)
- Because we are using a custom model via `mlflow.pyfunc`, we must define the environment files ourselves
- **[Why do this?]** While not strictly compulsory (it won't cause errors if omitted), including it makes it much easier for others to recreate the environment and utilize the model
- The `conda.env` is defined as a dictionary containing the following structure:
    - `channels`: A list of sources used to download packages (defaults are often sufficient)
    - `dependencies`: A list containing the environment specifications
        - Python version (e.g., `python=3.10`)
        - `pip`: A sub-dictionary containing `packages`, which is a list of required packages and their specific versions

```python
conda_env = {
    "channels": ["defaults"],
    "dependencies": [
        "python=3.10",
        "pip": {
            "packages": [
                "mlflow==2.1.1",
                "scikit-learn==1.2.2",
                "cloudpickle==2.0.0"
            ]
        },
        "name": "sklearn_env"
    ]
}
```

### Finalizing the Conda Environment

- Added the remaining dependencies and the environment name to the `conda_env` dictionary
    - Required packages: `mlflow`, `scikit-learn`, and `cloudpickle`
    - Environment name: `sklearn_env`

```python
conda_env = {
    "channels": ["defaults"],
    "dependencies": [
        "python=3.10",
        "pip": {
            "packages": [
                "mlflow==2.1.1",
                "scikit-learn==1.2.2",
                "cloudpickle==2.0.0"
            ]
        }
    ],
    "name": "sklearn_env"
}
```

### Configuring Artifacts

- An `artifacts` dictionary is used to map names to the file paths of objects you want to store within the MLflow model format
- **[What can be an artifact?]** Anything from a trained model file to specific datasets used during training

```python
artifacts = {
    "sklearn_model": sklearn_model_path,
    "input_datasets": artifacts_uri
}
```

- **[How to handle datasets?]** If datasets need to be included, they must first be saved to a directory structure
    - For example, creating a dictionary to map input data to specific paths before passing them to the `artifacts` dictionary

```python

# Example of preparing a directory for datasets
artifacts_uri = "./mlflow_artifacts"
import os

# Logic to ensure the directory exists and files are copied would go here
```

- Once both `conda_env` and `artifacts` are defined, they are passed into the `mlflow.pyfunc.log_model` function

```python
mlflow.pyfunc.log_model(
    artifact_path="sklearn_wrapper",
    python_model=sklearn_wrapper,
    conda_env=conda_env,
    artifacts=artifacts
)
```

### The `mlflow.pyfunc` Model Flavor

- The `mlflow.pyfunc` flavor defines a generic filesystem model format for Python models
- **[Why use it?]** It provides utilities for saving and loading models in a standardized format, irrespective of the specific library used
    - This enables other MLflow tools to work with any Python model, even if the original persistence module or framework was different

### Verifying the Logged Run in MLflow UI

- After running the code, the MLflow UI displays the details of the specific run
- **[What is captured?]**
        - Parameters
        - Metrics
        - Tags
        - Artifacts
- **[Artifact Directory Structure]** The logged artifact directory (e.g., `sklearn_ml4_pyfunc`) contains:
        - `sklearn_model.pkl`: The actual pickled model file
        - `data/`: The directory containing the input datasets used
        - `code/`: The source code used for the run

### MLflow Flavor Visibility

- Because the model was logged as a `python_function` flavor, only one flavor will be displayed in the MLflow UI
    - This is a consequence of using the generic `pyfunc` interface which abstracts away the underlying library-specific flavors

### Next Steps

- The custom Python model creation is complete
- The next objective is to load the logged model and use it for making predictions

### Model Inferencing with `mlflow.pyfunc`

- To perform inference, the model must first be loaded using the `load_model` function from the respective library
- Once loaded, the `.predict()` method is used to generate predictions
- **[Best Practice]** For production or clean code, it is recommended to separate loading and inferencing logic into a dedicated file (e.g., `predictor.py`), as the prediction stage does not require the original training or logging code

#### Loading the Model

- The `mlflow.pyfunc.load_model` function requires a specific URI to locate the model within the MLflow tracking server
- **[URI Structure]** The URI must follow the pattern: `runs:/<run_id>/<artifact_path>`
    - `runs:/` identifies the source as a specific MLflow run
    - `<run_id>` is the unique identifier for the run from the tracking server
    - `<artifact_path>` is the specific path within that run's artifacts where the model is stored

```python

# Loading the model for inference
model = mlflow.pyfunc.load_model(f"runs:/{run.info.run_id}/{artifacts_uri.get(artifacts_uri)}")

# Making predictions
predictions = model.predict(data)
```

### Model Evaluation and Summary

- **[Evaluation]** Once predictions are generated, performance can be assessed using evaluation metrics on a test dataset
    - Example workflow: `predict` $\rightarrow$ `eval_metrics` $\rightarrow$ `print results`
- **[Customizing MLflow Python Functions]** By defining custom behaviors within a `python_function` flavor, users can:
    - Add support for custom machine learning libraries
    - Define specific functionalities and artifact dependencies tailored to unique needs
    - Leverage MLflow's deployment capabilities across various production environments
    - Integrate custom models more seamlessly into existing machine learning workflows