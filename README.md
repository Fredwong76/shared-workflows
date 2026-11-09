# shared-workflows

Reusable GitHub Actions workflows for CI/CD across ECUPSE projects. Callers pin a
release tag (`@v1`); see [Versioning](#versioning) and [CHANGELOG.md](CHANGELOG.md).

## Available Workflows

| Workflow | Purpose |
|----------|---------|
| `ci-python.yml` | Run pytest for any Python project |
| `validate-cdk.yml` | Validate CDK templates with `cdk synth` (optional stack tests) |
| `deploy-cdk.yml` | Deploy CDK stacks using OIDC authentication |
| `deploy-s3-site.yml` | Sync a static site to S3 and invalidate CloudFront |

---

## ci-python.yml

Runs pytest on a Python project.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.12` | Python version |
| `test-path` | string | `tests/` | Test directory or file |
| `install-command` | string | `pip install -r requirements.txt` | Dependency install command |
| `working-directory` | string | `.` | Working directory for the project |

### Example

Trigger on `pull_request` and `workflow_dispatch` only. Adding `push` as well runs CI
twice for every PR branch commit. Run CI on the merged result
by making the CI job a required status check in branch protection.

```yaml
name: CI
on:
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  test:
    uses: Fredwong76/shared-workflows/.github/workflows/ci-python.yml@v1
    with:
      python-version: "3.12"
      test-path: "tests/"
```

---

## validate-cdk.yml

Validates AWS CDK templates by running `cdk synth --no-bundling`.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.12` | Python version |
| `node-version` | string | `24` | Node.js version for the CDK CLI |
| `cdk-version` | string | pinned (see workflow) | `aws-cdk` CLI version; bumped by releases |
| `cdk-directory` | string | `cdk` | Directory containing the CDK app |
| `install-command` | string | `pip install -r requirements.txt` | CDK dependency install command |
| `run-tests` | boolean | `false` | Run CDK stack tests (pytest) after synth |
| `test-install-command` | string | `pip install -r requirements.txt -r requirements-dev.txt` | Test dependency install command |

```yaml
jobs:
  validate:
    uses: Fredwong76/shared-workflows/.github/workflows/validate-cdk.yml@v1
    with:
      cdk-directory: "cdk"
      run-tests: true
```

CDK stack test notes:
- Tests run from the CDK directory with `python -m pytest tests/`, so relative asset
  paths such as `Code.from_asset("../lambdas/preprocessor")` resolve correctly.
- No Docker is needed. Use CDK context `aws:cdk:bundling-stacks: []` in your test
  fixture to skip Docker asset bundling (the synth step already passes `--no-bundling`).

---

## deploy-cdk.yml

Deploys CDK stacks using OIDC-based AWS authentication. Deploys are queued per calling
repository and stack selection; a running deploy is never cancelled.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `python-version` | string | `3.12` | Python version |
| `node-version` | string | `24` | Node.js version for the CDK CLI |
| `cdk-version` | string | pinned (see workflow) | `aws-cdk` CLI version; bumped by releases |
| `cdk-directory` | string | `cdk` | Directory containing the CDK app |
| `aws-region` | string | `ap-southeast-1` | AWS region |
| `install-command` | string | `pip install -r requirements.txt` | CDK dependency install command |
| `bundle` | string | `1` | Sets `TALEMUSE_CDK_BUNDLE`; keep ON for real deploys |
| `stacks` | string | `--all` | Stacks and flags for `cdk deploy`, e.g. `MyStack --exclusively` |
| `import-check-functions` | string | `""` | Lambda names to invoke after deploy as an import check |

`import-check-functions`: each listed function is invoked once with the payload `{}`, so
its handler runs. List only functions that are safe to invoke. A failed invoke (for
example missing permission) fails the job.

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_DEPLOY_ROLE_ARN` | Yes | ARN of the IAM role to assume via OIDC |

```yaml
jobs:
  deploy:
    uses: Fredwong76/shared-workflows/.github/workflows/deploy-cdk.yml@v1
    with:
      cdk-directory: "cdk"
      aws-region: "ap-southeast-1"
    secrets:
      AWS_DEPLOY_ROLE_ARN: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
```

---

## deploy-s3-site.yml

Syncs a static site directory to S3 and optionally invalidates a CloudFront distribution.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `source-directory` | string | *(required)* | Directory containing built site files |
| `s3-destination` | string | *(required)* | S3 bucket URI (e.g. `s3://my-bucket`) |
| `cloudfront-distribution-id` | string | `""` | CloudFront distribution ID (optional) |
| `aws-region` | string | `ap-southeast-1` | AWS region |
| `delete-removed` | boolean | `false` | Pass `--delete` to `aws s3 sync` |
| `include-filters` | string | `""` | Allowlist, one `--include` pattern per line |

`delete-removed` defaults to `false`. Earlier versions always deleted; callers that
rely on that must set `delete-removed: true`. When `include-filters` is set, everything
else is excluded, so `--delete` only touches matching keys.

| Secret | Required | Description |
|--------|----------|-------------|
| `AWS_DEPLOY_ROLE_ARN` | Yes | ARN of the IAM role to assume via OIDC |

```yaml
jobs:
  deploy-site:
    uses: Fredwong76/shared-workflows/.github/workflows/deploy-s3-site.yml@v1
    with:
      source-directory: "site/build"
      s3-destination: "s3://my-site-bucket"
      cloudfront-distribution-id: "E1234ABCDEF"
      delete-removed: true
      include-filters: |
        index.html
        assets/*
    secrets:
      AWS_DEPLOY_ROLE_ARN: ${{ secrets.AWS_DEPLOY_ROLE_ARN }}
```

---

## Authentication (OIDC onboarding)

Deploy workflows use OIDC for keyless AWS authentication.

1. Create an OIDC identity provider for `token.actions.githubusercontent.com` in the
   AWS account.
2. Create an IAM role whose trust policy matches the CALLING repository and branch
   narrowly. Do not use an account-wide wildcard. Prefer the owner-ID form, which
   resists rename takeover:

   ```json
   "StringEquals": {
     "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
     "token.actions.githubusercontent.com:sub": "repo:<OwnerName>@<OwnerId>/<repo>:ref:refs/heads/main"
   }
   ```

   The `sub` claim names the calling repo, not the repo that hosts the reusable
   workflow, so this repository's visibility does not change who can assume a role.
3. Give the role only what the deploy needs (for CDK, permission to assume the CDK
   bootstrap roles).
4. Store the role ARN as a repository secret `AWS_DEPLOY_ROLE_ARN`.
5. Verify with a `workflow_dispatch` run before relying on push triggers.

See [GitHub docs on OIDC with AWS](https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services).

---

## Versioning

- Releases are immutable annotated tags `v1.N.N`.
- `v1` is a floating tag pointing at the latest tested `v1.N.N`. Callers pin `@v1`.
- Rollback is moving `v1` back to the previous `v1.N.N`; no caller change is needed.
- Only the repository owners create or move tags.

```yaml
uses: Fredwong76/shared-workflows/.github/workflows/ci-python.yml@v1
```

Every pull request runs `lint.yml` (actionlint) and `smoke.yml` (fixture runs of
`ci-python` and `validate-cdk`).
