# Step 07: Offer to commit, then suggest the next story

## Step goal

Close the loop: **offer** to commit the work from this story and the review, then **suggest the
next story to work on. Dependency-aware, NOT strictly numeric.** It may jump from 1.2 to 1.5, or
to another epic entirely, if that is the correct unblocked next step.

## Mandatory rules

- 📖 Read this whole step before acting.
- 🛑 **Do NOT commit without the user's go-ahead.** Offer. **The user decides.** Run the quality
  gates before committing, and **never bypass them.**
- 🧭 **The next-story suggestion is DEPENDENCY-AWARE, not numeric.** A blocked story whose
  prerequisite is not done **is the wrong suggestion even if it is the next number.**
- 🔎 **Script-based:** resolve the suggestion with the helper. **Do not eyeball the tree.**

## Sequence

### 1. Recap what the review produced

Briefly, so the user knows what a commit would include:

> **Post-review complete for Story {ref}, {title}.**
>
> - Verification: {pass summary | skipped, no user-reachable surface}
> - User docs: {updated `<file>` | none needed | no docs yet, deferred}
> - Learnings: {N facts → rules / memory file / memory; compaction: …}
> - Team docs: {updated `<page>` | nothing asserted this story's changes}
> - Feed-forward: {dependents updated, or none}
> - Demo seed: {grown | created | not applicable}
> - **Pipeline improvement:** {what became a script or guard, plus the mutation that proved it |
>   none this run}

### 2. Offer to commit

> Ready to commit? This will stage the code, the documentation and seed changes, and run the
> quality gates. Run `/commit`? (yes / not yet)

- **If yes:** invoke **`/commit`**. It handles the staging choice, the message, the gates, and the
  default-branch warning. **Let it drive. Do not duplicate its logic.**
- **If not yet:** skip committing. The work stays in the working tree. Remind them they can run
  `/commit` whenever.

**Do NOT auto-push and do NOT auto-open a pull or merge request.** Committing is the offer here.
**Pushing and shipping are separate, explicit steps the user takes.**

### 3. Suggest the next story, dependency-aware

```bash
{{SPEC_HELPER_COMMAND}} suggest-next <ref> --json
```

This recommends the next story by **preferring a READY story**: one whose every explicit
dependency is done. Ideally the natural successor that depends on the one just finished, else a
ready story in the same epic, else any ready story. **It will not silently recommend a story whose
prerequisites are not met.**

Present it plainly, **and say WHY it is next, not just its number:**

> **Suggested next: Story {next-ref}, {title}.**
> Why: {it depends on {ref}, which is now done | it is the next unblocked story in {epic} | its
> prerequisites {list} are all done}.
> {If the numerically-next story is blocked, SAY SO: "Story 1.3 is blocked by 2.1, which is not
> done, so 1.5 is the better next step."}
> It {has a dev story already → run `/dev-story {ref}` | needs expanding → run
> `/create-story {ref}` first}.

⚠ **This resolver is a heuristic over freeform prose.** When it reports a story as ready,
**sanity-check that against the story's own text whenever the epic states an explicit ordering.** A
phrasing outside the recognized keywords defeats the pattern. See `rules/spec-pipeline.md`.

If it finds nothing: tell the user every story is in progress or done, and they can run `/epics` to
add more, or name one explicitly.

### 4. Final menu

- **[C] Commit**: run `/commit` now, if not already done.
- **[S] Start next**: kick off the suggested next story with the correct follow-on command.
- **[X] Done**: exit the review.

**Halt and wait for the user's choice.**

## Success / failure

✅ **Success:** a clear recap. The commit **offered** and **delegated to `/commit`, not
reimplemented**, never forced, never bypassing the gates. The next story suggested
**dependency-aware with a stated reason**, with numeric order overridden when a dependency demands
it. The **correct** follow-on command named. Menu presented and awaited.

❌ **Failure:** committing without asking. Bypassing the hooks or gates. **Suggesting the
numerically-next story when it is blocked.** Recommending the implementation command for a story
that has no dev story yet. **Auto-pushing or auto-opening a request.**

**Master rule:** Offer the commit, point at the CORRECT next story. Dependency truth over
numbering, and hand control back to the user.
