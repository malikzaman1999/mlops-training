# Deploy Intent Classifier on VMs (AWS VPC + ASG + ALB) — CLI Steps

This guide deploys the Intent Classifier model on AWS using EC2 instances in an Auto Scaling Group (ASG) behind an Application Load Balancer (ALB).

**Traffic path:**

```
Internet -> ALB -> Target Group -> ASG EC2 -> Nginx -> Gunicorn -> Flask (wsgi.py) -> Model
```

The commands run in dependency order: network first, then firewall, then the instance blueprint, then load balancing, then scaling. Each step below explains **what** the command does and **why** it is needed.

---

### 1. Find a recent Ubuntu AMI for your region

**What it does:** Asks AWS for official Ubuntu images and returns the newest AMI ID in your region.

**Why it is needed:** Every EC2 instance boots from an AMI. Without an AMI ID you cannot build a launch template, so the ASG would have nothing to launch.

```
aws ec2 describe-images \
--owners 099720109477 \
--filters "Name=name,Values=ubuntu/images/hvm-ssd/ubuntu-focal-20.04-amd64-server-*" "Name=state,Values=available" \
--query 'Images | sort_by(@, &CreationDate)[-1].ImageId' --output text --region $AWS_REGION
```

Save the result as `AMI_ID`.

| Flag | Why it is there |
|------|-----------------|
| `--owners 099720109477` | Canonical's account ID, so you only get official Ubuntu images and not community copies |
| `--filters ...` | Narrows to the Ubuntu release/architecture you want, and only images in `available` state |
| `--query '...[-1].ImageId'` | Sorts by creation date and returns only the newest image ID |
| `--output text` | Plain output that can be saved straight into a shell variable |

Docs: [describe-images](https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-images.html) · [Finding Ubuntu AMIs](https://documentation.ubuntu.com/aws/en/latest/aws-how-to/instances/find-ubuntu-images/)

---

### 2. Create a VPC, public subnets (multi-AZ), and Internet Gateway

**What this section does:** Builds a private network, splits it across two Availability Zones, gives it internet access, and configures routing.

**Why it is needed:** An ALB requires at least two subnets in different AZs. Public routing is required so an internet-facing ALB can be reached, and so instances can install packages and clone the repo while booting.

#### 2.1 Create the VPC

**What:** Creates an isolated virtual network with CIDR `10.10.0.0/16`.

**Why:** The VPC is the network boundary that every later resource (subnets, security group, ALB, EC2) lives inside. Nothing else can be created without it.

```
aws ec2 create-vpc --cidr-block 10.10.0.0/16 --query 'Vpc.VpcId' --output text --region $AWS_REGION
```

Save as `VPC_ID`.

#### 2.2 Create two public subnets in different AZs

**What:** Carves two `/24` slices out of the VPC range, one in `${AWS_REGION}a` and one in `${AWS_REGION}b`.

**Why:** A subnet is what pins a resource to a specific Availability Zone. Two AZs are mandatory for an ALB and give high availability — if one AZ has problems, the other still serves traffic.

```
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.10.1.0/24 --availability-zone ${AWS_REGION}a --query 'Subnet.SubnetId' --output text --region $AWS_REGION
```

Save as `SUBNET_ID1`.

```
aws ec2 create-subnet --vpc-id $VPC_ID --cidr-block 10.10.2.0/24 --availability-zone ${AWS_REGION}b --query 'Subnet.SubnetId' --output text --region $AWS_REGION
```

Save as `SUBNET_ID2`.

#### 2.3 Create and attach an Internet Gateway

**What:** Creates an IGW and attaches it to the VPC.

**Why:** A VPC on its own is completely isolated. The IGW is the door between the VPC and the public internet. Without it, an internet-facing ALB gets no traffic, and `apt install` / `git clone` inside `userdata.sh` would fail.

```
aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text --region $AWS_REGION
```

Save as `IGW_ID`.

```
aws ec2 attach-internet-gateway --internet-gateway-id $IGW_ID --vpc-id $VPC_ID --region $AWS_REGION
```

#### 2.4 Create a route table, add the default route, associate both subnets

**What:** Creates a route table, adds `0.0.0.0/0 -> IGW`, and associates that table with both subnets.

**Why:** Routing is decided per **subnet**, not per VPC. Attaching the IGW is not enough on its own — each subnet must be told to send unknown/internet-bound traffic to the IGW. The association is what actually turns these into public subnets.

```
aws ec2 create-route-table --vpc-id $VPC_ID --query 'RouteTable.RouteTableId' --output text --region $AWS_REGION
```

Save as `RTB_ID`.

```
aws ec2 create-route --route-table-id $RTB_ID --destination-cidr-block 0.0.0.0/0 --gateway-id $IGW_ID --region $AWS_REGION
```

```
aws ec2 associate-route-table --route-table-id $RTB_ID --subnet-id $SUBNET_ID1 --region $AWS_REGION
aws ec2 associate-route-table --route-table-id $RTB_ID --subnet-id $SUBNET_ID2 --region $AWS_REGION
```

Without the association the subnet still exists and instances still launch, but they have no path to the internet, so package installs and `git clone` fail.

#### 2.5 (Optional) Auto-assign public IPs

**What:** Instances launched in these subnets automatically get a public IP.

**Why:** Convenient for SSH debugging. It is not required for normal traffic, because the ALB has its own public addresses and reaches instances over private IPs.

```
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_ID1 --map-public-ip-on-launch
aws ec2 modify-subnet-attribute --subnet-id $SUBNET_ID2 --map-public-ip-on-launch
```

**Important distinction:** attaching an IGW to the VPC does not by itself make a subnet public. A subnet is effectively public only when it has a route to the IGW **and** its resources have public IPs or sit behind a public load balancer.

Docs: [create-vpc](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-vpc.html) · [create-subnet](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-subnet.html) · [create-internet-gateway](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-internet-gateway.html) · [create-route-table](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-route-table.html) · [create-route](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-route.html) · [associate-route-table](https://docs.aws.amazon.com/cli/latest/reference/ec2/associate-route-table.html) · [modify-subnet-attribute](https://docs.aws.amazon.com/cli/latest/reference/ec2/modify-subnet-attribute.html)

---

### 3. Create a Security Group for the instances

**What this section does:** Creates a virtual firewall and opens inbound TCP 80 (HTTP) and TCP 22 (SSH).

**Why it is needed:** A security group controls which traffic can reach the instance's network interface. Port 80 must be allowed or the ALB health checks and user requests never reach Nginx. Port 22 is only for manual debugging.

```
aws ec2 create-security-group --group-name intent-sg --description "Allow app and ssh" --vpc-id $VPC_ID --query 'GroupId' --output text --region $AWS_REGION
```

Save as `SG_ID`.

Allow HTTP:

```
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $AWS_REGION
```

Allow SSH:

```
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $AWS_REGION
```

| Rule | What it allows | Why it is used here | Safer alternative |
|------|----------------|---------------------|-------------------|
| TCP 80 from `0.0.0.0/0` | Anyone can send HTTP to the instance | Simplest setup while learning; also lets you test instances directly | Instance SG allows port 80 only from the ALB's security group ID |
| TCP 22 from `0.0.0.0/0` | Anyone can attempt SSH | Easy lab access | Restrict to your own IP `/32`, or drop SSH and use SSM Session Manager |

**Why the wide-open rule is not ideal:** it makes the instances directly reachable from the internet, bypassing the load balancer. The production pattern is two security groups:

1. ALB security group — inbound 80/443 from `0.0.0.0/0`
2. Instance security group — inbound 80 **only from the ALB security group**
3. SSH — your IP only, or none at all

That way the only public path is `Internet -> ALB -> instances`.

Docs: [create-security-group](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-security-group.html) · [authorize-security-group-ingress](https://docs.aws.amazon.com/cli/latest/reference/ec2/authorize-security-group-ingress.html)

---

### 4. Create the Launch Template (includes user-data)

**What this section does:** Stores the EC2 blueprint — AMI, instance type, key pair, security group, and the base64-encoded startup script — that the ASG reuses for every instance it launches.

**Why it is needed:** The ASG must be able to build identical, ready-to-serve instances on its own. The user-data script (`userdata.sh`) is what turns a plain Ubuntu AMI into a working intent-classifier server. Without a launch template, scaling out would produce empty machines.

Prepare `userdata.sh` first (see the file in this repo), and export `AMI_ID`, `INSTANCE_TYPE`, `KEY_NAME`, `LAUNCH_TEMPLATE_NAME`.

```
USER_DATA=$(base64 -w0 userdata.sh)
aws ec2 create-launch-template \
--launch-template-name "$LAUNCH_TEMPLATE_NAME" \
--version-description "v1" \
--launch-template-data "{\"ImageId\":\"$AMI_ID\",\"InstanceType\":\"$INSTANCE_TYPE\",\"KeyName\":\"$KEY_NAME\",\"SecurityGroupIds\":[\"$SG_ID\"],\"UserData\":\"$USER_DATA\"}" \
--region $AWS_REGION
```

| Piece | What it is | Why it is required |
|-------|------------|--------------------|
| `base64 -w0 userdata.sh` | Encodes the script as a single unwrapped line | Launch template `UserData` must be base64; `-w0` avoids line wrapping that would corrupt the value |
| `ImageId` | The OS image from step 1 | The instance needs something to boot |
| `InstanceType` | CPU/RAM size | Determines capacity and cost per instance |
| `KeyName` | SSH key pair | Lets you log in for debugging when port 22 is open |
| `SecurityGroupIds` | The SG from step 3 | Applies the firewall to every launched instance |
| `UserData` | Bootstrap script | Installs dependencies, trains the model, starts Gunicorn and Nginx on first boot |
| `--version-description` | Label for this template version | Launch templates are versioned; the ASG pins a version, so labels keep rollouts traceable |

Docs: [create-launch-template](https://docs.aws.amazon.com/cli/latest/reference/ec2/create-launch-template.html) · [EC2 user data](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)

---

### 5. Create the Target Group and Application Load Balancer (ALB)

**What this section does:** Creates the backend pool with health checks, the public ALB across both subnets, and the listener that forwards port 80 to that pool.

**Why it is needed:** The ALB is the single stable public entry point, and the target group is how AWS knows which instances are healthy enough to receive traffic.

#### 5.1 Create the target group

**What:** Defines an HTTP backend pool on port 80 and health-checks `/health`, treating HTTP 200 as healthy.

**Why:** The ASG registers its instances here. Health checks are what stop traffic from being sent to a booting or broken instance, and they let the ASG replace instances that never become healthy.

```
aws elbv2 create-target-group --name mlops-target-group --protocol HTTP --port 80 --vpc-id $VPC_ID --health-check-protocol HTTP --health-check-path /health --matcher HttpCode=200 --region $AWS_REGION
```

Save the ARN from the output as `TARGET_GROUP_ARN`.

| Flag | Why it is there |
|------|-----------------|
| `--protocol HTTP --port 80` | Matches where Nginx listens on the instance |
| `--health-check-path /health` | Probes the Flask health endpoint instead of running a real prediction |
| `--matcher HttpCode=200` | Defines what response counts as healthy |
| `--vpc-id` | A target group can only hold targets from one VPC |

#### 5.2 Create the public ALB

**What:** Creates an internet-facing Layer-7 load balancer in both subnets, using the security group.

**Why:** Clients get one DNS name that stays stable while instances come and go. Placing it in two AZs is both an AWS requirement and what makes it fault tolerant.

```
aws elbv2 create-load-balancer --name model-deployment --subnets $SUBNET_ID1 $SUBNET_ID2 --security-groups $SG_ID --scheme internet-facing --type application --region $AWS_REGION
```

Save as `ALB_ARN`.

| Flag | Why it is there |
|------|-----------------|
| `--subnets` (two AZs) | Required minimum for an ALB; also provides AZ redundancy |
| `--scheme internet-facing` | Gives the ALB public addresses so users can reach it |
| `--type application` | Layer-7 HTTP load balancer, which is what path-based routing and HTTP health checks need |

#### 5.3 Create the listener

**What:** Makes the ALB accept HTTP on port 80 and forward those requests to the target group.

**Why:** Without a listener the ALB exists but ignores traffic — nothing connects the public port to the backend pool.

```
aws elbv2 create-listener --load-balancer-arn $ALB_ARN --protocol HTTP --port 80 --default-actions Type=forward,TargetGroupArn=$TARGET_GROUP_ARN --region $AWS_REGION
```

Docs: [create-target-group](https://docs.aws.amazon.com/cli/latest/reference/elbv2/create-target-group.html) · [create-load-balancer](https://docs.aws.amazon.com/cli/latest/reference/elbv2/create-load-balancer.html) · [create-listener](https://docs.aws.amazon.com/cli/latest/reference/elbv2/create-listener.html)

---

### 6. Create the Auto Scaling Group that uses the Launch Template

**What it does:** Creates an ASG that launches instances from the launch template into both subnets, keeping between 1 and 3 instances with a desired count of 1.

**Why it is needed:** This is the self-healing and scaling layer. If an instance dies or fails health checks, the ASG replaces it automatically, and capacity can grow without anyone launching instances by hand.

```
aws autoscaling create-auto-scaling-group \
--auto-scaling-group-name mlops-autoscaling \
--launch-template LaunchTemplateName=mlops-template,Version=1 \
--min-size 1 --max-size 3 --desired-capacity 1 \
--vpc-zone-identifier "$SUBNET_ID1,$SUBNET_ID2" \
--region $AWS_REGION
```

| Flag | Why it is there |
|------|-----------------|
| `--launch-template` | Tells the ASG exactly how to build each instance, pinned to a template version |
| `--min-size 1` | Never drop below one running instance |
| `--desired-capacity 1` | Start with a single instance to keep cost low |
| `--max-size 3` | Upper bound so scaling cannot run away with cost |
| `--vpc-zone-identifier` | Lets the ASG spread instances across both AZs |

Docs: [create-auto-scaling-group](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/create-auto-scaling-group.html)

---

### 7. Attach the Target Group to the ASG

**What it does:** Links the ASG to the ALB target group so newly launched instances register themselves.

**Why it is needed:** Without this link the ASG still launches instances, but the ALB has no targets, so requests never reach the app. It also means replacement instances are wired up automatically instead of manually.

```
aws autoscaling attach-load-balancer-target-groups \
--auto-scaling-group-name mlops-autoscaling \
--target-group-arns "$TARGET_GROUP_ARN" \
--region $AWS_REGION
```

Docs: [attach-load-balancer-target-groups](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/attach-load-balancer-target-groups.html)

---

## What happens inside each EC2 instance

`userdata.sh` runs once on first boot and does the following, in this order and for these reasons:

| Step | Why |
|------|-----|
| Install `git`, Python, venv, pip, Nginx | The base AMI is plain Ubuntu with none of the app's runtime |
| Clone the app repository into `/opt/intent-app` | The AMI does not contain the application code |
| Create a virtualenv and install `requirements.txt` | Keeps app dependencies isolated from system Python |
| Run `model/train.py` | Produces the model artifact the API needs before serving traffic |
| Write the `intent_gunicorn` systemd unit | systemd restarts Gunicorn on crash and starts it on reboot |
| Write the Nginx reverse-proxy config | Nginx owns port 80 and forwards to Gunicorn on `127.0.0.1:6000` |
| Enable and start Gunicorn and Nginx | Makes the instance able to pass health checks and serve requests |

Flask endpoints:

- `GET /health` — used by the ALB target group health check
- `POST /predict` — prediction requests

Gunicorn loads the app through `wsgi.py`, which imports the Flask instance from `app.py`.

---

## Request flow

```
User / Browser
    |  DNS resolves the ALB name to its public addresses
    v
Internet Gateway  ->  VPC  ->  Public subnet (route 0.0.0.0/0 -> IGW)
    v
ALB listener on port 80  ->  Target group picks a healthy instance
    v
EC2 network interface  ->  Security group allows port 80  ->  Nginx :80
    v
Gunicorn 127.0.0.1:6000  ->  wsgi.py  ->  Flask  ->  model  ->  JSON
    v
Response returns: model -> Flask -> Gunicorn -> Nginx -> ALB -> user
```

Who decides what, and what they do not decide:

| Component | Decides | Does not decide |
|-----------|---------|-----------------|
| DNS | Which address the client connects to | Which EC2 instance handles the request |
| Internet Gateway | Whether traffic can enter/leave the VPC | Anything about HTTP contents |
| Route table | Where subnet traffic goes next | Load balancing or instance choice |
| Subnet | IP range and AZ placement | Packet filtering |
| Security group | Allow/deny traffic to the instance interface | Routing |
| Network ACL | Allow/deny at the subnet boundary | Application paths |
| ALB listener | Which target group receives the request | Running your app |
| Target group | Which healthy instance gets the request | Request body handling |
| Nginx | How HTTP is forwarded inside the instance | Model logic |
| Gunicorn | Runs the WSGI app processes | AWS networking |
| Flask | Which endpoint handler runs | Network path |
| Model | The prediction result | HTTP routing |

The common misconception: the subnet and route table do not choose an instance. They only make the network reachable. The ALB is what distributes requests.

---

## Why the commands run in this order

AWS resources depend on each other, so the infrastructure is built bottom-up and then traffic is wired to it:

1. VPC, subnets, IGW, routes — everything else needs a network to live in
2. Security group — the launch template and ALB both reference it
3. Launch template — the ASG needs a blueprint before it can launch anything
4. Target group, ALB, listener — the public entry point and health checking
5. ASG — launches the actual instances
6. Attach target group to ASG — connects instances to the load balancer

---

## Cleanup order

Teardown is the reverse, because of the same dependencies (see `delete-resources.md`):

1. Auto Scaling Group
2. ALB and its listeners
3. Target group
4. Launch template
5. Security groups, subnets, Internet Gateway, VPC

---

## Known issue to verify

The target group health check requests `/health`, but the Nginx config in `userdata.sh` proxies every path to `http://127.0.0.1:6000/predict`. That means the health check may hit `/predict` instead of Flask's `/health` endpoint and never return 200, which keeps targets unhealthy. Fix it by giving `/health` its own `location` block that proxies through unchanged.

---

## Beginner guide

If you are new to AWS, the easiest way to understand this deployment is to think about it like a building with security at the gate, a receptionist, and then the application inside.

### The story of one request

```text
Browser
  -> ALB
  -> Target Group
  -> EC2 instance
  -> Nginx
  -> Gunicorn
  -> Flask app
  -> Model
  -> Response back
```

A request does not go directly to the model. It first passes through the AWS networking layer, then the load balancer, then the EC2 machine, and only after that does it reach the Python app and model.

### What each part is for

#### VPC
The VPC is your private AWS network boundary.

- Why it exists: it keeps your deployment isolated from other AWS networks.
- Role: contains your subnets, route tables, security groups, ALB, and EC2 instances.
- If it were missing: there would be no private network space to place your app.

#### Subnets
Subnets are smaller slices of the VPC.

- Why they exist: resources need to live in specific Availability Zones.
- Role: they place resources into AZ-specific network ranges.
- If they were missing: you could not spread the load balancer across multiple AZs.

#### Internet Gateway
The Internet Gateway is the door between the VPC and the public internet.

- Why it exists: public traffic has to enter and leave the VPC somehow.
- Role: lets the ALB be internet-facing.
- If it were missing: users could not reach the public ALB, and instance startup downloads could fail.

#### Route table
The route table is the traffic map for a subnet.

- Why it exists: the subnet needs to know where traffic should go.
- Role: tells the subnet to send internet-bound traffic to the Internet Gateway.
- If it were missing: the subnet would not know how to route traffic out.

#### Route table association
This connects the route table to the subnet.

- Why it exists: route rules are applied per subnet.
- Role: makes the subnet actually use the route table.
- If it were missing: the route table would exist, but the subnet might not use it.

#### Security group
The security group is the firewall for the EC2 instance.

- Why it exists: you need allow/deny rules for inbound traffic.
- Role: allows HTTP on port 80 and, optionally, SSH on port 22.
- If it were missing: traffic might be blocked completely, or the instance might be too open.

#### Launch template
The launch template is the EC2 blueprint.

- Why it exists: the ASG needs a repeatable recipe for new instances.
- Role: stores the AMI, instance type, key pair, security group, and user-data.
- If it were missing: the ASG would not know how to create a ready-to-run instance.

#### User data
User data is the startup script run when EC2 boots.

This repo uses `userdata.sh` to:

- install system packages
- clone the app repository
- create a Python virtual environment
- install Python dependencies
- train the model
- create the Gunicorn service
- create the Nginx config
- start the services

- Why it exists: a fresh EC2 instance starts empty.
- Role: turns a plain Ubuntu machine into a working app server.
- If it were missing: the instance would boot, but the app would not be installed or running.

#### Target group
The target group is the backend pool for the ALB.

- Why it exists: the ALB needs to know which instances can receive traffic.
- Role: tracks healthy EC2 instances and performs health checks.
- If it were missing: the ALB would have nowhere to send requests.

#### ALB
The Application Load Balancer is the public front door.

- Why it exists: users should hit one stable address, not individual EC2 machines.
- Role: receives internet traffic and forwards it to a healthy instance.
- If it were missing: there would be no stable public entry point and no request distribution.

#### Listener
The listener is the ALB rule that handles incoming traffic.

- Why it exists: the ALB needs to know what to do with requests on port 80.
- Role: accepts HTTP traffic and forwards it to the target group.
- If it were missing: the ALB would receive traffic but not route it anywhere.

#### Auto Scaling Group
The Auto Scaling Group is the instance manager.

- Why it exists: instances should replace themselves if they fail.
- Role: launches and maintains the number of EC2 instances.
- If it were missing: you would need to manage EC2 instances manually.

#### Nginx
Nginx is the web server inside the EC2 instance.

- Why it exists: it is the first process that receives HTTP on the machine.
- Role: reverse proxies requests to Gunicorn.
- If it were missing: you would need to expose Gunicorn directly or use another web server.

#### Gunicorn
Gunicorn is the production Python app server.

- Why it exists: Flask's built-in server is for development, not production.
- Role: runs the Flask app as a WSGI application.
- If it were missing: the Flask app would not be served properly in production.

#### Flask app
The Flask app is the API logic.

In this repo, it is defined in `app.py`.

- Why it exists: it exposes the endpoints.
- Role: serves `/health` and `/predict`.
- If it were missing: there would be no API to answer requests.

#### Model code
The model code is the part that makes the actual prediction.

- Why it exists: the app is supposed to classify intent.
- Role: takes input text and returns a prediction.
- If it were missing: the API could respond, but it would not classify anything.

### What happens inside EC2 when it boots

When the Auto Scaling Group starts a new instance, `userdata.sh` runs automatically:

1. It updates the machine.
2. It installs `git`, Python, and `nginx`.
3. It clones the repo.
4. It creates a virtual environment.
5. It installs Python requirements.
6. It trains the model.
7. It creates a Gunicorn systemd service.
8. It creates the Nginx config.
9. It starts Gunicorn and Nginx.

That means the EC2 instance becomes a working application server by itself.

### How a request moves through the system

#### User request

```text
User
  -> ALB
  -> healthy EC2 instance
  -> Nginx
  -> Gunicorn
  -> Flask
  -> Model
```

#### Health check request

```text
ALB
  -> /health
  -> EC2 instance
  -> Nginx
  -> Flask /health
```

The ALB uses health checks to decide whether an instance is healthy enough to receive real traffic.

### The two kinds of decisions

There are two layers of decisions in this deployment.

#### Networking decisions
These answer questions like:

- Can the request enter the VPC?
- Which subnet is it in?
- Is it allowed by the security group?
- Which EC2 instance gets the request?

These are handled by:

- Internet Gateway
- Route table
- Security group
- ALB
- Target group

#### Application decisions
These answer questions like:

- Which endpoint was called?
- Should the app return `/health` or `/predict`?
- What prediction should the model return?

These are handled by:

- Nginx
- Gunicorn
- Flask
- Model

### One simple summary

This deployment creates a public AWS entry point, sends traffic to healthy EC2 machines, and inside each machine Nginx passes the request to Gunicorn, Gunicorn runs the Flask app, and Flask calls the model to return a prediction.

---

## Official references

- [AWS CLI EC2 reference](https://docs.aws.amazon.com/cli/latest/reference/ec2/)
- [AWS CLI ELBv2 reference](https://docs.aws.amazon.com/cli/latest/reference/elbv2/)
- [AWS CLI Auto Scaling reference](https://docs.aws.amazon.com/cli/latest/reference/autoscaling/)
- [EC2 user data guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/user-data.html)
- [Ubuntu images on AWS](https://documentation.ubuntu.com/aws/en/latest/aws-how-to/instances/find-ubuntu-images/)
Overall flow

  Internet
    -> ALB
    -> Target Group
    -> ASG
    -> EC2 instance
    -> Nginx
    -> Gunicorn
    -> Flask app
    -> Model

  ## Components and why they exist

   Component                  Why it was introduced                               Role in the system                                  If it were missing
  ━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   AMI                        You need a base OS image to boot EC2 instances      Defines what OS the instance starts from            EC2 cannot launch because there is no machine
                                                                                                                                      image to boot
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   VPC                        You need a private AWS network boundary             Contains all networking resources for this          Nothing is isolated or organized; later resources
                                                                                  deployment                                          cannot be built correctly
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Subnets                    You need to place resources in specific             Split the VPC into AZ-specific network slices       You lose multi-AZ placement and ALB requirements
                              Availability Zones                                                                                      are not met
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Internet Gateway           You need a path between the VPC and the public      Lets internet traffic enter and leave the VPC       Public access to the ALB breaks, and instance
                              internet                                                                                                startup downloads can fail
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Route Table                Subnets need routing rules                          Tells subnet traffic where to go, especially        Instances may launch but cannot reach the
                                                                                  0.0.0.0/0 -> IGW                                    internet
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Route Table Association    A route table must be attached to each subnet       Makes the subnet use the routing rules              The subnet exists, but it does not actually know
                                                                                                                                      how to route traffic
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Security Group             You need packet filtering at the instance level     Acts as the firewall for EC2 or ALB                 Traffic may be blocked, or if too open, the
                                                                                                                                      instance becomes directly exposed
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Launch Template            ASG needs a reusable instance blueprint             Defines AMI, instance type, key, SG, and user       ASG has no standard way to create new instances
                                                                                  data
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   User Data script           Instances need bootstrap automation                 Installs packages, clones repo, creates venv,       New instances come up empty and do not serve the
                                                                                  installs deps, trains model, starts services        app
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Target Group               ALB needs a pool of backend instances               Holds the EC2 instances and performs health         ALB has nowhere to send requests
                                                                                  checks
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Load Balancer (ALB)        You need one stable public entry point              Receives traffic and forwards it to healthy         Users would need to talk to individual EC2
                                                                                  instances                                           instances directly
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Listener                   ALB needs a rule for incoming traffic               Accepts port 80 and forwards to the target group    ALB receives traffic but does not know where to
                                                                                                                                      send it
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Auto Scaling Group         You need self-healing and scaling                   Creates, replaces, and scales EC2 instances         No automatic replacement, no horizontal scaling
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Nginx                      You need a web server/reverse proxy on the          Receives HTTP on port 80 and forwards to            Gunicorn is exposed directly or the app is not
                              instance                                            Gunicorn                                            reachable on port 80
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Gunicorn                   Flask should not run as a dev server in             Serves the Python app as a production WSGI          Flask dev server would be weak for production use
                              production                                          server
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Flask app                  You need the application logic                      Exposes /health and /predict                        There is no API to answer requests
  ─────────────────────────  ──────────────────────────────────────────────────  ──────────────────────────────────────────────────  ───────────────────────────────────────────────────
   Model code                 The app needs to classify text                      Generates the intent prediction                     The API responds, but no useful prediction is
                                                                                                                                      produced

  ## What each AWS piece does in this setup

  ### 1. VPC

  The VPC is the container for the whole network. In your doc it is created first because everything else must live inside it.

  - Why it exists: to isolate your deployment from other AWS networks
  - Role: network boundary
  - Without it: no subnets, no security groups, no ALB, no EC2 placement in the intended network

  ### 2. Subnets

  Your doc creates two subnets in different Availability Zones.

  - Why it exists: the ALB needs at least two subnets in different AZs for high availability
  - Role: network slices tied to AZs
  - Without it: the ALB cannot be deployed correctly for multi-AZ traffic distribution

  ### 3. Internet Gateway

  This is the public door to the VPC.

  - Why it exists: the ALB must be internet-facing
  - Role: lets inbound/outbound internet traffic cross the VPC boundary
  - Without it: the public ALB has no internet path

  ### 4. Route Table + Association

  The route table tells the subnet where to send traffic.

  - Why it exists: traffic routing is a subnet-level decision
  - Role: sends 0.0.0.0/0 to the IGW
  - Without it: even with an IGW attached, the subnet may still not behave as public

  ### 5. Security Group

  This is the firewall for the instance.

  - Why it exists: AWS needs an allow/deny layer for the instance
  - Role: controls inbound traffic to the instance network interface
  - Without it: requests may be blocked, or the instance may be overexposed if rules are too open

  ### 6. Launch Template

  This is the EC2 blueprint.

  - Why it exists: ASG needs a repeatable way to launch identical servers
  - Role: defines AMI, instance type, key pair, security groups, and user-data
  - Without it: ASG does not know how to create new instances

  ### 7. User Data

  This is the startup script in userdata.sh.

  - Why it exists: a new instance starts as a blank machine
  - Role: installs dependencies, clones the repo, trains the model, creates the systemd service, configures Nginx, and starts services
  - Without it: EC2 boots, but the app is not installed or running

  ### 8. Target Group

  This is the health-checked pool of EC2 instances.

  - Why it exists: ALB needs to know which instances are usable
  - Role: receives traffic from the ALB and performs health checks
  - Without it: the ALB has no backend to forward to

  ### 9. ALB

  This is the public entry point.

  - Why it exists: you do not want users hitting individual EC2 instances directly
  - Role: accepts internet traffic and distributes it across healthy targets
  - Without it: no stable public endpoint, no request distribution, no central health-aware routing

  ### 10. Listener

  The listener is the ALB rule engine for incoming requests.

  - Why it exists: the ALB needs a rule for what to do with port 80 traffic
  - Role: listens on HTTP/80 and forwards to the target group
  - Without it: the ALB exists, but it does not actually forward requests

  ### 11. Auto Scaling Group

  This is the instance manager.

  - Why it exists: instances should replace themselves if unhealthy and scale if needed
  - Role: launches and maintains the number of EC2 instances
  - Without it: no auto-healing, no automatic scaling, manual instance management only

  ## Components inside the EC2 instance

  These are not AWS resources, but they are part of the real request path.

  ### 12. Nginx

  Configured in userdata.sh

  - Why it exists: it is the web server front door on the instance
  - Role: receives HTTP on port 80 and reverse proxies to Gunicorn
  - Without it: you would expose Gunicorn directly or need another web server

  ### 13. Gunicorn

  Configured in userdata.sh

  - Why it exists: Flask’s dev server is not meant for production
  - Role: runs the Flask app as a WSGI application
  - Without it: the app would not be served in a proper production process manager

  ### 14. Flask app

  Defined in app.py

  - Why it exists: it exposes the HTTP API
  - Role: handles /health and /predict
  - Without it: there is no endpoint for the ALB or users to call

  ### 15. Model code

  Used by the Flask app through IntentModel

  - Why it exists: this is the actual classifier
  - Role: turns input text into an intent prediction
  - Without it: the API would respond, but it would not classify anything

