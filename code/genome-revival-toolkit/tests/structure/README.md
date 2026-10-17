# S0 structural seam

Run from the code directory:

```
python -X utf8 -B tools/check_structure.py
python -X utf8 -B -m unittest discover -s tests/structure -v
```

Runtime modules remain empty. Static checks prove that this tree conforms and
that deliberately injected violations are reported. They do not prove a future
engine, biological algorithm, read-only check or immutable seal works.

Each scanner family has a copied-tree negative control. Controls cover relative
imports, import aliases, cycles, forbidden capability/Kit fields, vocabulary and
source errors, versions, network imports, shell use, skip records, and schema
weakening. Positive controls exercise allowed public imports and a valid synthetic
capability. At least one copy uses a non-ASCII directory. Spec scanner controls
inject unregistered events/verbs/invariants, a retired term, and a changed count.

AST coverage is syntactic: ordinary imports/aliases, literals and named journal
calls. Dynamic code generation, indirect writes, scientific exception semantics,
and unresolved future APIs are not claimed. See PENDING_INV for partial checks.
No active Kit or product CLI exists. Scanners are development tools, not product
entry points. They never import runtime/Kit modules or retrieve schema references.

`SKIPS.json` is empty. Pending work is counted separately, never represented as a
passing or skipped test. No GitHub workflow was run or published; INV-Q1 is pending.
Official GitLab CI 未执行.
