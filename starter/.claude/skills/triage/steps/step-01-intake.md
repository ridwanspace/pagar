# Step 01: Intake: normalize the report into checkable issues

## Step goal

Turn whatever arrived, a chat dump, a spreadsheet, three screenshots and a sentence, an issue
tracker entry. Into a **numbered set of discrete issues**, each with the one thing triage needs:
**a claim specific enough to check. Nothing is judged in this step.**

## Mandatory rules

- 🛑 Do NOT check whether it is solved, verify, reproduce, or read code yet.
- 🛑 Do NOT write the triage file yet, and **do NOT edit any code.**
- 📖 Read this whole step before acting.
- ✂️ **One issue equals one observable behaviour.** **Reports routinely bundle three bugs in a
  sentence and split one across three bullets. Fix that HERE, or every later step inherits the
  mess.**
- 🖼️ **Open every image BEFORE you write a single issue line.** **An unread screenshot is unused
  evidence, and it is usually the only environment signal in the report.**

## Sequence

### 1. Take the input

- **Pasted with the invocation** → use it.
- **Invoked bare** → ask: *"Paste the issue report. Text, screenshots, a file path, or an issue
  link all work."* **Then STOP and wait.**
- **A file path** → read that file.
- **Images only, no prose** → read them, **state what you infer from each in one line, and confirm
  your reading with the user before splitting. Never invent a claim the reporter did not make.**

### 2. Read the images

For each image, extract and note:

- **Route or URL**: from the address bar or the visible navigation. **This decides which
  environment this is**, which changes everything downstream.
- **The literal rendered text**: error copy, labels, counts, empty-state strings. **Quote it
  EXACTLY. The reporter's paraphrase is not the string.**
- **State markers**: which tab, which record, toggles, ids, timestamps, **which account or role is
  signed in if visible.**
- **Panels**: a console or network tab in frame is **high-value evidence. Read it.** A request
  with its status code settles ownership faster than any amount of prose.

**If an image contradicts the prose, say so explicitly and go with the image.** If an image is
illegible, or was described but not actually attached, **note it as a gap.**

### 3. Establish the batch identity

One line each. Ask **only** if genuinely unclear **and** it changes the outcome:

- **Source**: who reported it, and where.
- **Environment**: which one, plus the version or date if given. ⚠ **Environments lag the default
  branch by different amounts, so "already fixed on the default branch" and "not yet promoted" are
  DIFFERENT ANSWERS**, and a report about an already-merged fix on a downstream environment is
  `/promotion-audit` territory, not triage.
- **Batch slug**: kebab-case, for the filename.

Then pick the next report number by listing the existing reports.

### 4. Split into discrete issues

Walk the input and emit a numbered list. **For each issue, fill only what the reporter actually
gave:**

```
### Issue N: <short title>
- **Raw report (verbatim):** "<exactly what was written. Do not paraphrase>"
- **Surface:** <route / page / component AND/OR endpoint / job>
- **Observed:** <what happened, as reported>
- **Expected (per reporter):** <what they expected, "(not stated)" if they did not say>
- **Repro steps:** <as given, or "(not given)">
- **Evidence:** <image N: what it shows / request id / status code / none>
- **Account / role (if known):** <username or role>
- **User-visible?** <yes|no>. Drives whether step 03 tries a cheap reproduction
```

**Splitting rules:**

- **Split** when one report names two surfaces or two behaviours → two issues.
- **Merge** when several bullets describe one behaviour from different angles → one issue, **keeping
  every raw quote.**
- **Keep the verbatim quote. Your paraphrase can smuggle in an assumption. The quote is the
  evidence of what was actually claimed.**
- **Do NOT judge yet.** Even if an issue is obviously already fixed or obviously working as
  designed, **record it neutrally.** Steps 02 and 03 prove it, **with a citation the reporter can
  check.**
- **Do NOT assign ownership yet.** "Looks like a server thing" is a guess until step 03 reads the
  code, **and recording it now biases the reading.**

### 5. Note the blocking gaps only

For issues that cannot be checked without more information, note the **specific** question.

Then apply this filter:

- **A few** issues have gaps → note them, proceed. **They may still resolve from the code**, and
  become NEEDS-INFO only if they do not.
- **Most or all** are uncheckable → **stop and ask the user once**, listing exactly what is missing
  per issue.

**Ask only what a HUMAN can answer**: scope, priority, environment, intent. **Anything answerable
from the code or the contract is YOUR job in steps 02 and 03. Never ask what you can look up.**

### 6. Confirm the split before checking anything

Present the numbered list compactly, title, surface, user-visible, one line each, and say:

> That's **N issues**. Next I check whether any are already solved, on the default branch, in a
> teammate's branch, or in a prior investigation. Before spending anything on investigation.

Ask: *"Anything mis-split, or any issue you want dropped or prioritized?"*

**Wait for confirmation.** **The user often knows that issue 4 is a duplicate or that issue 7 is
the only one that matters this sprint, and that reshapes everything downstream.**

## Step completion

Carry forward: the batch identity, the confirmed numbered issue list, and the per-image findings.

Then load `steps/step-02-already-solved.md`.
