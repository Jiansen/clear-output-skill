#!/usr/bin/env python3
"""Aggregate recorded model reviews; does not rejudge responses."""

import json
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "evals/results"


def read(name):
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def status(verdicts):
    if "fail" in verdicts:
        return "fail"
    if "needs_review" in verdicts:
        return "needs_review"
    return "pass"


def summarize():
    mapping = read("blind-map.json")
    reviews = read("blind-review.json")["reviews"]
    corrections = {(c["sample_id"], c["invariant_index"]): c["verdict"] for c in read("adjudications.json")["changes"]}
    assert len(reviews) == len(mapping) == len({r["sample_id"] for r in reviews})
    groups = {}
    for review in reviews:
        sample_id = review["sample_id"]
        condition = mapping[sample_id]["condition"]
        group = groups.setdefault(condition, {"independent_review": {"pass": 0, "fail": 0, "needs_review": 0}, "adjudicated": {"pass": 0, "fail": 0, "needs_review": 0}, "clarity_scores": []})
        original = [item["verdict"] for item in review["invariants"]]
        revised = [corrections.get((sample_id, item["index"]), item["verdict"]) for item in review["invariants"]]
        group["independent_review"][status(original)] += 1
        group["adjudicated"][status(revised)] += 1
        group["clarity_scores"].append(review["clarity"])
    for group in groups.values():
        group["clarity_mean"] = round(mean(group.pop("clarity_scores")), 3)
    retest = read("retest-review.json")["reviews"]
    retest_counts = {"pass": 0, "fail": 0, "needs_review": 0}
    assert len(retest) == len({r["id"] for r in retest})
    for review in retest:
        retest_counts[status([item["verdict"] for item in review["invariants"]])] += 1
    return {"initial_pilot": groups, "revised_skill_retest": retest_counts, "human_comprehension_test": False}


if __name__ == "__main__":
    print(json.dumps(summarize(), ensure_ascii=False, indent=2))
