# Adding a Kit

Follow the [runnable 30-minute tutorial](../developers/add-a-kit.md) and copy
[`examples/kit-template/`](../../examples/kit-template/README.md). The
[Kit anatomy](../developers/kit-anatomy.svg) maps the four contributions and
the three check moments. The tutorial's marked commands are executed verbatim
by `tests/e2e/run_add_a_kit.py`, including portable verification and a one-byte
tamper probe. Kits depend on the matching Core revision.

A Kit contributes capabilities, knowledge, pipeline templates and text through
its kit.json manifest. Undeclared contributions are not loaded. Kit names use
hyphens; Python modules are mapped by the loader. Implementations use only the
Core public interfaces, shared biology and their own package.

Each capability needs a parameter schema, typed ports, explicit effects, output
roles and stated limits. CHECKs include actually executed positive and negative
fixtures with independent answers. Document ports use either a shared schema
reference or one frozen inline schema. Knowledge comes from the owner-scoped,
read-only frozen context. Source-incomplete rules remain in knowledge/drafts
and are not declared as loadable knowledge.

Use fixed material ports for multiple inputs. An independent model receives
matching named inputs and parameters and compares the shared product's sequence,
topology and ends. Scientific meaning and its evidence must remain explicit.

Before contribution, run structural, declaration, unit, integration and synthetic
end-to-end checks. A correct output alone is not evidence that a scientific
method, host behavior or wet-laboratory operation works. Human review signing
and scientific acceptance must be supplied by the responsible people; this guide
does not supply them. Refer to the repository's current specification and the
Kit task before implementation. Official GitLab CI 未执行.
