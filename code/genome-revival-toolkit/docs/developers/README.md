# Development source map

Start with [Add a Kit in about 30 minutes](add-a-kit.md), the
[copyable template](../../examples/kit-template/README.md) and the
[Kit anatomy diagram](kit-anatomy.svg). Its [HTML source](kit-anatomy.html)
uses system fonts and contains no external resources.

This review source tree retains the original src/dna_design_core, tools and test
paths selected by ship.json. It does not contain the repository's internal
decision archive or personal development evidence. The repository specification
is the authority; the evaluator documents explain the currently shipped surface.

The release tools are build-time utilities. They do not add product verbs,
capability registries, runtime installers or a second version source. The current
runtime's release-manifest loading gap is tracked for its owner, not patched by
the build tool. Full repository structural tests use the complete development
checkout; the installed-package example uses only the installed public CLI.

Release support remains incomplete until the explicit pending items in the
evaluator guide and root README are resolved. Official GitLab CI 未执行.
