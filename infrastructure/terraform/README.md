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

## Remote State

Production Terraform state uses the Amazon S3 backend.

The backend configuration enables:

- encrypted state storage
- S3-native state locking
- remote state persistence
- state recovery through S3 versioning

DynamoDB-based Terraform state locking is not used.

The production backend declaration is located at:

```text
environments/production/backend.tf
```

Environment-specific backend values are supplied separately.

Use the committed example:

```text
backend.hcl.example
```

to create a local:

```text
backend.hcl
```

The real `backend.hcl` file is excluded from source control.

Once the remote-state bucket has been bootstrapped, initialization will use:

```bash
terraform init -backend-config=backend.hcl
```

AWS credentials must not be stored in the backend configuration.

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
