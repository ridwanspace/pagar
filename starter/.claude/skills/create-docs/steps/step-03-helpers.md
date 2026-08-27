# Step 03: Page patterns + structural guards

## Step goal

Establish **the vocabulary every page writes in**, and **the guards that keep it honest.**

## 1. Establish the page patterns

| Pattern | Purpose |
|---|---|
| **Reference table** | The generated surface list. Never hand-typed. |
| **Worked example** | A real request and its real response, captured. |
| **Understand first** | A collapsible mental-model block, **before** the steps, for concept-heavy flows only. |
| **Flow list** | A compact numbered sequence. **Replaces box diagrams.** |
| **See also** | Cross-links, so no page is a dead end. |
| **Error table** | The likely failures and what they mean. |

**Adapt the copy, labels, headings, to the guide's language. Do not adapt the STRUCTURE.**

## 2. Build the structural guards

**Two guards, both two-directional:**

1. **Parity.** **Every documented surface EXISTS in the contract**: no ghost surfaces surviving a
   rename, **AND every in-scope surface APPEARS in the documents**: no shipped-but-undocumented
   surface. ⚠ **BOTH DIRECTIONS. One direction alone catches half the drift.**
2. **Dead links.** **Every anchor resolves to a real heading in its file, and every relative link
   resolves to an existing file.** ⚠ **A renamed heading or a moved file SILENTLY STRANDS its
   links.**

### Guard discipline

- **Both are IMPORT-SHAPED or CALL-SHAPED.** The parity guard **loads the real application and
  reads the real contract.** ⚠ **Never a substring match against source files, never a live server,
  never the committed snapshot.**
- ⚠ **Both STRIP fenced blocks, inline code, and comments before matching. A GUARD MUST NOT FIRE ON
  ITS OWN DOCUMENTATION.**
- **Both carry a loud-scan sanity check.** ⚠ **Thresholds start low for a young corpus. RAISE THEM
  AS THE CORPUS GROWS, so the guard CANNOT PASS VACUOUSLY if the folder moves.**
- 🚨 **MUTATION-VERIFY EACH GUARD RED BEFORE TRUSTING IT.** Plant a ghost surface, delete a table
  row for an in-scope surface, and plant a dead anchor and a dead file link in a scratch page.
  **Watch the RIGHT test fail. Revert.** **A GUARD NEVER SEEN RED IS NOT EVIDENCE.**

**Place the guards where the project's existing test command already picks them up**, so they join
the regular suite and its coverage automatically.

Then load `steps/step-04-author-pages.md`.
