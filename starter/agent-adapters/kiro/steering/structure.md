# Structure

File organization, naming, imports, and the architecture rules that hold across the project.

Replace every `{{PLACEHOLDER}}`. Delete what does not apply.

## Layout

```
{{DIR_1}}/          {{WHAT_LIVES_THERE}}
{{DIR_2}}/          {{WHAT_LIVES_THERE}}
{{DIR_3}}/          {{WHAT_LIVES_THERE}}
{{DIR_4}}/          {{WHAT_LIVES_THERE}}
{{DIR_5}}/          {{WHAT_LIVES_THERE}}
docs/               documentation for humans
.kiro/steering/     these files
.kiro/specs/        Kiro specs
```

## Layering

{{LAYERING_RULE, e.g. "api calls services, services call models, and nothing calls upward."}}

Two rules that follow from it:

- A lower layer never imports from a higher one. If a model needs something from a service, the
  design is wrong, not the import.
- Business logic lives in the service layer. A request handler that contains a decision is a
  handler you cannot test without a web server.

A violation of the layering is a design bug, not a style preference. Raise it rather than working
around it.

## Where a new thing goes

| You are adding | It goes in | And you must also |
| --- | --- | --- |
| {{THING_1, e.g. "an endpoint"}} | {{LOCATION}} | {{REGISTRATION_STEP}} |
| {{THING_2, e.g. "a background job"}} | {{LOCATION}} | {{REGISTRATION_STEP}} |
| {{THING_3, e.g. "a database model"}} | {{LOCATION}} | {{REGISTRATION_STEP}} |
| {{THING_4, e.g. "a React page"}} | {{LOCATION}} | {{REGISTRATION_STEP}} |

The third column is the one people forget. A new page that no route reaches is invisible. A new
job that no queue routes to never runs. Wiring is part of the work, not a follow-up.

## Naming

- Files: {{FILE_NAMING_CONVENTION}}
- Types and classes: {{TYPE_NAMING_CONVENTION}}
- Functions: {{FUNCTION_NAMING_CONVENTION}}
- Tests: {{TEST_NAMING_CONVENTION}}
- Constants: {{CONSTANT_NAMING_CONVENTION}}

Use the product vocabulary from `product.md`. When the spec says "meeting" and the code says
"session", every future reader pays a small tax, and an agent connecting a requirement to its
implementation pays a large one.

## Imports

- {{IMPORT_STYLE, e.g. "absolute imports from the package root, no relative imports past one level"}}
- {{IMPORT_ORDERING, e.g. "standard library, third party, local, separated by blank lines"}}
- No wildcard imports. They defeat static analysis and hide what a module actually uses.
- No import that exists only for a side effect, unless the side effect is registration and there
  is a comment saying so.

## Change discipline

- Change the minimum that makes the task correct. Do not reorganize code you were not asked to
  touch.
- A refactor is its own change, with its own reason. Mixing a refactor into a feature makes the
  feature unreviewable, because nobody can tell which lines carry the behavior change.
- Match the file you are in. Existing patterns beat your preferences. If a pattern is genuinely
  bad, raise it as a decision rather than fixing it silently in one file, which leaves the
  codebase with two patterns instead of one.
- {{READ_ONLY_PATHS, e.g. "legacy/ is reference only, never modify it"}}

## Documentation lives in two homes

This one is easy to get wrong, and getting it wrong is how documentation goes stale.

- **Working notes** stay next to the workflow: specs, story files, review notes, recorded
  lessons. They are for the person and the agent doing the work.
- **Team-facing documentation** lives under `docs/` and is committed for everyone. It carries no
  references to private workflow files, no internal spec IDs, and no local paths that only exist
  on one machine.

When a change makes a fact wrong, fix it in both homes in the same change. A committed page that
contradicts the code is worse than no page, because people trust it.
