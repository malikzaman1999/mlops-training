# Tracing a Kubernetes Pod Failure (MLflow / kind)

Commands used to diagnose why the MLflow pod stayed in `Init:0/1` / restart loop, and what each one does. After every step: **what we found**.

## Mental model

1. `get pods` → something’s wrong (`Init`, restarts)
2. `describe` → events / which container
3. `logs -c <init>` → exact error
4. `helm get values` + ConfigMap/Secret → confirm misconfigured host/DB/user/SSL

---

### Step 1 — Point kubectl at the right cluster and list pods

```bash
kubectl config use-context kind-mlflow
```

Switches kubectl to the `kind-mlflow` cluster so later commands hit the right place.

```bash
kubectl get pods -n mlflow -o wide
```

Lists pods in the `mlflow` namespace, with status/restarts and node/IP (`-o wide`).

**What we found:** Pod `mlflow-…` was `0/1` with status `Init:0/1` and restart count climbing. So it never finished initializing — the main MLflow container had not started yet. Problem is in an **init container**, not the main app yet.

---

### Step 2 — Describe the pod (events + which container fails)

```bash
kubectl describe pod -n mlflow -l app.kubernetes.io/name=mlflow
```

Shows full pod details: containers, env, volumes, conditions, and **Events** (pulls, crashes, backoff). Best first deep-dive after `get pods`.

**What we found:**

- Init container name: `mlflow-db-migration`
- Last state: `Terminated`, `Reason: Error`, **exit code 1**
- Events: `Back-off restarting failed container mlflow-db-migration`
- Main container `mlflow` was `Waiting` / `PodInitializing` (blocked until init succeeds)

So DB migration/init is crashing in a loop; main MLflow never gets to run.

---

### Step 3 — Read init container logs (the smoking gun)

```bash
kubectl logs -n mlflow -l app.kubernetes.io/name=mlflow -c mlflow-db-migration --tail=100
```

Prints the last 100 log lines from the **init container** `mlflow-db-migration`.

```bash
kubectl logs -n mlflow -l app.kubernetes.io/name=mlflow --all-containers --tail=100
```

Same idea, but for **every** container in matching pods (init + main). Useful when you’re not sure which container is failing.

**What we found (exact errors):**

```text
FATAL: PAM authentication failed for user "mlflow_user"
FATAL: pg_hba.conf rejects connection ... no encryption
```

Meaning:

1. Auth to AWS RDS failed for `mlflow_user` (password / IAM / PAM issue)
2. Connection without SSL was rejected (`sslmode=require` needed)
3. Network could reach RDS (host resolved; not a DNS/firewall “unreachable”) — auth + encryption were the blockers

---

### Step 4 — Confirm init container names and runtime state

```bash
kubectl get pod -n mlflow -l app.kubernetes.io/name=mlflow \
  -o jsonpath='{range .items[0].spec.initContainers[*]}{.name}{"\n"}{end}'
```

Lists init container **names** from the pod spec (so you know what to pass to `-c`).

```bash
kubectl get pod -n mlflow -l app.kubernetes.io/name=mlflow \
  -o jsonpath='{range .items[0].status.initContainerStatuses[*]}{.name}{": "}{.state}{"\n"}{end}'
```

Shows each init container’s **runtime state** (running / waiting / terminated + exit code).

**What we found:** Only one init container, `mlflow-db-migration`, alternating between `running` and terminated with error — matches the CrashLoop/Init backoff. Confirmed we were logging the right container.

---

### Step 5 — Check what Helm / env actually deployed

```bash
helm get values mlflow -n mlflow
```

Shows the values you set on the Helm release (host, DB name, user, flags like `databaseMigration`).

```bash
kubectl get cm mlflow-env-configmap -n mlflow -o yaml
```

Dumps the ConfigMap env (e.g. `PGHOST`, `PGDATABASE`, `PGPORT`) the pod actually uses.

```bash
kubectl get secret mlflow-env-secret -n mlflow -o jsonpath='{.data}'
```

Lists secret **keys** (base64 values). Confirms credentials exist without needing to decode them in the terminal.

**What we found:**

- Helm had `backendStore.postgres.enabled=true` pointing at RDS host  
  `mlflow-instance-1….rds.amazonaws.com`
- ConfigMap `PGHOST` / `PGDATABASE` / `PGPORT` matched that external RDS setup
- Secret had `PGUSER` / `PGPASSWORD` keys present
- Chart default Postgres URI had **no** `sslmode=require`
- Later: DB name in Helm (`mlflow`) also didn’t match what was created in RDS (`mlflow2`); password login to RDS kept failing with PAM even after grants — so for local kind we abandoned RDS

**Resolution used for local kind:**

```bash
helm upgrade mlflow community-charts/mlflow -n mlflow \
  --set backendStore.databaseMigration=true \
  --set backendStore.postgres.enabled=false \
  --set postgresql.enabled=true
```

Then pods became healthy with in-cluster Bitnami Postgres (`PGHOST: mlflow-postgresql`).

---

### Outcome (pod init failure)

| Step | Finding |
|---|---|
| 1. `get pods` | Stuck in `Init:0/1`, restarts |
| 2. `describe` | Init `mlflow-db-migration` exit code 1; main waiting |
| 3. `logs -c …` | RDS PAM auth fail + SSL required |
| 4. init status jsonpath | Confirmed only that init container failing |
| 5. Helm / ConfigMap | External RDS wired in; no SSL in URI; DB naming/auth mismatch |

---

## Experiment created in Python but missing in MLflow UI

Symptom: `python3 connect-mlflow.py` logged that it created `my-first-experiment`, but the experiment did not appear at `http://localhost:7006`.

### Mental model

1. Confirm **what process owns port 7006** (which pod/cluster is behind the UI)
2. List MLflow pods across **all kubectl contexts** (easy to look at the wrong cluster)
3. Call the MLflow **HTTP API** on that port (see what the server actually has / if DB is healthy)
4. Point the port-forward at the **healthy** release, then re-run the client script

---

### Step 1 — See what is listening on 7006

```bash
ss -tlnp | grep 7006
```

| Piece | What it does |
|---|---|
| `ss` | Socket statistics — shows network sockets (who is listening/connected). Modern replacement for `netstat`. |
| `-t` | TCP sockets only |
| `-l` | Listening sockets only (servers waiting for connections) |
| `-n` | Numeric — show port numbers (e.g. `7006`) instead of service names |
| `-p` | Show the **process** that owns the socket (e.g. `kubectl`, pid) |
| `\|` | Pipe — send `ss` output as input to the next command |
| `grep 7006` | Filter lines: keep only those containing the text `7006` |

```bash
ps aux | grep 'port-forward' | grep -v grep
```

| Piece | What it does |
|---|---|
| `ps` | List running processes |
| `a` | All users’ processes (not only yours in this TTY) |
| `u` | User-oriented format (user, CPU, MEM, command, …) |
| `x` | Include processes not attached to a terminal |
| `grep 'port-forward'` | Keep lines whose command contains `port-forward` |
| `grep -v grep` | `-v` = invert match — drop the `grep` process itself from the results |

Port-forward syntax reminder: `HOST_PORT:CONTAINER_OR_SERVICE_PORT` → e.g. local `7006` maps to target `5000` or `80`.

**What we found:** Port 7006 was owned by a **stale** forward:

```text
kubectl port-forward pod/my-mlflow-586475db6-knln7 7006:5000 --address 0.0.0.0
```

That is the **old** `my-mlflow` pod (first install), not the new Helm release `mlflow` in namespace `mlflow`. So the browser and `connect-mlflow.py` were talking to the wrong MLflow instance.

---

### Step 2 — Find MLflow pods on every context

```bash
kubectl config get-contexts
```

Lists all kubeconfig contexts (cluster + user + optional namespace). `*` marks the current one.

```bash
kubectl config current-context
```

Prints only the active context name (quick check).

```bash
for ctx in $(kubectl config get-contexts -o name); do
  echo "===== $ctx ====="
  kubectl --context="$ctx" get pods -A | grep -i mlflow || echo '(no mlflow pods)'
done
```

| Piece | What it does |
|---|---|
| `for ctx in …; do …; done` | Bash loop — run the body once per context name |
| `$(…)` | Command substitution — run inner command, use its output as the list |
| `kubectl config get-contexts -o name` | `-o name` = print only context names (one per line), easy to loop |
| `echo "===== $ctx ====="` | Print a header so you know which cluster the next lines belong to |
| `kubectl --context="$ctx"` | Talk to that cluster **without** switching your default context |
| `get pods` | List pods |
| `-A` | All namespaces (`--all-namespaces`) |
| `grep -i mlflow` | `-i` = case-insensitive filter for lines containing `mlflow` |
| `\|\| echo '…'` | If `grep` finds nothing (exit code ≠ 0), print the fallback message |

**What we found:** Two separate MLflow installs:

| Context | What was running |
|---|---|
| `kind-basic-ml-flow` | `my-mlflow-…` in `default` (old, SQLite) ← behind `:7006` |
| `kind-mlflow` | `mlflow-…` + `mlflow-postgresql-0` in `mlflow` (new, Postgres) ← healthy |

Also: if current context is `kind-basic-ml-flow`, then `kubectl get pods -n mlflow` shows nothing even though the healthy stack exists on `kind-mlflow`. Wrong context ≠ deleted pods.

---

### Step 3 — Ask the tracking server what experiments it has

```bash
curl -sS "http://127.0.0.1:7006/api/2.0/mlflow/experiments/search" \
  -H 'Content-Type: application/json' \
  -d '{"max_results":25}' | python3 -m json.tool
```

| Piece | What it does |
|---|---|
| `curl` | HTTP client — call the MLflow REST API directly (same backend the UI uses) |
| `-s` | Silent — hide progress meter |
| `-S` | With `-s`, still show errors if the request fails |
| `http://127.0.0.1:7006/...` | Hit whatever is behind local port 7006 (the active port-forward) |
| `-H 'Content-Type: …'` | Set request header (JSON body) |
| `-d '{…}'` | Request body / data (`max_results` required by this API) |
| `\` | Line continuation — command continues on the next line |
| `python3 -m json.tool` | Pretty-print JSON so the response is readable |

```bash
curl -sS "http://127.0.0.1:7006/api/2.0/mlflow/experiments/create" \
  -H 'Content-Type: application/json' \
  -d '{"name":"my-first-experiment"}' | python3 -m json.tool
```

Same pattern, but **creates** an experiment via API.

Optional local check (in case the client wrote to a file store instead of the server):

```bash
find . -maxdepth 3 -type d -name 'mlruns'
```

| Piece | What it does |
|---|---|
| `find .` | Search starting from the current directory |
| `-maxdepth 3` | Don’t recurse deeper than 3 directory levels |
| `-type d` | Only directories |
| `-name 'mlruns'` | Exact directory name `mlruns` (MLflow local artifact/experiment store) |

**What we found:**

- Search on `:7006` did **not** show a stable `my-first-experiment` (UI wasn’t lying — that backend didn’t have it reliably)
- Create via API failed with:  
  `sqlite3.OperationalError: no such table: experiments`
- No useful local `mlruns` tree explaining a hidden file-store experiment

So the old SQLite-backed MLflow behind `:7006` was **broken**. Python could still print “Creating a new experiment” against a bad/wrong server while the UI had nothing good to display.

---

### Step 4 — Fix: port-forward the healthy MLflow, then retry

Stop the old forward: `Ctrl+C` in that terminal, or:

```bash
kill 1853109
```

| Piece | What it does |
|---|---|
| `kill <pid>` | Send SIGTERM to that process (graceful stop). Pid comes from `ss -p` / `ps`. |

```bash
kubectl config use-context kind-mlflow
```

Makes `kind-mlflow` the default context for following kubectl commands.

```bash
kubectl -n mlflow port-forward svc/mlflow 7006:80 --address 0.0.0.0
```

| Piece | What it does |
|---|---|
| `-n mlflow` | Namespace containing the release |
| `port-forward` | Tunnel a local port to something in the cluster |
| `svc/mlflow` | Target the **Service** named `mlflow` (stable; better than a pod name that changes on restart) |
| `7006:80` | Local port `7006` → **Service** port `80` (Service then routes to pod container port `5000`) |
| `--address 0.0.0.0` | Listen on all interfaces (not only `127.0.0.1`); needed if other machines/devices hit your host |

**Why `80` not `5000`?** Pod listens on `5000`; Service exposes `80` and forwards to `5000`.  
`port-forward svc/...` uses the **Service** port (`80`).  
`port-forward pod/...` uses the **container** port (`5000`). Prefer Service for day-to-day.

Keep that process running.

```bash
python3 connect-mlflow.py
```

Client script (for reference):

```python
import mlflow

mlflow.set_tracking_uri("http://localhost:7006")  # not set_tracking_url
mlflow.set_experiment("my-first-experiment")
```

| Piece | What it does |
|---|---|
| `set_tracking_uri(...)` | Tell the MLflow client which tracking server to use |
| `set_experiment(...)` | Select or create a named experiment on that server |

**What we found after the fix:**

- `:7006` now tunnels to healthy `svc/mlflow` on `kind-mlflow` (Postgres-backed)
- Re-running `connect-mlflow.py` creates the experiment on the correct server
- Refreshing `http://127.0.0.1:7006` shows **my-first-experiment**

---

### Outcome (UI / tracking mismatch)

| Step | Finding |
|---|---|
| 1. `ss` / `ps` | `:7006` still mapped to old `my-mlflow` pod |
| 2. contexts loop | Healthy MLflow on `kind-mlflow` / namespace `mlflow`; old one on `kind-basic-ml-flow` |
| 3. MLflow REST API | Old server SQLite missing `experiments` table / experiment not present |
| 4. New port-forward + script | Experiment appears in UI on the healthy release |

**Resolution:** kill the stale port-forward, forward `svc/mlflow` on `kind-mlflow` / namespace `mlflow`, re-run `connect-mlflow.py`, refresh the UI.

---

## How to check Services (kind-mlflow)

A **Service** is a stable network front door in front of pods. Pods change name/IP on restart; the Service name and port stay the same.

### List services

```bash
# all namespaces on the current context
kubectl get svc -A

# only the mlflow namespace on kind-mlflow (even if another context is current)
kubectl --context=kind-mlflow -n mlflow get svc -o wide
```

| Piece | What it does |
|---|---|
| `get svc` | List Services (`svc` = short for `services`) |
| `-A` | All namespaces |
| `-o wide` | Extra columns (e.g. selector) |
| `--context=kind-mlflow` | Query that cluster without switching default context |

### Which Service is the MLflow UI/API?

On **`kind-mlflow`**, namespace **`mlflow`**:

| Field | Value |
|---|---|
| Name | `mlflow` |
| Type | `ClusterIP` |
| Service port | **80** |
| Forwards to (pod) | container port **5000** (seen via Endpoints) |

Confirm:

```bash
kubectl --context=kind-mlflow -n mlflow get svc mlflow
kubectl --context=kind-mlflow -n mlflow get endpoints mlflow
```

Example from this cluster:

```text
NAME     TYPE        CLUSTER-IP      PORT(S)
mlflow   ClusterIP   10.96.234.218   80/TCP

NAME     ENDPOINTS
mlflow   10.244.0.7:5000
```

So: clients hit **Service `:80`** → Kubernetes routes to **Pod `:5000`** (where `mlflow server --port=5000` listens).

### Related services in namespace `mlflow`

| Service | Port | Role |
|---|---|---|
| `mlflow` | **80** → pod **5000** | MLflow UI / tracking API |
| `mlflow-postgresql` | **5432** | In-cluster Postgres for MLflow |
| `mlflow-postgresql-hl` | **5432** | Postgres headless Service (StatefulSet) |

### Port-forward from your laptop

```bash
# prefer Service (stable name + Service port 80)
kubectl --context=kind-mlflow -n mlflow port-forward svc/mlflow 7006:80 --address 0.0.0.0

# equivalent, but tied to one pod name (container port 5000)
kubectl --context=kind-mlflow -n mlflow port-forward pod/<pod-name> 7006:5000 --address 0.0.0.0
```

Then open `http://127.0.0.1:7006`.

**Prefer `svc/mlflow` + `80`** for daily use. Use `pod/…` + `5000` only when debugging that exact pod.

---

## Quick flag / tool glossary

| Piece | What it does |
|---|---|
| `kubectl` | Kubernetes CLI — talk to the API server for the current (or `--context`) cluster |
| `-n <ns>` / `--namespace` | Scope the command to one namespace |
| `-l key=value` | Label selector — only resources with that label |
| `-o wide` | Extra columns (e.g. node, pod IP) |
| `-o yaml` | Full object as YAML |
| `-o jsonpath='…'` | Pull specific fields from the JSON API response |
| `-c <container>` | Choose which container in a multi-container pod (`logs` / `exec`) |
| `--tail=100` | Only the last N log lines |
| `--all-containers` | Logs from every container in the pod |
| `helm get values <release>` | Show values used for an installed Helm release |
| `kubectl describe …` | Human-readable detail + **Events** (scheduling, pulls, crashes) |
| `kubectl logs …` | stdout/stderr from a container |
| Service port vs pod port | Service (here `80`) is the stable front door; pod/container (here `5000`) is where the process listens |
