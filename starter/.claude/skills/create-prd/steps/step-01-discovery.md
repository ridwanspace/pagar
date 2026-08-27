# Step 1: Discovery: vision, sources of truth, constraints

## Step goal

Elicit the product vision and its boundaries **before** any requirements are enumerated or
anything is drafted. The output is an **approved discovery summary**. Two paths reach it:
**1A from an input document**, **1B from scratch**.

## Mandatory rules (read first)

- 🛑 NEVER write the PRD in this step. Discovery only.
- 📖 Read this entire step file before acting.
- 📋 You are a **facilitator**, not a content generator. Ask, then listen. Propose only to
  sharpen what the user or their document said, never to substitute for it.
- 🚫 Do not invent domain facts. If a source of truth exists, plan to quote it. If none does,
  the user's answers are the source.
- 📄 **Document mode: the document is read in full, first, before a single question is asked.**
  A discovery summary that paraphrases a document you skimmed is **worse than no document**,
  because it looks grounded and is not. Every summary bullet carries a pointer to where in the
  document it came from, or is explicitly marked *(not in document, needs your answer)*.

## Sequence

### 1. Load the PRD quality standards

Read `data/prd-purpose.md` in full. Internalize it. It guides every question you ask and every
recommendation you make.

### 1A. Document mode: read the input document completely

Only if a path was given.

1. **Resolve and open the file.** Read it all, every page. If it is in a format you cannot open
   directly, convert it first, and **ask before installing anything**. **Never guess the
   contents of a file you could not open.** If the path does not resolve, list the likely
   directory and ask which file. Do not proceed on a guess.
2. **Extract, section by section, quoting.** Build a working outline of what the document
   actually says about:
   - **Vision and goals**, noting which are measurable and which are not.
   - **Users, roles, sponsor**, and any authorization statements.
   - **The problem** it solves, and what happens today.
   - **Features**, meaning anything that reads as a capability. **Keep the document's own names
     and ids.** If it already uses ids, record them verbatim. That is team vocabulary and will
     be cited, never renumbered.
   - **Flows**: numbered steps, screens, sequences.
   - **Constraints**: deadlines, integrations, devices, locales, compliance, performance
     numbers.
   - **Decisions already made**: anything phrased as "must", "always", or "never".
   - **Non-goals and out of scope.**
   - **Open items the document itself flags**: to-be-decided markers, questions.
3. **Check the document against reality, lightly and read-only.** The document may predate the
   codebase. Spot-check the claims that would change the PRD's spine: does the stack it assumes
   match what the repository actually is? Do the roles it names match the real authorization
   module? Do the endpoints it names exist in the API contract? **Record each mismatch as a
   contradiction to raise. Do not resolve it yourself.**
4. **Build the gap list.** For each of the six discovery questions in 1B, decide: *answered by
   the document* with a quote and a pointer, *partially answered* with what is missing, or *not
   in the document*. Add the contradictions from step 3 and the document's own open items.

Then skip 1B's interview. Present the summary in section 4 directly, with the gap list as the
only questions.

### 1B. From-scratch mode: interview: the vision

Ask the user, adapting the wording but keeping the coverage, in **one compact message**, not an
interrogation drip:

> **New PRD. Discovery**
>
> I'll interview you in two rounds (vision now, detailed requirements next), then draft the PRD
> for your approval. First, the big picture:
>
> 1. **What are we building?** One or two sentences: the product and its core job.
> 2. **For whom?** Who uses it, and who sponsors or owns it?
> 3. **What problem does it solve?** What happens today without it, and what is painful about
>    that?
> 4. **Domain sources of truth?** Is there an existing system this replaces or must match. A
>    legacy app, a spreadsheet, an API spec, a written brief, business rules? If yes, where do
>    they live? Their rules and copy carry over **verbatim** into the PRD.
> 5. **Hard constraints?** Deadlines, budget, compliance, integrations that must be used,
>    devices or locales that must be supported.
> 6. **Non-goals?** Anything explicitly out of scope for this version.

**Wait for the user's response.** Do not proceed without substantive answers to at least 1
through 3.

### 3. Probe gaps, lightly

- **Document mode:** ask **only** the gap list from 1A.4. Group them in one message and cite
  the document location next to each: "section 3 says X, but the API contract has no such
  endpoint. Build it, or is section 3 stale?" Cap at what actually changes the PRD. Everything
  else lives in the open-questions section.
- **From-scratch mode:** if answers are thin, ask **at most 2 or 3** targeted follow-ups. For
  example: "who is the very first user on day one?", "does the legacy system have behaviour we
  must reproduce exactly?", "is this greenfield or a migration at feature parity?". Do not
  interrogate. A PRD can carry open questions.

If sources of truth were named and are accessible, you may skim them now, read-only, to ground
later questions. **Do not dump their contents back at the user.**

### 4. Present the discovery summary for approval

Display:

> **Discovery summary. Please confirm**
>
> - **Source:** {document mode: `<path>`, read in full, N sections | from scratch: your answers}
> - **Product:** {one-line statement} {[document section]}
> - **Users / sponsor:** {who} {[section]}
> - **Problem:** {the pain, stated concretely} {[section]}
> - **Domain sources of truth:** {each source, where it lives, what carries over verbatim, or
>   "none, greenfield, the user's answers are the source"}
> - **Hard constraints:** {list, or "none stated"}
> - **Non-goals:** {list, or "none stated"}
> - **Decisions the document already makes:** {list. Each becomes a locked decision in step 2
>   unless you object}
> - **Contradictions with the codebase / open items:** {list, or "none found"}
> - **Open questions so far:** {anything unresolved}
>
> **Menu:**
>
> - **[A] Approved**: continue to detailed requirements.
> - **[R] Revise**: tell me what to change.
> - **[Q] Add detail**: answer more questions first.

**Halt and wait for the user's choice.**

#### Menu handling

- IF A: proceed to section 5.
- IF R: apply the corrections, re-present, re-show the menu.
- IF Q: take the additions, update the summary, re-show the menu.
- IF anything else: clarify, then re-show the menu.

### 5. Route

Once approved, note "Discovery approved" and carry the summary forward. In document mode, carry
the quoted outline too, because step 2 proposes the requirement set from it.

Then read fully and follow `step-02-requirements.md`.

## Success / failure

✅ **Success:** vision, users, problem, sources of truth, constraints, and non-goals captured in
the user's or the document's own terms. In document mode the document was read completely, every
bullet points at its origin, and the interview covered only gaps, contradictions, and open
decisions. Sources of truth recorded with locations. Summary explicitly approved.

❌ **Failure:** drafting PRD content in this step. Inventing domain facts to fill silence.
**Skimming the input document and paraphrasing it as if read.** Re-asking the user what the
document already answers. Skipping the sources-of-truth question. Proceeding without approval.

**Master rule:** Understand the product before enumerating it. Sources of truth are found at
discovery time, not discovered mid-draft, and when the user hands you one, you read all of it
first.
