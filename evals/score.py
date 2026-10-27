"""Summarize paired human judgments; never generate or grade agent responses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PureWindowsPath
from statistics import fmean
import sys


class ScoreError(ValueError):
    """The experiment cannot be compared as recorded."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ScoreError(message)


def nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def unique_object(items: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in items:
        require(key not in result, f"Duplicate JSON field: {key}.")
        result[key] = value
    return result


def validate_suite(suite: object) -> dict:
    require(isinstance(suite, dict), "Cases must be a JSON object.")
    require(type(suite.get("schema_version")) is int and suite["schema_version"] == 1,
            "Unsupported cases schema_version.")
    cases = suite.get("cases")
    require(isinstance(cases, list) and bool(cases), "Cases must be a nonempty list.")
    indexed = {}
    for case in cases:
        require(isinstance(case, dict), "Each case must be an object.")
        case_id = case.get("id")
        require(nonempty(case_id), "Each case needs an id.")
        require(case_id not in indexed, f"Duplicate case: {case_id}.")
        require(type(case.get("control")) is bool, f"{case_id}: control must be boolean.")
        for field in ("category", "prompt", "setup"):
            require(nonempty(case.get(field)), f"{case_id}: missing {field}.")
        criteria = case.get("criteria")
        require(isinstance(criteria, list) and bool(criteria), f"{case_id}: empty criteria.")
        criterion_ids = set()
        for criterion in criteria:
            require(isinstance(criterion, dict), f"{case_id}: invalid criterion.")
            criterion_id = criterion.get("id")
            require(nonempty(criterion_id), f"{case_id}: criterion needs an id.")
            require(criterion_id not in criterion_ids, f"{case_id}: duplicate criterion.")
            require(nonempty(criterion.get("text")), f"{case_id}: criterion needs text.")
            require(type(criterion.get("critical")) is bool,
                    f"{case_id}/{criterion_id}: critical must be boolean.")
            criterion_ids.add(criterion_id)
        indexed[case_id] = case
    return indexed


def summarize(suite: object, scores: object, artifact_root: Path) -> dict:
    cases = validate_suite(suite)
    require(isinstance(scores, dict), "Scores must be a JSON object.")
    require(type(scores.get("schema_version")) is int and scores["schema_version"] == 1,
            "Unsupported scores schema_version.")
    runs = scores.get("runs")
    require(isinstance(runs, list), "runs must be a list.")
    result = {
        "status": "not_measured",
        "note": "No agent evaluations recorded; behavioral impact is unmeasured.",
        "coverage": {"represented": 0, "total": len(cases), "missing": list(cases)},
        "pairs": 0,
        "model": None,
        "conditions": None,
        "groups": None,
        "per_case": {},
    }
    if not runs:
        return result

    artifact_root = artifact_root.resolve()
    pairs = {}
    models = set()
    artifacts = set()
    for run in runs:
        require(isinstance(run, dict), "Each run must be an object.")
        case_id = run.get("case_id")
        require(nonempty(case_id) and case_id in cases, "Unknown or invalid case_id.")
        for field in ("pair_id", "model", "setup_id", "artifact"):
            require(nonempty(run.get(field)), f"{case_id}: missing {field}.")
        condition = run.get("condition")
        require(condition in ("baseline", "skill"), f"{case_id}: invalid condition.")
        key = (case_id, run["pair_id"])
        pair = pairs.setdefault(key, {})
        require(condition not in pair, f"{case_id}/{run['pair_id']}: duplicate condition.")

        relative = run["artifact"]
        require(not Path(relative).is_absolute() and not PureWindowsPath(relative).drive
                and "\\" not in relative, f"{case_id}: use a relative forward-slash artifact path.")
        artifact = (artifact_root / relative).resolve()
        require(artifact.is_relative_to(artifact_root), f"{case_id}: artifact escapes score directory.")
        require(artifact.is_file() and artifact.stat().st_size > 0,
                f"{case_id}: artifact must be an existing nonempty file.")
        require(artifact not in artifacts, f"{case_id}: each run needs a distinct artifact.")
        artifacts.add(artifact)

        grades = run.get("criteria")
        expected = {item["id"] for item in cases[case_id]["criteria"]}
        require(isinstance(grades, dict) and set(grades) == expected,
                f"{case_id}: record exactly the case's criteria.")
        for criterion_id, grade in grades.items():
            require(isinstance(grade, dict) and type(grade.get("passed")) is bool,
                    f"{case_id}/{criterion_id}: passed must be boolean.")
            require(nonempty(grade.get("evidence")), f"{case_id}/{criterion_id}: missing evidence note.")
        pair[condition] = {
            "model": run["model"],
            "setup_id": run["setup_id"],
            "score": fmean(int(grade["passed"]) for grade in grades.values()),
            "critical_failure": any(item["critical"] and not grades[item["id"]]["passed"]
                                    for item in cases[case_id]["criteria"]),
        }
        models.add(run["model"])

    for (case_id, pair_id), pair in pairs.items():
        require(set(pair) == {"baseline", "skill"}, f"{case_id}/{pair_id}: incomplete pair.")
        for field in ("model", "setup_id"):
            require(pair["baseline"][field] == pair["skill"][field],
                    f"{case_id}/{pair_id}: different {field} within pair.")
    require(len(models) == 1, "Use a separate score file for each model version.")

    per_case = {}
    for case_id, case in cases.items():
        trials = [pair for (current_id, _), pair in pairs.items() if current_id == case_id]
        if not trials:
            continue
        per_case[case_id] = {"control": case["control"], "pairs": len(trials)}
        for condition in ("baseline", "skill"):
            per_case[case_id][condition] = {
                "mean_criterion_score": fmean(pair[condition]["score"] for pair in trials),
                "critical_failure_rate": fmean(int(pair[condition]["critical_failure"]) for pair in trials),
            }
    conditions = {}
    for condition in ("baseline", "skill"):
        conditions[condition] = {
            metric: fmean(case[condition][metric] for case in per_case.values())
            for metric in ("mean_criterion_score", "critical_failure_rate")
        }
    groups = {}
    for label, is_control in (("target_cases", False), ("control_cases", True)):
        members = {case_id: case for case_id, case in per_case.items()
                   if case["control"] == is_control}
        if members:
            groups[label] = {"case_ids": list(members)}
            for condition in ("baseline", "skill"):
                groups[label][condition] = {
                    metric: fmean(case[condition][metric] for case in members.values())
                    for metric in ("mean_criterion_score", "critical_failure_rate")
                }
            groups[label]["skill_minus_baseline"] = (
                groups[label]["skill"]["mean_criterion_score"]
                - groups[label]["baseline"]["mean_criterion_score"])
    result.update({
        "status": "human_scores_summarized",
        "note": "Descriptive human scores only; no significance or general effectiveness claim.",
        "coverage": {"represented": len(per_case), "total": len(cases),
                     "missing": [case_id for case_id in cases if case_id not in per_case]},
        "pairs": len(pairs),
        "model": next(iter(models)),
        "conditions": conditions,
        "groups": groups,
        "skill_minus_baseline": conditions["skill"]["mean_criterion_score"]
                               - conditions["baseline"]["mean_criterion_score"],
        "per_case": per_case,
    })
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scores", type=Path)
    parser.add_argument("--cases", type=Path, default=Path(__file__).with_name("cases.json"))
    args = parser.parse_args()
    try:
        suite = json.loads(args.cases.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
        scores = json.loads(args.scores.read_text(encoding="utf-8-sig"), object_pairs_hook=unique_object)
        result = summarize(suite, scores, args.scores.parent)
    except (OSError, ValueError) as error:
        print(f"Invalid evaluation: {error}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
