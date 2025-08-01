# Deployment Guide

## 1. Prerequisites
Before deploying the Context Engineering Platform, ensure the following are available:
*   **Docker Desktop** or equivalent container runtime.
*   **Kubernetes Cluster** (v1.24+).
*   **kubectl** configured to access your cluster.
*   **Kustomize** (v4.0+).
*   **Terraform** (v1.5+) or OpenTofu.
*   **AWS CLI** configured with appropriate IAM credentials.

## 2. Infrastructure Provisioning (Terraform)
The foundational infrastructure (DynamoDB, ElastiCache, IAM roles) is managed via Terraform.
1.  Navigate to the `infra/terraform/env/prod` directory.
2.  Initialize the workspace: `terraform init`
3.  Review the planned changes: `terraform plan -out=tfplan`
4.  Apply the infrastructure: `terraform apply tfplan`

*Note: This will output the Redis endpoint and DynamoDB table names required for the application configuration.*

## 3. Docker Build and Push
The application is containerized and must be pushed to a registry (e.g., Amazon ECR).
1.  Authenticate Docker with your registry: `aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account_id>.dkr.ecr.<region>.amazonaws.com`
2.  Build the image: `docker build -t context-engineering-api:latest -f build/Dockerfile .`
3.  Tag the image: `docker tag context-engineering-api:latest <account_id>.dkr.ecr.<region>.amazonaws.com/context-engineering:v1.0.0`
4.  Push the image: `docker push <account_id>.dkr.ecr.<region>.amazonaws.com/context-engineering:v1.0.0`

## 4. Environment Configuration
Configuration is managed via Kubernetes ConfigMaps and Secrets.
Update the `deploy/k8s/overlays/prod/kustomization.yaml` with the correct image tags and environment variables:
*   `REDIS_HOST`: Endpoint from Terraform output.
*   `DYNAMODB_TABLE_MEMORY`: Table name from Terraform output.
*   `LOG_LEVEL`: Set to `INFO` for production.

## 5. Kubernetes Deployment (Kustomize)
Deploy the application using Kustomize to manage environment-specific overlays.
1.  Navigate to the deployment directory: `cd deploy/k8s`
2.  Apply the production overlay: `kubectl apply -k overlays/prod`
3.  Verify the deployment status: `kubectl rollout status deployment/context-engineering-api -n context-platform`

## 6. Health Checks
The platform exposes a standard health endpoint.
1.  Determine the service IP or Ingress endpoint.
2.  Execute a health check request: `curl http://<endpoint>/health`
3.  Expected response: `{"status": "healthy", "components": {"redis": "ok", "dynamodb": "ok"}}`

## 7. Rollout Strategy
The platform utilizes a standard Kubernetes RollingUpdate strategy to ensure zero downtime during upgrades.
*   `maxSurge`: 25% (allows scaling up slightly during rollout)
*   `maxUnavailable`: 0 (ensures all desired pods are available before terminating old ones)
Monitor the rollout via `kubectl get pods -w` to ensure new pods stabilize before the deployment completes.
