# Azure MLOps Project — Status

Context doc for picking this back up later (a future session, or you after a
break). Written 2026-08-27, paused mid-Phase 4.

## What this project is

An end-to-end MLOps build on Azure: MLflow for tracking/versioning, Docker
for packaging, AKS (Kubernetes) for serving with real autoscaling, and
proper networking (VNet/subnets/NSGs) — the Azure equivalent of the
VM+ALB+ASG pattern in `../AWS.md` (from a different course), with no AWS
anywhere in the actual build. Full architecture/reasoning was worked out in
chat; the short version is in the table at the bottom of `../AWS.md`.

**File organization rule:** everything touched by this project — Terraform
config, Dockerfiles, training code, future AKS manifests/CI config — lives
under this `terraform/` folder, not split by infra-vs-app convention.

## Done so far

### Phase 1 — Networking (`main.tf`)
Resource group, VNet (`10.0.0.0/16`), 2 subnets (`10.0.1.0/24`,
`10.0.2.0/24`), NSG (ports 80/22 open), NSG-subnet associations. All in
**`centralus`** (not `eastus` — see gotcha below).

### Phase 2 — MLflow storage (`database.tf`, `storage.tf`)
- Postgres Flexible Server `psql-mlops` (Postgres 16, Burstable
  `B_Standard_B1ms`), database `mlflow`, firewall rule scoped to one IP —
  the backend store.
- Storage account (`stmlopsmekqrm`) + blob container `mlflow-artifacts` —
  the artifact store.
- Public access + IP-scoped firewall rules, not Private Endpoints (a
  deliberate simplification for now, flagged as a later upgrade once AKS
  exists to actually need VNet-internal access).

### Phase 3 — Tracking server (`mlflow-server/`)
- `Dockerfile`: mlflow==2.19.0 + psycopg2-binary + azure-storage-blob.
- `.env.example` / `.env` (gitignored) / `run.sh`: reproducible
  build+run, config via env vars, nothing baked into the image.
- **Currently running** locally in Docker (container name `mlflow-server`,
  port 5000) — check with `docker ps --filter name=mlflow-server`. If it's
  not running, restart with `./mlflow-server/run.sh` (needs `.env` —
  see `.env.example` for what's required and where each value comes from).

### Phase 4 — Training (`training/`), IN PROGRESS
- `train.py`: wine-quality ElasticNet (same dataset/model as the MLflow
  course), logs to the real tracking server, registers as model
  `wine-quality-elasticnet`.
- `requirements.txt` pinned to match the server's mlflow version exactly
  (2.19.0) — **important**: the ambient system Python had mlflow 3.15.2
  installed, which broke `log_model()` against the 2.19.0 server (a real
  client/server version mismatch bug we hit and fixed). Always run
  training via the dedicated venv:
  ```bash
  cd terraform/training
  python3.12 -m venv .venv   # if not already created
  .venv/bin/pip install -r requirements.txt
  export AZURE_STORAGE_CONNECTION_STRING="<see mlflow-server/.env>"
  .venv/bin/python train.py --alpha 0.5 --l1-ratio 0.5
  ```
- Verified end-to-end: run logged, model registered (version 1), full
  `MLmodel` artifact directory confirmed present in Blob Storage.
- **STOPPED HERE**: about to design the serving API (Flask/Gunicorn,
  mirroring `AWS.md`'s pattern) that loads this registered model and
  exposes `/predict`. Open decision not yet made: should the serving
  container load the model from the Model Registry at startup (via
  `models:/wine-quality-elasticnet/1`, requires the MLflow server
  reachable at runtime), or bake the model file into the image at build
  time (no runtime dependency on the server, but rebuild-to-update)? —
  ask the user this before writing the serving code.

## Next steps (in order)

1. Decide + build the serving API + Dockerfile for the trained model
   (the open question above).
2. AKS cluster (the actual Kubernetes piece) — node pools, connect to the
   Phase 1 VNet/subnets.
3. Push the serving image to ACR (Azure Container Registry — not created
   yet).
4. Deploy to AKS: Deployment + Service + Ingress (AGIC or NGINX), with
   real readiness/liveness probes this time (`AWS.md`'s own health check
   was broken — a gap to actually fix here).
5. Autoscaling: HPA (pods) + Cluster Autoscaler (nodes) — the two-layer
   Azure equivalent of AWS's single-layer ASG.
6. CI/CD (GitHub Actions or Azure DevOps).
7. Monitoring (Azure Monitor / Container Insights).
8. Upgrade Postgres/Storage from public+firewall to Private Endpoints
   (explicitly deferred from Phase 2).

## Known gotchas (don't rediscover these)

- **Region restriction**: this Azure subscription (10pearls work tenant)
  silently blocks Postgres Flexible Server provisioning in `eastus` and
  several other regions. `centralus` is confirmed unrestricted. Check with
  `az postgres flexible-server list-skus --location <region>` before
  trying a new region for anything.
- **Terraform "no-op" trap**: when a parent resource (e.g. resource group)
  is replaced, child resources whose own arguments didn't change (e.g.
  subnets) can show as `no-op` in the plan even though the real Azure
  object was cascade-deleted — leading to stale state. If ever changing
  `location` or another resource-group-forcing value again, prefer a full
  `terraform destroy` + fresh `apply` over trusting the diff.
- **MLflow client/server version pinning**: always match the training
  environment's mlflow version to whatever's pinned in
  `mlflow-server/Dockerfile`. Check both before debugging a weird 404 from
  the tracking server.
- **Non-proxied artifact access**: any client that calls
  `mlflow.log_artifact()`/`log_model()` needs its own
  `azure-storage-blob` install AND its own `AZURE_STORAGE_CONNECTION_STRING`
  — the server's credentials don't cover the client's direct writes to
  Blob Storage.
- **Secrets**: Postgres admin password and the storage account key are
  NOT stored in any git-tracked file. They exist in
  `terraform/mlflow-server/.env` (gitignored) and in this chat's history.
  If you need them again and don't have `.env` handy:
  `az storage account keys list --resource-group rg-mlops --account-name stmlopsmekqrm --query "[0].value" -o tsv`
  (Postgres password: you'll need to reset it via `az postgres flexible-server update`
  if genuinely lost, since Azure doesn't let you retrieve it after the fact.)

## Cost note

Real resources are running right now and cost real (small) money while
they exist: primarily the Postgres Flexible Server (~$12-15/month). If
pausing this project for an extended period, consider
`terraform destroy` in `terraform/` to stop the charges, and re-`apply`
when resuming (everything is captured in code, so this is fully
reproducible — just re-run training afterward since the registered model
would also be destroyed along with the database).

## Git status as of pause

Two commits made locally but **not yet pushed** to `origin/main` due to a
persistent network-level TLS reset when reaching github.com from this
machine (not an auth or git problem — `curl` to github.com fails the same
way). Retry `git push origin main` when networking is back; nothing needs
to change about the commits themselves.
