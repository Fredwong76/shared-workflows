# Changelog

Releases are tagged `v1.N.N`; `v1` floats to the latest tested release.

## Unreleased

## v1.1.0 - 2026-11-09

### Behavior changes (caller-visible)

- `deploy-s3-site`: `--delete` is no longer always passed. New input `delete-removed`
  defaults to `false`. Callers that rely on deletion must set `delete-removed: true`.
- `deploy-cdk`, `validate-cdk`: Node.js default is now 24 (was 20) and the `aws-cdk`
  CLI is pinned (was unpinned `latest`). Override with `node-version` / `cdk-version`.
- `deploy-cdk`: a failed `aws lambda invoke` in the import check now fails the job
  (previously swallowed). The check runs each function's handler with payload `{}`.
- `monitor-kiro.yml` removed (no callers).

### Added

- `deploy-s3-site`: `include-filters` (newline-separated allowlist, no `eval`).
- `deploy-cdk`, `validate-cdk`: `node-version` and `cdk-version` inputs.
- `deploy-cdk`: concurrency group per calling repo and stack selection (queues, never
  cancels).
- `lint.yml` (actionlint) and `smoke.yml` (fixture runs) self-tests.

### Security

- Least-privilege `permissions` and `timeout-minutes` on every job.
- All `inputs.*` moved out of `run:` text into `env:`.

## Earlier

- `validate-cdk`: opt-in CDK stack tests (`run-tests`).
- `deploy-cdk`: `stacks` input (default `--all`).
- `deploy-cdk`: bundling toggle and runtime import check.
- Actions bumped to Node 24-native majors.
