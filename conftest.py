import json
from datetime import datetime
import re

import pytest

from config.paths import (
    JUNIT_DIR,
    PROJECT_ROOT,
    REPORTS_DIR,
    SCREENSHOTS_DIR,
    TRACES_DIR,
)
from config.settings import BASE_URL, BROWSER
from pages.home_page import HomePage

ARTIFACTS_JSON = JUNIT_DIR / "failure_artifacts.json"
DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
BROWSER_MAP = {
    "safari": "webkit",
    "webkit": "webkit",
    "chromium": "chromium",
    "firefox": "firefox",
}


def pytest_configure(config):
    cli_args = list(getattr(config.invocation_params, "args", ()))
    browser_arg_passed = any(
        arg == "--browser" or arg.startswith("--browser=") for arg in cli_args
    )
    if not browser_arg_passed:
        config.option.browser = [BROWSER_MAP.get(BROWSER, "chromium")]


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


@pytest.fixture
def page_object(page):
    page.set_viewport_size(DESKTOP_VIEWPORT)
    return HomePage(page)


@pytest.fixture
def home_page(page_object):
    page_object.open()
    return page_object


@pytest.fixture
def smoke_setup(page_object):
    response = page_object.page.goto(BASE_URL, wait_until="domcontentloaded")
    return page_object, response


def _load_artifacts():
    if not ARTIFACTS_JSON.exists():
        return {}
    return json.loads(ARTIFACTS_JSON.read_text())


def _save_artifacts(data):
    JUNIT_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACTS_JSON.write_text(json.dumps(data, indent=2))


def _safe_name(nodeid: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "-", nodeid)


def _build_trace_name(nodeid: str) -> str:
    test_name = nodeid.split("::")[-1]
    parts = [part for part in test_name.split("[") if part]
    base_name = re.sub(r"[^A-Za-z0-9_]+", "_", parts[0]).strip("_")
    browser = ""
    if "[" in test_name and test_name.endswith("]"):
        browser = re.sub(r"[^A-Za-z0-9_]+", "_", test_name.rsplit("[", 1)[-1].rstrip("]"))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if browser:
        return f"{base_name}_{browser}_{timestamp}.zip"
    return f"{base_name}_{timestamp}.zip"


def _is_smoke_test(item) -> bool:
    return item.fspath.basename == "test_smoke.py"


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
