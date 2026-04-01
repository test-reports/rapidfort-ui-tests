import shutil

from config.paths import HTML_DIR, SCREENSHOTS_DIR, SITE_DIR, TRACES_DIR


def reset_site_directory():
    if SITE_DIR.exists():
        shutil.rmtree(SITE_DIR)
    SITE_DIR.mkdir(parents=True, exist_ok=True)


def copy_tree_if_exists(source, destination):
    if source.exists():
        shutil.copytree(source, destination)


def write_root_index():
    index_html = """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta http-equiv="refresh" content="0; url=./html/index.html" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RapidFort UI Test Reports</title>
  </head>
  <body>
    <p>Redirecting to the latest dashboard...</p>
    <p><a href="./html/index.html">Open dashboard</a></p>
  </body>
</html>
"""
    (SITE_DIR / "index.html").write_text(index_html)


def write_nojekyll():
    (SITE_DIR / ".nojekyll").write_text("")


def main():
    if not HTML_DIR.exists():
        raise FileNotFoundError(
            f"Dashboard output not found at {HTML_DIR}. Run scripts/generate_dashboard.py first."
        )

    reset_site_directory()
    copy_tree_if_exists(HTML_DIR, SITE_DIR / "html")
    copy_tree_if_exists(SCREENSHOTS_DIR, SITE_DIR / "screenshots")
    copy_tree_if_exists(TRACES_DIR, SITE_DIR / "traces")
    write_root_index()
    write_nojekyll()

    print(f"Built GitHub Pages site at {SITE_DIR}")


if __name__ == "__main__":
    main()
