# CTRF Jira Reporter: Upload Any Framework's Test Results to Jira with Testream

This repository is a practical **CTRF + Jira integration example** using [`@testream/cli`](https://docs.testream.app/reporters/cli). It demonstrates a framework-agnostic pattern: generate a [CTRF](https://ctrf.io) JSON report, then upload it to Testream so results appear in Jira.

This example uses **Python + pytest** with [`pytest-json-ctrf`](https://pypi.org/project/pytest-json-ctrf/), but the same upload model works for any test tool that can output CTRF.

If you are searching for **"CTRF Jira reporter"**, **"pytest results to Jira"**, or **"framework-agnostic test reporting to Jira"**, this repo is the implementation template.

## Why this example is useful

- **Framework-agnostic**: Works beyond native reporters.
- **CI-portable**: Same upload command can run in GitHub Actions, CircleCI, GitLab, Jenkins, or Azure.
- **Fallback path**: Useful when your framework has no native Testream reporter.
- **Real triage demo**: Intentional failing tests show Jira failure insights.

## What is Testream?

[Testream](https://testream.app) is an automated test management and reporting platform for Jira teams. It ingests test results from native integrations and CTRF uploads, then provides failure diagnostics, trends, and release quality visibility in Jira.

If this sample repository is not the framework you need, browse all native reporters in the Testream docs: <https://docs.testream.app/>.

### Watch Testream in action

Click to see how Testream turns raw CI test results into actionable Jira insights (failures, trends, and release visibility):  
[![Watch the video](https://img.youtube.com/vi/5sDao2Q8k1k/maxresdefault.jpg)](https://www.youtube.com/watch?v=5sDao2Q8k1k)

Install **[Testream Automated Test Management and Reporting for Jira](https://marketplace.atlassian.com/apps/3048460704/testream-automated-test-management-and-reporting-for-jira)** in your Jira workspace to view uploaded runs.

## When to use CTRF + CLI uploader

Use this approach when:

- Your framework does not have a native Testream reporter.
- You already generate CTRF in your pipeline.
- You want one upload pattern across multiple CI providers.

If a native reporter exists (Vitest, Jest, Playwright, Cypress, Mocha, WebdriverIO), use that first for simpler setup and richer auto-metadata.

## Project structure

```text
src/
  cart.py
  product.py
  discount.py
tests/
  test_cart.py     - Passing + intentional failure
  test_product.py  - Passing + intentional failure
  test_discount.py - Passing + intentional failure
requirements.txt
.github/workflows/ctrf.yml
.env.example
```

The intentional failures help verify how failed test output appears in Testream/Jira.

## Quick start: CTRF to Jira reporting

### 1. Create your Testream project and API key

1. Sign in at [testream.app](https://testream.app).
2. Create a project.
3. Copy your API key.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Generate CTRF report from pytest

```bash
python -m pytest --ctrf ctrf/ctrf-report.json
```

### 4. Upload CTRF report to Testream

```bash
TESTREAM_API_KEY=<your key> npx @testream/cli \
  --report-path ctrf/ctrf-report.json \
  --test-tool pytest \
  --app-name ctrf-jira-reporter-example \
  --test-environment local \
  --test-type unit \
  --fail-on-error
```

## GitHub Actions setup

The workflow at `.github/workflows/ctrf.yml` runs on push, pull request, and manual dispatch.

Add this repository secret:

**Settings -> Secrets and variables -> Actions -> New repository secret**

| Name               | Value                 |
| ------------------ | --------------------- |
| `TESTREAM_API_KEY` | Your Testream API key |

Important CI behavior in this repo:

- Pytest step uses `continue-on-error: true` so upload still runs if tests fail.
- Upload step includes `--fail-on-error` to fail CI on upload issues.
- CI metadata (branch, SHA, repository URL, build number, build URL) is auto-detected.

## Other CI providers

You can run the same CLI uploader in other systems:

- CircleCI
- Bitbucket Pipelines
- GitLab CI
- Jenkins
- Azure Pipelines

Use the same parameters and map provider-specific env vars for branch/SHA/build metadata when needed.

## How results appear in Jira

After connecting Testream to Jira, you get:

- Dashboard pass/fail summaries
- Failure diagnostics with stack traces
- Trend analytics across runs
- Jira issue creation from failed tests

## Troubleshooting

### Upload command runs but no data appears

- Verify `TESTREAM_API_KEY`.
- Verify `ctrf/ctrf-report.json` exists and is valid JSON.
- Verify Testream project is connected to the correct Jira workspace.

### CI uploads missing metadata

- Ensure provider env vars are present or pass metadata flags explicitly.

### Should I use native reporter instead?

- Yes, if available for your framework. Keep CTRF flow for unsupported stacks.

## FAQ

### Is this only for pytest?

No. Pytest is the example here, but any framework that outputs CTRF can use this flow.

### Why include failing tests?

To demonstrate end-to-end failure triage in Testream/Jira.

### Is this production-ready?

It is an example with production-style CI wiring intended to be adapted.

## CTRF Jira reporting alternatives (quick view)

| Approach                           | Benefit                                       | Tradeoff                                |
| ---------------------------------- | --------------------------------------------- | --------------------------------------- |
| Native Testream reporter           | Lowest setup for supported frameworks         | Not available for every framework       |
| Custom uploader scripts            | Flexible                                      | More maintenance and edge-case handling |
| CTRF + `@testream/cli` (this repo) | Framework-agnostic, CI-portable, standardized | Requires CTRF generation step           |

## Related links

- Testream app: <https://testream.app>
- Testream Automated Test Management and Reporting for Jira: <https://marketplace.atlassian.com/apps/3048460704/testream-automated-test-management-and-reporting-for-jira>
- CTRF format: <https://ctrf.io>
- CLI uploader docs: <https://docs.testream.app/reporters/cli>
