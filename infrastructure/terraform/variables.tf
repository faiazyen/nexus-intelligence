variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Short project slug used as a resource name prefix"
  type        = string
  default     = "nexus"
}

variable "environment" {
  description = "Deployment environment (production, staging)"
  type        = string
  default     = "production"
}

# ---------- Network ----------

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "az_count" {
  description = "Number of availability zones to spread subnets across"
  type        = number
  default     = 2
}

# ---------- Database ----------

variable "db_name" {
  description = "PostgreSQL database name"
  type        = string
  default     = "nexus"
}

variable "db_username" {
  description = "PostgreSQL master username"
  type        = string
  default     = "nexus"
}

variable "db_password" {
  description = "PostgreSQL master password"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t4g.small"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GiB"
  type        = number
  default     = 20
}

# ---------- Cache ----------

variable "redis_node_type" {
  description = "ElastiCache node type"
  type        = string
  default     = "cache.t4g.micro"
}

# ---------- ECS services ----------

variable "backend_image_tag" {
  description = "Image tag for the backend ECR image (set by deploy.yml to the git SHA)"
  type        = string
  default     = "latest"
}

variable "frontend_image_tag" {
  description = "Image tag for the frontend ECR image (set by deploy.yml to the git SHA)"
  type        = string
  default     = "latest"
}

variable "backend_cpu" {
  description = "Fargate CPU units for the backend task (256 = 0.25 vCPU)"
  type        = string
  default     = "512"
}

variable "backend_memory" {
  description = "Fargate memory (MiB) for the backend task"
  type        = string
  default     = "1024"
}

variable "frontend_cpu" {
  description = "Fargate CPU units for the frontend task"
  type        = string
  default     = "256"
}

variable "frontend_memory" {
  description = "Fargate memory (MiB) for the frontend task"
  type        = string
  default     = "512"
}

variable "backend_desired_count" {
  description = "Desired backend task count"
  type        = number
  default     = 2
}

variable "frontend_desired_count" {
  description = "Desired frontend task count"
  type        = number
  default     = 2
}

# ---------- External services / API keys ----------

variable "qdrant_url" {
  description = "Qdrant endpoint (Qdrant Cloud cluster URL; no AWS-managed Qdrant exists)"
  type        = string
  default     = "http://qdrant.internal:6333"
}

variable "openrouter_api_key" {
  description = "OpenRouter API key (stored in Secrets Manager) — all LLM calls route through OpenRouter, see app/core/llm_router.py"
  type        = string
  sensitive   = true
}

variable "apollo_api_key" {
  description = "Apollo.io API key (optional; agents degrade gracefully)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "newsapi_key" {
  description = "NewsAPI key (optional; agents degrade gracefully)"
  type        = string
  sensitive   = true
  default     = ""
}

variable "crunchbase_api_key" {
  description = "Crunchbase API key (optional; agents degrade gracefully)"
  type        = string
  sensitive   = true
  default     = ""
}

# ---------- Observability ----------

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 30
}
