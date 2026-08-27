# Step 02: Write the smallest correct fix

You have a proven mechanism. **Write the FAILING TEST FIRST**, then the fix.

⚠ **A test written AFTER a passing fix is a test that has NEVER BEEN SEEN TO FAIL**, which is
exactly what step 03 exists to catch. **Writing it first means you get that evidence FOR FREE
instead of manufacturing it later.**

## Sequence

### 1. Fix at the right altitude

**Two opposite failure modes, and both are common:**

- **TOO NARROW. Patching the INSTANCE instead of the MECHANISM.** If the root cause is "these two
  sides can disagree", **fixing the one field in today's report LEAVES THE NEXT FIELD BROKEN.** Ask:
  **what is the most general statement of this bug, and does my fix cover it?**
- **TOO BROAD. Refactoring the neighbourhood while you are in there.** A hotfix diff that
  reorganizes someone else's module **will not survive review and BURIES THE ACTUAL CHANGE.**

**Two rules that resolve most altitude questions:**

- ⚠ **PREFER FIXING BY VALUE OVER FIXING BY NAME.** **A fix keyed on a hardcoded list of field
  names DECAYS SILENTLY the moment someone adds a field. A fix keyed on the PROPERTY that makes
  those fields special CANNOT.** Dropping every key whose value is absent fixes the **class**.
  Listing three field names fixes **only today's instances, and the next field added to the schema
  is broken on arrival.**
- ⚠ **FIX AT THE SHARED CHOKE POINT, NOT PER CALL SITE.** If several call sites must agree, **the
  fix belongs in the one function they all route through, and IF THERE IS NOT ONE, CREATING IT IS
  THE FIX. Two call sites each normalizing independently IS THE BUG, not the shape of the
  solution.**

### 2. Match the surrounding code

Follow the project's conventions for the surface you are in. **A shared repository's patterns win
over your preferences.**

### 3. Write the reasoning down where it will be read

> **THE SINGLE MOST VALUABLE ARTIFACT OF A HOTFIX IS *WHY*, RECORDED NEXT TO THE CODE. A one-line
> fix with no explanation is RE-BROKEN by the next person who finds the line surprising.**

Record three things:

1. **What the two sides, states, or inputs actually are.**
2. ⚠ **Why the obvious NARROWER fix is wrong. THIS IS WHAT STOPS THE NEXT ENGINEER "SIMPLIFYING"
   YOUR FIX BACK INTO THE BUG.**
3. **What still correctly triggers the guarded behaviour**: what you did **not** loosen.

### 4. Write the test that would have caught it

**Cover THREE things. THE THIRD IS THE ONE PEOPLE SKIP:**

1. **The bug**: the exact case that failed, **asserted at the level the bug LIVES.** If it is a
   key-set divergence, assert on the key set. If it is a status code, assert on the wire. If it is
   a rendered string, assert on the rendered output.
2. **The general case**: **the instance the report did NOT name**: field N+1, the other writer,
   the other enumerated value, the other role. **If your fix is by-value, THIS IS WHAT PROVES IT.**
3. **The gate still closes**: **every behaviour the fix must NOT have loosened.** ⚠ **A FIX THAT
   STOPS A FALSE POSITIVE BY DISABLING THE CHECK IS A WORSE BUG WITH A GREENER SUITE.** Assert the
   real change **still** fails, the real error **still** raises, the real rejection **still**
   rejects for the caller that should get it.

⚠ **If a premise of your test could silently stop being true, ASSERT THE PREMISE TOO. Otherwise
the test quietly starts testing nothing.**

⚠ **BEWARE THE VACUOUS NEGATIVE.** An assertion that something *did not happen* **proves nothing
until you have seen the detector return TRUE at least once.** **Any "X did not change" assertion
over a collection that could be EMPTY needs a POSITIVE CONTROL.** The same applies to asserting an
element is absent: it is meaningless unless a sibling test shows the element **can** appear.

## → Next

Read fully and follow `steps/step-03-verify.md`.
