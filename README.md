# CTRF Reporter for Jira Teams using Testream

This repository demonstrates how to upload test results to [Testream](https://testream.app) using the **CLI reporter** (`@testream/upload-action`) — the framework-agnostic approach that works with *any* test tool that can produce a [CTRF](https://ctrf.io) JSON report.

The project uses **Python + pytest** as the test framework — a language Testream does not natively support yet — paired with [`pytest-json-ctrf`](https://pypi.org/project/pytest-json-ctrf/) to generate a CTRF report. The report is then uploaded to Testream via the `testream/upload-action` GitHub Action (or CLI for other CI providers).

## What is Testream?

[Testream](https://testream.app) is a test reporting tool for Jira teams. It imports CI/CD test results from native reporters (Playwright, Jest, Cypress, and others) as well as any tool that can produce a **CTRF JSON** report, giving your team failure inspection, trends, and release visibility directly inside Jira — without manual test case management.

Once configured, every test run streams structured results to Testream. Failed tests appear in Jira with the full error message and stack trace attached, so triage starts with complete context.

## Why the CLI approach?

The CTRF + CLI workflow is the right choice when:

- Your test framework does **not** have a native Testream reporter (e.g. pytest, RSpec, Go test, Rust cargo-test)
- You want to use a **different CI provider** (CircleCI, Bitbucket Pipelines, GitLab CI, Jenkins, Azure Pipelines)
- You already have a CTRF report and just need to upload it

If Testream has a native reporter for your tool (Playwright, Vitest, Jest, Cypress, Mocha, WebdriverIO), prefer that over the CLI approach — it is simpler and captures more metadata automatically.

## Project structure

```
src/
  cart.py          — Cart class: add/remove items, calculate totals, checkout
  product.py       — Product dataclass, format_price, validate_product, get_discounted_price
  discount.py      — Coupon dataclass, apply_percentage, apply_fixed, validate_coupon
tests/
  test_cart.py     — Cart tests (passing + 1 intentional failure)
  test_product.py  — Product tests (passing + 1 intentional failure)
  test_discount.py — Discount tests (passing + 1 intentional failure)
requirements.txt
.github/workflows/ctrf.yml
.env.example
```

The three intentionally failing tests exist so you can see exactly what a failed test looks like inside Testream and Jira — with the error diff and stack trace surfaced in the dashboard.

## Getting started

### 1. Install Testream for Jira

Install the **[Testream for Jira](https://marketplace.atlassian.com/apps/3048460704/testream-for-jira)** app from the Atlassian Marketplace into your Jira workspace. This is what surfaces test results, failure details, trends, and dashboards inside Jira.

### 2. Create a Testream project

1. Sign in at [testream.app](https://testream.app) (free plan available).
2. Create a project and copy your API key.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

```bash
cp .env.example .env
# then set TESTREAM_API_KEY=<your key> in .env
```

### 5. Run the tests and generate a CTRF report

```bash
python -m pytest --ctrf ctrf/ctrf-report.json
```

This writes a CTRF JSON to `ctrf/ctrf-report.json`.

### 6. Upload the report to Testream

```bash
TESTREAM_API_KEY=your_api_key_here npx @testream/upload-action \
  --report-path ctrf/ctrf-report.json \
  --test-tool pytest \
  --app-name ctrf-jira-reporter-example \
  --test-environment local \
  --test-type unit
```

Results will appear in your Testream project immediately.

## CI with GitHub Actions

The workflow at `.github/workflows/ctrf.yml` runs all tests on every push and pull request. The only secret you need to add is your Testream API key:

**Settings → Secrets and variables → Actions → New repository secret**

| Name | Value |
|---|---|
| `TESTREAM_API_KEY` | your Testream API key |

All other metadata (branch, commit SHA, build number, build URL, repository URL) is resolved automatically by `@testream/upload-action` from the GitHub Actions environment — nothing else to configure.

## Other CI providers

Use `@testream/upload-action` as a CLI in any CI provider that has Node.js available.

### CircleCI

```yaml
# .circleci/config.yml
version: 2.1
jobs:
  test:
    docker:
      - image: cimg/python:3.12
    steps:
      - checkout
      - run: pip install -r requirements.txt
      - run: python -m pytest --ctrf ctrf/ctrf-report.json || true
      - run:
          name: Upload to Testream
          command: |
            npx @testream/upload-action \
              --report-path ctrf/ctrf-report.json \
              --test-tool pytest \
              --api-key $TESTREAM_API_KEY \
              --branch $CIRCLE_BRANCH \
              --commit-sha $CIRCLE_SHA1 \
              --repository-url $CIRCLE_REPOSITORY_URL \
              --build-number $CIRCLE_BUILD_NUM \
              --build-url $CIRCLE_BUILD_URL \
              --test-environment ci
```

### Bitbucket Pipelines

```yaml
# bitbucket-pipelines.yml
image: python:3.12
pipelines:
  default:
    - step:
        name: Tests
        script:
          - pip install -r requirements.txt
          - python -m pytest --ctrf ctrf/ctrf-report.json || true
          - npx @testream/upload-action
              --report-path ctrf/ctrf-report.json
              --test-tool pytest
              --api-key $TESTREAM_API_KEY
              --branch $BITBUCKET_BRANCH
              --commit-sha $BITBUCKET_COMMIT
              --build-number $BITBUCKET_BUILD_NUMBER
              --test-environment ci
```

### GitLab CI

```yaml
# .gitlab-ci.yml
test:
  image: python:3.12
  script:
    - pip install -r requirements.txt
    - python -m pytest --ctrf ctrf/ctrf-report.json || true
    - npx @testream/upload-action
        --report-path ctrf/ctrf-report.json
        --test-tool pytest
        --api-key $TESTREAM_API_KEY
        --branch $CI_COMMIT_BRANCH
        --commit-sha $CI_COMMIT_SHA
        --repository-url $CI_PROJECT_URL
        --build-number $CI_PIPELINE_ID
        --build-url $CI_PIPELINE_URL
        --test-environment ci
```

### Jenkins

```groovy
// Jenkinsfile
pipeline {
  agent { label 'python' }
  stages {
    stage('Test') {
      steps {
        sh 'pip install -r requirements.txt'
        sh 'python -m pytest --ctrf ctrf/ctrf-report.json || true'
      }
    }
    stage('Upload to Testream') {
      steps {
        withCredentials([string(credentialsId: 'TESTREAM_API_KEY', variable: 'TESTREAM_API_KEY')]) {
          sh """
            npx @testream/upload-action \\
              --report-path ctrf/ctrf-report.json \\
              --test-tool pytest \\
              --api-key \$TESTREAM_API_KEY \\
              --branch \${env.BRANCH_NAME} \\
              --build-number \${env.BUILD_NUMBER} \\
              --build-url \${env.BUILD_URL} \\
              --test-environment ci
          """
        }
      }
    }
  }
}
```

### Azure Pipelines

```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: UsePythonVersion@0
    inputs:
      versionSpec: '3.12'

  - script: pip install -r requirements.txt
    displayName: Install dependencies

  - script: python -m pytest --ctrf ctrf/ctrf-report.json || true
    displayName: Run tests

  - script: |
      npx @testream/upload-action \
        --report-path ctrf/ctrf-report.json \
        --test-tool pytest \
        --api-key $(TESTREAM_API_KEY) \
        --branch $(Build.SourceBranchName) \
        --commit-sha $(Build.SourceVersion) \
        --build-number $(Build.BuildNumber) \
        --build-url "$(System.TeamFoundationCollectionUri)$(System.TeamProject)/_build/results?buildId=$(Build.BuildId)" \
        --test-environment ci
    displayName: Upload to Testream
    env:
      TESTREAM_API_KEY: $(TESTREAM_API_KEY)
```

## Viewing results in Jira

Once tests are uploaded, open your Testream project and connect it to your Jira workspace. With the **[Testream for Jira](https://marketplace.atlassian.com/apps/3048460704/testream-for-jira)** app installed you get:

- **Dashboard** — pass rates, failure counts, flaky test detection, and execution summaries at a glance
- **Failure Insights** — inspect failed tests with the full error, stack trace, and diff
- **Trends & Analytics** — pass/fail trends, duration patterns, and suite growth over custom date ranges
- **Test Suite Changes** — see which tests were added or removed between runs
- **Release Visibility** — link test runs to Jira releases to track quality before shipping
- **Jira Issues** — create issues directly from any failed test with failure context pre-filled

See the [Testream CLI reporter docs](https://docs.testream.app/reporters/cli) for the full list of upload options.
