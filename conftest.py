import json
from datetime import datetime
import hashlib
import os
from pathlib import Path
import re

import pytest

from config.paths import (
    JUNIT_DIR,
    PROJECT_ROOT,
    REPORTS_DIR,
    SCREENSHOTS_DIR,
    TRACES_DIR,
)
from config.settings import BROWSER

pytest_plugins = ("utils.lambdatest",)

ARTIFACTS_PREFIX = "failure_artifacts_"
ARTIFACTS_GLOB = f"{ARTIFACTS_PREFIX}*.json"
DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
BROWSER_MAP = {
    "safari": "webkit",
    "webkit": "webkit",
    "chromium": "chromium",
    "firefox": "firefox",
}


def pytest_addoption(parser):
    parser.addoption(
        "--env",
        action="store",
        choices=("dev", "qa", "staging"),
        help="Target environment base URL mapping: dev, qa, staging.",
    )


def pytest_configure(config):
    target_env = config.getoption("--env")
    if target_env:
        os.environ["TEST_ENV"] = target_env

    cli_args = list(getattr(config.invocation_params, "args", ()))
    browser_arg_passed = any(
        arg == "--browser" or arg.startswith("--browser=") for arg in cli_args
    )
    if not browser_arg_passed:
        config.option.browser = [BROWSER_MAP.get(BROWSER, "chromium")]


def pytest_sessionstart(session):
    # Cleanup only in controller/local mode to avoid workers racing cleanup.
    if hasattr(session.config, "workerinput"):
        return
    if not JUNIT_DIR.exists():
        return
    for artifacts_file in JUNIT_DIR.glob(ARTIFACTS_GLOB):
        artifacts_file.unlink(missing_ok=True)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "viewport": DESKTOP_VIEWPORT,
        "screen": DESKTOP_VIEWPORT,
        "device_scale_factor": 1,
        "is_mobile": False,
        "has_touch": False,
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {
        **browser_type_launch_args,
        "headless": False,
    }


@pytest.fixture(autouse=True)
def _set_playwright_timeout(page):
    page.set_default_timeout(5_000)


@pytest.fixture(autouse=True)
def trace_context(context, request):
    request.node._trace_path = TRACES_DIR / _build_trace_name(request.node.nodeid)
    request.node._trace_failed = False
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield
    should_save_trace = _is_smoke_test(request.node) or request.node._trace_failed
    if should_save_trace:
        TRACES_DIR.mkdir(parents=True, exist_ok=True)
        context.tracing.stop(path=str(request.node._trace_path))
        artifacts = _load_artifacts()
        existing_artifact = artifacts.get(request.node.nodeid, {})
        artifacts[request.node.nodeid] = {
            "screenshot": existing_artifact.get("screenshot", ""),
            "trace": str(request.node._trace_path.relative_to(PROJECT_ROOT)),
            "errorMessage": existing_artifact.get("errorMessage", ""),
        }
        _save_artifacts(artifacts)
    else:
        context.tracing.stop()


def _load_artifacts():
    artifacts_file = _artifact_file_path()
    if not artifacts_file.exists():
        return {}
    try:
        return json.loads(artifacts_file.read_text())
    except json.JSONDecodeError:
        return {}


def _save_artifacts(data):
    JUNIT_DIR.mkdir(parents=True, exist_ok=True)
    artifacts_file = _artifact_file_path()
    tmp_file = artifacts_file.with_suffix(f"{artifacts_file.suffix}.tmp")
    tmp_file.write_text(json.dumps(data, indent=2))
    tmp_file.replace(artifacts_file)


def _worker_id() -> str:
    return os.getenv("PYTEST_XDIST_WORKER", "main")


def _artifact_file_path() -> "Path":
    return JUNIT_DIR / f"{ARTIFACTS_PREFIX}{_worker_id()}.json"


def _safe_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", nodeid)


def _build_trace_name(nodeid: str) -> str:
    test_name = nodeid.split("::")[-1]
    parts = [part for part in test_name.split("[") if part]
    base_name = re.sub(r"[^A-Za-z0-9_]+", "_", parts[0]).strip("_")
    browser = ""
    if "[" in test_name and test_name.endswith("]"):
        browser = re.sub(r"[^A-Za-z0-9_]+", "_", test_name.rsplit("[", 1)[-1].rstrip("]"))
    worker = _worker_id()
    node_hash = hashlib.sha1(nodeid.encode("utf-8")).hexdigest()[:8]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    if browser:
        return f"{base_name}_{browser}_{worker}_{timestamp}_{node_hash}.zip"
    return f"{base_name}_{worker}_{timestamp}_{node_hash}.zip"


def _is_smoke_test(item) -> bool:
    return item.get_closest_marker("smoke") is not None


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when != "call":
        return

    if report.passed:
        return

    item._trace_failed = True

    page = item.funcargs.get("page")
    if page is None:
        return

    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    screenshot_name = f"{_safe_name(item.nodeid)}.png"
    screenshot_path = SCREENSHOTS_DIR / screenshot_name
    page.set_viewport_size(DESKTOP_VIEWPORT)
    page.wait_for_timeout(250)
    page.screenshot(path=str(screenshot_path), full_page=False)

    artifacts = _load_artifacts()
    artifacts[item.nodeid] = {
        "screenshot": str(screenshot_path.relative_to(PROJECT_ROOT)),
        "trace": str(item._trace_path.relative_to(PROJECT_ROOT)),
        "errorMessage": str(report.longreprtext).strip(),
    }
    _save_artifacts(artifacts)
