#!/usr/bin/env python3
import json
import pathlib
import re
import sys
from typing import List

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONFIG = ROOT / ".github" / "automation" / "alerts.json"

ALLOWED_KINDS = {"required_files", "ci_recent_failures", "action_required_runs", "url_health"}
ALLOWED_PHASES = {"discovery", "build"}
ALLOWED_SEVERITIES = {"low", "medium", "high", "critical"}


def is_discovery_phase() -> bool:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    return "## Status: 🔍 Discovery" in readme


def add(errs: List[str], msg: str) -> None:
    errs.append(msg)


def main() -> int:
    errs: List[str] = []

    if not CONFIG.exists():
        print(f"ERROR: missing {CONFIG}")
        return 1

    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {CONFIG}: {exc}")
        return 1

    if cfg.get("schema_version") != 1:
        add(errs, "schema_version must be 1")

    phase = cfg.get("project_phase")
    if phase not in ALLOWED_PHASES:
        add(errs, f"project_phase must be one of {sorted(ALLOWED_PHASES)}")

    cooldown = cfg.get("cooldown_hours")
    if not isinstance(cooldown, int) or cooldown < 1 or cooldown > 168:
        add(errs, "cooldown_hours must be an integer in [1, 168]")

    alerts = cfg.get("alerts")
    if not isinstance(alerts, list) or not alerts:
        add(errs, "alerts must be a non-empty array")
        alerts = []

    ids = set()
    for i, alert in enumerate(alerts):
        where = f"alerts[{i}]"
        if not isinstance(alert, dict):
            add(errs, f"{where} must be an object")
            continue

        aid = alert.get("id")
        if not isinstance(aid, str) or not re.fullmatch(r"[a-z0-9-]{3,64}", aid):
            add(errs, f"{where}.id must match [a-z0-9-]{{3,64}}")
        elif aid in ids:
            add(errs, f"duplicate alert id: {aid}")
        else:
            ids.add(aid)

        kind = alert.get("kind")
        if kind not in ALLOWED_KINDS:
            add(errs, f"{where}.kind must be one of {sorted(ALLOWED_KINDS)}")

        sev = alert.get("severity")
        if sev not in ALLOWED_SEVERITIES:
            add(errs, f"{where}.severity must be one of {sorted(ALLOWED_SEVERITIES)}")

        title = alert.get("issue_title")
        if not isinstance(title, str) or not title.strip():
            add(errs, f"{where}.issue_title must be a non-empty string")

        if kind == "required_files":
            files = alert.get("files")
            if not isinstance(files, list) or not files:
                add(errs, f"{where}.files must be a non-empty array")
            else:
                for f in files:
                    if not isinstance(f, str) or not f.strip() or pathlib.Path(f).is_absolute():
                        add(errs, f"{where}.files contains invalid path: {f!r}")

        if kind in {"ci_recent_failures", "action_required_runs", "url_health"}:
            wh = alert.get("window_hours")
            if not isinstance(wh, int) or wh < 1 or wh > 168:
                add(errs, f"{where}.window_hours must be integer in [1, 168]")

        if kind == "url_health":
            url = alert.get("url")
            if not isinstance(url, str) or not re.match(r"^https?://", url):
                add(errs, f"{where}.url must be http(s) URL")

    # Discovery safety guard: disallow URL checks while repo is in discovery phase.
    if is_discovery_phase() and any(a.get("kind") == "url_health" for a in alerts if isinstance(a, dict)):
        add(errs, "url_health checks are out-of-scope during discovery phase")

    if errs:
        print("Configuration validation failed:")
        for e in errs:
            print(f" - {e}")
        return 1

    print("alerts.json is valid and in-scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
