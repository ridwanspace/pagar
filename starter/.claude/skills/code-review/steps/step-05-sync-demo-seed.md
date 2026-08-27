# Step 05: Grow the demo and development seed

## Step goal

Keep the project's **seed data** growing in lockstep with the codebase. As each story ships a new
seedable thing, extend the seed script so the demo and development data exercises it too, then
re-apply it locally and verify.

**Not every story needs this. Only ones that introduce data a user or tester would want to see
populated.** If the project has **no seed script yet**, offer to create one the first time a story
would benefit. **Skip cleanly otherwise.**

**This is what makes the seed compound: every qualifying story means more realistic demo data, so
the next verification pass starts from a fuller system instead of empty responses.**

## Mandatory rules

- 📖 Read this whole step before acting. **Skim the existing seed script before deciding.**
- 🎯 **Judgment-gated. Skip cleanly when there is nothing to seed.** A pure read surface, a
  presentation-only tweak, a job, a refactor, or a rule change means **no seed growth. State why
  and advance. "Skip the work, not the step."**
- ♻️ **Reuse the REAL writers, never raw inserts.** New data goes through the story's actual
  service writer, **so every seeded row respects validation, audit, and cascade rules.** Raw
  inserts only for tables that genuinely have no writer.
- 🔑 **Idempotent and duplicate-tolerant.** Every seeded entity uses a **stable key**, so a re-run
  dedups to a no-op, and every create tolerates an already-existing row. **Re-running the whole
  seed must add ZERO rows. No randomness. Deterministic values only.**
- 🚫 **Never touch test fixtures.** If the project has pinned datasets a guard test asserts against,
  **the seed stays separate from them.** If your new seed data is adjacent to a locked invariant,
  **re-run the relevant guard test to confirm it is untouched.**
- 🛑 **Local automatic, remote asks.** Re-run the seed on the local store automatically. **If the
  project seeds a shared environment, HALT at a menu before touching it. Never seed production
  from this step.**
- 🔒 **Keep teardown honest.** If the seed has a teardown path and you add rows to a new table,
  **add its delete in an order that respects foreign keys, children before parents, so teardown
  stays complete.**

## Sequence

### 1. Decide if this step applies

Classify what the story shipped:

| What the story shipped | Seed growth? |
| --- | --- |
| A new **master or catalog** entity | **Yes**. Seed a couple of representative rows via its create service. |
| A new **transactional writer** that appends rows | **Yes**. Drive a few realistic rows through it. |
| A new **concept or field that changes what a response shows** | **Maybe**. Seed enough to make the new surface non-empty. |
| A pure **read surface or report** over existing data | **No**, it renders data already seeded. Note it and skip. |
| **Presentation-only**, a **job**, a **library**, a **refactor**, or a **rule or infrastructure** change | **No**, nothing new to seed. Note it and skip. |

- **No persistence layer at all yet** → print one line and go to `step-06-improve-pipeline.md`.
- **NO** → print one line naming why and go to `step-06-improve-pipeline.md`.
- **YES but no seed script exists yet** → offer to create one now:
  > This story shipped seedable data ({what}), but the project has no development seed yet. Create
  > one now. Idempotent, driving data through the real writers, starting with just this story's
  > data? (yes / skip for now)

  If yes, create it minimally: any prerequisite rows, this story's data, idempotent, with a
  teardown path. **If skip, note it as a deferred follow-up** and advance.
- **YES and a seed exists** → continue. State in one line what you will add.

### 2. Grow the seed script

**Read the script first. Match its existing shape and helpers.**

- **A new master** → import its create service, push representative rows keyed on a **stable
  natural unique**, tolerating an already-existing row. **A re-run, or a row created by hand, must
  not throw.**
- **A new transactional writer** → call it with a stable key and **realistic, deterministic,
  varied** values. **Respect the writer's real constraints. Pull them from the service, do not
  guess.**
- **A new table with no writer** → a guarded find-then-insert keyed on its natural unique.
- **Update the teardown** with the new table's delete, in foreign-key-safe order.

**Respect the invariants the PRD's locked decisions declare. Seeded data must satisfy them like
real data would.**

Then run the project's gates over the seed script itself, where they exist.

### 3. Apply to LOCAL, automatically

Run the seed. Then **verify the new rows landed and the seed is still idempotent**:

- **Run it a SECOND time. It must add ZERO rows.**
- Spot-check the new table's count.

If the new data is adjacent to a guard-tested invariant, **re-run that guard test to confirm it is
untouched.**

### 4. Remote environments: HALT and ask first

If this project seeds a shared environment too, **present a menu and WAIT**: apply the same grown
seed there with whatever credential procedure the project documents, or leave it as a documented
follow-up. **If the project has no such environment, skip this silently.**

### 5. Update the seed documentation

If the project documents its seed dataset, a dedicated page, a README section, a header comment,
reflect the growth: what the seed now covers, and any expected counts. **Keep it accurate to what a
fresh run actually produces. A stale count is worse than none.**

⚠ **If a documented count and reality disagree, do NOT reflexively "fix the doc".**

- A count that went **UP** is usually the document lagging a story that grew the seed. **Fix the
  document.**
- A count that went **DOWN, or to zero, is the signature of a SEED REGRESSION. Fix the seed.**
  **Investigate before renumbering, or you hide the regression permanently.**

### 6. Close the step

> **Demo seed. Story {ref}:** {grew the seed: +{entity}, +{N} rows | created the seed, first
> seedable story | no growth, {why} | no persistence layer yet | deferred by the user}. Local:
> {re-seeded and idempotent-verified, second run added 0 rows | n/a}. Guard tests: {re-run, intact
> | not invariant-adjacent}. Seed docs: {updated | none kept}. Teardown: {extended for {table} |
> unchanged | n/a}.

Then read fully and follow `steps/step-06-improve-pipeline.md`.

## Success / failure

✅ **Success:** correct apply-or-skip decision. New data driven **through the real writers**, with
raw inserts only where no writer exists. **Stable keys, so a re-run is a VERIFIED no-op.**
Duplicate-tolerant creates. Teardown kept complete. Local re-seeded automatically **and verified**.
Any shared environment seeded **only after the user said so.** Invariant guard tests confirmed
untouched where relevant. **Seed documentation matching a fresh run, with any downward drift
investigated as a possible regression rather than silently renumbered.**

❌ **Failure:** raw-inserting data a writer exists for. Growing the seed for a read-only story. **A
non-idempotent addition, where a re-run adds rows.** A create that throws on a pre-existing row.
**Leaving teardown stale**, which breaks on the new foreign key. **Seeding a shared environment
without asking.** Mutating a pinned test fixture. **Stale documented counts.** Silently creating a
seed the user deferred.

**Master rule:** Every story that ships seedable data grows the demo dataset through the real
writers, idempotently, on local automatically, so the seed always mirrors what the system can now
do.
