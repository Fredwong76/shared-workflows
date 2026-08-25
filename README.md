# shared-workflows

Reusable GitHub Actions workflow templates for CI/CD automation across Fredwong76 projects.

## Available Workflows

| Workflow | Purpose |
|----------|--------|
| `ci-python.yml` | Run pytest for any Python project |
| `validate-cdk.yml` | Validate CDK templates with `cdk synth` |
| `deploy-cdk.yml` | Deploy CDK stacks using OIDC authentication |
| `deploy-s3-site.yml` | Sync static site to S3 + CloudFront invalidation |
| `monitor-kiro.yml` | Scheduled feed fetch, classify, and report generation |

---

## ci-python.yml

Runs pytest on a Python project with configurable version and test path.

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.12` | Python version to use |
| `test-path` | string | `tests/` | Path to test directory or file |
| `install-command` | string | `pip install -r requirements.txt` | Dependency install command |
| `working-directory` | string | `.` | Working directory for the project |

### Example

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    uses: Fredwong76/shared-workflows/.github/workflows/ci-python.yml@main
    with:
      python-version: "3.12"
      test-path: "tests/"
```

---

## validate-cdk.yml

Validates AWS CDK templates by running `cdk synth`.

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.12` | Python version to use |
| `cdk-directory` | string | `cdk` | Directory containing the CDK app |
| `install-command` | string | `pip install -r requirements.txt` | CDK dependency install command |

### Example

```yaml
jobs:
  validate:
    uses: Fredwong76/shared-workflows/.github/workflows/validate-cdk.yml@main
    with:
      cdk-directory: "cdk"
```

---

## deploy-cdk.yml

Deploys CDK stacks using OIDC-based AWS authentication.

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.12` | Python version to use |
| `cdk-directory` | string | `cdk` | Directory containing the CDK app |
| `aws-region` | string | `ap-southeast-1` | AWS region to deploy to |
| `install-command` | string | `pip install -r requirements.txt` | CDK dependency install command |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_DEPLOY_ROLE_ARN` | Yes | ARN of the IAM role to assume via OIDC |

### Example

```yaml
jobs:
  deploy:
    uses: Fredwong76/shared-workflows/.github/workflows/deploy-cdk.yml@main
    with:
      cdk-directory: "cdk"
      aws-region: "ap-southeast-1"
    secrets:
      AWS_DEPLOY_ROLE_ARN: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
```

---

## deploy-s3-site.yml

Syncs a static site directory to S3 and optionally invalidates a CloudFront distribution.

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `source-directory` | string | *(required)* | Directory containing built site files |
| `s3-destination` | string | *(required)* | S3 bucket URI (e.g. `s3://my-bucket`) |
| `cloudfront-distribution-id` | string | `""` | CloudFront distribution ID (optional) |
| `aws-region` | string | `ap-southeast-1` | AWS region |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_DEPLOY_ROLE_ARN` | Yes | ARN of the IAM role to assume via OIDC |

### Example

```yaml
jobs:
  deploy-site:
    uses: Fredwong76/shared-workflows/.github/workflows/deploy-s3-site.yml@main
    with:
      source-directory: "ecupse-site/build"
      s3-destination: "s3://my-site-bucket"
      cloudfront-distribution-id: "E1234ABCDEF"
    secrets:
      AWS_DEPLOY_ROLE_ARN: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
```

---

## monitor-kiro.yml

Runs scheduled monitoring: fetch feeds, classify entries, and generate a report.

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.12` | Python version to use |
| `scripts-directory` | string | `scripts` | Directory containing monitoring scripts |
| `reports-directory` | string | `reports` | Directory to write generated reports |
| `install-command` | string | `pip install -r requirements.txt` | Dependency install command |

### Secrets

| Secret | Required | Description |
|--------|----------|-------------|
| `KIRO_MONITOR_API_KEY` | Yes | API key for the classification service |

### Example

```yaml
name: Daily Monitor
on:
  schedule:
    - cron: "0 6 * * *"
  workflow_dispatch:

jobs:
  monitor:
    uses: Fredwong76/shared-workflows/.github/workflows/monitor-kiro.yml@main
    with:
      scripts-directory: "scripts"
      reports-directory: "reports"
    secrets:
      KIRO_MONITOR_API_KEY: ${{ secrets.KIRO_MONITOR_API_KEY }}
```

---

## Authentication

Deploy workflows use OIDC (OpenID Connect) for keyless AWS authentication. Prerequisites:

1. An OIDC identity provider for `token.actions.githubusercontent.com` in your AWS account
2. An IAM role with a trust policy scoped to your repository/branch
3. The role ARN stored as a repository secret (`AWS_DEPLOY_ROLE_ARN`)

See [GitHub docs on OIDC with AWS](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services) for setup instructions.

---

## Versioning

Workflow references should use `@main` during initial development. Once stable, tag releases and pin callers to `@v1`.

```yaml
# Development
uses: Fredwong76/shared-workflows/.github/workflows/ci-python.yml@main

# Production (after tagging)
uses: Fredwong76/shared-workflows/.github/workflows/ci-python.yml@v1
```
