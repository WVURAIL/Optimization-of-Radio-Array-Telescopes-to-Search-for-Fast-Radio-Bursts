"""Convert a complete pip installation report into a dependency snapshot."""

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


def make_snapshot(report, manifest, environment):
    if report.get("version") != "1" or not report.get("install"):
        raise ValueError("Expected a nonempty pip installation report, version 1")

    resolved = {}
    for package in report["install"]:
        metadata = package["metadata"]
        name = re.sub(r"[-_.]+", "-", metadata["name"]).lower()
        version = quote(metadata["version"], safe="")
        purl = f"pkg:pypi/{name}@{version}"
        resolved[purl] = {
            "package_url": purl,
            "relationship": "direct" if package["requested"] else "indirect",
            "scope": "runtime",
        }

    repository = environment["GITHUB_REPOSITORY"]
    run_id = environment["GITHUB_RUN_ID"]
    return {
        "version": 0,
        "sha": environment["GITHUB_SHA"],
        "ref": environment["GITHUB_REF"],
        "job": {
            "id": run_id,
            "correlator": "comparison-pip-dependencies",
            "html_url": f"https://github.com/{repository}/actions/runs/{run_id}",
        },
        "detector": {
            "name": "pip-install-report",
            "version": "1.0.0",
            "url": f"https://github.com/{repository}/blob/main/.github/scripts/dependency_snapshot.py",
        },
        "scanned": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "manifests": {
            manifest: {
                "name": manifest,
                "file": {"source_location": manifest},
                "resolved": resolved,
            }
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("report", type=Path)
    parser.add_argument("manifest")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    snapshot = make_snapshot(json.loads(args.report.read_text()), args.manifest, os.environ)
    args.output.write_text(json.dumps(snapshot, indent=2) + "\n")
