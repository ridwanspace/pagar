# Step 01: Find the story & initialize

## Step goal

Identify which dev story to implement, load it as the authoritative guide, mark it in progress,
and locate the first incomplete task.

## Mandatory rules

- 🔎 Use the helper to find and resolve. **Do not scan the tree manually.**
- 📖 Read this whole step before acting.
- 🧱 **The dev story file is your primary context.** Read it fully once located. **Do not
  pre-load the PRD or the epics.**

## Sequence

### 1. Resolve the target

**If the user named a story:**

```bash
{{SPEC_HELPER_COMMAND}} story-info "<ref>" --json
```

**If the user did NOT name one** ("implement the next story"):

```bash
{{SPEC_HELPER_COMMAND}} next-dev --json
```

This returns the next story that **has a dev story file and is not done**, preferring in-progress
then blocked.

**If nothing resolves:**

- Nothing to implement → either everything is done, or no dev story files exist yet. Tell the
  user. If a planned story needs expanding first, point them at `/create-story`. **HALT.**
- The dev story does not exist → the planning story has not been expanded. Offer `/create-story`
  for it first. **HALT.**
- Bad reference → show the dev listing and ask.

### 2. Load the dev story: your authoritative guide

Read the **complete** dev story file. Parse its sections:

- **Story and acceptance criteria**: what "done" means.
- **Dev guardrails**: **the invariants you MUST hold.**
- **Architecture and stack guidance**: the patterns to follow, cited.
- **Files to create or modify**: what you will touch, and **what to preserve**.
- **Tasks and subtasks**: your ordered execution plan. **Authoritative.**
- **Testing**: the required coverage.
- **References**: where to verify a claim, **by section only**.
- **Dev agent record, file list, status**: the sections you will update.

**If the file is missing required sections or is clearly a stub with placeholders left: HALT** and
recommend `/create-story`, or its self-check, to complete it first.

### 3. Carry previous-story context

If there is a previous story with a dev file, the current story's carry-over section should
already summarize it. **Trust that.** Only open the previous dev file if you need a specific
detail it references.

### 4. Mark in progress

```bash
{{SPEC_HELPER_COMMAND}} set-status <ref> in_progress
```

Also ensure the dev story file's own status line reads in progress.

### 5. Find the first incomplete task

Scan the tasks section top to bottom for the first unchecked item.

- **All tasks already checked** → skip implementation. Go straight to
  `steps/step-03-validate.md`.
- **A task's requirements are ambiguous or conflict with the PRD or epic** → surface it now. **If
  it is a genuine spec conflict, that is a HALT trigger**, and you suggest `/edit-prd` or
  `/epics`. Otherwise note your interpretation and proceed.

### 6. Confirm and route

> **Implementing:** Story {ref}, {title}
> **Dev story:** {path} (status → in_progress)
> **First task:** {first unchecked task}
> **Guardrails in play:** {the applicable invariants}

Then read fully and follow `steps/step-02-implement.md`.

## Success / failure

✅ **Success:** exactly one dev story resolved via the helper. The full dev story loaded as the
guide. Status set. First incomplete task identified. **A stub or a conflict caught early.**

❌ **Failure:** manual tree scanning. Pre-loading the whole PRD or epics. Implementing without the
dev story. **Starting on a stub story.** Not setting status.

**Master rule:** Load the one authoritative guide, mark the work started, and know your first
task. Before writing any code.
