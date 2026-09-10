import boto3
from datetime import datetime

# ── Configuration ──────────────────────────────────────────
REGION           = "ap-south-1"
ASG_NAME         = "iac-demo-asg"
TARGET_GROUP_ARN = "arn:aws:elasticloadbalancing:ap-south-1:566777078870:targetgroup/iac-demo-tg/0bdc917476dacbb3"
PROFILE          = "terraform"
# ───────────────────────────────────────────────────────────

session = boto3.Session(profile_name=PROFILE, region_name=REGION)

def get_asg_instances():
    client = session.client("autoscaling")
    response = client.describe_auto_scaling_groups(
        AutoScalingGroupNames=[ASG_NAME]
    )
    groups = response.get("AutoScalingGroups", [])
    if not groups:
        print(f"ERROR: ASG '{ASG_NAME}' not found.")
        return []
    return groups[0].get("Instances", [])

def get_alb_health():
    client = session.client("elbv2")
    response = client.describe_target_health(
        TargetGroupArn=TARGET_GROUP_ARN
    )
    return {
        item["Target"]["Id"]: item["TargetHealth"]["State"]
        for item in response.get("TargetHealthDescriptions", [])
    }

def get_ec2_details(instance_id):
    client = session.client("ec2")
    response = client.describe_instances(InstanceIds=[instance_id])
    reservations = response.get("Reservations", [])
    if not reservations:
        return {}
    instance = reservations[0]["Instances"][0]
    return {
        "instance_id":   instance.get("InstanceId"),
        "instance_type": instance.get("InstanceType"),
        "public_ip":     instance.get("PublicIpAddress", "N/A"),
        "private_ip":    instance.get("PrivateIpAddress", "N/A"),
        "state":         instance.get("State", {}).get("Name"),
        "launch_time":   str(instance.get("LaunchTime", ""))
    }

def run_report():
    print("\n" + "=" * 60)
    print("  INFRASTRUCTURE HEALTH REPORT")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Region: {REGION}  |  ASG: {ASG_NAME}")
    print("=" * 60)

    asg_instances = get_asg_instances()
    print(f"\n  ASG: {len(asg_instances)} instance(s) registered\n")

    alb_health = get_alb_health()
    all_healthy = True

    for inst in asg_instances:
        iid        = inst["InstanceId"]
        lifecycle  = inst["LifecycleState"]
        asg_health = inst["HealthStatus"]
        alb_status = alb_health.get(iid, "unknown")
        details    = get_ec2_details(iid)
        icon       = "✅" if alb_status == "healthy" else "❌"

        if alb_status != "healthy":
            all_healthy = False

        print(f"  {icon}  {iid}")
        print(f"       Type       : {details.get('instance_type', 'N/A')}")
        print(f"       Public IP  : {details.get('public_ip', 'N/A')}")
        print(f"       Private IP : {details.get('private_ip', 'N/A')}")
        print(f"       EC2 State  : {details.get('state', 'N/A')}")
        print(f"       ASG Health : {asg_health} ({lifecycle})")
        print(f"       ALB Health : {alb_status}")
        print(f"       Launched   : {details.get('launch_time', 'N/A')}")
        print()

    print("-" * 60)
    if all_healthy:
        print("ALL INSTANCES HEALTHY")
    else:
        print("SOME INSTANCES UNHEALTHY")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    run_report()
