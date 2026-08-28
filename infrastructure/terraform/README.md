# AIOS Terraform Infrastructure

This directory contains the Infrastructure-as-Code implementation for the AIOS v1.1.0 Production Deployment milestone.

## Toolchain

- Terraform 1.16.0
- HashiCorp AWS Provider 6.60.0
- Amazon Web Services

## Current Status

The Terraform repository foundation is established, but no AWS infrastructure resources are declared at this stage.

Infrastructure will be introduced incrementally through protected pull requests.

## Structure

```text
terraform/
├── environments/
│   └── production/
│       ├── versions.tf
│       ├── providers.tf
│       └── variables.tf
├── .gitignore
└── README.md
```

## Production Environment

The production root configuration is located at:

```text
infrastructure/terraform/environments/production
```

The production AWS region must be supplied explicitly.

Example:

```bash
terraform plan -var="aws_region=us-east-1"
```

The example above does not establish `us-east-1` as the AIOS production region.

## State Management

Remote Terraform state has not yet been configured.

The production milestone will establish secure remote state before application infrastructure is provisioned.

Terraform state must never be committed to Git.

## Credentials

AWS credentials must not be committed to this repository.

Terraform authentication will ultimately use short-lived AWS identity through the CI/CD deployment mechanism.

Static AWS access keys are not part of the target production design.

## Local Validation

From:

```text
infrastructure/terraform/environments/production
```

initialize providers without configuring a remote backend:

```bash
terraform init -backend=false
```

Validate formatting:

```bash
terraform fmt -check -recursive
```

Validate configuration:

```bash
terraform validate
```

## Change Management

Production infrastructure changes must follow:

```text
Feature Branch
      |
      v
Pull Request
      |
      v
Terraform Validation
      |
      v
Existing Application CI
      |
      v
Protected main
```

Infrastructure changes must not be pushed directly to `main`.
