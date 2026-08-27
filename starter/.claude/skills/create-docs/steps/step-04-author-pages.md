# Step 04: Author the guide pages

## Step goal

Each page **teaches before it instructs**, where the flow needs it, **shows the real surface**, and
**links outward.**

## 1. Page anatomy

- **The heading is the TASK, IN THE USER'S WORDS.** "Check the service is healthy", **not** "Health
  operations".
- **Understand-first block**, for concept-heavy flows only, in this order: **analogy → how it works
  as a flow list → why it matters.**
- **Steps**, numbered, each ending with **its observable result, so the user can self-verify.**
- **Auth is part of the surface.** **Say which role the flow needs, and show it in the worked
  example.**
- **See-also links.**

## 2. Examples: real responses, NEVER remembered ones

> ⚠ **A RESPONSE TYPED FROM MEMORY IS A PARAPHRASE WEARING A CODE FENCE.**

**Capture from a real call.**

- ⚠ **Redact or seed anything non-deterministic, timestamps, ids, tokens, AND SAY SO NEXT TO THE
  BLOCK. An example the reader cannot reproduce verbatim READS AS BROKEN.**
- 🔒 **NEVER paste a real credential, token, or customer record into a page.**
- **Error paths too.** **Every documented surface shows at least its most likely failure, captured
  the same way.**
- **Multi-page flows get ONE end-to-end worked example**, a single concrete scenario walked start to
  finish, **before** the per-page detail.

## 3. Wire the navigation as you go

**Order pages by THE USER'S TASK ORDER, not alphabetically.** ⚠ **An unlinked page is
unreachable.**

**Every page gets at least one see-also link where a second page exists. NO DEAD ENDS.**

## 4. Review with the user

⏸️ **After the FIRST page, HALT and show it.**

**Tone, depth, and example style set the pattern for the rest. It is CHEAPER TO CORRECT NOW.**

> **[A] All good · [R] Revise (say which) · [M] More pages needed**

Then load `steps/step-05-verify.md`.
