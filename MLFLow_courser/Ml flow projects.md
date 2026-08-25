---
title: "Course: MLflow in Action - Master the art of MLOps using MLflow tool | Udemy Business"
description: A master guide to unleash the full potential of MLflow to optimize MLOps. Streamline MLOps workflows using MLflow tool
author: Udemy Business
source: https://10pearls.udemy.com/course/mlflow-course/learn/lecture/40444510#overview
created: "2026-08-21"
tags:
  - hover-notes
  - udemy
hovernotes-id: doc_6a13586a-dc97-45cf-b727-0816b52050d2
---

## MLflow Projects

- A tool used to organize and share machine learning code and models
- **[The Problem]** Data science projects often exist in "silos" where code cannot be easily used or modified by others due to differences in:
    - Dependencies
    - Environments
    - Operating systems
- **[The Solution]** MLflow Projects provides a simple way to define and manage:
    - Project dependencies
    - Environments
    - Entry points
- `MLProject` file
    - Explains the project structure
    - Defines which files are part of the project
    - Specifies required dependencies
    - Dictates how to execute the project
- Provides both API and CLI tools to run projects, facilitating the integration of various projects into a unified workflow

### MLflow Project Conventions

- A project is treated as a folder containing all files related to the code
    - This folder can reside on a local machine or in a cloud directory/machine
- MLflow uses specific conventions to recognize project components
    - For example, a `.yml` file can be treated as an environment definition
- **[The MLproject file]** Acts as a central "guidebook" for the project
    - It is a YAML-formatted text file
    - It specifies the project's:
        - Entry points
        - Dependencies
        - Associated parameters
    - This standardization makes it easier to manage and reproduce experiments across different environments

### MLflow Project vs. Single Model

- **[Distinction]** While a single model describes the nature of a specific model, an MLflow Project describes the overall workflow and execution steps of the entire project
    - It encompasses the complete project directory structure

### The MLproject File

- Acts as a "guidebook" for the machine learning project
- While a project can function without it, including this file is highly recommended for formalizing the workflow
- **[Purpose]** It serves as a central configuration file used to define:
        - Project name
        - Description
        - Entry points
        - Dependencies
        - Other organizational details to dictate the behavior of the machine learning code

### Practical Implementation: PyChamp Project

- **[Code Refactoring]** To prepare the script for MLflow, the code is encapsulated within a `main()` function
    - This ensures the logic is contained and can be explicitly called by the MLflow entry point
    - Example structure:

```python
def main():

# ... existing code logic ...
          pass

      if __name__ == "__main__":
          main()
```

- **Creating the MLproject File**
    - A new file is created in the project directory
    - **[Critical Naming Rules]**
        - The file must be named exactly `MLproject`
        - It must have **no file extension** (e.g., do not use `.yml` or `.txt`)
        - Spelling and capitalization are strict and must be exact

### MLproject File Structure

- The file uses the YAML format
- **[Core Characteristics]** The file is characterized by three primary components:
    - **Name**: The identifier for the project
    - **Entry points**: Definitions for different tasks or actions that can be executed within the project
        - These act like "mini programs" within the overall project
        - Each entry point is associated with a specific command and a set of parameters
        - **[Examples]** Tasks could include model training, performance evaluation, data pre-processing, or deployment
        - Users can customize settings or options for each entry point when running the code
    - **Environment**: Specifies the execution environment required for the entry points
        - This includes all library dependencies needed by the project code
        - MLflow supports managing these environments through:
            - Conda environments
            - Docker containers

```mermaid
mindmap
  root((MLproject File))
    Name
      Project identifier
    Entry Points
      Mini programs/tasks
      Specific commands
      Customizable parameters
    Environment
      Library dependencies
      Conda environments
      Docker containers
```

### Writing the MLproject File

- **[Implementation]** Starting the actual creation of the file
    - The first configuration being defined is the project name

```yaml
name: "Elastic Regression project"
```

- **MLflow Project Environments**
    - These are the execution environments where the machine learning code runs
    - **[What they include]**
        - Necessary dependencies
        - Libraries
        - System configurations required for proper execution
    - **[Supported Environment Types]**
        - Virtual ENV
        - Docker container
        - Conda
        - System environment

```mermaid
mindmap
  root((MLflow Environments))
    Virtual ENV
    Docker container
    Conda
    System environment
```

### System Environment

- This is essentially the host operating system
    - It includes the installed version of Python and other required system-level dependencies

### Virtual Environment

- Acts as a separate, isolated workspace for a project
    - Uses tools like `virtualenv` and `pyenv` to prevent dependency conflicts between different projects on the same machine
    - **[How it works]** When specified, MLflow uses `pyenv` to download the required Python version and creates an environment containing the project's specific dependencies
    - The environment is automatically created and activated before the project code runs
- **[Configuration]** Defined in the MLproject file using the `python_env` entry
    - The value must be a relative path to a Python environment file within the project directory

```yaml
name: "Elastic Regression project"
python_env: files/config/python_env.yml
```

### Python Environment File Structure

- The `python_env.yml` file internally defines the required Python packages and their versions
- **[Structure]** A typical file includes:
    - The required Python version
    - Build dependencies (optional, required to build certain packages)
    - Dependencies to be installed via `pip`

```yaml

# Python version required to run the project.
python: "3.6.15"

# Dependencies required to build packages. This field is optional.
build_dependencies:
    pip:
        - setuptools
        - wheel=0.37.1

# Dependencies required to run the project.
dependencies:
    mlflow=2.3
    scikit-learn=1.0.2
```

### Conda Environment

- A highly popular and simple virtual environment option for Python
- **[Configuration]** Specified in the MLproject file using the `conda_env` entry
    - Requires a configuration file (typically `conda.yml`) that lists the necessary packages and versions

```yaml
name: "Elastic Regression project"
conda_env: files/config/conda.yml
```

- **[Pro-tip]** Instead of writing a `conda.yml` file from scratch, you can export your currently running Conda environment
    - Use the Conda export command to generate a `conda.yml` file directly from your active environment

### Exporting a Conda Environment

- Use the terminal to capture the current environment's configuration
    - Command: `conda env export --name <env_name> > <filename>.yml`
    - Example: `conda env export --name mlflow_demo1 > conda.yml`

### Structure of a `conda.yml` File

- The exported file contains the specific blueprint needed to recreate the environment
- **[Components]**
        - **name**: The name of the Conda environment
        - **channels**: The locations/repositories used to find packages
        - **dependencies**: The core packages required to build the Python kernel
        - **pip dependencies**: A sub-section for packages installed via `pip` within the Conda environment

### Integrating Conda with MLflow

- Once the `.yml` file is created, it must be referenced in the `MLproject` file
- **[Configuration]** Use the `conda_env` key followed by the path to the file

```yaml
name: "Elastic Regression project"
conda_env: conda.yml
```

- If the file is in the same directory as the `MLproject` file, only the filename is required; otherwise, a full path must be provided.

### Docker Environments

- Provides a self-contained environment for running MLflow projects
- **[Key Advantage]** Allows the inclusion of non-Python dependencies
    - Can manage system-level libraries like Java or C++ that are required for certain ML tasks
- MLflow can execute the project using a specific Docker image to ensure environment consistency

### Docker Environment Execution

- MLflow can run an existing Docker image as-is using parameters from the MLproject file
- Alternatively, the `--build-image` flag can be used with `mlflow run` to build a new image based on an existing one
    - This new image will include the project's contents located in the `mlflow/project/code` directory
- **[Data Persistence & Connectivity]** To ensure metrics, parameters, and artifacts are accessible:
    - Environment variables (such as `MLFLOW_TRACKING_URI`) are propagated inside the container
    - The host system's tracking directory is mounted inside the container

### Configuring Docker in MLproject

- Specify the environment using a top-level `docker_env` entry in the `MLproject` file
- The value must be the name of a Docker image that is accessible

#### Example: Image without a registry path

- This approach provides just the image name; Docker will look for it locally first and then attempt to pull it from Docker Hub if it is not found

```yaml
docker_env:
  image: mlflow-docker-example-environment
```

### Advanced Docker Configurations

Beyond just specifying an image, the `docker_env` entry can include parameters for volumes and environment variables to customize the container's behavior.

#### Mounting Volumes

- Use the `volumes` key to mount local directories from the host system into the container
    - This is useful for providing the container with access to specific datasets or files located on the host
    - **[Syntax]** The format follows `"[/host/path/directory/on/host/system:"/container/mount/path" ]`

#### Specifying Environment Variables

- Use the `environment` key to define variables within the container
- The value can be a single string or a list of strings:
    - **Single string**: Represents an existing environment variable from the host system that should be copied into the container
    - **List of strings**: Used to define new environment variables specifically for the Docker environment

```yaml
docker_env:
  image: mlflow-docker-example-environment
  volumes: ["/local/path:/container/mount/path"]
  environment: [["NEW_ENV_VAR", "new_var_value"], "VAR_TO_COPY_FROM_HOST_ENVIRONMENT"]
```

### Image in a Remote Registry

- Use the full registry path to point to images hosted outside of Docker Hub
    - This allows the use of private or cloud-specific registries like Amazon Elastic Container Registry (ECR)
    - **[Requirement]** The system executing the MLflow project must have the necessary credentials to access the remote registry

```yaml
docker_env:
  image: 012345678910.dkr.ecr.us-west-2.amazonaws.com/mlflow-docker-example-environment:7.0
```

### Building a New Image

- If a pre-built image is not available, MLflow can build a new one based on an existing base image and the files in the project directory
    - You specify the base image in the `docker_env` entry
    - To trigger this process, use the `--build-image` argument with the `mlflow run` command

#### Example: Building from a Python base image

```yaml
docker_env:
  image: python:3.8
```

```bash
mlflow run ... --build-image
```

### MLproject Entry Points

- Entry points define the specific tasks or operations that can be executed as part of a machine learning project
    - They essentially act as commands for "mini programs" within the project
- An MLproject file typically consists of three main properties:
        - `name`
        - `environment`
        - `entry_point`

### Project Functionalities and Workflows

- Specific functionalities or workflows can be defined to run within the project context
    - These are used for executing particular tasks or processes required by the project

### Components of an Entry Point

- Each entry point is composed of three key parts:
    - **Name**: Serves as a unique identifier for a specific task or action within the project
    - **Command**: Specifies the script or executable to be run for that task
        - This can be a Python script, a shell command, or any other executable
    - **Parameters**: Define the inputs or configurations required for executing the entry point
        - These provide flexibility and customization
        - They can be provided as command line arguments or within the MLproject file itself

### Entry Point Implementation Details

- **Environment Specification**
    - Each entry point can have its own specific execution environment
    - This allows for task-specific dependencies, Python versions, or configurations
    - Supported environment types:
        - Conda environments
        - Docker containers
- **Practical Use Cases**
    - A single Git repository can contain multiple feature engineering algorithms, each accessible via different entry points
    - Entry points can execute various file types, such as `.py` scripts or `.sh` shell files
- **Project Complexity**
    - While most projects contain at least one entry point, production-level projects often utilize multiple entry points to handle different stages of the machine learning lifecycle

### MLproject File Syntax

- The `MLproject` file uses a specific YAML-based structure to define entry points
- Each entry point is declared under the `entry_points` key in the file

### Entry Point Components (Continued)

- **Environment** (Optional)
    - Specifies the execution environment for the specific task
    - Includes necessary dependencies, Python versions, or additional configurations
    - Supported methods:
        - Conda environments
        - Docker containers

### Implementing an Entry Point

- **Example: ElasticNet Task**
    - The goal is to create an entry point to run the existing machine learning code
    - **Name**: `ElasticNet`
    - **Command**: Uses the standard Python CLI command to execute the script

```yaml
name: "Elastic Regression project"
conda_env: conda.yaml

entry_points:
  ElasticNet:
    command: "python main.py"
```

### Parameter Implementation in MLproject

- **Using Placeholders in Commands**
    - Instead of hardcoding values in the `command` field, use placeholders that get substituted at runtime
    - **[Security Note]**: MLflow automatically escapes parameter values using the `shlex.quote` function, so manual escaping (like adding quotes) is not required within the command field
    - Example command with placeholders:

```yaml
command: "python main.py --alpha ${alpha} --l1_ratio ${l1_ratio}"
```

- **Declaring Parameters**
    - Parameters are defined in the YAML configuration, similar to how one might define `argparse` arguments in a Python script
    - **MLflow Supported Parameter Types**:
    - `string`: A standard text string
    - `float`: A real number (MLflow validates that the input is a number)
    - `path`: A path on the local file system
        - MLflow automatically converts relative paths to absolute paths
        - It also handles downloading distributed URIs to local files
    - `uri`: A Uniform Resource Identifier

```yaml
name: "Elastic Regression project"
conda_env: conda.yaml

entry_points:
  ElasticNet:
    command: "python main.py --alpha ${alpha} --l1_ratio ${l1_ratio}"
    parameters:
      alpha:
        type: float
```

### MLflow Supported Parameter Types (Continued)

- **uri**
    - Used for data located in local or distributed storage systems
    - Similar to `path`, it can handle relative paths
    - Specifically intended for programs designed to read from distributed storage (e.g., Spark)

### Implementing the ElasticNet Entry Point

- **Parameter Configuration**
    - For this specific implementation, both `alpha` and `l1_ratio` are defined as `float` types

```yaml
name: "Elastic Regression project"
conda_env: conda.yaml

entry_points:
  ElasticNet:
    command: "python main.py --alpha ${alpha} --l1_ratio ${l1_ratio}"
    parameters:
      alpha:
        type: float
```

- **path**
    - Refers to a path on the local file system
    - MLflow handles several automation tasks for paths:
        - Converts relative paths to absolute paths
        - Downloads distributed URIs (such as from S3, DBFS, or GS) to local files
- **uri**
    - Used for data in local or distributed storage systems
    - Similar to `path`, it handles relative paths
    - **[Key Distinction]**: It is specifically intended for programs designed to read directly from distributed storage systems, such as Spark

### Implementing the ElasticNet Entry Point (Continued)

- **Parameter Implementation**
    - For this implementation, both `alpha` and `l1_ratio` are set to the `float` type
    - Default values can be assigned within the configuration

```yaml
name: "Elastic Regression project"
conda_env: conda.yaml

entry_points:
  ElasticNet:
    command: "python main.py --alpha ${alpha} --l1_ratio ${l1_ratio}"
    parameters:
      alpha:
        type: float
        default: 0.4
      l1_ratio:
        type: float
        default: 0.4
```

### MLproject Parameter and Command Rules

- **Parameter Declaration**
    - Parameters must be declared in the `parameters` field to be recognized as specific types
    - Parameters are substituted into the `command` string during execution
- **Undeclared Parameters**
    - Any parameter used in a command that is *not* explicitly declared in the `parameters` field is treated as a `string` type
- **Passing Additional Parameters**
    - You can pass parameters not listed in the `parameters` field using key-value syntax; MLflow will pass these directly to the entry point command
- **Entry Point Constraints**
    - Each entry point is limited to exactly **one** command
    - An entry point can have multiple parameters
    - **[Note]**: To run additional or different commands, you must define a separate entry point

### MLproject File Summary

- **Core Components**
    - `name`: The name of the project
    - `conda_env`: The environment configuration
    - `entry_points`: The executable commands and their parameters
- **Supported Execution Environments**
    - **System**: Does not require an entry in the project file (configured manually)
    - **Virtual**: Requires a Python environment entry
    - **Docker**: Requires a Docker environment entry
    - **Conda**: Requires a `conda_env` entry (e.g., `conda.yaml`)

```mermaid
mindmap
  root((MLproject Components))
    name
    environment
      system
      virtual
      docker
      conda
    entry_points
      command
      parameters
```

## Running MLflow Project

- Two ways to run projects in a specified environment:
    - **CLI command**
        - `mlflow run` (used in the terminal)
    - **API function**
        - `mlflow.projects.run` (used within a script)

### MLflow Project Concept

- A packaged unit of work that can be shared and run by others
    - Projects can be uploaded to platforms like GitHub for easy distribution
- **[What it means to run a project]** Executing the defined entry points within a specified environment

### CLI Run Command

- Syntax for executing a project via terminal:

```bash
mlflow run [OPTIONS] URI
```

- **[The URI Parameter]** This is a required argument that points to the MLflow project you want to run
    - It can be a local file path
    - It can be a remote repository (e.g., GitHub)

### Project Execution and Sharing Context

- The specific options used in the `mlflow run` command depend on two main factors:
    - **The execution platform** (where the code runs)
    - **The access method** (how the code is provided)
- **Execution Platforms**
    - **Local machine**: Running the project on a personal laptop
    - **Remote machine**: Running the project on cloud platforms like Databricks or Azure Machine Learning
- **Code Access Methods**
    - **Directory structure**: Providing the code physically (e.g., via a USB drive or a local folder)
    - **Git repository**: Using tools like GitHub to run the code directly from a remote repository without needing the files physically on the machine

```mermaid
flowchart TD
    Start[MLflow Project] --> Platform{Execution Platform}
    Start --> Access{Access Method}

    Platform -->|Local| LocalEnv[Personal Laptop]
    Platform -->|Remote| RemoteEnv[Databricks / Azure ML]

    Access -->|Physical| Dir[Directory Structure / USB]
    Access -->|Remote| Git[Git Repository / GitHub]
```

### MLflow Run Command Options

- `-e, --entry-point <NAME>`
    - Specifies the entry point to run within the project
    - Defaults to `main`
    - Example: `mlflow run -e <my_entry_point> <my_project_uri>`
- `-v, --version <VERSION>`
    - Used when running a project from a Git repository
    - Allows specifying a specific version, such as a Git commit reference
    - Example: `mlflow run -v <abc123> <my_project_uri>`
- `-P, --param-list <NAME=VALUE>`
    - Used to pass parameters to the run
    - **[Note on parameter handling]** Any parameters provided that are not listed in the MLproject file's entry points will be passed as command-line arguments to that entry point
    - Example: `mlflow run -P param1=value1 -P param2=value2 <my_project_uri>`
- `-A, --docker-args <NAME=VALUE>`
    - Used when the project is running in a Docker container
    - Allows passing Docker run arguments or flags directly to the `docker run` command
    - Example: `mlflow run -A gpus=all -A t <my_project_uri>`
- `--experiment-name <experiment_name>`
    - Specifies the name of the experiment under which to launch the run
    - Example: `mlflow run --experiment-name <my_experiment> <my_project_uri>`
- `--experiment-id <experiment_id>`
    - Specifies the specific ID of the experiment to use for the run
    - Example: `mlflow run --experiment-id <my_experiment_id> <my_project_uri>`
- `-b, --backend <BACKEND>`
    - Determines the execution backend to use
    - Supported values:
        - `local` (the default value)
        - `databricks` (launches the run against the specified workspace)
        - `kubernetes` (currently experimental)
    - Example: `mlflow run -b databricks <my_project_uri>`

### MLflow Run Command Options (Continued)

- `-c, --backend-config <FILE>`
    - Provides a path to a JSON file or a JSON string for backend configuration
    - Content must be specific to the chosen execution backend
    - Example: `mlflow run -c backend_config.json <my_project_uri>`
- `--env-manager <env_manager>`
    - Specifies the environment manager to use for the ML project
    - Supported values: `local`, `virtualenv`, and `conda`
    - If omitted, MLflow automatically selects an appropriate manager based on project configuration
    - Example: `mlflow run --env-manager conda <my_project_uri>`
- `--storage-dir <storage_dir>`
    - **[Note]** Only valid when the backend is set to `local`
    - MLflow downloads artifacts from distributed URIs into sub-directories of this specified directory
    - Example: `mlflow run --storage-dir <storage_dir> <my_project_uri>`
- `--run-id <RUN_ID>`
    - Allows specifying an existing run ID instead of creating a new run
    - Primarily used internally by MLflow project APIs and should not be manually specified
    - Example: `mlflow run --run-id <my_run_id> <my_project_uri>`
- `--run-name <RUN_NAME>`
    - Sets the name of the MLflow run associated with the project execution
    - If not specified, the run name is left unset
    - Example: `mlflow run --run-name <my_run_name> <my_project_uri>`
- `--build-image`
    - **[Note]** Only valid for Docker projects
    - If specified, MLflow builds a new Docker image based on the one specified in the `MLproject` file, including files in the project directory
    - Example: `mlflow run --build-image <my_project_uri>`

### MLflow Environment Variables

- **MLFLOW\_EXPERIMENT\_NAME**
    - Can be set to provide a default value for the `--experiment-name` option
    - Example: `export MLFLOW_EXPERIMENT_NAME=my_experiment`
- **MLFLOW\_EXPERIMENT\_ID**
    - Can be set to provide a default value for the `--experiment-id` option
    - Example: `export MLFLOW_EXPERIMENT_ID=<123>`
- **MLFLOW\_TMP\_DIR**
    - Can be set to provide a default value for the `--storage-dir` option when using the local backend
    - Example: `export MLFLOW_TMP_DIR=/path/to/storage`

### MLflow Environment Variables

- Setting these variables allows you to avoid specifying certain options every time you run the `mlflow run` command
- The values provided by these variables act as defaults and will be used unless overridden by explicit command-line options
- **Key Variables:**
    - `MLFLOW_EXPERIMENT_NAME`
        - Provides a default value for the `--experiment-name` option
        - Example: `export MLFLOW_EXPERIMENT_NAME=my_experiment`
    - `MLFLOW_EXPERIMENT_ID`
        - Provides a default value for the `--experiment-id` option
        - Example: `export MLFLOW_EXPERIMENT_ID=<123>`
    - `MLFLOW_TMP_DIR`
        - Provides a default value for the `--storage-dir` option when using the local backend
        - Example: `export MLFLOW_TMP_DIR=/path/to/storage`

### MLflow CLI Configuration and Execution

- **Setting the Tracking URI**
    - When using the CLI, the tracking URI is set by defining the `MLFLOW_TRACKING_URI` environment variable
    - Example: `export MLFLOW_TRACKING_URI=http://127.0.0.1:5000`
- **Executing an MLflow Project**
    - The `mlflow run` command is used to execute a project
    - **Specifying Entry Points and Parameters:**
        - The command follows the structure: `mlflow run <project_uri> --entry-point <entry_point_name> -p <param1> <value1> -p <param2> <value2>`
        - To specify multiple parameters, the `-p` flag must be used for each one individually
        - Example: `mlflow run --entry-point elastic_net -p alpha 0.5 -p l1_ratio 0.5`
    - **Specifying the Experiment:**
        - The `--experiment-name` option can be used to define which experiment the run belongs to
        - Alternatively, the `MLFLOW_EXPERIMENT_NAME` environment variable can be set as a default
        - Example: `mlflow run --entry-point elastic_net -p alpha 0.5 -p l1_ratio 0.5 --experiment-name "Project exp 1"`

### MLflow CLI Execution Completion

- **Executing from the Project Directory**
    - When running `mlflow run` from within the project directory, you can use `.` as the project URI because MLflow automatically searches the current directory
    - Example: `mlflow run . --entry-point elastic_net -p alpha 0.5 -p l1_ratio 0.5 --experiment-name "Project exp 1"`
- **Troubleshooting:&#32;`chcp`&#32;Error**
    - If you encounter an error stating `chcp is not recognized as an internal or external command`, it can be resolved by setting the appropriate environment variable in your system
- **Verifying Results**
    - Successful runs will pass the specified parameters to the model (e.g., `alpha=0.5`, `l1_ratio=0.5`)
    - Metadata and artifacts are saved and can be inspected via the MLflow UI

### MLflow Projects API

- **The&#32;`run`&#32;Function**
    - The `mlflow.projects.run` function provides a way to execute an MLflow project programmatically within a script, rather than using the command line interface (CLI)
- **Parameter Comparison with CLI**
    - Most parameters used in the CLI `mlflow run` command are identical when using this function
- **The&#32;`synchronous`&#32;Parameter**
    - A boolean parameter that determines how the execution behaves
    - **Synchronous Execution (`synchronous=True`):**
        - The program waits for the operation to complete before proceeding
        - It blocks further execution until the current operation finishes
        - **Use Case:** Useful when immediate access to the results or errors of the run is required
    - **Asynchronous Execution (`synchronous=False`):**
        - The operation is initiated without waiting for it to complete
        - Allows for concurrent or parallel execution
        - **Use Case:** Beneficial for long-running operations where progress can be monitored separately

### MLflow Projects API Implementation

- **Synchronous vs. Asynchronous Behavior**
    - **`mlflow.projects.run`&#32;(API):**
        - Uses a `synchronous` parameter to control execution.
        - Defaults to `True`.
    - **`mlflow run`&#32;(CLI):**
        - Is synchronous by default.
        - Lacks a specific `synchronous` property but provides other customization options (e.g., skipping environment creation).
- **Programmatic Execution with Python**
    - To run a project within a Python script, you can define parameters and entry points directly in your code.
    - **Example Setup:**

```python
import mlflow

      parameters = {
          "alpha": 0.3,
          "l1_ratio": 0.3
      }
      experiment_name = "Project exo 1"
      entry_point = "Elasticnet"
```