# ============================================================
# variables.tf - All configurable values in one place
# Mumbai (ap-south-1) configured throughout
# ============================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Prefix for all resource names and tags"
  type        = string
  default     = "iac-demo"
}

variable "instance_type" {
  description = "EC2 instance type - t3.micro is free tier eligible"
  type        = string
  default     = "t3.micro"
}

variable "ami_id" {
  description = "Ubuntu 24.04 LTS AMI for ap-south-1 (Mumbai)"
  type        = string
  default     = "ami-0f58b397bc5c1f2e8"
}

variable "key_pair_name" {
  description = "Name of SSH key pair created in AWS Console"
  type        = string
  default     = "iac-demo-key-v3"
}

variable "desired_capacity" {
  description = "ASG desired capacity - set to 1 while configuring"
  type        = number
  default     = 1
}
