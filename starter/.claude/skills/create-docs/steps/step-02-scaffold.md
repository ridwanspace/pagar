# Step 02: Scaffold the tree

## Step goal

The tree exists, with a real index and **an API reference table generated FROM THE CODE.**

## Sequence

### 1. Create the tree

⚠ **THE INDEX IS THE NAVIGATION.** **There is usually no navigation generator, so A PAGE NOT LINKED
FROM ITS INDEX IS UNREACHABLE, and NOTHING FAILS AT BUILD TIME to tell you.**

**Every page created in any later step gets its index link IN THE SAME EDIT.**

⚠ **Folder and file names are USER-FACING COPY TOO.**

⚠ **If this file type is ignored by default in your repository, the files you create are INVISIBLE
to your version-control status until you force-add them.** Know that before you wonder where they
went.

### 2. Generate the reference table

**GENERATE, never hand-type.** Derive it **by loading the application in-process.**

⚠ **NEVER by calling a running server, which may be running stale code, and NEVER from the
committed snapshot, which is a snapshot.**

**Paste the output between marker comments:**

```
<!-- reference-table:start -->
<!-- reference-table:end -->
```

⚠ **The markers make regeneration IDEMPOTENT**, and `/code-review` re-runs this exact command after
every surface-shaping story.

⚠ **An empty summary means the handler has no docstring. FIX IT AT THE SOURCE, not by typing prose
into the table.**

### 3. Verify before proceeding

Run the project's test suite. **If it has pre-existing failures, compare against the recorded
baseline rather than chasing them. You touched only documentation.**

Then **open the index and follow every link by hand, once.**

Then load `steps/step-03-helpers.md`.
