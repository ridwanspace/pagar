# Step 01: Determine the target story

## Step goal

Pick exactly which planning story to expand, guard against mistakes, and load **just that
story's** planning context, all via the helper, not by loading full context.

## Mandatory rules

- 🔎 Use the helper to find and resolve the story. **Do not scan the whole tree by hand.**
- 📖 Read this whole step before acting.
- 🛑 Do NOT write the dev story yet.

## Sequence

### 1. Resolve the target

**If the user named a story**: "create story 1.2", an id, or a description:

```bash
{{SPEC_HELPER_COMMAND}} story-info "<ref>" --json
```

Use the resolved epic, story, planning file, dev-story path, previous story, and whether the dev
story already exists.

**If the user did NOT name one** ("create the next story"):

```bash
{{SPEC_HELPER_COMMAND}} next-story --json
```

This returns the first `planned` story in epic then story order: the natural next thing to
build. Then call `story-info` on it to get the full resolution, including the previous story.

**If nothing resolves:**

- No next story → everything is already in progress, blocked, or done. Tell the user and offer:
  run `/epics` to add more stories, or name a specific story to rebuild.
- The reference did not match → show the tree listing and ask the user to pick.
- No epics or stories exist at all → tell the user to run `/epics` first. **HALT.**

### 2. Guard checks, before any work

- **Already created?** If the dev story file exists, **ask the user**: overwrite, pick a
  different story, or stop. **Do not silently clobber a dev story that may contain
  implementation notes.**
- **Epic done?** If the epic is marked done, **warn** that you would be adding work to a
  completed epic, and confirm before proceeding.
- **Status sanity.** Note the story's current status. Normal is `planned`. If it is already in
  progress or done, surface that and confirm intent.
- **First story of an epic?** If there is no previous story, this is an **epic boundary**. If
  your project keeps any index or knowledge artifact that is refreshed on a slower cadence than
  each commit, **this is the right moment to prompt for the full refresh**: a full epic's worth
  of new code has landed, and the next epic is when cross-cutting questions start getting asked.
  **This is a PROMPT, not a gate.** State the recommendation, let the user decide, proceed either
  way. If they skip it, **do not silently trust stale cross-layer results later in this story.**

### 3. Load the planning story, scoped

Read **only** these:

- The planning story file: the user story, acceptance criteria, covered features, related flows,
  the invariants the epic noted, and what is out of scope.
- The epic context: `{{SPEC_HELPER_COMMAND}} show <epic>` for the goal, cohesion, dependencies,
  and story list.

**Do NOT read other epics or the whole PRD here.** You now know the story's scope, which features
and flows it touches, and what comes before it.

### 4. Confirm and route

State briefly:

> **Target:** Story {ref}, {title} (epic {epic-id})
> **Planning source:** {path}
> **Dev story will be written to:** {path}
> **Previous story:** {ref, and whether it has a dev story}, or "first in epic"
> **Covers:** {feature codes} · **Flows:** {flow refs}

If a guard in section 2 needs a decision, **ask now and wait.** Otherwise proceed.

Then read fully and follow `steps/step-02-analyze.md`.

## Success / failure

✅ **Success:** exactly one target story resolved via the helper. Guards checked, with **no silent
overwrite** and no accidental work in a done epic. Epic boundary detected and surfaced. Planning
story and epic context loaded scoped. Clear statement of target, source, output path, and
previous story.

❌ **Failure:** scanning the whole tree manually. **Loading the full PRD or all epics.**
Overwriting an existing dev story without asking. Proceeding when no planning story exists.

**Master rule:** Know precisely what you are building and where it goes, cheaply, before
analyzing anything.
