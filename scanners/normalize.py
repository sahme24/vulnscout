import json
from pathlib import Path

def context(path, line, n=15):
    lines = Path(path).read_text(errors="ignore").splitlines()
    start, end = max(0, line - 1 - n), min(len(lines), line + n)
    return "\n".join(f"{i+1}: {lines[i]}" for i in range(start, end))

findings = []

for file in ["results/semgrep_dvwa.json", "results/semgrep_flask.json"]:
    for r in json.load(open(file))["results"]:
        findings.append({
            "tool": "semgrep",
            "file": r["path"],
            "line": r["start"]["line"],
            "rule": r["check_id"],
            "severity": r["extra"].get("severity"),
            "cwe": r["extra"].get("metadata", {}).get("cwe"),
            "message": r["extra"]["message"],
            "code_context": context(r["path"], r["start"]["line"]),
        })

for r in json.load(open("results/bandit_flask.json"))["results"]:
    findings.append({
        "tool": "bandit",
        "file": r["filename"],
        "line": r["line_number"],
        "rule": r["test_id"],
        "severity": r["issue_severity"],
        "cwe": r.get("issue_cwe", {}).get("id"),
        "message": r["issue_text"],
        "code_context": context(r["filename"], r["line_number"]),
    })

for i, f in enumerate(findings):
    f["id"] = i

json.dump(findings, open("results/findings.json", "w"), indent=2)
print(f"{len(findings)} findings")
