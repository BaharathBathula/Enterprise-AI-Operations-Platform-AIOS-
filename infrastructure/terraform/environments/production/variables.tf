variable "aws_region" {
  description = "AWS region used for the AIOS production environment."
  type        = string
  nullable    = false
}

variable "project_name" {
  description = "Project identifier used for AIOS infrastructure."
  type        = string
  default     = "aios"
  nullable    = false
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "production"
  nullable    = false

  validation {
    condition     = var.environment == "production"
    error_message = "This Terraform root module is reserved for the production environment."
  }
}
