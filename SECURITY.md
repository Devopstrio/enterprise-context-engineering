# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

To report a security vulnerability, email **security@devopstrio.co.uk** with:

1. Description of the vulnerability
2. Steps to reproduce
3. Impact assessment
4. Suggested remediation (if applicable)

Response SLA: 48 hours for initial acknowledgement, 7 business days for triage.

## Security Controls

- Non-root container execution with read-only root filesystem
- TLS 1.3 transport encryption for Redis and API connections
- AWS IAM least-privilege policies for DynamoDB and CloudWatch access
- Kubernetes NetworkPolicy restricting ingress/egress
- No secrets stored in source code or container images
- PII detection and masking in context audit logs
- Dependency vulnerability scanning via GitHub Actions
