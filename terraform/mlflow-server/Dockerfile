# ==============================================================================
# mlflow-server/Dockerfile
#
# Builds a container image that runs the MLflow TRACKING SERVER process
# itself (`mlflow server ...`) -- NOT a container for training a model, and
# NOT the model-serving container we'll build in a later phase. This is
# purely the "always-on service that receives log_param/log_metric/
# log_model calls and stores them" role -- the same role `mlflow server
# --backend-store-uri sqlite:///mlflow.db ...` played on your local machine
# in the MLflow course notes, just packaged to run anywhere Docker runs
# (today: this machine; later: an AKS pod, once that phase exists).
#
# Deliberately talks to the Postgres + Blob Storage we created in Phase 2
# via environment variables passed in at `docker run` time -- NOTHING
# secret is baked into this image. Anyone could read this Dockerfile and
# learn nothing about your actual credentials.
# ==============================================================================

FROM python:3.11-slim

# Three packages, each with a distinct job:
#   mlflow            -- the tracking server itself (the `mlflow` CLI/package)
#   psycopg2-binary    -- the PostgreSQL DRIVER. mlflow's --backend-store-uri
#                         speaks "postgresql://..." at a high level, but
#                         something has to actually know how to talk the
#                         real Postgres wire protocol underneath -- that's
#                         psycopg2. Without it, mlflow can parse a
#                         postgresql:// URI but can't actually connect.
#                         (the "-binary" variant ships precompiled, so we
#                         don't need a C compiler in this image just to
#                         install it.)
#   azure-storage-blob -- same idea for the artifact store: this is the
#                         library mlflow uses under the hood to actually
#                         read/write blobs when --default-artifact-root is
#                         a wasbs://... (Azure Blob) URI, the Azure
#                         equivalent of needing `boto3` for an s3:// URI.
RUN pip install --no-cache-dir \
    mlflow==2.19.0 \
    psycopg2-binary==2.9.10 \
    azure-storage-blob==12.24.0

# The port the MLflow UI/API listens on -- matches the course notes'
# convention (`mlflow server ... --port 5000`). EXPOSE is documentation for
# humans/tooling reading this Dockerfile; it doesn't by itself publish the
# port -- that happens via `docker run -p`.
EXPOSE 5000

# Notice there is NO hardcoded --backend-store-uri or --default-artifact-root
# here. Instead, this reads them from environment variables
# ($BACKEND_STORE_URI, $ARTIFACT_ROOT) that get supplied at `docker run`
# time (see the run command in this project's notes/chat history) -- this
# is what makes the SAME image usable against different Postgres/Storage
# targets (e.g. a "dev" vs "prod" backend) without ever rebuilding it.
#
# The "sh -c '...'" form is required (rather than the plain exec-form
# CMD ["mlflow", "server", ...]) specifically because exec-form CMD does
# NOT perform shell environment-variable substitution -- "$BACKEND_STORE_URI"
# would be passed to mlflow literally, as the four characters
# "$BACKEND_STORE_URI", instead of being replaced with its value. Wrapping
# it in `sh -c "..."` forces a real shell to interpret the string first,
# which does perform that substitution, before mlflow ever sees the result.
CMD ["sh", "-c", "mlflow server --backend-store-uri \"$BACKEND_STORE_URI\" --default-artifact-root \"$ARTIFACT_ROOT\" --host 0.0.0.0 --port 5000"]
