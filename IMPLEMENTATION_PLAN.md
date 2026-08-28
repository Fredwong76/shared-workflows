# Shared Workflows Implementation Plan

> **Goal**: Standardize Python deployments and reduce agentic workflow token usage by 35-50%

**Status**: 🟡 In Progress  
**Last Updated**: 2026-08-28  
**Owner**: Fredwong76

---

## Table of Contents

- [Overview](#overview)
- [Phase 1: Foundation](#phase-1-foundation--week-1)
- [Phase 2: Optimization](#phase-2-optimization--week-1-2)
- [Phase 3: Documentation & Versioning](#phase-3-documentation--versioning--week-2)
- [Phase 4: Observability & Safety](#phase-4-observability--safety--week-2)
- [Phase 5: Dependency Management](#phase-5-dependency-management--week-3)
- [Phase 6: Code Quality & Standards](#phase-6-code-quality--standards--week-3)
- [Phase 7: Advanced Deployment Patterns](#phase-7-advanced-deployment-patterns--week-4)
- [Phase 8: Monitoring & Metrics](#phase-8-monitoring--metrics--week-4)
- [Phase 9: Review & Release](#phase-9-review--release--week-4)
- [Compatibility Matrix](#compatibility-matrix)
- [Known Consumers](#known-consumers)

---

## Overview

This repository provides reusable GitHub Actions workflow templates for Python-based CI/CD automation. The implementation plan standardizes these workflows to reduce:

- 🔴 **Setup duplication** across workflows (15-20% token savings)
- 🟡 **Dependency installation overhead** (10-15% token savings)
- 🟢 **Failed deployments requiring re-runs** (prevents cascading failures)

### Key Principles

1. **Backward Compatibility**: All changes maintain existing caller contracts
2. **Optional Enhancements**: New features are opt-in via inputs
3. **Semantic Versioning**: Tag releases (v1.0.0, v1.1.0, v2.0.0)
4. **Zero Breaking Changes**: Callers can upgrade at their pace

---

## Phase 1: Foundation — Week 1

**Goal**: Establish composite actions to eliminate setup duplication  
**Token Savings**: ~15-20% per run  
**Total Effort**: 50 minutes  
**Risk**: ✅ None (new files, no existing changes)

### 1.1 Create: `.github/actions/setup-python-env/`

**Status**: ⬜ Not Started

- **Description**: Reusable composite action for Python + pip cache setup
- **File**: `.github/actions/setup-python-env/action.yml`
- **Effort**: 30 mins
- **Acceptance Criteria**:
  - [ ] Action accepts `python-version` input (default: 3.12)
  - [ ] Action accepts `cache-dependency-path` input (default: requirements.txt)
  - [ ] Caches pip dependencies using actions/setup-python@v5
  - [ ] Displays Python version after setup
  - [ ] Action can be called from any workflow: `uses: ./.github/actions/setup-python-env`
  - [ ] Tested in at least one workflow

### 1.2 Create: `.github/actions/setup-aws-oidc/`

**Status**: ⬜ Not Started

- **Description**: Reusable composite action for AWS OIDC authentication
- **File**: `.github/actions/setup-aws-oidc/action.yml`
- **Effort**: 20 mins
- **Acceptance Criteria**:
  - [ ] Action accepts `role-arn` input (required)
  - [ ] Action accepts `aws-region` input (default: ap-southeast-1)
  - [ ] Configures AWS credentials via OIDC using aws-actions/configure-aws-credentials@v4
  - [ ] Verifies credentials with `aws sts get-caller-identity`
  - [ ] Action can be called from deployment workflows

### 1.3 Refactor: Update All Workflows to Use Composite Actions

**Status**: ⬜ Not Started

- **Workflows to update**: ci-python.yml, validate-cdk.yml, deploy-cdk.yml, deploy-s3-site.yml, monitor-kiro.yml
- **Effort**: 30 mins (across all workflows)
- **Acceptance Criteria**:
  - [ ] `ci-python.yml` uses `setup-python-env`
  - [ ] `validate-cdk.yml` uses `setup-python-env`
  - [ ] `deploy-cdk.yml` uses `setup-python-env` + `setup-aws-oidc`
  - [ ] `deploy-s3-site.yml` uses `setup-aws-oidc`
  - [ ] `monitor-kiro.yml` uses `setup-python-env`
  - [ ] All workflows maintain same inputs/outputs (backward compatible)
  - [ ] Existing callers (ai-diary, etc.) continue to work without changes

### 1.4 Testing & Validation

**Status**: ⬜ Not Started

- **Effort**: 20 mins
- **Acceptance Criteria**:
  - [ ] Run `ai-diary` CI workflow successfully with updated templates
  - [ ] Run `ai-diary` deploy workflow successfully with updated templates
  - [ ] Verify no new permissions required
  - [ ] Measure token usage reduction (if available)

---

## Phase 2: Optimization — Week 1-2

**Goal**: Enhance test coverage, reduce false negatives  
**Token Savings**: ~5-10% (prevents re-runs from version incompatibilities)  
**Total Effort**: 1.5 hours

### 2.1 Enhance: `ci-python.yml` with Matrix Testing

**Status**: ⬜ Not Started

- **Description**: Test against multiple Python versions (3.10, 3.11, 3.12)
- **Effort**: 15 mins
- **Acceptance Criteria**:
  - [ ] Add `strategy.matrix.python-version: ['3.10', '3.11', '3.12']`
  - [ ] Default behavior unchanged (single version for existing callers)
  - [ ] Test passes on all three versions
  - [ ] `ai-diary` continues to work without changes

### 2.2 Enhance: `ci-python.yml` with Linting & Type Checking

**Status**: ⬜ Not Started

- **Description**: Optional pre-test linting and type-check steps
- **Effort**: 30 mins
- **New Inputs Required**:
  - `enable-linting` (default: false)
  - `enable-type-check` (default: false)
  - `source-path` (default: src)
- **Acceptance Criteria**:
  - [ ] Add linting job using `ruff check`
  - [ ] Add type-check job using `mypy`
  - [ ] New inputs have sensible defaults (off by default)
  - [ ] Existing callers unaffected
  - [ ] Document in README how to enable in calling repos

### 2.3 Refactor: Consolidate CDK Workflows

**Status**: ⬜ Not Started

- **Description**: Merge `validate-cdk.yml` + `deploy-cdk.yml` into single `deploy-cdk.yml` with mode input
- **Effort**: 45 mins
- **Strategy**: Keep `validate-cdk.yml` as wrapper (NO breaking changes)
- **New Inputs Required**:
  - `mode` (validate | deploy, default: deploy)
- **Acceptance Criteria**:
  - [ ] Create new `deploy-cdk.yml` with consolidated setup (Python + Node.js)
  - [ ] Add conditional job for validate-only mode
  - [ ] Add conditional job for deploy (only runs if mode=deploy)
  - [ ] Keep `validate-cdk.yml` as wrapper calling new workflow with mode=validate
  - [ ] `ai-diary` calls to both workflows still work
  - [ ] Documentation updated with new workflow structure

---

## Phase 3: Documentation & Versioning — Week 2

**Goal**: Reduce misconfiguration, standardize usage  
**Total Effort**: 2 hours

### 3.1 Add: `TROUBLESHOOTING.md`

**Status**: ⬜ Not Started

- **Effort**: 1 hour
- **Content Coverage**:
  - [ ] OIDC configuration errors (most common issue)
  - [ ] CDK synthesis timeouts and solutions
  - [ ] S3 deployment permission errors
  - [ ] Git commit failures in monitor-kiro
  - [ ] Cache-related issues
  - [ ] Python version incompatibilities
- **Acceptance Criteria**:
  - [ ] Each issue has: cause, symptoms, fix, links to relevant docs
  - [ ] Includes AWS IAM policy examples
  - [ ] Linked from README

### 3.2 Add: `VERSIONING.md`

**Status**: ⬜ Not Started

- **Effort**: 30 mins
- **Content Coverage**:
  - [ ] Semantic versioning strategy (v1.0.0, v1.1.0, v2.0.0)
  - [ ] Development branch policy (@main for dev, @v1.x for prod)
  - [ ] Release process (tag creation, changelog updates)
  - [ ] Migration guide for callers (how to upgrade versions)
- **Acceptance Criteria**:
  - [ ] Clear examples of safe (@vX.Y.Z) and unsafe (@main) usage
  - [ ] Release process documented
  - [ ] Linked from README

### 3.3 Add: `CHANGELOG.md`

**Status**: ⬜ Not Started

- **Effort**: 20 mins
- **Content Coverage**:
  - [ ] Unreleased section (for current work)
  - [ ] v1.0.0 section (initial release)
  - [ ] Breaking changes flagged clearly
  - [ ] Upgrade notes for callers
- **Acceptance Criteria**:
  - [ ] Follows [Keep a Changelog](https://keepachangelog.com) format
  - [ ] Updated with each phase completion
  - [ ] Linked from README

### 3.4 Enhance: `README.md` with Quick-Start Templates

**Status**: ⬜ Not Started

- **Effort**: 45 mins
- **Content Coverage**:
  - [ ] Add "Quick Start" section for each workflow
  - [ ] Minimal example for Python testing
  - [ ] Minimal example with linting/type-check
  - [ ] Minimal example for CDK deployment
  - [ ] Minimal example for S3 deployment
  - [ ] Minimal example for monitoring
  - [ ] Add "Upgrade Guide" section
- **Acceptance Criteria**:
  - [ ] Each example is copy-paste ready
  - [ ] Examples reference latest stable version (@v1.x.x)
  - [ ] Examples show optional inputs

---

## Phase 4: Observability & Safety — Week 2

**Goal**: Prevent silent failures, enable faster debugging  
**Token Savings**: Prevents cascading failures, faster MTTR  
**Total Effort**: 1.5 hours

### 4.1 Enhance: All Workflows with Failure Notifications

**Status**: ⬜ Not Started

- **Description**: Composite action for post-job notifications on failure
- **File**: `.github/actions/notify-failure/action.yml`
- **Effort**: 30 mins
- **Acceptance Criteria**:
  - [ ] Create composite action that logs failure summary
  - [ ] Action accepts optional `webhook-url` input (for Slack/etc)
  - [ ] Captures: repo, branch, author, run URL
  - [ ] Add to all CI/CD workflows: ci-python.yml, deploy-cdk.yml, deploy-s3-site.yml
  - [ ] Triggers only on failure

### 4.2 Create: `verify-deployment.yml` Workflow

**Status**: ⬜ Not Started

- **Description**: Post-deployment health checks
- **File**: `.github/workflows/verify-deployment.yml`
- **Effort**: 1 hour
- **Inputs Required**:
  - `health-check-url` (required) - e.g. https://api.example.com/health
  - `max-retries` (default: 5)
  - `retry-delay-seconds` (default: 10)
- **Acceptance Criteria**:
  - [ ] Workflow accepts health-check URL
  - [ ] Polls URL with exponential backoff
  - [ ] Fails if health check doesn't pass after max retries
  - [ ] Can be used as `needs:` dependency in deployment workflows
  - [ ] Example added to README showing chained deployment + verification

---

## Phase 5: Dependency Management — Week 3

**Goal**: Support multiple Python package managers, enable reproducible builds  
**Token Savings**: ~10-15% (faster installs with locked versions)  
**Total Effort**: 45 mins

### 5.1 Enhance: `setup-python-env` with Lockfile Support

**Status**: ⬜ Not Started

- **Description**: Update composite action to support poetry, pipenv
- **Effort**: 45 mins
- **New Inputs Required**:
  - `package-manager` (pip | poetry | pipenv, default: pip)
  - `cache-dependency-path` (auto-detected if omitted)
- **Acceptance Criteria**:
  - [ ] Action detects and caches `requirements.lock`
  - [ ] Action detects and caches `poetry.lock`
  - [ ] Action detects and caches `Pipfile.lock`
  - [ ] Falls back to default cache path if lockfile not found
  - [ ] All three package managers tested
  - [ ] Documentation updated

---

## Phase 6: Code Quality & Standards — Week 3

**Goal**: Enforce consistency, catch regressions early  
**Total Effort**: 1 hour

### 6.1 Create: `code-quality.yml` Workflow

**Status**: ⬜ Not Started

- **Description**: Centralized security + coverage checks
- **File**: `.github/workflows/code-quality.yml`
- **Effort**: 1 hour
- **Inputs Required**:
  - `python-version` (default: 3.12)
  - `test-path` (default: tests/)
  - `source-path` (default: src/)
  - `min-coverage` (default: 80)
- **Acceptance Criteria**:
  - [ ] Security scanning with `bandit`
  - [ ] Coverage reporting with `pytest-cov`
  - [ ] Coverage threshold enforcement
  - [ ] Optional CodeCov integration
  - [ ] Runs as separate job in CI workflows

---

## Phase 7: Advanced Deployment Patterns — Week 4

**Goal**: Support multi-environment deployments, manual approval gates  
**Total Effort**: 45 mins

### 7.1 Create: `deploy-with-approval.yml` Workflow

**Status**: ⬜ Not Started

- **Description**: Deployment with manual approval step
- **File**: `.github/workflows/deploy-with-approval.yml`
- **Effort**: 45 mins
- **Inputs Required**:
  - `environment` (staging | production, required)
  - `cdk-directory` (default: cdk)
  - `aws-region` (default: ap-southeast-1)
- **Acceptance Criteria**:
  - [ ] Uses GitHub environment protection rules
  - [ ] Requires approval before production deployment
  - [ ] Shows deployment summary before approval
  - [ ] Logs approver info
  - [ ] Example added to README

---

## Phase 8: Monitoring & Metrics — Week 4

**Goal**: Track workflow performance, identify optimization opportunities  
**Total Effort**: 1 hour

### 8.1 Create: `log-metrics` Composite Action

**Status**: ⬜ Not Started

- **Description**: Log workflow performance metrics
- **File**: `.github/actions/log-metrics/action.yml`
- **Effort**: 30 mins
- **Metrics to Capture**:
  - [ ] Job duration
  - [ ] Runner info
  - [ ] Disk usage
  - [ ] Cache hit/miss stats
- **Acceptance Criteria**:
  - [ ] Action outputs duration-seconds
  - [ ] Logs to workflow summary
  - [ ] Can be added as final step to any workflow

### 8.2 Add: Workflow Performance Tracking

**Status**: ⬜ Not Started

- **Description**: Add metrics logging to all workflows
- **Effort**: 30 mins
- **Acceptance Criteria**:
  - [ ] All workflows use `log-metrics` action
  - [ ] Track token usage trends (manual tracking via workflow logs)
  - [ ] Document baseline metrics for comparison

---

## Phase 9: Review & Release — Week 4

**Goal**: Validate all changes, tag stable release  
**Total Effort**: 2 hours

### 9.1 Comprehensive Testing

**Status**: ⬜ Not Started

- **Effort**: 1 hour
- **Test Checklist**:
  - [ ] Run `ai-diary` CI workflow (full test)
  - [ ] Run `ai-diary` validation workflow
  - [ ] Run `ai-diary` deploy workflow (staging)
  - [ ] Test all workflows with various Python versions
  - [ ] Test composite actions in isolation
  - [ ] Verify no new permissions required
  - [ ] Verify backward compatibility with v1.0.0

### 9.2 Documentation Review

**Status**: ⬜ Not Started

- **Effort**: 30 mins
- **Review Checklist**:
  - [ ] README is complete and accurate
  - [ ] TROUBLESHOOTING covers common issues
  - [ ] VERSIONING strategy is clear
  - [ ] CHANGELOG is up-to-date
  - [ ] All code examples are tested
  - [ ] No broken links

### 9.3 Release v1.0.0 → v2.0.0 (or v1.x.x)

**Status**: ⬜ Not Started

- **Effort**: 30 mins
- **Release Checklist**:
  - [ ] All phases complete and tested
  - [ ] CHANGELOG updated with all changes
  - [ ] Git tag created: `git tag -a v2.0.0 -m "Composite actions, matrix testing, improved docs, failure notifications"`
  - [ ] Tag pushed: `git push origin v2.0.0`
  - [ ] Release notes posted to team
  - [ ] Migration guide provided for callers

### 9.4 Communicate & Support

**Status**: ⬜ Not Started

- **Effort**: 30 mins
- **Communication**:
  - [ ] Post release announcement to team
  - [ ] Show token savings metrics
  - [ ] Provide migration guide with examples
  - [ ] Link to troubleshooting guide
  - [ ] Offer support for caller migrations

---

## Compatibility Matrix

This table shows the compatibility status of each phase with known consumers.

| Phase | ai-diary | Others | Status |
|-------|----------|--------|--------|
| 1: Composite Actions | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 2.1: Matrix Testing | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 2.2: Linting/Type-Check | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 2.3: Consolidate CDK | ✅ Safe* | ✅ Safe* | ⬜ Not Started |
| 3: Documentation | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 4: Observability | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 5: Lockfile Support | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 6: Code Quality | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 7: Approval Gates | ✅ Safe | ✅ Safe | ⬜ Not Started |
| 8: Metrics | ✅ Safe | ✅ Safe | ⬜ Not Started |

**\* Using wrapper pattern (validate-cdk.yml stays as wrapper calling deploy-cdk.yml with mode=validate)**

---

## Known Consumers

### ai-diary

**Usage**:
- `.github/workflows/ci.yml` → calls `ci-python.yml@main` + `validate-cdk.yml@main`
- `.github/workflows/deploy.yml` → calls `deploy-cdk.yml@main`
- `.github/workflows/deploy-site.yml` → calls `deploy-s3-site.yml@main`

**Current Ref**: `@main` (development ref)

**Migration Path**:
1. After Phase 1: Can optionally upgrade to `@v1.1.0` (composite actions)
2. After Phase 9: Should upgrade to `@v2.0.0` (all enhancements)

**Contact**: @Fredwong76

---

## Release Timeline

- **Week 1** (Aug 28 - Sep 3):
  - [ ] Phase 1: Composite Actions (estimated tag: v1.1.0)
  - [ ] Phase 2.1-2.2: Enhanced CI workflow (estimated tag: v1.2.0)

- **Week 2** (Sep 4 - Sep 10):
  - [ ] Phase 2.3: Consolidated CDK workflows (estimated tag: v1.3.0)
  - [ ] Phase 3: Documentation & Versioning (estimated tag: v1.4.0)

- **Week 3** (Sep 11 - Sep 17):
  - [ ] Phase 4: Observability (estimated tag: v1.5.0)
  - [ ] Phase 5: Dependency Management (estimated tag: v1.6.0)

- **Week 4** (Sep 18 - Sep 24):
  - [ ] Phase 6: Code Quality (estimated tag: v1.7.0)
  - [ ] Phase 7: Deployment Patterns (estimated tag: v1.8.0)
  - [ ] Phase 8: Metrics (estimated tag: v1.9.0)

- **Final** (Sep 25+):
  - [ ] Phase 9: Review & Release v2.0.0 (or bump to appropriate version)

---

## Progress Tracking

### Summary

| Phase | Status | % Complete | Last Updated |
|-------|--------|-----------|--------------|
| 1 | ⬜ Not Started | 0% | - |
| 2 | ⬜ Not Started | 0% | - |
| 3 | ⬜ Not Started | 0% | - |
| 4 | ⬜ Not Started | 0% | - |
| 5 | ⬜ Not Started | 0% | - |
| 6 | ⬜ Not Started | 0% | - |
| 7 | ⬜ Not Started | 0% | - |
| 8 | ⬜ Not Started | 0% | - |
| 9 | ⬜ Not Started | 0% | - |

**Overall**: 🔴 0% Complete

### Recent Activity

- 2026-08-28: Created implementation plan document

---

## How to Update This Document

1. **When starting a phase**: Update status to 🟡 In Progress
2. **When completing a task**: Check box `[x]` and update % complete
3. **When completing a phase**: Update status to 🟢 Complete
4. **After each release**: Update "Recent Activity" section
5. **For blockers**: Add section below with issue link

---

## Known Issues & Blockers

*None at this time*

---

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Reusable Workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows)
- [Composite Actions](https://docs.github.com/en/actions/creating-actions/creating-a-composite-action)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

---

**Last Updated**: 2026-08-28  
**Next Review**: After Phase 1 completion
