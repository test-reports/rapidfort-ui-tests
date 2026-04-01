# rapidfort-ui-tests

UI smoke and regression checks for `rapidfort.com`, plus a static dashboard that can be published to GitHub Pages.

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

The GitHub Actions workflow in `.github/workflows/deploy-pages.yml` keeps concerns separated:

- `pytest` produces raw test artifacts in `reports/`
- `python -m scripts.generate_dashboard` turns those artifacts into static dashboard files
- `python -m scripts.build_pages_site` prepares a GitHub Pages site in `site/`
- GitHub Actions deploys only the `site/` artifact to Pages

Set the repository Pages source to GitHub Actions. If you want to override the target URL under test, add a repository variable named `BASE_URL`.