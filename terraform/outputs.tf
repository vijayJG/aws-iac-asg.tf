# ============================================================
# outputs.tf — Values printed after terraform apply
# Copy these after apply — you need them for Ansible and boto3
# ============================================================

output "alb_dns_name" {
  description = "Open this URL in your browser to see the live app"
  value       = aws_lb.main.dns_name
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_subnet_ids" {
  description = "Both public subnet IDs"
  value       = [aws_subnet.public_1.id, aws_subnet.public_2.id]
}

output "asg_name" {
  description = "Auto Scaling Group name — paste into health_check.py"
  value       = aws_autoscaling_group.main.name
}

output "target_group_arn" {
  description = "Target Group ARN — paste into health_check.py"
  value       = aws_lb_target_group.main.arn
}
