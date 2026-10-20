# Vehicle Telemetry: GitHub Actions + Docker CI Extension

This add-on supplies a **small, original CI demonstration** for an existing
Databricks/PySpark batch telemetry portfolio project. It is not an Azure/GM
production deployment and does not execute Databricks notebooks.

## What it checks
- Required telemetry fields and illustrative invalid readings.
- Alert boundaries used in the original synthetic dashboard: temp > 105 C,
  battery voltage < 11.8 V.
- Bronze = Silver + Quarantine counts, using the documented project metrics.

The explicit 0-20 V and 0-300 km/h validation bounds in `checks.py` are
illustrative for this exercise and may not match the original Databricks
notebook's detailed validation rules. Do not claim they are identical without
cross-checking the original notebooks.

## Add to an existing GitHub repository
Copy this folder's files into the repository **root** while preserving paths.
Make sure `.github/workflows/telemetry-ci.yml` is included in the commit.
Then push a branch or open a pull request. GitHub Actions should build the
Python test image using `Dockerfile.ci` and run tests inside that container.

## Local verification
From the repository root:

    python -m pip install -r requirements-ci.txt
    python -m pytest -q tests/

Or, with Docker installed:

    docker build -f Dockerfile.ci -t telemetry-ci:test .
    docker run --rm telemetry-ci:test

## Evidence for the Growing a Competency assignment
1. Show a readable screenshot of the `Dockerfile.ci` and workflow YAML.
2. Push to GitHub and screenshot the Actions page with a completed run.
3. Optional: deliberately modify one expected count in a test on a *temporary*
   branch, capture the failed run, then restore it and show the passing run.
4. Link to the committed `.github/workflows/telemetry-ci.yml` and tests.

**Status:** Configuration and example test suite are authored. A hosted GitHub
Actions execution is **not verified** until the user commits these files and
checks the run. No automatic deployment/CD stage is included.
