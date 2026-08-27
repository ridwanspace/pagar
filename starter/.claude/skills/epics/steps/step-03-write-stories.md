# Step 03: Write stories

## Step goal

Write the stories for each epic, **one file per story**: with complete, testable acceptance
criteria and the invariants each story must hold. Handles both creating all stories (create
mode) and adding or revising specific stories (edit mode).

## Mandatory rules

- 🔎 Use the helper. Read only the epic you are working on and the **specific PRD sections** the
  features need. **Not the whole PRD, not every other epic.**
- 🔗 **Stories must NOT depend on future stories in the same epic.** Each is completable using
  only earlier stories' output.
- 🧱 **Create only the tables a story actually needs.** Never a "create all tables" story.
- 🛡️ **Every data-mutating story must encode the relevant locked invariants** from the PRD's
  key-decisions table.
- 🎯 Carry the persistent facts from `SKILL.md`.

## Sequence

### 1. Pick the working set

- **Create mode:** process epics in order. For the current epic, run
  `{{SPEC_HELPER_COMMAND}} show <epic>` to load **just its epic file.**
- **Edit mode:** work only on what the user named.

### 2. Read only the PRD sections you need

For the features in this epic, read **by section**:

- The **feature catalog** entry: what the feature does.
- The matching **flow**: step-by-step behaviour and **exact user-facing copy**.
- The **data-model section**: the tables this feature touches.
- The **locked decisions**: which invariants constrain this feature.
- The **roles and permissions** section: who can perform the action.

If the PRD names a domain source of truth, **pull business rules, formulas, and copy from it
verbatim. Quote, do not invent.**

### 3. Break the epic into stories

- Each story is **one distinct user capability, sized for a single working session.**
- Order them so each builds **only on previous ones**.
- A story maps to one, or a few tightly-coupled, features, or one slice of a feature.

**Good granularity**, using an ordering workflow as an example: *Create an order* → *Submit the
order for approval* → *Approve or reject an order* → *Mark an order fulfilled* → *Daily overdue
reminders*. Each builds only on the previous.

**Avoid:** "Build the whole ordering system" (too large). "Set up the database" (no user value).
"Approve endpoint, needs the Fulfill story first" (**a forward dependency**).

### 4. Write each story file

For each story:

1. Get the number and slug from the helper.
2. Create the story file from `templates/story-template.md`, filling:
   - **User story**: "As a {role}…", using roles the PRD defines.
   - **Context and source of truth**: link the PRD section, name the domain source if it
     applies, and **name the real code surfaces this touches on every half**: the transport
     module and route, the service function, the data model change **plus its migration file**,
     the boundary schema, a background job if the work is async, the client page or component,
     the client service call, and any feature flag that gates it.
   - **Acceptance criteria**: Given/When/Then, each independently testable. Include edge cases,
     error paths, **idempotency**, and **authorization**.
     - **⚠ Edge cases are budgeted and sourced. See `edge-cases.md`.** Cap edge-case criteria at
       **3** per story, or **5** if the story touches money, authorization, or file upload. Every
       one must trace to one of the five sources: boundaries, equivalence classes, stack-forced
       error paths, state and concurrency, or domain. **Name the sources you skipped in one
       line. Needing more than 5 means the story is too big: split it** and give each half its
       own 3. The cap excludes happy-path criteria and the idempotency and authorization
       criteria a locked decision forces.
   - **Invariants and guards**: pull the applicable **locked decisions**, made specific to this
     story. For example: "a double-submit of this request never creates two rows", "authorization
     is checked server-side on the route; **the client-side gate is UX only**".
   - **Data and schema touched**: only the tables **this** story creates or alters. **Every
     model change ships with its migration file.**
   - **Out of scope**: what a sibling or later story handles.
3. **Update the epic's story table** to include the new story.

### 5. Per-epic check

After an epic's stories are written:

- Confirm **every feature the epic claims is covered** by at least one of its stories.
- Confirm **no story references a feature implemented only by a LATER story** in the same epic.
- In create mode, summarize the epic and proceed to the next.

### 6. Sync and verify

```bash
{{SPEC_HELPER_COMMAND}} sync-status   # add new stories as planned; preserves manual status
{{SPEC_HELPER_COMMAND}} coverage      # confirm features now map through the stories
{{SPEC_HELPER_COMMAND}} list          # eyeball the tree
```

### 7. Route

When all in-scope stories are written, or the requested edits are done, display a one-line
summary and read fully and follow `steps/step-04-finalize.md`.

## Success / failure

✅ **Success:** one file per story. Testable Given/When/Then criteria within the edge-case budget.
Invariants and guards encoded. Tables created only as needed. **No forward dependencies.** Epic
story tables updated. Status synced. Coverage holds.

❌ **Failure:** **reading the whole PRD or all epics into context.** Vague or untestable criteria.
**Missing idempotency or authorization guards on a mutation story.** "Create all tables" stories.
Forward dependencies. Forgetting to sync status.

**Master rule:** Each story is a self-contained, testable, single-session unit that honors the
PRD's invariants, and the status mirror reflects it.
