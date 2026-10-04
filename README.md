# ⚙️ Introduction to GitHub Actions

An interactive Reveal.js presentation on using GitHub Actions: writing workflows, triggers, expressions, matrices, caching, artifacts, reusable workflows and your own actions; securing them (least-privilege tokens, environments, OIDC, pinning, script injection); debugging and cost; protecting `main` with rulesets and required checks; and Lighthouse CI as a quality gate. Every workflow shown ran for real in this repository, and the slides link the runs.

## ▶ [Open the Presentation](https://brendanjameslynskey.github.io/Introduction_to_GitHub_Actions/)

## 📄 [Markdown Version](presentation.md)

---

## Contents

| # | Topic | Description |
|---|-------|-------------|
| 01 | Title | Event → workflow → jobs → steps → checks |
| 02 | Topics | Topics at a glance |
| 03 | What GitHub Actions Is | Events, workflows, jobs, steps, actions; GitHub-hosted, larger and self-hosted runners; SVG diagram |
| 04 | Anatomy of a Workflow File | `on`, `permissions`, `env`, `defaults`, `runs-on`, `steps`, `uses` vs `run`, `with` |
| 05 | Triggers | `push`, `pull_request`, `schedule`, `workflow_dispatch` with inputs, `workflow_call` |
| 06 | Expressions and Contexts | `${{ }}`, the contexts, `if:`, `success()` / `failure()` / `always()`, outcome vs conclusion |
| 07 | Matrices | include / exclude, `fail-fast`, `max-parallel`, how legs are named |
| 08 | Jobs Together | `needs`, job outputs via `$GITHUB_OUTPUT`, a Redis service container |
| 09 | Caching | `actions/cache` keyed by `hashFiles`, `setup-python` caching; a miss, a race, then hits |
| 10 | Artifacts, Summaries, Annotations | upload / download, retention, `$GITHUB_STEP_SUMMARY`, `::notice` |
| 11 | Reuse | A composite action and a reusable workflow (`workflow_call`), called twice |
| 12 | Writing Your Own Action | Composite vs JavaScript vs Docker; a tiny one of each kind, run |
| 13 | Least-Privilege `GITHUB_TOKEN` | `permissions: {}`, per-job scopes; a write refused with HTTP 403 |
| 14 | Secrets and Environments | Masking, environment secrets, a wait-timer protection rule |
| 15 | OIDC, Pinning, Dependabot | Real OIDC claims; actions pinned by SHA; Dependabot for actions |
| 16 | `pull_request_target` and Script Injection | The dangerous trigger, injection via `${{ }}`, the `env` fix; actionlint's finding |
| 17 | Debugging | Reading logs, `--debug` re-runs, `ACTIONS_STEP_DEBUG`, actionlint, `act` |
| 18 | Real Failures from This GitHub | A git-ignored fixture, a silently skipped test, a stale git dependency |
| 19 | Cost, Limits and Speed | Concurrency groups (a run cancelled), timeouts, path filters, limits (hedged, linked) |
| 20 | Protecting `main` | Branch protection vs rulesets; every term in plain words |
| 21 | Required Checks, Shown Blocking | This repo's ruleset; a refused push, a failing PR, a renamed job that blocks |
| 22 | Lighthouse CI | Lighthouse scores, LHCI budgets; a real `ci.yml` job; the post-deploy smoke check |
| 23 | Real Workflows (1) | Torch_Sim_Frontend's matrix; Rust_DES_Kernel's Rust + maturin jobs |
| 24 | Real Workflows (2) | FHE_Accelerator_Sim's headline gate; Memory_System_Sim's integration job |
| 25 | Actions vs Jenkins vs GitLab CI | The Actions view; links the Jenkins deck's full comparison |
| 26 | Takeaways & Next Steps | Summary, Introduction to CI/CD, Introduction to Jenkins, SimEng 07, Interview_CI_CD |

---

## Demo workflows

Every snippet on the slides is cut from a file in this repository (or, for the real-world slides, from another repository at a pinned commit) by the build script, so the slides show exactly what ran. All were checked with [actionlint](https://github.com/rhysd/actionlint) 1.7.12 with shellcheck 0.11.0: clean, apart from the deliberate injection example below.

| Workflow | What it shows | Run(s) |
|----------|---------------|--------|
| [`ci.yml`](.github/workflows/ci.yml) | The required check `Demo gate` | [37216325824](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37216325824) (as on the slides); first version: [37214324600](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324600); failing on PR #1: [37214705396](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214705396) |
| [`demo-matrix.yml`](.github/workflows/demo-matrix.yml) | Matrix, both caches, artifacts, job summary, annotation | [37214324617](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324617) (cache misses), [37214874461](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214874461) (hits) |
| [`demo-jobs.yml`](.github/workflows/demo-jobs.yml) | `needs`, outputs, a service container, status functions | [37214324637](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324637) (attempt 2 re-run with `--debug`) |
| [`demo-reuse.yml`](.github/workflows/demo-reuse.yml) + [`demo-reusable.yml`](.github/workflows/demo-reusable.yml) | Reusable workflow, [composite](.github/actions/setup-demo/action.yml), [JavaScript](.github/actions/js-hello/) and [Docker](.github/actions/docker-hello/) actions | [37214324885](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324885) |
| [`demo-dispatch.yml`](.github/workflows/demo-dispatch.yml) | `workflow_dispatch` inputs, untrusted text through `env` | [37214439700](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214439700), [37214441911](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214441911) |
| [`demo-concurrency.yml`](.github/workflows/demo-concurrency.yml) | A concurrency group cancelling the older run | [37214446270](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214446270) (cancelled, as intended), [37214470039](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214470039) |
| [`demo-permissions.yml`](.github/workflows/demo-permissions.yml) | `permissions: {}`, a refused write, OIDC claims | [37214432837](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214432837) |
| [`demo-environment.yml`](.github/workflows/demo-environment.yml) | Environment `demo`: a 1-minute wait timer, `main` only, a masked secret | [37214444150](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214444150) |
| [`demo-node-skip.yml`](.github/workflows/demo-node-skip.yml) | A green job that skipped a test, and the fix | [37214324624](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324624) |
| [`dependabot.yml`](.github/dependabot.yml) | Dependabot for actions | [37214327007](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214327007) |

[`demo/lint_examples/`](demo/lint_examples/) holds files that are linted but never run: every trigger in one file ([`triggers.yml`](demo/lint_examples/triggers.yml)), and the injection example in its unsafe ([`bad-injection.yml`](demo/lint_examples/bad-injection.yml)) and safe ([`good-injection.yml`](demo/lint_examples/good-injection.yml)) forms. actionlint's output on the unsafe one:

```text
demo/lint_examples/bad-injection.yml:13:31: "github.event.pull_request.title" is potentially untrusted. avoid using it directly in inline scripts. instead, pass it through an environment variable. see https://docs.github.com/en/actions/reference/security/secure-use#good-practices-for-mitigating-script-injection-attacks for more details [expression]
```

**Not run here:** `act` (no Docker on the build machine), the cloud side of OIDC (no cloud account), and the `schedule` trigger (linted, not waited for).

## Protecting `main` in this repository

The ruleset **Protect main** (active on the default branch, no bypass actors) requires a pull request (0 approvals), the status check **Demo gate** from GitHub Actions (not strict), and blocks force pushes and deletion. A direct push is refused (`GH013`), [PR #1](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/pull/1) is blocked by a failing check, and [PR #3](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/pull/3) is blocked although green, because it renames the job. Both are kept open as examples and will never be merged.

---

## Key terms

Slide numbers are the tags in each slide's header (and the `Slide NN` headings of [presentation.md](presentation.md)).

| Term | Plain meaning | Slide |
|------|---------------|-------|
| Event | Something that happens in a repository (push, PR, schedule, button) and can start workflows | 02 |
| Workflow / run | A YAML file in `.github/workflows/`; one execution of it is a run | 02 |
| Job | Steps that run together on one fresh machine | 02 |
| Step | One shell command (`run`) or one action (`uses`) | 02 |
| Action | Packaged, reusable step code, referenced with `uses:` | 02, 03 |
| Runner (hosted, larger, self-hosted) | The machine a job runs on | 02 |
| Label | A tag that picks a runner (`runs-on`) | 02 |
| Check | The pass/fail mark GitHub shows on a commit or PR; each job reports one | 03 |
| `permissions` | What the job's automatic token may do | 03, 12 |
| Trigger / `on` | The events a workflow listens for | 04 |
| Inputs | Typed values given to `workflow_dispatch` or `workflow_call` | 04 |
| Expression | `${{ … }}`, evaluated by GitHub before the step runs | 05 |
| Context | A named object an expression reads (`github`, `env`, `matrix`, `secrets`, `needs`, `steps`…) | 05 |
| Status functions | `success()`, `failure()`, `always()`, `cancelled()` in `if:` | 05 |
| Outcome vs conclusion | A step's result before and after `continue-on-error` | 05 |
| Matrix / leg | One job run once per combination of values; each combination is a leg | 06 |
| `fail-fast`, `max-parallel` | Cancel the other legs on a failure; cap legs running at once | 06 |
| `needs` / job outputs | Job ordering, and values passed between jobs | 07 |
| Service container | A Docker container (database, cache) beside the job | 07 |
| Cache / cache key | Saved directory restored by later jobs; the key decides when it is reused | 08 |
| Artifact / retention | A file uploaded to a run; how long it is kept | 09 |
| Job summary | Markdown a job writes to `$GITHUB_STEP_SUMMARY`, shown on the run page | 09 |
| Annotation | A `::notice` / `::warning` / `::error` pinned to a file and line | 09 |
| Composite action | Several steps behind one `uses:` | 10 |
| Reusable workflow | A whole workflow called with `workflow_call` | 10 |
| JavaScript / Docker action | Actions that run Node code or a container | 11 |
| `GITHUB_TOKEN` / scopes | The job's short-lived repository credential and what it may touch | 12 |
| Least privilege | Grant only the access a job needs | 12 |
| Fork | A copy of a repository under another account; its PRs get no secrets | 02, 12, 15 |
| Secret / masking | An encrypted setting; the log shows it as `***` | 13 |
| Environment / protection rules | A deployment target with its own secrets, reviewers, timers and branch rules | 13 |
| OIDC | Short-lived identity tokens exchanged for cloud credentials instead of stored keys | 14 |
| Pinning to a SHA | Referencing an action by full commit hash, which cannot be moved | 14 |
| Dependabot | GitHub's bot that opens dependency-update PRs | 14 |
| `pull_request_target` | A trigger that runs the base repo's workflow, with secrets, for fork PRs | 15 |
| Script injection | Untrusted text pasted into a script by `${{ }}` | 15 |
| Debug logging | `ACTIONS_STEP_DEBUG` / `ACTIONS_RUNNER_DEBUG`, or a `--debug` re-run | 16 |
| actionlint | A linter for workflow files | 16 |
| `act` | A tool that runs workflows locally in Docker | 16 |
| Concurrency group | Runs sharing a name never overlap; `cancel-in-progress` cancels the older | 18 |
| Timeout | `timeout-minutes`, the limit before a job is killed | 18 |
| Path filters | `paths` / `paths-ignore`, which skip a workflow for unrelated changes | 18 |
| Protected branch | A branch guarded by rules | 19 |
| Branch protection rule | The older per-branch protection mechanism | 19 |
| Ruleset | The newer, layered, publicly visible rule mechanism | 19 |
| Required status check | A named check that must pass before merging | 19, 20 |
| Require up to date (strict) | The PR must contain the latest `main` before merging | 19 |
| Required reviews | Approvals needed before merging | 19 |
| Force push / deletion blocks | Rules that stop history rewrites and branch deletion | 19 |
| Bypass list / include administrators | Who may ignore the rules | 19 |
| Lighthouse | Google's page auditor (performance, accessibility, best practices, SEO) | 21 |
| Lighthouse CI (LHCI) / budget | Lighthouse in CI, failing below set scores | 21 |
| Smoke check | A quick post-deploy check that the live site is healthy | 21 |
| `repository_dispatch` | An API event one repository's CI can send to start another's | 23 |

---

## Slide Controls

| Action | Key |
|--------|-----|
| Next / Previous | `→` `←` or swipe |
| Overview | `Esc` |
| Fullscreen | `F` |
| Export to PDF | Append `?print-pdf` to URL, then print |

## Technology

[Reveal.js 4.6](https://revealjs.com) · [highlight.js](https://highlightjs.org) · Big Shoulders Display + Public Sans + Overpass Mono

Single self-contained `index.html` plus screenshots in `images/` — no build step, no npm, no dependencies to install. The screenshots are of public github.com pages as a logged-out visitor sees them.

## See also

- [Introduction_to_CI_CD](https://github.com/BrendanJamesLynskey/Introduction_to_CI_CD) — the practice behind all of this: pipelines, testing, deployment strategies, DORA metrics.
- [Introduction_to_Jenkins](https://github.com/BrendanJamesLynskey/Introduction_to_Jenkins) — the self-hosted alternative, and the full Jenkins vs Actions vs GitLab comparison.
- [Introduction_to_GitHub](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub) — GitHub itself: repositories, pull requests, the CLI, Pages, security features.
- [SimEng_07_Jenkins_for_Simulation_Teams](https://github.com/BrendanJamesLynskey/SimEng_07_Jenkins_for_Simulation_Teams) — CI for hardware and simulation pipelines.
- [Interview_CI_CD](https://github.com/BrendanJamesLynskey/Interview_CI_CD) — interview questions on CI/CD.

## References

[GitHub Actions documentation](https://docs.github.com/en/actions) · [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax) · [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use) · [Dependency caching](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching) · [OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect) · [Actions limits](https://docs.github.com/en/actions/reference/limits) · [About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) · [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci) · [actionlint](https://github.com/rhysd/actionlint)

## License

Educational use. Code examples provided as-is.
