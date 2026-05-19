#!/usr/bin/env python3
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone


def api(path: str):
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    url = f"https://api.github.com/repos/{repo}{path}"
    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Accept", "application/vnd.github+json")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def pct(part: int, total: int) -> float:
    return 0.0 if total == 0 else round((part / total) * 100.0, 1)


def main() -> int:
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    prs = api("/pulls?state=all&per_page=100")
    recent_auto_prs = [
        pr for pr in prs
        if pr.get("head", {}).get("ref", "").startswith("auto/remediate-")
        and datetime.fromisoformat(pr["created_at"].replace("Z", "+00:00")) >= week_ago
    ]
    auto_fixed = len([pr for pr in recent_auto_prs if pr.get("state") == "closed" and pr.get("merged_at")])

    issues = api("/issues?state=open&per_page=100&labels=automation-alert")
    blocked = 0
    unresolved = 0
    for issue in issues:
        labels = {l.get("name") for l in issue.get("labels", [])}
        unresolved += 1
        if "automation-alert:blocked" in labels or "automation-alert:automation-blocked" in labels:
            blocked += 1

    denominator = max(unresolved + auto_fixed, 1)

    report = (
        "## Weekly automation self-check\n\n"
        f"- Auto-fixed: **{pct(auto_fixed, denominator)}%** ({auto_fixed})\n"
        f"- Blocked-by-policy/manual-action: **{pct(blocked, denominator)}%** ({blocked})\n"
        f"- Unresolved open alerts: **{pct(unresolved, denominator)}%** ({unresolved})\n"
    )

    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(report)

    print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
