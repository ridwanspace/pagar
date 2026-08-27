# Product

What this project is, who uses it, and what it is for. Kiro reads this to understand intent, so
that when a request is ambiguous it resolves the ambiguity toward the product rather than away
from it.

Replace every `{{PLACEHOLDER}}`. Delete what does not apply.

## What it is

{{ONE_PARAGRAPH: what the product does, in plain words a new engineer would understand on the
first read. No marketing. No feature list.}}

## Who uses it

| User | What they are trying to do | What breaks their day |
| --- | --- | --- |
| {{USER_TYPE_1}} | {{THEIR_GOAL}} | {{THEIR_PAIN}} |
| {{USER_TYPE_2}} | {{THEIR_GOAL}} | {{THEIR_PAIN}} |
| {{USER_TYPE_3}} | {{THEIR_GOAL}} | {{THEIR_PAIN}} |

The third column matters more than the second. It tells you which bugs are expensive.

## Core capabilities

- {{CAPABILITY_1}}
- {{CAPABILITY_2}}
- {{CAPABILITY_3}}
- {{CAPABILITY_4}}

## What this product deliberately does not do

Listing non-goals stops an agent from helpfully building the thing you decided not to build.

- {{NON_GOAL_1}}
- {{NON_GOAL_2}}

## Locked decisions

These are invariants, not defaults and not preferences. Later work is not allowed to weaken one.
If a task appears to require breaking one, stop and raise it. Do not implement it and mention the
concern afterward.

| ID | Decision | Why it is locked |
| --- | --- | --- |
| D1 | {{DECISION, e.g. "Every list endpoint is paginated, no exceptions"}} | {{REASON}} |
| D2 | {{DECISION, e.g. "Authorization is checked server side in the handler"}} | {{REASON}} |
| D3 | {{DECISION}} | {{REASON}} |

Keep this table short. A table of thirty invariants is a table nobody reads. If something belongs
here only because it is a good idea, it belongs in `tech.md` instead.

## Business constraints

- {{CONSTRAINT_1, e.g. "single tenant per deployment, tenancy is not a feature"}}
- {{CONSTRAINT_2, e.g. "data residency is fixed to one region"}}
- {{CONSTRAINT_3, e.g. "must run without a GPU"}}

## Vocabulary

Use these words in code, in tests, and in commit messages. Consistent naming across the spec and
the code is what lets an agent connect a requirement to the function that implements it.

| Term | What it means here | What it is not |
| --- | --- | --- |
| {{TERM_1}} | {{MEANING}} | {{COMMON_CONFUSION}} |
| {{TERM_2}} | {{MEANING}} | {{COMMON_CONFUSION}} |
| {{TERM_3}} | {{MEANING}} | {{COMMON_CONFUSION}} |
