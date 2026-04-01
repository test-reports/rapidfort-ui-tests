# rapidfort-ui-tests

UI smoke and regression checks for `rapidfort.com`, plus a static dashboard history published from the `test-reports` branch.

## Local workflow

Install dependencies, run the tests, then generate the dashboard:

```bash
pip install -r requirements.txt
python -m playwright install chromium
pytest
python -m scripts.generate_dashboard
python -m scripts.build_pages_site
```

Raw test outputs are written to `reports/`.
The publishable static site is assembled in `site/`.

## GitHub Pages

The GitHub Actions workflow in `.github/workflows/ci-regression-tests-report.yml` follows a regression-first CI flow with dashboard publishing:

- push runs the full regression suite on `macos-latest`
- pull requests and manual runs keep using the smoke suite
- `pytest` produces raw test artifacts in `reports/`
- `python -m scripts.generate_dashboard` turns those artifacts into static dashboard files
- `python -m scripts.build_pages_site` prepares a GitHub Pages site in `site/`
- GitHub Actions publishes each run to `test-reports/<suite>/<run-id>/`
- GitHub Actions refreshes `test-reports/<suite>/latest/` as the stable dashboard URL

Set the repository Pages source to the `test-reports` branch, rooted at `/`. If you want to override the target URL under test, add a repository variable named `BASE_URL`. The workflow also requires the repository secret `RAPIDFORT_TOKEN` for checkout and branch publishing.