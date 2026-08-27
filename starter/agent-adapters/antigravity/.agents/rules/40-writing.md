# Writing

Always active. Style for anything written in prose: commit messages, pull request descriptions,
code comments, and documentation.

This rule is short on purpose. It is the cheapest one to follow and the easiest to drift on.

## Style

- Short sentences. Plain words. Active voice, and name who does the thing.
- **No em dashes.** Use a period or a comma.
- Do not open with "Great question" or "You are absolutely right".
- Cut these: "In order to", "It is important to note that", "leverage" as a verb, "robust",
  "seamless", "delve", "utilize".
- No decorative emoji.
- Be specific. "Fixed the 500 on empty upload" beats "improved error handling".
- Say the uncertain thing plainly. "I did not test this against a real database" is useful. Hedged
  prose that avoids admitting it is not.

## Commit messages

- Format: {{COMMIT_CONVENTION, e.g. "conventional commits with a scope, feat(api): ..."}}
- The subject line says what changed and where. The body says why, when why is not obvious.
- Describe the change, not the process. "Add pagination to the meetings list" beats "address
  review feedback".
- {{TRAILER_POLICY, e.g. "no trailers, no co-author lines, no tool attribution"}}

## Pull request descriptions

Three things, in this order:

1. What changed, in one or two sentences.
2. Why, if the reason is not obvious from the subject.
3. How you verified it. Name the command you ran, not the intention. "Ran the scoped suite,
   14 passed" beats "tests pass".

Add a fourth section for anything a reviewer would otherwise have to discover: a schema change, a
config change, a behavior change that affects an existing client, or something you deliberately
left out of scope.

## Code comments

- Comment the why, not the what. The code says what it does. It cannot say why the obvious
  approach was wrong.
- A comment that restates the line above it is noise that goes stale.
- Comment the surprising thing. If you had to think for a minute about why this works, write down
  what you thought.
- No commented-out code. That is what version control is for.
- No TODO without a name and a reason. An anonymous TODO is a wish.

## Documentation

- Lead with what the page answers, so a reader can leave immediately if it is the wrong page.
- Write for someone who has not read the previous page.
- Every claim about behavior is either verifiable from the code or marked as unverified. A
  confident wrong statement in documentation costs more than an omission, because people trust it.
- When a change makes a documented fact wrong, fix the documentation in the same change. Grep for
  what you changed.

## Claims about behavior

When you write that something works, say how you know.

- Ran and observed: name the command and the output.
- Read the code: say so, and note that you did not run it.
- Assumed: do not write it.

"Should work" is not a result. Neither is "this looks correct".
