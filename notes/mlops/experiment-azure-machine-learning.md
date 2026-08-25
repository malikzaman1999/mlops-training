# Experiment with Azure Machine Learning

Source: https://learn.microsoft.com/en-us/training/modules/experiment-azure-machine-learning/

## Module snapshot

- Type: Microsoft Learn module
- Level: Beginner
- Role focus: Data Scientist
- Platform: Azure Machine Learning
- Units: 10

## What this module covers

This module explains how to use Azure Machine Learning to find a strong model
through a mix of automated experimentation, notebook-based tracking, and
Responsible AI evaluation.

The workflow centers on three ideas:

- use AutoML to quickly train and compare classification models
- track notebook experiments with MLflow
- evaluate trained models with the Responsible AI dashboard

## Learning objectives

After completing the module, you should be able to:

- prepare data for AutoML classification
- configure and run an AutoML experiment
- compare and evaluate AutoML models
- configure MLflow for tracking in notebooks
- log and track training runs with MLflow
- evaluate a model with the Responsible AI dashboard

## Prerequisites

- None listed by the module

## Unit outline

1. Introduction
1. Preprocess data and configure featurization
1. Run an automated machine learning experiment
1. Evaluate and compare models
1. Configure MLflow for model tracking in notebooks
1. Train and track models in notebooks
1. Evaluate models with the Responsible AI dashboard
1. Exercise: Find the best classification model with Azure Machine Learning
1. Module assessment
1. Summary

## Key takeaways

- AutoML reduces the manual work of trying many model and featurization
  combinations.
- Good data preparation still matters before launching an experiment.
- MLflow helps make notebook-based training reproducible and easier to compare.
- Responsible AI tools add a post-training evaluation layer for model behavior
  and interpretability.

## Study notes

- Use AutoML when you want a fast baseline and systematic model comparison.
- Use notebook tracking when you need more control over code, data, and custom
  training logic.
- Use Responsible AI review before treating a model as ready for broader use.

## Unit 2 - Preprocess data and configure featurization

Source: https://learn.microsoft.com/en-us/training/modules/experiment-azure-machine-learning/2-preprocess-data-configure-featurization

Before running AutoML, the training data needs to be prepared as an Azure
Machine Learning data asset, specifically an `MLTable` asset that includes the
schema AutoML uses to read the dataset.

In practice, this means:

- a data asset is a reusable reference to your dataset inside Azure ML
- the `MLTable` file tells Azure ML how to read the data correctly
- the schema describes the columns, types, and layout of the dataset
- AutoML needs that structure so it can load and preprocess the data properly

If your data is stored in a folder, you place an `MLTable` file in that same
folder. Azure ML uses that file when it registers the folder as a data asset,
and you can then pass that asset into an experiment as the training input.

The code snippet shown in the module creates an `Input` object that points to
the registered MLTable asset:

- `Input(...)` marks the dataset as an experiment input
- `type=AssetTypes.MLTABLE` says the input is an MLTable asset
- `path="azureml:input-data-automl:1"` refers to the registered dataset name
  and version in Azure ML

### Core ideas

- AutoML expects training data as input only.
- `MLTable` is the data asset format used here.
- Preprocessing can happen automatically before model training.

### What AutoML can do for you

- scale and normalize numeric features
- impute missing values
- encode categorical variables
- drop high-cardinality features like record IDs
- derive new features from datetime fields

### Important behavior

- Featurization is enabled by default.
- You can disable featurization if you want raw features only.
- You can also customize featurization, including imputation behavior for
  specific features.
- After the run, AutoML reports which scaling and normalization methods it
  applied and flags issues such as missing values or class imbalance.

## MLTable guide

Source: https://learn.microsoft.com/en-us/azure/machine-learning/how-to-mltable?view=azureml-api-2&tabs=cli

`mltable` is the Azure Machine Learning table format for describing how tabular
or path-based data should be loaded. It is not just a file format; it is a
reproducible loading blueprint that tells Azure ML how to turn files and paths
into a Pandas or Spark dataframe.

### What MLTable is for

- define how data should be read instead of hard-coding parsing logic in Python
- keep loading steps reproducible and shareable
- version a dataset together with its read logic
- support AutoML and notebook-based workflows
- load tabular data, partitioned data, images, and Delta Lake data

### When to use MLTable

Use `mltable` when:

- you need to read from multiple files, folders, or glob patterns
- the storage path contains useful information you want to extract as columns
- the schema changes often and you want the reading logic to stay maintainable
- you want a reusable blueprint that the team can share
- you want AutoML to consume the data directly
- you need to stream paths, such as image locations, instead of loading raw file
  contents immediately

For very simple CSV or Parquet data, Azure ML files or folders may be enough if
you are comfortable writing your own parsing code.

### Prerequisites

- Azure subscription
- Azure Machine Learning workspace
- Azure Machine Learning SDK for Python
- latest `mltable` package installed

Typical installation:

```bash
pip install -U mltable azureml-dataprep[pandas]
```

### Supported source types

`mltable` can be built from:

- delimited text files such as CSV
- Parquet files
- JSON Lines files
- Delta Lake tables
- paths only, which is useful when you want a table of file locations, such as
  image paths

### Supported locations

An MLTable definition can read from:

- a local path
- a public `https` URL
- Azure Storage paths such as `wasbs://` or `abfss://`
- Azure Machine Learning datastore paths using the long-form `azureml://`
  syntax

If you do not have permission to the underlying storage, `mltable` will not be
able to access the data.

### What an MLTable file describes

An `MLTable` file is a YAML-based blueprint. It can describe:

- where the data lives
- file or folder patterns to read
- file format details such as delimiter, header behavior, or encoding
- column type conversions to enforce schema
- transformations such as filtering rows or dropping columns
- derived columns from folder structure or partition layout
- random sampling or subsetting

### Core transformations

The article highlights these common transformations:

- `from_delimited_files`, `from_parquet_files`, `from_json_lines_files`,
  `from_delta_lake`, and `from_paths`
- `filter(...)` to keep rows that match a condition
- `drop_columns(...)` to remove unnecessary fields
- `convert_column_types(...)` to enforce data types
- `extract_columns_from_partition_format(...)` to build columns from path
  structure
- `take_random_sample(...)` to reduce a large dataset

### Authoring pattern

A typical workflow is:

1. define the data locations
2. build an `mltable` object
3. apply filters, drops, type conversions, or derived columns
4. inspect a few rows with `show()`
5. optionally convert to Pandas with `to_pandas_dataframe()`
6. save the loading logic with `save()`

Example pattern:

```python
import mltable

paths = [{"file": "<supported_path>"}]
tbl = mltable.from_delimited_files(paths=paths)
tbl = tbl.filter("col('Age') > 0")
tbl = tbl.drop_columns(["PassengerId"])
tbl.show(5)
```

### Save and reuse

Once the loading logic works, save it into an MLTable folder. This preserves
the blueprint so you can load the same table later without rewriting the
transformation code.

You can then reload it with `mltable.load("./your-folder/")` or point Azure ML
to the saved artifact through a data asset.

### Create a data asset

Saving the table locally is useful for development, but sharing is easier when
you register it as a data asset in Azure ML.

Why that matters:

- the MLTable is uploaded and bookmarked in cloud storage
- the asset gets a friendly name
- the asset is versioned
- teammates can reference the same dataset consistently

Conceptually, the workflow is:

1. save the MLTable folder
2. register it as a `Data` asset with type `mltable` using either CLI or the
   Python SDK
3. retrieve it later by name and version
4. load it with `mltable.load(f"azureml:/{data_asset.id}")`

The article shows the CLI form as:

```bash
az ml data create --name <name> --version <version> --path ./<mltable-folder> --type mltable
```

### Use in a notebook

In interactive work, you can fetch the data asset by name and version through
`MLClient`, then load it into `mltable` and convert it to Pandas when needed.

### Use in a job

In a training script, pass the MLTable path as a command-line argument and load
it inside the job with `mltable.load(args.input)`.

That keeps the training code independent from the exact storage location.

### Delta Lake note

Delta Lake tables are handled differently from ordinary files:

- the path points to the table directory that contains `_delta_log`
- time travel is supported through `timestamp_as_of`
- the current version can be loaded by passing the current timestamp

Limitation:

- partition key extraction with `extract_columns_from_partition_format` does not
  work for Delta Lake reads through `mltable`

### Image-path pattern

`mltable` can also create a table of file paths, which is useful for image
datasets. In that pattern, the table stores the path to each image and can
derive labels from the directory structure.

### Practical guidance

- Use `mltable` when you want a single, reusable definition of how to read
  your data.
- Use file or folder inputs when the data is simple and the parsing logic is
  trivial.
- Make sure your storage permissions are set correctly before trying to load
  the data.
- Prefer saving the table and registering it as a data asset if you need team
  sharing or repeatable experiments.

## Next actions

- Recreate the module flow in a small local notebook example.
- Add a sample classification dataset and compare a few models.
- Record runs with MLflow and inspect the logged metrics and artifacts.
