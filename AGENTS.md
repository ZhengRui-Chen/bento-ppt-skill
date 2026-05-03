# Repository Agent Instructions

These rules apply to coding agents working in this repository.

## Issue Guidelines

1. Each issue should use labels that match its type, affected area, and priority when applicable.
2. Bug reports should include a bug-related label and enough context to reproduce or verify the problem.
3. Feature requests should include a feature-related label and describe the user-visible outcome.
4. If no existing label fits, mention the missing label in the issue body instead of leaving the issue unlabeled.

## Priority Labels

Each open issue should have at most one `priority:P0` through `priority:P3` label.

- `priority:P0`: critical or blocking; fix immediately.
- `priority:P1`: high priority; target the next active iteration.
- `priority:P2`: medium priority; planned but not blocking.
- `priority:P3`: low priority; backlog or opportunistic.

## Pull Request Guidelines

1. One PR should solve one problem.
2. Every PR should declare its type: `feature`, `bug fix`, `refactor`, `test infrastructure`, `docs`, or `chore`.
3. Every PR should apply labels that match its declared type, affected area, and review or release priority when applicable.
4. Feature and bug-fix PRs should include required tests in the same PR.
5. Test infrastructure may be submitted as a separate PR before feature work.
6. Refactors should ideally be preceded by tests that lock current behavior.
7. Refactor PRs should state whether user-visible behavior changes. If behavior changes, it is not a pure refactor.
8. Avoid drive-by refactors, formatting churn, or unrelated cleanup unless explicitly called out.
9. Dependency changes must explain why the change is needed and mention migration or compatibility risk.
10. **Failing required checks must not be merged to `main`.**
11. Expected failures must be explicitly marked, scoped, linked to a follow-up issue, and include a removal condition.

## Project Architecture Boundaries

bento-ppt-skill is a dual-renderer slide generation engine: SVG (Jinja2 templates) for visual quality + Native (python-pptx) for 100% PowerPoint editability.

### Key Contracts

- `layout.json` is the single source of truth — it says "what goes where", themes say "how it looks".
- Every component MUST have both an SVG template AND a native renderer method.
- Colors, fonts, spacing are token-driven — never hardcoded in component code.
- Theme inheritance: derived themes need only `manifest.json`; templates fallback to `bento-tech/`.

### Component Checklist (when adding a new component)

1. SVG template: `themes/bento-tech/components/<name>.svg.j2`
2. Native method: `NativeRenderer._render_<name>()` in `scripts/native_render.py`
3. Data schema doc in `reference/bento-layouts-guide.md`

### High-Risk Areas

Be especially careful when modifying:

- `scripts/native_render.py` — dual renderer parity, hardcoded colors, coordinate mapping
- `scripts/render.py` — SVG assembly, theme inheritance, jinja2 template loading
- `themes/bento-tech/components/*.svg.j2` — template changes affect both themes
- `themes/*/manifest.json` — design token changes cascade to all rendered output
- `scripts/lint_cn.py` — typography lint is blocking (not warning), changes can break valid decks
- `scripts/ppt.py` — workspace validation, path resolution, CLI contract
- `scripts/export.py` — PPTX OOXML injection, svgBlip extension

Changes in these areas require focused tests, not only broad test-suite runs.

## Review and Merge Workflow

1. Push branch to remote.
2. Wait for GitHub Actions CI to complete (all checks must pass).
3. Run local multi-agent review (3-5 read-only agents covering: correctness, tests, security, code quality, integration).
4. Trigger remote @codex review:
   ```bash
   gh pr comment <PR> --body "@codex review"
   ```
5. Triage all findings: local + remote, deduplicate, classify (MUST_FIX / SHOULD_FIX / PARK).
6. Fix MUST_FIX findings, reply in threads with fix evidence.
7. Re-trigger @codex review if changes are substantial.
8. **Merge only when**: zero unresolved MUST_FIX findings AND CI is green AND remote @codex review has zero actionable unresolved threads.
9. Max 5 review-fix iterations.

## Large PRs

If a PR exceeds 800 changed lines, the author must mark:

- core logic files
- test files
- generated, golden, fixture, or lock files
- review focus
- files reviewers can safely skim

If a PR exceeds 1500 changed lines, the author should explain why it cannot be split.

## Validation Expectations

Each PR should list the validation performed:

- unit tests
- type checks
- lint and format checks
- relevant manual checks
- not run, with the reason

Feature and bug-fix PRs should make the validation path easy to reproduce.

## Direct Commits

Prefer PRs for code, behavior, dependency, and policy changes.

Direct commits are acceptable only for clearly low-risk docs-only updates when the maintainer explicitly approves them.
