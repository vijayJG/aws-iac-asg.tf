# Auto-Scaling Web Infrastructure on AWS
**Infrastructure as Code · DevOps · Cloud Architecture**

> Fully automated, production-style AWS infrastructure built entirely with code.
> No manual console clicks. Every resource defined, versioned, and reproducible.

![Region](https://img.shields.io/badge/Region-ap--south--1%20Mumbai-orange)
![Terraform](https://img.shields.io/badge/Terraform-v1.16.1-purple)
![Ansible](https://img.shields.io/badge/Ansible-2.16.3-red)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![AWS](https://img.shields.io/badge/AWS-EC2%20%7C%20ALB%20%7C%20ASG%20%7C%20VPC-yellow)


## What This Project Does

This project provisions, configures, and monitors a complete cloud infrastructure on AWS using Infrastructure as Code (IaC). A Flask web application runs across multiple EC2 instances behind a load balancer that automatically distributes traffic. The Auto Scaling Group adds or removes instances based on CPU load - no human intervention required.

Every new EC2 instance bootstraps itself completely on boot via cloud-init userdata - installing Python, creating a virtual environment, deploying the Flask app, and starting it as a systemd service. The ALB verifies each instance is healthy before sending it traffic.


## Architecture

```
                        INTERNET
                            │
                            ▼
             Application Load Balancer (ALB)
             iac-demo-alb-158717779.ap-south-1.elb.amazonaws.com
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
    EC2 (ap-south-1a)           EC2 (ap-south-1b)
    Ubuntu 24.04 LTS            Ubuntu 24.04 LTS
    t3.micro                    t3.micro
    ┌─────────────────┐         ┌─────────────────┐
    │  Flask App      │         │  Flask App      │
    │  systemd svc    │         │  systemd svc    │
    │  port 80        │         │  port 80        │
    └─────────────────┘         └─────────────────┘
             │                             │
             └──────────┬──────────────────┘
                        │
              Auto Scaling Group
              min=1  desired=2  max=3
              CPU target: 70%
                        │
          VPC (10.0.0.0/16) · ap-south-1
          ├── Public Subnet 1 (10.0.1.0/24) · ap-south-1a
          ├── Public Subnet 2 (10.0.2.0/24) · ap-south-1b
          ├── Internet Gateway
          ├── Route Table
          ├── ALB Security Group (inbound :80 from 0.0.0.0/0)
          └── EC2 Security Group (inbound :80 from ALB only, :22 SSH)
```


## Tech Stack

| Tool | Version | Role |
|---|---|---|
| Terraform | v1.16.1 | Provision all 15 AWS resources as code |
| Ansible | 2.16.3 | Configuration management playbook |
| Python + Flask | 3.12 + 3.1.3 | Web application on each EC2 instance |
| boto3 | 1.43.87 | AWS SDK - infrastructure health monitoring |
| AWS EC2 | t3.micro | Compute - Ubuntu 24.04 LTS |
| AWS ALB | - | Load balancing + health checks |
| AWS ASG | - | Auto scaling based on CPU utilisation |
| AWS VPC | - | Isolated network across 2 availability zones |


## Project Structure

```
aws-iac-project/
│
├── terraform/
│   ├── main.tf          # All 15 AWS resources defined here
│   ├── variable.tf      # Configurable values (region, AMI, instance type)
│   ├── outputs.tf       # Post-deploy values (ALB DNS, ASG name, VPC ID)
│   └── userdata.sh      # EC2 bootstrap - self-configuring on boot
│
├── ansible/
│   ├── inventory.ini    # Target server list (EC2 public IPs)
│   └── playbook.yml     # Configuration tasks (Flask, systemd, venv)
│
├── script/
│   └── health_check.py  # boto3 monitoring - queries ASG + ALB + EC2
│
├── app.py               # Flask web application
├── .gitignore           # Excludes tfstate, credentials, venv
└── README.md
```


## AWS Resources Created (15 total)

| Resource | Name | Purpose |
|---|---|---|
| aws_vpc | iac-demo-vpc | Isolated network, 10.0.0.0/16 |
| aws_internet_gateway | iac-demo-igw | VPC internet access |
| aws_subnet (×2) | iac-demo-public-subnet-1/2 | One per AZ for high availability |
| aws_route_table | iac-demo-public-rt | Routes internet traffic via IGW |
| aws_route_table_association (×2) | - | Links subnets to route table |
| aws_security_group (×2) | iac-demo-alb-sg, iac-demo-ec2-sg | ALB and EC2 firewalls |
| aws_lb | iac-demo-alb | Application Load Balancer |
| aws_lb_target_group | iac-demo-tg | Pool of EC2 targets, /health check |
| aws_lb_listener | - | Listens on port 80, forwards to TG |
| aws_launch_template | iac-demo-lt | EC2 blueprint with userdata |
| aws_autoscaling_group | iac-demo-asg | Manages instance count |
| aws_autoscaling_policy | iac-demo-cpu-policy | CPU target tracking at 70% |


## How It Works - Layer by Layer

### Layer 1 - Terraform provisions infrastructure
Terraform reads `.tf` files and makes API calls to AWS to create all resources. It tracks state - running `terraform apply` twice doesn't create duplicate resources. The entire infrastructure is reproducible with two commands.

### Layer 2 - userdata.sh bootstraps every EC2 instance
When the ASG launches a new EC2 instance, the Launch Template runs `userdata.sh` automatically via cloud-init. This script:
- Runs `apt-get update` and installs Python3 + venv
- Creates `/home/ubuntu/app/venv`
- Installs Flask inside the venv
- Writes `app.py` directly to the instance
- Creates a systemd service (`flaskapp.service`) running as root
- Enables and starts the service

This means **every new ASG instance configures itself completely on boot** - no manual SSH, no Ansible trigger needed.

### Layer 3 - Ansible for configuration management
An Ansible playbook was written and used for initial configuration and deployment verification. For ephemeral ASG instances, userdata is the correct bootstrap mechanism. Ansible is appropriate for managing long-lived server fleets and was retained in the project to demonstrate configuration management skills.

### Layer 4 - Flask serves traffic
The Flask app runs on port 80 as a systemd service (User=root to bind to privileged port). It exposes two routes:
- `/` - returns an HTML page showing the server hostname and timestamp
- `/health` - returns `{"status": "healthy", "host": "hostname"}` with HTTP 200

The ALB calls `/health` every 30 seconds. Two consecutive successes = healthy. Two consecutive failures = removed from rotation.

### Layer 5 - boto3 monitors the infrastructure
A Python script using boto3 queries three AWS APIs simultaneously:
- `autoscaling` - instance lifecycle state and ASG health
- `elbv2` - ALB target health status
- `ec2` - public IP, private IP, instance type, launch time

Combines all three into a live health dashboard printed to the terminal.


## Key Concepts Demonstrated

**Infrastructure as Code**
Every AWS resource is defined in `.tf` files. The entire infrastructure can be destroyed and recreated identically with `terraform destroy` + `terraform apply`. Version controlled in Git - every change is tracked.

**Idempotency**
Running `terraform apply` twice produces the same result. Terraform compares desired state (`.tf` files) against current state (`.tfstate`) and only makes necessary changes. Ansible playbooks are also idempotent.

**High Availability**
Instances are spread across two Availability Zones (`ap-south-1a` and `ap-south-1b`). The ALB spans both subnets. If one AZ has an outage, traffic continues to the other AZ automatically.

**Auto Scaling**
The ASG monitors average CPU via CloudWatch. When CPU exceeds 70%, new instances are launched automatically from the Launch Template. When CPU drops, instances are terminated. No human action required.

**Self-healing infrastructure**
If an EC2 instance fails its ALB health check, the ALB stops sending it traffic. The ASG detects the unhealthy instance and launches a replacement. The replacement bootstraps itself via userdata and is automatically registered with the ALB.

**Separation of concerns**
Terraform provisions. userdata bootstraps. Ansible configures. Python monitors. Each layer has a single, clear responsibility.

**IAM best practice**
A dedicated IAM user (`terraform-user`) with AWS CLI profile `terraform` was used for all development. The root account was not used for normal operations.


## Development Environment

```
Windows 11
├── Terraform v1.16.1    (native Windows)
├── VS Code
└── Git

WSL2 Ubuntu 24.04
├── Ansible 2.16.3
├── AWS CLI (profile: terraform)
├── Python 3.12.3
└── boto3 1.43.87 (inside aws-env virtual environment)
```

**Why WSL2?** Ansible does not support Windows as a control node. WSL2 provides a full Linux environment inside Windows 11 where Ansible, AWS CLI, and Python tooling run natively.


## Real Challenges Solved

This project was not a tutorial walkthrough. Real problems were encountered and solved:

**AMI mismatch** - Original config used Amazon Linux 2 (`yum`, `ec2-user`). The actual AMI was Ubuntu 24.04 (`apt`, `ubuntu`). All scripts and Ansible tasks were rewritten accordingly.

**Instance type rejection** - `t2.micro` was rejected as not free-tier eligible on this account. Used `aws ec2 describe-instance-types --filters "Name=free-tier-eligible,Values=true"` to identify `t3.micro` as the correct type.

**Port 80 permission denied** - Flask running as `ubuntu` user cannot bind to port 80 (privileged port, requires root). Fixed by setting `User=root` in the systemd service unit file.

**SSH key mismatch** - Two key pairs (`iac-demo-key`, `iac-demo-key-v2`) did not match the local `.pem` file. Created `iac-demo-key-v3`, verified with `ssh-keygen -y -f` against the AWS console public key.

**ASG instance cycling** - With `desired_capacity=2`, the ASG kept replacing the second instance because it was unhealthy (Flask not running). Root cause: userdata only installed prerequisites, not the app. Fixed by embedding the complete app deployment into `userdata.sh`.

**AWS credentials for Terraform** - `aws login --remote` produced temporary root credentials that Terraform could not consume reliably. Fixed by creating a dedicated IAM user (`terraform-user`) with a permanent access key and AWS CLI profile.

**boto3 `unhashable type: dict`** - Flask's `/health` route returned a raw dict, which caused a 500 error in some Flask versions. Fixed by using `jsonify()` to properly serialise the response.


## IAM Setup

```
AWS Root Account
    └── IAM User: terraform-user
          └── Policy: AdministratorAccess (temporary - learning project)
          └── AWS CLI profile: terraform
          └── Used for: Terraform, AWS CLI, boto3
```

Root account credentials were never used for development or committed anywhere.


## Screenshots

See the `/screenshots` folder for:
- Both ALB targets healthy simultaneously
- ALB serving different hostnames (load balancing proof)
- Flask app in browser
- Terraform output
- Ansible playbook run
- boto3 health report
- AWS Console: EC2, ALB, ASG, VPC


## Deployment Guide

### Prerequisites
- AWS account with IAM user configured
- Terraform installed
- WSL2 with Ansible, AWS CLI, Python, boto3

### Deploy
```bash
cd terraform/
terraform init
terraform plan
terraform apply
```

### Configure (optional - instances self-configure via userdata)
```bash
# Update ansible/inventory.ini with EC2 public IPs
ansible-playbook -i ansible/inventory.ini ansible/playbook.yml
```

### Monitor
```bash
source ~/aws-env/bin/activate
python script/health_check.py
```

### Destroy (always run this when done to avoid charges)
```bash
cd terraform/
terraform destroy
```

**Skills line:**
Cloud & DevOps: Terraform (IaC), Ansible, AWS (EC2, VPC, ALB, ASG, IAM, CloudWatch), Python, boto3, Flask, Git, systemd, Linux (Ubuntu 24.04), WSL2


