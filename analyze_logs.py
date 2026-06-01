"""
Log Analyzer — Lab 3 Phase 4: Failure Analysis
Parses JSON logs and summarizes agent performance metrics.
"""

import json
import os
import glob
from collections import defaultdict


def parse_log_file(filepath: str) -> list[dict]:
    events = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return events


def analyze(events: list[dict]) -> None:
    sessions = []
    current = None

    for ev in events:
        event_type = ev.get("event", "")
        data = ev.get("data", {})

        if event_type == "AGENT_START":
            current = {
                "input": data.get("input", ""),
                "model": data.get("model", ""),
                "steps": 0,
                "tools_called": [],
                "hallucination_flags": [],
                "outcome": "timeout",
                "answer": "",
                "timestamp": ev.get("timestamp", ""),
            }

        elif event_type == "TOOL_EXECUTION" and current:
            current["steps"] += 1
            current["tools_called"].append(data.get("tool", ""))

            # Flag potential hallucination: calculator called before calc_shipping
            if data.get("tool") == "calculator":
                if "calc_shipping" not in current["tools_called"][:-1]:
                    current["hallucination_flags"].append(
                        f"Step {current['steps']}: calculator called before calc_shipping "
                        f"(args: {data.get('args', '')})"
                    )

            # Flag tool not found errors
            obs = data.get("observation", "")
            if "not found" in obs.lower() or "Tool Error" in obs:
                current["hallucination_flags"].append(
                    f"Step {current['steps']}: {data.get('tool')} error — {obs}"
                )

        elif event_type == "AGENT_FINAL_ANSWER" and current:
            current["outcome"] = "success"
            current["answer"] = data.get("answer", "")
            sessions.append(current)
            current = None

        elif event_type == "AGENT_END" and current:
            current["outcome"] = "timeout"
            sessions.append(current)
            current = None

    # ── Summary ──────────────────────────────────────────────
    total = len(sessions)
    if total == 0:
        print("No completed agent sessions found in logs.")
        return

    successes = sum(1 for s in sessions if s["outcome"] == "success")
    timeouts = total - successes
    avg_steps = sum(s["steps"] for s in sessions) / total
    all_flags = [f for s in sessions for f in s["hallucination_flags"]]

    print("=" * 60)
    print("AGENT PERFORMANCE REPORT")
    print("=" * 60)
    print(f"Total sessions : {total}")
    print(f"Success        : {successes} ({successes/total*100:.0f}%)")
    print(f"Timeout        : {timeouts}")
    print(f"Avg steps/task : {avg_steps:.1f}")
    print(f"Hallucinations : {len(all_flags)}")

    print("\n── Session Details ─────────────────────────────────────")
    for i, s in enumerate(sessions, 1):
        status = "✅" if s["outcome"] == "success" else "❌"
        print(f"\n[{i}] {status} \"{s['input'][:60]}...\"" if len(s["input"]) > 60
              else f"\n[{i}] {status} \"{s['input']}\"")
        print(f"     Steps: {s['steps']} | Tools: {s['tools_called']}")
        if s["answer"]:
            print(f"     Answer: {s['answer']}")
        if s["hallucination_flags"]:
            print(f"     ⚠️  Failures:")
            for flag in s["hallucination_flags"]:
                print(f"        - {flag}")

    print("\n── Root Cause Analysis ─────────────────────────────────")
    if all_flags:
        print("Detected failure patterns:")
        for flag in all_flags:
            print(f"  ⚠️  {flag}")
        print("\nRecommended fix for Agent v2:")
        print("  → Add explicit tool ordering rule in system prompt")
        print("  → Instruct agent: never assume numeric values, always call tools first")
    else:
        print("No hallucinations detected in this log.")
    print("=" * 60)


if __name__ == "__main__":
    log_dir = "logs"
    log_files = sorted(glob.glob(os.path.join(log_dir, "*.log")))

    if not log_files:
        print(f"No log files found in '{log_dir}/'")
    else:
        print(f"Analyzing {len(log_files)} log file(s)...\n")
        all_events = []
        for f in log_files:
            all_events.extend(parse_log_file(f))
        analyze(all_events)
