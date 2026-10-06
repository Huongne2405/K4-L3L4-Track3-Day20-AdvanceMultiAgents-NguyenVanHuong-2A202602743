"""Run remaining official jobs sequentially with quota cooldowns, without git writes.

Completed jobs and bounded agent failures are retained regardless of score.
Only API rate-limit failures are archived and retried.
Run from the repository root: python report/run_official.py
"""
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from lab.runner import run_task
from lab.tasks import ROOT, hash_skills, list_tasks


def main():
    subprocess.run(["git", "rev-parse", "--verify", "freeze"], cwd=ROOT, check=True, capture_output=True)
    frozen_hash = hash_skills(ROOT / "skills" / "auto")
    jobs = [("subagents", task.id) for task in list_tasks("eval")]
    jobs += [("skills-auto", task.id) for task in list_tasks()]
    log_path = ROOT / "report" / "official-execution.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {"cooldown_seconds": 35, "events": []}
    for condition, task_id in jobs:
        out = ROOT / "results" / condition / task_id
        if (out / "run.json").exists():
            saved = json.loads((out / "run.json").read_text())
            if saved.get("error") is None or (saved.get("error") or "").startswith("GraphRecursionError:"):
                if condition == "skills-auto":
                    assert saved["skills_sha256"] == frozen_hash and not saved["skills_modified"]
                print(f"KEEP {condition}/{task_id}: measured score={saved['passed']}/{saved['total']} error={saved['error']}", flush=True)
                continue
            raise RuntimeError(f"Unarchived failed run at {out}; review it before resuming")
        for attempt in range(1, 4):
            assert hash_skills(ROOT / "skills" / "auto") == frozen_hash
            print(f"COOLDOWN 35s before {condition}/{task_id} attempt {attempt}", flush=True)
            time.sleep(35)
            print(f"START {condition}/{task_id} attempt {attempt}", flush=True)
            record = run_task(task_id, condition, results_dir=ROOT / "results", recursion_limit=60)
            log["events"].append({
                "timestamp": datetime.now(timezone.utc).isoformat(), "condition": condition,
                "task": task_id, "attempt": attempt, "error": record["error"],
                "passed": record["passed"], "total": record["total"], "tokens": record["tokens"]["total"],
            })
            log_path.write_text(json.dumps(log, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            print(f"DONE {condition}/{task_id} score={record['passed']}/{record['total']} "
                  f"tokens={record['tokens']['total']} calls={record['tool_calls']} "
                  f"seconds={record['seconds']} error={record['error']}", flush=True)
            if record["error"] is None or (record["error"] or "").startswith("GraphRecursionError:"):
                assert not record["skills_modified"], "Agent changed sandbox skills; review run"
                break
            if "RateLimit" not in record["error"] or attempt == 3:
                raise RuntimeError(f"Review failed {condition}/{task_id}; record and trace retained")
            target = ROOT / "results" / "infrastructure-errors" / f"official-{condition}-attempt-{attempt}" / task_id
            if target.exists():
                raise RuntimeError(f"Archive already exists: {target}")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(out), str(target))
        assert hash_skills(ROOT / "skills" / "auto") == frozen_hash
    print("OFFICIAL JOBS COMPLETE", flush=True)


if __name__ == "__main__":
    main()
