# Step 05: Verify the guide end to end

## Step goal

**PROOF, NOT HOPE.** The machine gates green, **AND** every documented call exercised against the
real running system, **AND** every identifier checked against the schema that ships it.

## 1. Machine gates

Run the guards and the project's test suite.

⚠ **A parity failure naming a documented surface usually means the guide TYPED A PATH FROM MEMORY.
REGENERATE THE TABLE instead of editing the row by hand.**

## 2. The field-name diff: the guard's other blind spot

> 🔑 **THE PARITY GUARD CHECKS SURFACES, NOT FIELDS.**
>
> ⚠ **A PAGE NAMING A FIELD THE RESPONSE LACKS READS AS COMPLETELY PLAUSIBLE, BECAUSE THE SENTENCE
> AROUND IT IS TRUE. READING CANNOT FIND THIS.**

**DIFF IT MECHANICALLY, PER PAGE.** Dump the schema's declared fields, extract every backticked
identifier from the page, and compare.

**Every backticked identifier that is not a declared field, a route, a status code, or a command is
a DEFECT.**

⚠ **AND COMPARE BOTH DIRECTIONS. Documents can be wrong BY OMISSION: if a schema gained a field, an
enumeration of its fields is now INCOMPLETE WITH EVERY WORD STILL TRUE.**

## 3. The live check: the guards' real blind spot is the actual wire

**The parity guard proves the surfaces exist in the contract. ONLY A LIVE CALL PROVES THE
DOCUMENTED REQUESTS AND RESPONSES ARE REAL.**

**Replay EVERY worked example EXACTLY AS WRITTEN, copying it from the page.**

⚠ **Any mismatch FAILS THIS STEP: FIX THE PAGE, or fix the seed. NOT THE DIFF.**

## 4. Read-through checklist

- The index reaches **all** pages, in the planned order.
- **Every see-also resolves, both ways.**
- Anchors land.
- Code blocks carry a language hint.
- **Guide-language prose with as-shipped identifiers.** ⚠ **No half-translated keys.**
- 🔒 **No credential, token, or customer record survived from a capture.**

## 5. The human look

⏸️ **HALT.** **Ask the user to read the guide and REPLAY ONE EXAMPLE THEMSELVES.**

> **[A] Looks right · [R] Revise (say what)**

> **GUARD TESTS DO NOT REPLACE THE USER'S OWN EYES ON THEIR GUIDE.**

Then load `steps/step-06-record.md`.
