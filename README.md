# Auto-Scaling Web Infrastructure on AWS
**Terraform · Ansible · Python · AWS | Region: ap-south-1 (Mumbai)**

## Architecture
Internet → ALB → EC2 (ap-south-1a) + EC2 (ap-south-1b)
Auto Scaling Group (min=1, desired=2, max=3)
VPC / Subnets / Security Groups

## Tech Stack
| Tool | Purpose |
|---|---|
| Terraform | Provision all AWS infrastructure as code |
| Ansible | Configuration management playbook |
| Flask | Web app running on each EC2 instance |
| boto3 | Python AWS SDK health monitoring |
| AWS ALB | Load balancing and health checks |
| AWS ASG | Auto scaling based on CPU target 70% |

## Key Concepts
- Infrastructure as Code — entire AWS setup in .tf files
- Auto Scaling — instances added/removed at 70% CPU
- High Availability — instances across 2 Availability Zones
- Health Checks — ALB checks /health every 30 seconds
- Self-configuring instances — userdata bootstraps Flask automatically
- Separation of concerns — Terraform provisions, Ansible configures, Python monitors

## AWS Resources Created
VPC, Internet Gateway, 2 Public Subnets, Route Table, 2 Security Groups,
Application Load Balancer, Target Group, ALB Listener,
Launch Template, Auto Scaling Group, Auto Scaling Policy

## IAM
Uses dedicated terraform-user IAM user. Root account not used for development.

## Cleanup
terraform destroy
