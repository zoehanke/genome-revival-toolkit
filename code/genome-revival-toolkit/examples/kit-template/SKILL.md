---
name: word-count
description: Run the tutorial word counter when explicitly asked to count a phrase or exercise the add-a-Kit walkthrough.
disable-model-invocation: true
---

Read `README.md` for counting semantics, independent answers and limits.
Use the project's single public CLI with `--kit-dir` pointing to this folder.

1. Describe this Kit and its capabilities. Resolve exact versions from declarations.
2. Create a run with this Kit loaded. Declare the goal using `examples/goal.json`.
3. Instantiate this Kit's `count` template with the returned goal digest and text.
4. Submit `result.draft`, then execute. Check the step verdict as well as run state.
5. Judge and seal. Only claim a seal when `result.sealed` is true.
6. Copy only the sealed directory, keeping its basename, and verify with matching
   Core and Kit code. Require `verified: true` and no entries in `not_rerun`.
7. Report the literal count, minimum decision and verified computational scope.
   Human review belongs to the responsible person. Laboratory work is `NOT_PERFORMED`.

This example depends on the same Core version. It makes no scientific claim.
