# Step 04: Adversarial self-check & finalize

## Step goal

Review the just-written dev story with **fresh, skeptical eyes** against `checklist.md`, surface
gaps that would cause implementation mistakes, apply the fixes the user wants, and finalize.

## Mandatory rules

- 🧪 **Review as an independent validator who did NOT write the story.** Hunt for what is missing
  or wrong. **Assume something is missing. Prove the story complete, do not assume it.**
- 🔎 Re-verify claims against sources via **scoped** reads. Do not re-load everything. Spot-check
  the risky parts.
- 📖 Read this whole step before acting.

## Sequence

### 1. Run the checklist

Read `checklist.md` and apply it to the dev story file. It targets the disaster categories:
reinvention, wrong libraries or locations, regressions, missing invariants, vague tasks, uncited
claims, and unreadability for the implementing agent.

You may delegate the fresh-eyes pass to a **subagent in a clean context**, giving it the dev
story path, the checklist, and the relevant source paths, then **judge its findings yourself**.
Either way, **the validation must be genuinely adversarial.**

### 2. Spot-verify the high-risk parts

Re-check, with targeted reads, the things most likely to be wrong:

- **Files-to-modify "must preserve": does it match what the actual file does?** Re-open one or
  two.
- **Cited formulas and copy: do they match the source verbatim?**
- **Invariants:** is each guardrail the one the locked decisions **actually specify for this
  story's mutation**? Is the role rule the one the roles section states?
- **Tasks against criteria:** every criterion has a task, and no task introduces a forward
  dependency or out-of-scope work.

### 3. Present findings

Grouped by severity:

> **Self-check. Story {ref}**
>
> **🚨 Critical (must fix):** {gaps that would cause wrong, broken, or incomplete implementation
>, a missing invariant, a wrong path, an uncited or incorrect formula, a missing
> files-to-modify entry, a regression risk}
> **⚡ Enhancements (should add):** {guidance that materially helps the developer}
> **✨ Optional:** {nice-to-haves}
>
> Apply: **[all] / [critical] / [select #] / [none]** ?

### 4. Apply fixes

- Apply the user's selection by editing the dev story directly. **Make fixes read naturally. Do
  not annotate "added during review".**
- **If the user is absent or you are running autonomously: apply all Critical fixes
  automatically**, list the enhancements as suggestions, and proceed.
- Re-verify that **no placeholders remain** and every applicable invariant is present and cited.

### 4b. Resolve open questions: non-negotiable for genuine forks

**A developer may have ONLY this story file. An unresolved open question is a decision DEFERRED
ONTO THEM, which is a defect, not a courtesy.**

So before finalizing, **drive every open question to a concrete decision**, not a list of
trade-offs.

- **For each genuine fork**: one where the answer changes the build: a library, pattern, or
  scope choice, not a trivial "we do not need this", **make the call**, grounded in this
  codebase. Find the precedents: how is this kind of thing already done here, with two or three
  comparable surfaces and their file and line? ⚠ **Precedents that DISAGREE with each other are
  the most valuable finding**, because they mean the codebase has no house rule, and the split
  usually tracks **purpose**. Name the axis. That is what makes your recommendation an argument
  rather than a preference. **Then fold the decision back into the story body**: into the
  architecture guidance, the files table, or the tasks, wherever it lands, **so the file ships
  self-contained with the call already made.**
- **For a trivial or already-decided question**, resolve it inline in one line. **Do not
  manufacture a fork to justify ceremony.**
- **Result: the open-questions section ends with ZERO open forks.** Replace it with an "all
  resolved, none remain open" note listing each decision in one line: what was decided, and where
  in the body it lives.

**A story is not ready while a real fork is still listed as a question.**

### 5. Finalize

Confirm status is consistent via the helper's dev listing and story info. Then report:

> **✓ Dev story ready, {ref}: {title}**
>
> - **File:** {path}
> - **Status:** in_progress
> - **Covers:** {features} · **Flows:** {flows}
> - **Self-check:** {N critical fixed, M enhancements applied or suggested}
> - **Hazard scan:** {N shipped stories reviewed, K hazards folded in | none applicable because …}
> - **Open questions:** none remain open ({N} resolved. List each one-liner)
>
> **Next:** implement it. The developer has everything in this one file. When done, mark it done
> via the helper.
>
> Want me to **create the next story**, or stop here?

### 6. Menu

- **[N] Next story**: loop back to `steps/step-01-target.md` for the next planned story.
- **[R] Re-check**: run the checklist again after manual edits.
- **[X] Done**: exit. The story files live in the personal, git-excluded tree, so there is
  nothing to commit. If you changed the helper script, run its tests.

## Success / failure

✅ **Success:** genuinely adversarial review done. High-risk claims spot-verified **against
sources**. Findings presented by severity. Selected and critical fixes applied cleanly. **Every
genuine open-question fork resolved and folded into the body, none left listed as a question.**
No placeholders. Status consistent. Clear next step offered.

❌ **Failure:** a rubber-stamp review. Not verifying cited formulas or paths. Leaving an
inapplicable invariant, or missing an applicable one. **Shipping a story with a real open fork
still listed as a question**, which the developer would have to re-decide. Claiming done while
placeholders remain.

**Master rule:** Assume the first draft missed something. Find it, fix it, and only then call
the story ready.
