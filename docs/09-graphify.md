# Graphify: token optimization via navigation

**What this page answers:** how to stop paying the whole-repo context price on every
agent session, by building a navigable index of the codebase once and then paying
only for the parts each question actually needs.

## The definition

**Graphify: turn the repository into a persistent, queryable graph, then answer
questions by navigating the graph instead of re-reading the repository.**

The dominant cost of agentic engineering is not the model, it is the *context
feed*. An agent that greps and reads its way to understanding pays the
whole-corpus price every session, on every question, forever — and the
[lost-in-the-middle](https://arxiv.org/abs/2307.03172) effect means a fat context is
not just expensive, it is worse at attending to the part that matters. The fix is
old engineering: **build an index once, navigate it cheaply, update it
incrementally.** Databases did not replace table scans with more RAM; they replaced
them with B-trees. A code graph is the B-tree of agentic context.

The concrete tool pagar uses is the open-source **graphify** — PyPI package
[`graphifyy`](https://pypi.org/project/graphifyy/), by Safi Shamsi,
[github.com/Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify). pagar
contributes the method and ships an operating-manual skill for it in the starter
kit: [`starter/.claude/skills/graphify/`](../starter/.claude/skills/graphify/SKILL.md).
The tool is a dependency of the *method's convenience*, not of pagar: the gate
runner still starts with a plain `node`.

## How the economics work

A graph build has two halves, and only one of them costs tokens:

- **Structural extraction is deterministic and free.** Code is parsed with local
  tree-sitter ASTs — imports, calls, definitions, dependencies. No LLM, no API key,
  code never leaves the machine. On a code-only corpus the entire build costs zero
  model tokens.
- **Semantic extraction is optional and cached.** Docs, papers, and images get
  entity/relationship extraction (the host agent, or Gemini if a key happens to be
  set). Results are cached per file and per extraction prompt; an incremental
  `--update` re-extracts only new or changed files.

After the build, `graphify-out/graph.json` is a plain, committed-or-ignored file in
your repo. Questions become traversals:

```
graphify query "how does publish flow through the API?" --budget 1500
graphify path "AuthModule" "Database"
graphify explain "NoteService"
```

A `--budget` cap turns an answer into a bounded expense. Navigation touches the
neighborhood of the question — two communities and a bridge node — instead of the
whole forest. The graph is the map; the agent is the guide.

## Why a graph and not a search index

Search answers "where is X mentioned." A graph answers "what is X connected to, and
what crosses the boundary X lives in." The graph build also runs community
detection and surfaces two things nobody thinks to search for:

- **God nodes** — the nodes with outsized connectivity. Your real architecture,
  as built, not as drawn.
- **Surprising connections** — edges crossing community boundaries that the
  directory layout says should not exist. These are your hidden couplings, and the
  reports say so in plain language.

And the whole thing carries an honest audit trail: every edge is EXTRACTED (parsed,
deterministic) or INFERRED (model-derived, with a confidence) or AMBIGUOUS. An
index that cannot tell you which of its facts are measured and which are guessed is
a liability in a harness.

## Keeping it honest

- **Never invent an edge.** Unsure is AMBIGUOUS, not connected.
- **Always show the token cost.** The report carries input/output token counts and
  a cumulative cost tracker, because the entire point is economics.
- **The shrink guard.** A rebuild that produces fewer nodes than the committed
  graph refuses to overwrite it — an empty extraction must never clobber a good
  index.
- **The health check.** Dangling endpoints, self-loops, collapsed edges — the
  silent corruption modes of incremental updates — are surfaced, read-only, every
  build.
- **A stale graph is a best-effort failure, never a gate.** Per the
  [loop-engineering laws](08-loop-engineering.md): a stale index degrades the
  quality of assistance; it does not make this story's code wrong. Re-cluster on
  epic boundaries, refresh in a hook, warn — never block a merge on it.

## When not to

A graph of a 20-file service is ceremony; grep is faster than the build. The graph
pays for itself when onboarding into an unfamiliar codebase, working across many
communities (frontend, backend, infra), or answering cross-cutting questions
("everything that touches money"). The method's own rule applies: where a piece is
not carrying its weight, delete it.

For the joining-a-repo workflow in practice, see
[`workflows/05-joining-a-repo.md`](../workflows/05-joining-a-repo.md).

---

Next: [10-six-principles-one-workflow.md](10-six-principles-one-workflow.md) — the
whole fence, assembled.
