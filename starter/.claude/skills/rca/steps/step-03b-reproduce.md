# Step 03b: Reproduce: see the user-visible findings with your own eyes

## Step goal

**A reproduction, with the network call behind it captured, is the STRONGEST OWNERSHIP EVIDENCE
this skill produces: it shows what the client SENT and what the server ANSWERED in one frame.**

## Mandatory rules

- 🎥 **Use one harness. Do not invent a second one.** This is **verify mode, not capture mode.**
- 🔐 **Credentials from the environment only. Never inline them.**
- 🛑 **Read-only in the interface against a shared system.** Reproduce **by navigating and
  observing.** **Mutating flows are reproduced ONLY with the client pointed at your own local
  system**, or noted as reproduction-blocked → NEEDS-INFO.
- ⏱️ **Timebox.** Two or three honest attempts per finding. **A non-reproduction is a RESULT.**
- 🔑 **Name the account role beside every authorization-flavoured result.** ⚠ **A forbidden result
  behind a disabled button is still a forbidden result.**

## ⚠ Which system is the client actually talking to?

| Setup | What a result proves | Mutations |
|---|---|---|
| Dev server proxying to a **shared** system | "the deployed build does or does not do this" | **read-only** |
| Local override pointing at **your own** system | "**this checkout** does or does not do this" | allowed |
| The **deployed host** directly | "what the reporter saw" | **read-only** |

**A mismatch between the reporter's environment and yours is THE FIRST THING TO RECORD when
something does not reproduce.**

## Sequence

### 1. Decide whether this step runs at all

### 2. Reproduce, one finding at a time

**Where the steps are vague, use the most ordinary interpretation AND RECORD THE INTERPRETATION YOU
CHOSE.**

**Capture, every time:**

- **A screenshot** named for the finding.
- **Console and page errors.** ⚠ **These frequently ARE the root cause.**
- **Network reality**: the method, path, status, and **the SHAPE of the payload: keys, not
  values.** ⚠ **Include the RETRY PATTERN**, because "slow" may actually be "failing three times".
- **Flag state**, if the surface is gated.

Then **look at the screenshot.** ⚠ **DO NOT CLAIM A VISUAL OUTCOME YOU HAVE NOT LOOKED AT.**

### 3. Record the verdict per finding

`REPRODUCED | NOT-REPRODUCED | BLOCKED`, plus what you attempted and the artifacts.

- **Reproduced on one account but not another** → **conditional, not universal. Scope the finding's
  TITLE to the condition.** ⚠ **Whether that state is even supported is a PRODUCT QUESTION →
  NEEDS-INFO, not automatically a bug.**
- **Reproduced differently than reported** → **keep it confirmed, but rewrite the observed line to
  what you ACTUALLY SAW.**
- **NOT-REPRODUCED** → **state the environment delta**: data, account, flag state, which system the
  client talked to, or already fixed on this branch.

### 4. Clean up

Then load `steps/step-04-root-cause.md`.
