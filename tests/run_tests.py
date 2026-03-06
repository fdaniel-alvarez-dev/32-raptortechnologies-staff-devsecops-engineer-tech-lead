#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = REPO_ROOT / "artifacts"


def run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        env=os.environ.copy(),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def fail(message: str, *, output: str | None = None, code: int = 1) -> None:
    print(f"FAIL: {message}")
    if output:
        print(output.rstrip())
    raise SystemExit(code)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"Invalid JSON: {path}", output=str(exc))
    return {}


def require_file(path: Path, description: str) -> None:
    if not path.exists():
        fail(f"Missing {description}: {path}")


def demo_mode() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = ARTIFACTS_DIR / "chef_guardrails.json"

    guard = run([sys.executable, "tools/chef_guardrails.py", "--format", "json", "--out", str(report_path)])
    if guard.returncode != 0:
        fail("Chef guardrails failed (demo mode must be offline).", output=guard.stdout)

    report = load_json(report_path)
    if report.get("summary", {}).get("errors", 0) != 0:
        fail("Chef guardrails reported errors.", output=json.dumps(report.get("findings", []), indent=2))

    for required in ["NOTICE.md", "COMMERCIAL_LICENSE.md", "GOVERNANCE.md"]:
        require_file(REPO_ROOT / required, required)

    license_text = (REPO_ROOT / "LICENSE").read_text(encoding="utf-8", errors="replace")
    if "it.freddy.alvarez@gmail.com" not in license_text:
        fail("LICENSE must include the commercial licensing contact email.")

    print("OK: demo-mode tests passed (offline).")


def production_mode() -> None:
    if os.environ.get("PRODUCTION_TESTS_CONFIRM") != "1":
        fail(
            "Production-mode tests require an explicit opt-in.",
            output=(
                "Set `PRODUCTION_TESTS_CONFIRM=1` and rerun:\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 python3 tests/run_tests.py\n"
            ),
            code=2,
        )

    ran_external_integration = False

    if os.environ.get("CHEF_VALIDATE") == "1":
        chef = shutil.which("chef-client")
        if chef is None:
            fail(
                "CHEF_VALIDATE=1 requires Chef (chef-client).",
                output="Install Chef Workstation/Infra Client and rerun production mode, or unset CHEF_VALIDATE.",
                code=2,
            )
        ran_external_integration = True

        cookbook = REPO_ROOT / "chef" / "cookbooks" / "db_lab"
        if not cookbook.exists():
            fail("Cookbook missing.", output=str(cookbook))

        solo = run(
            [
                chef,
                "-z",
                "-o",
                "db_lab::default",
                "-c",
                "/dev/null",
                "-l",
                "warn",
            ],
            cwd=cookbook,
        )
        if solo.returncode != 0:
            fail(
                "chef-client local run failed.",
                output=(
                    "Chef local mode executes on your machine. Use a disposable environment.\n\n" + solo.stdout
                ),
            )

    if not ran_external_integration:
        fail(
            "No external integration checks were executed in production mode.",
            output=(
                "Enable at least one real integration:\n"
                "- Set `CHEF_VALIDATE=1` to run a local Chef validation (requires chef-client).\n\n"
                "Then rerun:\n"
                "  TEST_MODE=production PRODUCTION_TESTS_CONFIRM=1 CHEF_VALIDATE=1 python3 tests/run_tests.py\n"
            ),
            code=2,
        )

    print("OK: production-mode tests passed (integrations executed).")


def main() -> None:
    mode = os.environ.get("TEST_MODE", "demo").strip().lower()
    if mode not in {"demo", "production"}:
        fail("Invalid TEST_MODE. Expected 'demo' or 'production'.", code=2)

    if mode == "demo":
        demo_mode()
        return

    production_mode()


if __name__ == "__main__":
    main()

