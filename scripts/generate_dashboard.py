import json
from datetime import datetime
import xml.etree.ElementTree as ET
from zoneinfo import ZoneInfo

from config.paths import HTML_DIR, JUNIT_DIR, REPORTS_DIR, SCREENSHOTS_DIR, TRACES_DIR


RESULTS_XML = JUNIT_DIR / "results.xml"
SUMMARY_JSON = HTML_DIR / "summary.json"
HISTORY_JSON = HTML_DIR / "history.json"
ARTIFACTS_JSON = JUNIT_DIR / "failure_artifacts.json"
ARTIFACTS_GLOB = "failure_artifacts_*.json"
DASHBOARD_HTML = HTML_DIR / "index.html"
LOS_ANGELES_TZ = ZoneInfo("America/Los_Angeles")


def load_artifacts():
    artifacts = {}
    worker_artifact_files = sorted(JUNIT_DIR.glob(ARTIFACTS_GLOB))
    for artifacts_file in worker_artifact_files:
        try:
            data = json.loads(artifacts_file.read_text())
        except json.JSONDecodeError:
            print(f"Warning: skipping malformed artifact file {artifacts_file}")
            continue
        if isinstance(data, dict):
            artifacts.update(data)

    if artifacts:
        return artifacts

    # Backward compatibility for historical single-file artifact format.
    if ARTIFACTS_JSON.exists():
        try:
            data = json.loads(ARTIFACTS_JSON.read_text())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            print(f"Warning: skipping malformed artifact file {ARTIFACTS_JSON}")
    return {}


def junit_nodeid(classname, name):
    return f"{classname.replace('.', '/')}.py::{name}"


def extract_error_message(testcase, details):
    failure = testcase.find("failure")
    error = testcase.find("error")
    message = ""
    if failure is not None:
        message = failure.attrib.get("message", "")
    elif error is not None:
        message = error.attrib.get("message", "")

    if message:
        return message.strip()

    lines = [line.strip() for line in details.splitlines() if line.strip()]
    assertion_lines = [line[2:].strip() for line in lines if line.startswith("E ")]
    if assertion_lines:
        return assertion_lines[0]

    relevant_lines = [
        line
        for line in lines
        if not (
            line.startswith(">")
            or line.startswith("tests/")
            or line.startswith("def ")
            or "object at 0x" in line
            or line.startswith("home_page =")
        )
    ]
    return relevant_lines[-1] if relevant_lines else ""


def clean_error_message(message):
    if not message:
        return ""

    lines = [line.strip() for line in str(message).splitlines() if line.strip()]
    assertion_lines = [line[2:].strip() for line in lines if line.startswith("E ")]
    if assertion_lines:
        return assertion_lines[0]

    filtered_lines = [
        line
        for line in lines
        if not (
            line.startswith(">")
            or line.startswith("tests/")
            or line.startswith("def ")
            or "object at 0x" in line
            or line.startswith("home_page =")
        )
    ]
    if filtered_lines:
        return filtered_lines[-1]

    return lines[-1] if lines else ""


def parse_results():
    if not RESULTS_XML.exists():
        raise FileNotFoundError(
            f"JUnit results not found at {RESULTS_XML}. Run pytest first."
        )

    root = ET.parse(RESULTS_XML).getroot()
    testsuite = root if root.tag == "testsuite" else root.find("testsuite")
    if testsuite is None:
        raise ValueError("Could not locate testsuite in JUnit XML.")

    artifacts = load_artifacts()
    suite_duration = round(float(testsuite.attrib.get("time", 0)), 3)
    results = []
    for testcase in testsuite.findall("testcase"):
        failure = testcase.find("failure")
        skipped = testcase.find("skipped")
        error = testcase.find("error")

        if failure is not None or error is not None:
            status = "failed"
            details = (
                (failure.text if failure is not None else None)
                or (error.text if error is not None else None)
                or ""
            ).strip()
        elif skipped is not None:
            status = "skipped"
            details = (skipped.text or "").strip()
        else:
            status = "passed"
            details = ""

        classname = testcase.attrib.get("classname", "")
        name = testcase.attrib.get("name", "unknown")
        nodeid = junit_nodeid(classname, name)
        artifact = artifacts.get(nodeid, {})

        results.append(
            {
                "name": name,
                "classname": classname,
                "time": round(float(testcase.attrib.get("time", 0)), 3),
                "status": status,
                "details": details,
                "errorMessage": clean_error_message(
                    artifact.get("errorMessage") or extract_error_message(testcase, details)
                ),
                "screenshot": artifact.get("screenshot", ""),
                "trace": artifact.get("trace", ""),
            }
        )

    status_order = {"failed": 0, "skipped": 1, "passed": 2}
    return (
        sorted(
            results,
            key=lambda test: (
                status_order.get(test["status"], 99),
                test["classname"],
                test["name"],
            ),
        ),
        suite_duration,
    )


def infer_test_type(results):
    test_types = {
        result["classname"].replace("tests.test_", "").replace("tests.", "")
        for result in results
        if result.get("classname")
    }
    if len(test_types) == 1:
        return next(iter(test_types))
    return "full_suite"


def infer_browser_name(results):
    for result in results:
        name = result.get("name", "")
        if "[" in name and name.endswith("]"):
            return name.rsplit("[", 1)[-1].rstrip("]")
    return "chromium"


def build_report_filename(summary):
    test_type = infer_test_type(summary["results"])
    browser = infer_browser_name(summary["results"])
    timestamp = datetime.fromisoformat(summary["generatedAt"]).strftime("%Y%m%d_%H%M%S")
    return f"rapidfort_{test_type}_{browser}_{timestamp}.html"


def build_summary(results, suite_duration=None):
    status_order = {"failed": 0, "skipped": 1, "passed": 2}
    sorted_results = sorted(
        results,
        key=lambda test: (
            status_order.get(test["status"], 99),
            test["classname"],
            test["name"],
        ),
    )
    passed = sum(1 for test in results if test["status"] == "passed")
    failed = sum(1 for test in results if test["status"] == "failed")
    skipped = sum(1 for test in results if test["status"] == "skipped")
    total = len(results)
    pass_rate = round((passed / total) * 100, 1) if total else 0
    duration = (
        round(float(suite_duration), 3)
        if suite_duration is not None
        else round(sum(test["time"] for test in results), 3)
    )
    generated_at = datetime.now(LOS_ANGELES_TZ).isoformat()
    generated_at_display = datetime.now(LOS_ANGELES_TZ).strftime("%b %-d, %Y %-I:%M %p %Z")

    return {
        "generatedAt": generated_at,
        "generatedAtDisplay": generated_at_display,
        "total": total,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "passRate": pass_rate,
        "duration": duration,
        "results": sorted_results,
    }


def load_history():
    if not HISTORY_JSON.exists():
        return []
    return json.loads(HISTORY_JSON.read_text())


def update_history(summary):
    history = load_history()
    history.append(
        {
            "generatedAt": summary["generatedAt"],
            "passRate": summary["passRate"],
            "passed": summary["passed"],
            "failed": summary["failed"],
            "skipped": summary["skipped"],
            "total": summary["total"],
        }
    )
    return history[-5:]


def render_dashboard(summary, history):
    results = json.dumps(summary["results"])
    history_data = json.dumps(history)
    generated_at = summary["generatedAtDisplay"]
    screenshots_prefix = "../screenshots"
    traces_prefix = "../traces"

    return f"""<!DOCTYPE html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RapidFort Test Dashboard</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
      tailwind.config = {{
        darkMode: "class",
        theme: {{
          extend: {{
            colors: {{
              surface: "#161b22",
              panel: "#0f1720",
              success: "#22c55e",
              failed: "#ef4444",
              skipped: "#f59e0b",
              accent: "#60a5fa"
            }}
          }}
        }}
      }};
    </script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
      body {{
        background: #0f1114;
        color: #e6e8eb;
      }}
      .chart-container {{
        position: relative;
        height: 280px;
        width: 100%;
      }}
      .glass {{
        background: rgba(22, 27, 34, 0.9);
        backdrop-filter: blur(10px);
      }}
      .summary-card {{
        background: #202735;
        border-radius: 0.875rem;
        border: 1px solid rgba(94, 114, 138, 0.45);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
      }}
      .summary-card.success {{
        border-color: rgba(34, 197, 94, 0.35);
      }}
      .summary-card.failed {{
        border-color: rgba(239, 68, 68, 0.35);
      }}
      .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        border-radius: 0.875rem;
        border: 1px solid rgba(34, 197, 94, 0.35);
        background: rgba(20, 83, 45, 0.5);
        color: #86efac;
        padding: 0.75rem 1rem;
        font-weight: 600;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
        font-size: 0.95rem;
        letter-spacing: 0.01em;
      }}
      .status-pill.failed {{
        border-color: rgba(239, 68, 68, 0.35);
        background: rgba(127, 29, 29, 0.45);
        color: #fda4af;
      }}
      .screenshot-thumb {{
        width: 96px;
        height: 64px;
        object-fit: cover;
        border-radius: 0.75rem;
        border: 1px solid rgba(148, 163, 184, 0.25);
        box-shadow: 0 10px 30px rgba(15, 23, 32, 0.45);
        transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
      }}
      .screenshot-thumb:hover {{
        transform: scale(1.04);
        border-color: rgba(96, 165, 250, 0.6);
        box-shadow: 0 14px 36px rgba(15, 23, 32, 0.6);
      }}
    </style>
  </head>
  <body class="min-h-screen">
    <div class="mx-auto max-w-7xl px-6 py-10">
      <div class="mb-6">
        <div class="status-pill {"failed" if summary["failed"] else ""}">
          <span>{"✖" if summary["failed"] else "✅"}</span>
          <span>{"Failed" if summary["failed"] else "Success"}</span>
        </div>
      </div>

      <div class="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p class="mb-2 text-xs uppercase tracking-[0.26em] text-slate-400">RapidFort UI Tests</p>
          <h1 class="text-3xl font-semibold tracking-tight text-white">Test Results Dashboard</h1>
          <p class="mt-2 text-sm text-slate-400">Generated {generated_at}</p>
        </div>
        <p class="text-xs uppercase tracking-[0.26em] text-slate-500">Pass rate {summary["passRate"]}%</p>
      </div>

      <div class="mb-8 grid gap-6 md:grid-cols-2 xl:grid-cols-4">
        <div class="summary-card p-6 text-center">
          <p class="text-4xl font-semibold tracking-tight text-white">{summary["total"]}</p>
          <p class="mt-3 text-[11px] uppercase tracking-[0.24em] text-slate-400">Tests Executed</p>
        </div>
        <div class="summary-card success p-6 text-center">
          <p class="text-4xl font-semibold tracking-tight text-emerald-400">{summary["passed"]}</p>
          <p class="mt-3 text-[11px] uppercase tracking-[0.24em] text-slate-400">Passed</p>
        </div>
        <div class="summary-card failed p-6 text-center">
          <p class="text-4xl font-semibold tracking-tight text-rose-400">{summary["failed"]}</p>
          <p class="mt-3 text-[11px] uppercase tracking-[0.24em] text-slate-400">Failed</p>
        </div>
        <div class="summary-card p-6 text-center">
          <p class="text-4xl font-semibold tracking-tight text-white">{round(summary["duration"])}</p>
          <p class="mt-2 text-sm font-medium text-slate-300">seconds</p>
          <p class="mt-2 text-[11px] uppercase tracking-[0.24em] text-slate-400">Duration</p>
        </div>
      </div>

      <div class="mb-8 grid gap-6 lg:grid-cols-2">
        <div class="glass rounded-2xl border border-slate-800 p-6 shadow-xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-semibold text-white">Result Distribution</h2>
            <span class="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">Doughnut</span>
          </div>
          <div class="chart-container">
            <canvas id="distributionChart"></canvas>
          </div>
        </div>

        <div class="glass rounded-2xl border border-slate-800 p-6 shadow-xl">
          <div class="mb-4 flex items-center justify-between">
            <h2 class="text-xl font-semibold text-white">Pass Rate Snapshot</h2>
            <span class="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">Bar</span>
          </div>
          <div class="chart-container">
            <canvas id="passRateChart"></canvas>
          </div>
        </div>
      </div>

      <div class="mb-8 glass rounded-2xl border border-slate-800 p-6 shadow-xl">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-white">Last 5 Runs</h2>
          <span class="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">Line</span>
        </div>
        <div class="chart-container">
          <canvas id="historyChart"></canvas>
        </div>
      </div>

      <div class="glass rounded-2xl border border-slate-800 p-6 shadow-xl">
        <div class="mb-4 flex items-center justify-between">
          <h2 class="text-xl font-semibold text-white">Test Case Details</h2>
          <span class="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">Detailed view</span>
        </div>
        <div class="max-h-[34rem] overflow-y-auto overflow-x-hidden rounded-lg border border-slate-800">
          <table class="min-w-full table-fixed text-left text-xs">
            <colgroup>
              <col class="w-[16%]" />
              <col class="w-[9%]" />
              <col class="w-[8%]" />
              <col class="w-[7%]" />
              <col class="w-[28%]" />
              <col class="w-[8%]" />
              <col class="w-[24%]" />
            </colgroup>
            <thead class="sticky top-0 z-10 border-b border-slate-700 bg-slate-900">
              <tr class="text-slate-400">
                <th class="px-2 py-3 font-medium">Test Name</th>
                <th class="px-2 py-3 font-medium">Suite</th>
                <th class="px-2 py-3 font-medium">Status</th>
                <th class="px-2 py-3 font-medium">Duration</th>
                <th class="px-2 py-3 font-medium">Error Message</th>
                <th class="px-2 py-3 font-medium">Screenshot</th>
                <th class="px-2 py-3 font-medium">Trace</th>
              </tr>
            </thead>
            <tbody id="resultsTable" class="divide-y divide-slate-900"></tbody>
          </table>
        </div>
      </div>
    </div>

    <script>
      const results = {results};
      const history = {history_data};

      const buildArtifactHref = (artifactPath, artifactRoot) => {{
        if (!artifactPath) {{
          return "";
        }}
        return `${{artifactRoot}}/${{artifactPath.split("/").pop()}}`;
      }};

      const toAbsoluteUrl = (href) => {{
        if (!href) {{
          return "";
        }}
        return new URL(href, window.location.href).href;
      }};

      const buildTraceViewerUrl = (href) => {{
        if (!href) {{
          return "";
        }}
        return `https://trace.playwright.dev/?trace=${{encodeURIComponent(toAbsoluteUrl(href))}}`;
      }};

      const formatSuiteName = (classname) => {{
        if (!classname) {{
          return "n/a";
        }}
        return classname.replace(/^tests\\./, "").replace(/^test_/, "");
      }};

      const statusColors = {{
        passed: "#22c55e",
        failed: "#ef4444",
        skipped: "#f59e0b"
      }};

      const tableBody = document.getElementById("resultsTable");
      results.forEach((test) => {{
        const badgeColor =
          test.status === "passed"
            ? "bg-success/15 text-success"
            : test.status === "failed"
              ? "bg-failed/15 text-failed"
              : "bg-skipped/15 text-skipped";
        const statusLabel =
          test.status === "passed"
            ? "Passed"
            : test.status === "failed"
              ? "Failed"
              : "Skipped";

        const row = document.createElement("tr");
        row.className = "border-b border-slate-900 hover:bg-slate-900/60";
        const suiteName = formatSuiteName(test.classname);
        const screenshotHref = buildArtifactHref(test.screenshot, "{screenshots_prefix}");
        const screenshotCell = test.screenshot
          ? `<a href="${{screenshotHref}}" target="_blank" rel="noreferrer" title="${{toAbsoluteUrl(screenshotHref)}}">
               <img class="screenshot-thumb" src="${{screenshotHref}}" alt="Failure screenshot for ${{test.name}}" />
             </a>`
          : `<span class="text-slate-500">-</span>`;
        const traceHref = buildArtifactHref(test.trace, "{traces_prefix}");
        const traceViewerHref = buildTraceViewerUrl(traceHref);
        const traceCell = test.trace
          ? `<div>
               <a class="text-accent underline underline-offset-4" href="${{traceViewerHref}}" target="_blank" rel="noreferrer">Viewer</a>
               <div class="mt-0.5">
                 <a class="text-slate-300 underline underline-offset-4" href="${{traceHref}}" target="_blank" rel="noreferrer">ZIP</a>
               </div>
             </div>`
          : `<span class="text-slate-500">-</span>`;
        const errorCell = test.errorMessage
          ? test.errorMessage.replaceAll("<", "&lt;").replaceAll(">", "&gt;")
          : "-";
        row.innerHTML = `
          <td class="px-2 py-2 align-top text-white"><div class="break-words leading-snug" title="${{test.name}}">${{test.name}}</div></td>
          <td class="px-2 py-2 align-top text-slate-400"><div class="break-words leading-snug" title="${{test.classname || "n/a"}}">${{suiteName}}</div></td>
          <td class="px-2 py-2"><span class="rounded-full px-2 py-0.5 text-[11px] font-medium ${{badgeColor}}">${{statusLabel}}</span></td>
          <td class="px-2 py-2 align-top text-slate-300 whitespace-nowrap">${{test.time.toFixed(3)}}s</td>
          <td class="px-2 py-2 align-top text-slate-300 break-words leading-snug">${{errorCell}}</td>
          <td class="px-2 py-2 align-top text-slate-300">${{screenshotCell}}</td>
          <td class="px-2 py-2 align-top text-slate-300 break-words">${{traceCell}}</td>
        `;
        tableBody.appendChild(row);
      }});

      new Chart(document.getElementById("distributionChart"), {{
        type: "doughnut",
        data: {{
          labels: ["Passed", "Failed", "Skipped"],
          datasets: [{{
            data: [{summary["passed"]}, {summary["failed"]}, {summary["skipped"]}],
            backgroundColor: ["#22c55e", "#ef4444", "#f59e0b"],
            borderWidth: 0
          }}]
        }},
        options: {{
          maintainAspectRatio: false,
          plugins: {{
            legend: {{
              labels: {{ color: "#cbd5e1" }}
            }}
          }}
        }}
      }});

      new Chart(document.getElementById("passRateChart"), {{
        type: "bar",
        data: {{
          labels: ["Current Run"],
          datasets: [{{
            label: "Pass Rate",
            data: [{summary["passRate"]}],
            backgroundColor: "#60a5fa",
            borderRadius: 10
          }}]
        }},
        options: {{
          maintainAspectRatio: false,
          scales: {{
            y: {{
              beginAtZero: true,
              max: 100,
              ticks: {{ color: "#94a3b8" }},
              grid: {{ color: "rgba(148, 163, 184, 0.15)" }}
            }},
            x: {{
              ticks: {{ color: "#94a3b8" }},
              grid: {{ display: false }}
            }}
          }},
          plugins: {{
            legend: {{ display: false }}
          }}
        }}
      }});

      new Chart(document.getElementById("historyChart"), {{
        type: "line",
        data: {{
          labels: history.map((run, index) => `Run ${{index + 1}}`),
          datasets: [{{
            label: "Pass Rate",
            data: history.map((run) => run.passRate),
            borderColor: "#60a5fa",
            backgroundColor: "rgba(96, 165, 250, 0.15)",
            fill: true,
            tension: 0.35,
            pointBackgroundColor: "#22c55e",
            pointBorderColor: "#22c55e"
          }}]
        }},
        options: {{
          maintainAspectRatio: false,
          scales: {{
            y: {{
              beginAtZero: true,
              max: 100,
              ticks: {{ color: "#94a3b8" }},
              grid: {{ color: "rgba(148, 163, 184, 0.15)" }}
            }},
            x: {{
              ticks: {{ color: "#94a3b8" }},
              grid: {{ display: false }}
            }}
          }},
          plugins: {{
            legend: {{
              labels: {{ color: "#cbd5e1" }}
            }}
          }}
        }}
      }});
    </script>
  </body>
</html>
"""


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    HTML_DIR.mkdir(parents=True, exist_ok=True)
    JUNIT_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    TRACES_DIR.mkdir(parents=True, exist_ok=True)

    results, suite_duration = parse_results()
    summary = build_summary(results, suite_duration=suite_duration)
    history = update_history(summary)
    report_filename = build_report_filename(summary)
    report_file = HTML_DIR / report_filename

    SUMMARY_JSON.write_text(json.dumps(summary, indent=2))
    HISTORY_JSON.write_text(json.dumps(history, indent=2))
    dashboard_html = render_dashboard(summary, history)
    DASHBOARD_HTML.write_text(dashboard_html)
    report_file.write_text(dashboard_html)

    print(f"Saved summary to {SUMMARY_JSON}")
    print(f"Saved history to {HISTORY_JSON}")
    print(f"Saved dashboard to {DASHBOARD_HTML}")
    print(f"Saved named dashboard to {report_file}")


if __name__ == "__main__":
    main()
