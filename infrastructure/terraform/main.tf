# NEXUS Intelligence — AWS infrastructure (Terraform)
#
# Topology: VPC (public/private subnets) > ALB > ECS Fargate (backend +
# frontend) > RDS PostgreSQL 16 + ElastiCache Redis + S3 assets bucket.
# Images live in ECR; API keys live in Secrets Manager; logs in CloudWatch.
#
# Remote state is partial-config S3 — deploy.yml supplies bucket/key/region
# via -backend-config at init time.
#
# NOTE: Qdrant has no AWS-managed equivalent. Production uses Qdrant Cloud
# (or a self-managed ECS service added later); set var.qdrant_url.

terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {}
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "nexus-intelligence"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

locals {
  name = "${var.project}-${var.environment}"
  azs  = slice(data.aws_availability_zones.available.names, 0, var.az_count)
}
