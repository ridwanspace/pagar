---
description: The two-homes rule. Personal process knowledge stays in .claude/, repo facts get mirrored into committed team docs, cross-linked both ways, with a checkpoint in the review step
paths:
  - ".claude/rules/**"
  - "{{TEAM_DOCS_DIR}}/**"
---

# The two-homes rule

Knowledge learned while building falls into exactly two homes. Putting a fact in the wrong one
is how a shared repository ends up with documentation that decays into a snapshot of the day it
was written.

| Lives in `.claude/rules/` | Lives in `{{TEAM_DOCS_DIR}}/` |
|---|---|
| How **I** work: baselines, mutation-verify discipline, my gate scripts, the spec pipeline | What **the repo** is: layering, endpoint rules, traps, how to run things |
| References `.claude/` paths, story references, the status file | **Zero** `.claude/` references, a reader with no access to my tree must lose nothing |
| May name the exact file and line of a known committed secret | **Never** names a secret's location. States the rule and the rotation cost |
| Loads on demand into my context | Read by a human in the code-hosting UI |

**Everything in the right-hand column is a repo fact.** A repo fact that a story changed, and
that is now wrong in a committed document, is a **defect**. This rule exists to catch it.

## Mirror, do not duplicate

- A fact belongs in **exactly one** home when it is purely personal or purely a repo fact.
- A fact that is genuinely both, an endpoint rule the repo enforces and that I also enforce
  personally. Appears in **both**, stated once each, **in the register of that home.**
- ⚠ **Never as a copy-paste of the other file's wording.** That is precisely how the two drift
  apart invisibly: the copy looks maintained because the words match, right up until one side
  is edited and the other is not.

## Cross-link both ways

Each local rule file carries a pointer to its committed counterpart at the top, and each
committed page carries a pointer back where that makes sense for the reader. The local pointer
reads:

```
> **Team-facing counterpart:** `{{TEAM_DOCS_DIR}}/<page>.md` (committed).
> This file may carry personal-workflow detail the committed page must not. When a change
> makes the repo fact here wrong, fix BOTH. `/code-review` step 03b is the checkpoint.
```

## The checkpoint

`/code-review` step 03b is the enforcement point, and it is cheap:

```bash
git diff --name-only {{DEFAULT_BRANCH}}...HEAD | sed 's#/[^/]*$##' | sort -u   # which surfaces moved
grep -rn "<the identifier, path, or number that changed>" {{TEAM_DOCS_DIR}}/
```

**The grep is the real check: a committed page that names the thing you changed is the page
that is now wrong.**

Each hit is one of exactly three things. Only the first two produce an edit:

1. **Now false**: the page states behaviour, a path, a line number, or a count that this
   change made wrong. **Fix it.** This is the case the checkpoint exists for.
2. **Now incomplete**: still true, but the change added a case a reader would need. **Add one
   tight entry** in the page's existing shape.
3. **Still true**: the page names the file, but the claim is unaffected. **Leave it.** Do not
   churn a correct page.

A learning with **no** page it belongs in is a **signal, not a gap**: it was personal-workflow,
and `.claude/` was the right and only home. Say so in the close-out.

## Rules for the committed side

- **Surgical edits.** Change the sentence that is wrong. Do not restructure a page as a side
  effect of a one-line behaviour change.
- **Match the page's register**: statements of what the code does, with a path, a line, or a
  commit hash as evidence. No hedging, no "we should".
- **Update a "verified on" date only when you actually re-checked the page's claims**, not
  merely because you edited one line. **A false freshness stamp is worse than a stale one**,
  because it stops the next reader from checking.
- **A genuinely new subsystem gets a new page and a row in the index.** Do not create a page
  for one fact. It belongs in the closest existing page.
- **Verify the cross-links still resolve.** A renamed page breaks relative links silently.
- **Confirm the edited pages are actually staged.** ⚠ A pull request that reads as "docs
  updated" and contains no docs is a real failure mode, usually caused by an ignore rule the
  author forgot about. Check `git status` on the docs path, do not assume.

## The ignore-rule trap

⚠ If your repository ignores a file type by default and re-includes a documentation subtree,
**write the exact rule and its line number here**, and note that a new document **outside** the
re-included subtree needs a force-add.

This costs someone an hour the first time, every time, because the file simply does not appear
in `git status` and nothing explains why.
