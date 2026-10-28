# PatchProof

**Choose the next useful action before making the next edit.**

[Tiếng Việt](README.vi.md) · [The skill](skills/feedback-to-fix/SKILL.md) ·
[Design tradeoffs](docs/design-options.vi.md) · [Evaluation](evals/README.md)

[Initial review and open limitations](docs/review.vi.md)

PatchProof is an instruction-only Agent Skill that helps AI coding agents
respond to feedback, make focused code changes, and report what was verified.
It guides the agent to inspect, experiment, implement, ask, verify, or finish
according to the available evidence and the consequences of being wrong.

It targets three observable failures:

- Acting on an assumed cause without a useful check.
- Making an incomplete patch or expanding beyond the requested behavior.
- Claiming an outcome broader than the evidence supports.

There is one skill, a collection of invented evaluation scenarios, and a small
offline helper for summarizing human-graded paired runs. No model API, account,
or background service is required to read or use the skill.

## Quick start

From your project directory, run:

```bash
npx skills add giakhanhzzz/PatchProof --skill feedback-to-fix --copy
```

The installer requires Node.js 22.20 or later. Select your coding agent if
prompted. Review the [skill instructions](skills/feedback-to-fix/SKILL.md)
before use. The command installs in the current project by default; manual
installation is described below.

## Why another skill?

Planning, debugging, and verification skills already exist. PatchProof explores
a narrower question: **which action is useful now, and when is more process
unnecessary?** It includes straightforward control cases where extra questions,
planning, or investigation would be a regression.

This is a testable design hypothesis, not a claim of a novel algorithm or a
proven improvement over an unmodified agent. See the
[alternatives and their limitations](docs/design-options.vi.md).

## Installation in a repository

For a coding agent that discovers repository-local skills in `.agents/skills`,
copy the complete `skills/feedback-to-fix` folder into your target repository:

```text
your-repository/
└── .agents/
    └── skills/
        └── feedback-to-fix/
            ├── SKILL.md
            └── references/
                └── decision-examples.md
```

In PowerShell, from this repository, replace the target path with your project:

```powershell
$targetProject = 'C:\path\to\your-project'
New-Item -ItemType Directory -Force -Path "$targetProject\.agents\skills" | Out-Null
Copy-Item -LiteralPath '.\skills\feedback-to-fix' -Destination "$targetProject\.agents\skills" -Recurse
```

Review an existing folder before copying over it. If your agent supports
explicit skill invocation, use:

```text
$feedback-to-fix Resolve this feedback: [requested behavior and constraints].
```

For the discovery rules behind this example, see the
[official setup documentation](https://learn.chatgpt.com/docs/build-skills).
The skill uses the [Agent Skills format](https://agentskills.io/home).
Other clients may use different locations; check their documentation.
Compatibility has not been tested across clients. Copying the skill is separate
from running this repository's evaluation helper.

## A small example

**Feedback:** “The list is slow; add caching. You may choose another fix if the
evidence points elsewhere.”

An agent might immediately add a cache. The skill instead calls for a cheap
measurement that distinguishes the likely causes. If duplicate requests explain
the delay, correct their source and check that the list updates correctly. If
the measurement supports caching, implement it within the existing design.

For an exact wording change, perform the edit. The skill should add no ceremony.

These examples illustrate the intended behavior; they are not benchmark results.

## Evaluate before adopting

The suite contains eight invented cases, including two simple controls. Each
has behavior-based criteria and a setup that can be reproduced in a code agent.
Read the [evaluation protocol](evals/README.md) before collecting paired runs.

The helper requires Python 3.11 or later and only the standard library:

```text
python -m unittest discover -s tests -v
python evals/score.py evals/scores.template.json
```

The empty template reports **no data**. It does not generate model responses,
grade them, or fabricate an improvement. The helper validates paired score
records and averages human judgments; the reviewer remains responsible for
checking the saved transcripts and artifacts.

## What is and is not established

- Package structure and evaluation-helper behavior can be checked locally.
- The workflow file defines CI checks; a local pass is not a hosted CI result.
- No agent A/B results ship with this initial version.
- Instructions cannot enforce permissions or guarantee correct decisions.
- A successful command only establishes what its check actually covers.
- Existing agent guidance may already produce the same behavior, making this
  skill redundant or harmful through added overhead. Keep or remove it based
  on paired evaluations, including the control cases.

## Repository layout

```text
skills/feedback-to-fix/   The installable skill and optional examples
docs/                    Alternatives, limitations, and the chosen design
evals/                   Synthetic cases, scoring protocol, offline helper
tests/                   Helper regression tests and package integrity checks
.github/workflows/       Cross-platform checks, ready for GitHub Actions
```

## Contribute

Useful contributions include a new invented counterexample, a clearer decision
boundary, or reproducible paired results. Avoid uploading private repositories,
session transcripts, credentials, or identifying project details. Extra rules
should solve a demonstrated failure without making the simple controls worse.

## License

[MIT](LICENSE).
