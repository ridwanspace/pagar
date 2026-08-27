# Step 03: Write the dev story file

## Step goal

Write the comprehensive dev story to its **mirrored path**, filled entirely from the step-02
analysis, then flip its status.

## Mandatory rules

- 📖 Read this whole step before acting.
- 🧩 **Fill the template with REAL, cited content.** No placeholders left, no generic
  boilerplate. **Drop guardrail lines that genuinely do not apply**: do not leave empty
  scaffolding, **but never drop one that DOES apply.**
- ✍️ Match the project's voice. Technical content in the project's working language. **Any
  user-facing strings quoted VERBATIM from the flow**, in whatever copy language the PRD's
  decisions declare.

## Sequence

### 1. Confirm the output path

From step 01 you have the dev-story path. Create the epic subfolder if it does not exist,
mirroring the planning layout. If the file exists and the user approved overwrite, proceed.
Otherwise stop.

### 2. Instantiate the template

Start from `templates/story-template.md` and fill every section from the step-02 findings:

- **Header, story, covers, flows, epic**: from the planning story.
- **Acceptance criteria**: refine the planning criteria into testable Given/When/Then, adding
  edge cases, error paths, and any **idempotency** or **authorization** criteria the locked
  decisions imply but the planning story left implicit.
  - **⚠ Edge cases are budgeted and sourced. Read `rules/edge-cases.md` before writing them.**
    Cap edge-case criteria at **3**, or **5** for money, authorization, or file-upload stories.
    Walk the five sources in order. Boundaries, equivalence classes, stack-forced error paths,
    state and concurrency, domain. Pick what applies, and **record in one line why you skipped
    each source you skipped.**
  - **Refining a planning story is where the count usually creeps. If the refined list needs
    more than 5, the story is too big: say so and PROPOSE THE SPLIT rather than shipping a
    bloated criteria list.**
  - Happy-path and locked-decision criteria do not count against the cap.
- **Dev guardrails**: include **ONLY the applicable locked decisions**, each made concrete for
  this story **and cited**: the exact idempotency key the PRD specifies, the exact role rule.
  **Remove inapplicable lines.**
- **Architecture and stack guidance**: the concrete patterns, per half, **with the hazards from
  step 02b folded in and their source stories cited**. Name real files: the transport module and
  route shape, the boundary schema, the service function, the data model change **plus its
  migration file name**, the background job and its queue if async, the client page or component,
  the client service call, the feature flag, and the route registration. Plus any **verbatim**
  domain formula or copy. **Every claim cited.**
- **Files to create or modify**: the explicit table. For every UPDATE row, fill "must preserve"
  from **the file you actually read** in step 02. For greenfield, list NEW files at correct
  locations.
- **Tasks and subtasks**: ordered, each tied to a criterion, sized for one session, **no forward
  dependencies**. Include a tests task.
- **Testing**: the concrete must-cover list, including idempotency, authorization, and any
  regression assertion a locked decision demands.
- **Previous-story carry-over**: real patterns and gotchas from the previous dev story, plus any
  inherited ground truth, **or "first story in epic".**
- **References**: every source you cited.
- **Open questions**: anything uncertain. Step 04 resolves these.
- **Definition of done**: keep the checklist, tailored to the invariants that apply.

### 3. Set status to in progress

Leave the file's status line as in progress and update the shared mirror:

```bash
{{SPEC_HELPER_COMMAND}} set-status {ref} in_progress
{{SPEC_HELPER_COMMAND}} dev-list          # confirm the story now shows up
```

### 4. Hand off to self-check

State briefly what was written, path plus section coverage, then read fully and follow
`steps/step-04-self-check.md`.

## Success / failure

✅ **Success:** the dev story file written at the **mirrored** path. Every section filled with
real, cited content. Applicable invariants encoded concretely. Files-to-modify table complete
with "must preserve". **No leftover placeholders.** Status flipped via the helper.

❌ **Failure:** leftover placeholders or generic boilerplate. **Uncited technical claims.**
Missing an applicable invariant. An empty files-to-modify table when files are being changed.
Forgetting to flip status. Writing to a non-mirrored path.

**Master rule:** The file must be self-sufficient and source-grounded, a developer with only
this file should implement correctly without re-deriving anything.
