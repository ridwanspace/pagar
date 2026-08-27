# Step 02: Create or update the end-user documentation

## Step goal

Keep the project's **end-user documentation** current with what this story changed. Whatever form
that takes: a documentation site, a docs folder, a usage section in the README. **Update only if
this story changed something a user or operator must DO or SEE.** If the project maintains no user
documentation, note it and **skip cleanly.**

## Mandatory rules

- 📖 Read this whole step before acting. **If the project has a documented docs approach, read it
  first.** It is the source of record for *how* the documents are built. **Follow it. Do not
  invent a parallel system.**
- 🎯 **Only write guide content for a user-facing change**: a new or changed surface a client
  calls, a new command, a changed request or response shape, a new report to read, or a new step
  in an operator flow. **Internal changes invisible to users mean no update. Say so and advance.**
- 🗣️ **Write in the project's copy language**, per the PRD's locked decisions. **Use the exact
  paths, field names, and messages the system returns. Pull them from the code and the generated
  contract. Do not paraphrase.**
- 🚫 **These documents are COMMITTED, so no private spec ids.** See `rules/no-local-spec-refs.md`.
  They point at a tree no reader can open. State the behaviour and its why. Cite a file path, a
  commit hash, or the contract. **The team's own requirement vocabulary is fine.**
  **Also sweep the story's committed source before the commit offer in step 07:**
  ```bash
  git diff --name-only {{DEFAULT_BRANCH}}...HEAD -- {{SOURCE_ROOT}} {{TEST_DIR}} \
    | xargs grep -nE '[Ss]tory [0-9]+\.[0-9]|\bAC[0-9]{1,2}\b|[Ee]pic [0-9]|RCA-[0-9]|\.claude/' 2>/dev/null
  ```
  Rewrite hits on lines this story authored. **Leave pre-existing ones alone.**
- 👤 **Audience-scoped.** Write for the person doing the task, at their level. Put the page where
  its audience will look, and **add it to any index or navigation config so it is discoverable.**
- 🧠 **Mental model first, then steps.** For anything a user could **do yet not understand**, teach
  the why and how-it-fits **before** the how-to. **Simple mechanical tasks need only the steps. Do
  not over-build.** One-line test: *if understanding adds nothing beyond the steps, skip the
  model.*
- 🚀 **Complex or multi-step flows get ONE end-to-end worked example**: a single concrete scenario
  walked start to finish with real requests and responses. Before the per-surface detail. Add
  internal navigation once a page is long enough to scroll, and **verify the internal links
  resolve. A wrong slug is a silent dead link.**
- ♻️ **You may reorganize a whole page, not just patch in the change.** If a story touches a page
  whose structure no longer serves the reader, **restructure it.** The goal is "the user
  understands and can do it", not a minimal diff.

## Sequence

### 1. Decide if this step applies

Does this story change what a **user or operator** does or sees?

- **If NO:** print,
  > ℹ️ Story {ref} changed nothing a user does or sees, no documentation update needed.

  then go to `step-03-extract-learning.md`.
- **If YES:** continue.

### 2. Find where this project's user documentation lives, scoped

Look for a documentation folder, a documentation-approach record, or a usage section in the README.

- **Documentation exists** → that is the target. **Follow its established format, structure, and
  tooling.**
- **No user documentation yet** → **do NOT silently invent a documentation stack. That is a HALT
  trigger.** Print:
  > ℹ️ This project has no end-user documentation yet. Story {ref} is user-facing, so a guide would
  > help. Options: (1) run **`/create-docs`** as its own session, not inline here, (2) start a
  > minimal README usage section now covering just this flow, or (3) skip and revisit later.
  > Which?

  and **wait.** Note the choice in the close-out and continue.

### 3. Route the change to the right page

- **An existing page covers this flow** → **update it surgically.** Read only that file. Find it
  with a scoped search.
- **No page yet** → create one in the right place per the documentation's organization, and
  **cross-link it from the nearest index page so it is reachable.**

### 4. Write user-facing content

- Numbered steps, short sentences, **the real paths, field names, and messages the story
  shipped.**
- Lead with the mental model when the flow is concept-heavy. Go straight to steps when it is
  mechanical.
- For a multi-step flow: **one concrete end-to-end scenario first**, with real requests and real
  bodies, cross-linking each step to its detailed section, **with an expected-result line per step
  so the user can confirm as they go.**
- **Prefer examples the contract can vouch for.** Pull request and response shapes from the
  generated contract rather than typing them from memory. ⚠ **A response typed from memory is a
  paraphrase wearing a code fence.** Where you paste a captured transcript, keep it field-exact
  and date it.
- ⚠ **Redact or seed anything non-deterministic**: timestamps, ids, tokens, **and say so next to
  the block.** An example the reader cannot reproduce verbatim reads as broken.
- ⚠ **Never paste a real credential, token, or customer record into a page.**
- **Error paths too.** Every documented surface shows at least its most likely failure, captured
  the same way.
- End with cross-links to related pages.

### 5. Verify it builds and the claims are true

- **Run whatever documentation guard tests the project keeps**, and fix any failure. **Do not leave
  the documentation guards red.**
- 🔑 **Diff the field names mechanically. Do NOT hand-check them.** Dump the schema's declared
  fields and compare them against every backticked identifier on the page. **Prose reading cannot
  find this class of error: a page naming a field the response lacks reads as completely plausible,
  because the sentence around it is true.**
- ⚠ **Documents can also be wrong BY OMISSION.** If a schema gained a field, **an enumeration of
  its fields is now incomplete with every word still true. Compare both directions.**
- **Replay every worked example exactly as written**, copying it from the page. **Any mismatch
  fails this step: fix the page, not the diff.**

### 6. Close the step

> **User docs. Story {ref}:** {created or updated `<path>` | no update needed | no user docs,
> {started a minimal page | deferred by the user}}. Structure: {model + end-to-end + detail |
> single procedure | minor surgical edit}. Cross-links: {targets or "n/a"}. Verified: {field diff,
> examples replayed | n/a}.

Then read fully and follow `steps/step-03-extract-learning.md`.

## Success / failure

✅ **Success:** correct apply-or-skip decision. The change documented **where this project's users
actually look**, in the established format and copy language, **using the exact shipped paths,
fields, and messages.** Mental model present only where the flow is concept-heavy. Multi-step flows
get one end-to-end example. **Field names diffed mechanically in both directions. Examples
replayed.** Links verified.

❌ **Failure:** writing a guide for an invisible internal change. **Paraphrased paths or fields that
do not match the wire.** Inventing a parallel documentation system when one exists, **or silently
installing one when none does.** A concept-heavy flow documented as bare steps. Dead internal
links. Bolting a change onto a sprawling page that needed restructuring. **Hand-checking field
names instead of diffing them.**

**Master rule:** The documentation mirrors the real system in the user's language, organized where
the user will look, teaching the model before the steps, and if the project keeps no user
documentation, say so and skip cleanly rather than inventing infrastructure.
