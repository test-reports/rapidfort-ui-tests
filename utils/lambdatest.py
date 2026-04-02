import json
import os
from datetime import datetime
from urllib.parse import quote

import pytest


LT_WS_ENDPOINT = "wss://cdp.lambdatest.com/playwright"
BROWSER_NAME_MAP = {
    "chromium": "pw-chromium",
    "firefox": "pw-firefox",
    "webkit": "pw-webkit",
}


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value.strip() if isinstance(value, str) else default


def _is_truthy(value: str) -> bool:
    return value.lower() in {"1", "true", "yes", "on"}


def pytest_addoption(parser):
    parser.addoption(
        "--cloud",
        action="store_true",
        default=False,
        help="Run tests on cloud provider (LambdaTest).",
    )
    parser.addoption(
        "--lambdatest",
        action="store_true",
        default=False,
        help="Run tests on LambdaTest cloud.",
    )
    parser.addoption(
        "--local",
        action="store_true",
        default=False,
        help="Force local browser execution (disable cloud).",
    )


def _lt_enabled(request) -> bool:
    if request.config.getoption("--local"):
        return False
    if request.config.getoption("--cloud") or request.config.getoption("--lambdatest"):
        return True
    return _is_truthy(_env("LT_ENABLED", "false"))


@pytest.fixture(scope="session")
def connect_options(browser_name, request):
    if not _lt_enabled(request):
        return None
    if not _env("LT_USERNAME") or not _env("LT_ACCESS_KEY"):
        raise pytest.UsageError(
            "LambdaTest is enabled but LT_USERNAME/LT_ACCESS_KEY are missing."
        )

    lt_options = {
        "platform": _env("LT_PLATFORM", "macOS Ventura"),
        "projectName": _env("LT_PROJECT", "rapidfort-ui-tests"),
        "build": _env(
            "LT_BUILD", f"rapidfort-ui-tests-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        ),
        "name": _env("LT_TEST_NAME", "pytest-playwright run"),
        "user": _env("LT_USERNAME"),
        "accessKey": _env("LT_ACCESS_KEY"),
        "w3c": True,
    }

    capabilities = {
        "browserName": BROWSER_NAME_MAP.get(browser_name, browser_name),
        "browserVersion": _env("LT_BROWSER_VERSION", "latest"),
        "LT:Options": lt_options,
    }
    encoded_caps = quote(json.dumps(capabilities))
    return {"ws_endpoint": f"{LT_WS_ENDPOINT}?capabilities={encoded_caps}"}
