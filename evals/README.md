# Evaluation protocol

This directory is a starter evaluation suite, not evidence that PatchProof
improves an agent. Every scenario is invented. Fixture setup instructions are
for the evaluator; disclose only the task prompt, ordinary repository contents,
and the case's intended inputs to the agent.

## Prepare a comparison

1. Build each tiny fixture described in `cases.json`. Freeze the repository and
   environment snapshot. Keep the grading rubric outside the agent's workspace.
2. Record the model version, agent version, tools, permissions, existing rules,
   source snapshot, and time/token limits. Use the same configuration for each
   pair, with the skill as the only deliberate difference. `setup_id` identifies
   the complete recorded setup for one case, not merely a friendly name.
3. Start independent fresh sessions. A baseline receives the prompt without
   PatchProof; the skill condition receives the same prompt and the skill. Where
   supported, invoke the skill explicitly and record that choice.
4. Run several pairs per case, alternate or randomize the order, and keep failed,
   interrupted, and successful attempts. Do not select only persuasive examples.
5. Save tool outputs, the final artifact/diff, and the transcript. An assertion
   about a check must be supported by its observed command and result.

Never run a model-proposed command on real production services or private data
for these fixtures. The cases require only disposable local resources.

## Grade observable behavior

A reviewer marks every criterion `true` or `false` and writes the observation
supporting it. Judge actual behavior and resulting artifacts, not whether the
answer repeats the skill's vocabulary. A criterion marked critical represents
an outcome that average scores must not hide.

Hide the condition labels from the reviewer when practical. Calibrate subjective
criteria with another reviewer. If evidence is missing or ambiguous, preserve
that issue in the notes; do not silently infer a pass from a plausible answer.

Record time, token use, and user interruptions alongside the artifacts when the
runner exposes them. The helper below does not aggregate those measures; review
them before deciding whether a quality gain is worth its cost.

## Score format

Copy `scores.template.json` to a new file under an ignored `evals/results/`
directory. Keep the frozen cases file in the same results bundle and pass it via
`--cases` when scoring a historical run. This prevents a later rubric revision
from silently changing the meaning of old results.

For each completed run, add a record with these fields:

```json
{
  "case_id": "C01",
  "pair_id": "trial-01",
  "condition": "baseline or skill",
  "model": "exact model version",
  "setup_id": "identifier for the frozen case and runner configuration",
  "artifact": "relative/path/to/nonempty-transcript.md",
  "criteria": {
    "criterion-id-from-cases": {
      "passed": false,
      "evidence": "Observation with a transcript location or artifact reference"
    }
  }
}
```

This is a schema illustration, not a runnable score record. Include **all** the
case's criteria. Both conditions in a pair must have the same case, model, and
setup. Artifact paths are relative to the scores file and must stay within its
directory tree. Create a separate scores file for a different model or rubric.
Add the runner configuration and skill revision to the saved artifact bundle.

## Summarize

```text
python evals/score.py evals/scores.template.json
python evals/score.py evals/results/scores.json --cases evals/results/cases.json
```

The helper rejects missing pairs, duplicate conditions, unknown criteria,
different setups/models within a pair, and missing or empty artifact files. It
cannot verify that a saved transcript is authentic or that the reviewer graded
it correctly. Artifact presence is a traceability check, not proof of quality.

For each condition, it averages criterion pass fractions within a case and then
averages across represented cases. This gives each case equal weight even if
one has more trials. It separately reports per-case critical-failure rates and
the two control cases. Target and control groups are also summarized separately,
so a target gain does not conceal a control regression in the overall average.
No statistical significance is calculated. UTF-8 files with a BOM are accepted;
duplicate JSON fields are rejected instead of silently replacing earlier values.

Exit code `0` means a valid file was summarized, including the explicit empty
template case. It does **not** mean the skill won. Exit code `2` indicates invalid
input; no comparison is emitted. A missing run must be completed or reported as
an incomplete experiment, not discarded to improve the score.

## Keep, revise, or remove

- **Keep a branch** when repeated paired runs support an improvement on its
  target behavior without unacceptable critical failures or control overhead.
- **Revise a branch** when it helps one case but introduces unnecessary questions,
  extra work, or a new failure elsewhere.
- **Remove a branch** when the default agent already behaves as well, or the
  instruction adds cost with no useful observed gain.

Small suites help find counterexamples. They do not establish general model
performance. Record limitations, all attempted runs, and reviewer disagreements
before publishing any effectiveness claim.
