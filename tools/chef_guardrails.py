#!/usr/bin/env python3
import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Finding:
    severity: str  # ERROR | WARN | INFO
    rule_id: str
    message: str
    path: str | None = None


def add(findings: list[Finding], severity: str, rule_id: str, message: str, path: Path | None = None) -> None:
    findings.append(
        Finding(
            severity=severity,
            rule_id=rule_id,
            message=message,
            path=str(path.relative_to(REPO_ROOT)) if path else None,
        )
    )


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def summarize(findings: list[Finding]) -> dict:
    return {
        "errors": sum(1 for f in findings if f.severity == "ERROR"),
        "warnings": sum(1 for f in findings if f.severity == "WARN"),
        "info": sum(1 for f in findings if f.severity == "INFO"),
    }


def check_cookbooks(findings: list[Finding]) -> None:
    cookbooks_dir = REPO_ROOT / "chef" / "cookbooks"
    if not cookbooks_dir.exists():
        add(findings, "ERROR", "chef.cookbooks_missing", "chef/cookbooks is missing.", cookbooks_dir)
        return

    recipes = sorted(cookbooks_dir.rglob("recipes/*.rb"))
    if not recipes:
        add(findings, "ERROR", "chef.recipes_missing", "No Chef recipes found under chef/cookbooks/**/recipes/.", cookbooks_dir)
        return

    for r in recipes:
        text = read_text(r)
        if "execute " in text:
            add(findings, "WARN", "chef.execute", "Avoid raw execute resources unless strictly necessary; prefer idempotent resources.", r)
        if re.search(r"mode\\s+\"0?777\"", text):
            add(findings, "ERROR", "chef.world_writable", "World-writable permissions detected; avoid mode 777.", r)


def check_readme_mentions(findings: list[Finding]) -> None:
    readme = REPO_ROOT / "README.md"
    if not readme.exists():
        return
    text = read_text(readme)
    if "TEST_MODE" not in text:
        add(findings, "WARN", "docs.test_mode", "README should document TEST_MODE=demo|production.", readme)
    if "Chef" not in text:
        add(findings, "WARN", "docs.chef", "README should mention the included Chef example and how it is validated.", readme)


def main() -> int:
    parser = argparse.ArgumentParser(description="Offline Chef guardrails for cookbook hygiene.")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--out", default="", help="Write output to a file (optional).")
    args = parser.parse_args()

    findings: list[Finding] = []
    check_cookbooks(findings)
    check_readme_mentions(findings)

    report = {"summary": summarize(findings), "findings": [asdict(f) for f in findings]}
    if args.format == "json":
        output = json.dumps(report, indent=2, sort_keys=True)
    else:
        lines = []
        for f in findings:
            where = f" ({f.path})" if f.path else ""
            lines.append(f"{f.severity} {f.rule_id}{where}: {f.message}")
        lines.append("")
        lines.append(f"Summary: {report['summary']}")
        output = "\n".join(lines)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())

