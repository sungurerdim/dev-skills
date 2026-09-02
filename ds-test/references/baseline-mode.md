# Baseline Mode — ds-test Phase 2e (`--baseline`)

Full steps for capturing a characterization baseline before refactoring a legacy module. Loaded when `--baseline` mode runs.

1. **Identify surface:** collect the target module's public interface (exported functions, class/struct methods, CLI commands, API endpoints). `=path` provided → narrow to that path only; otherwise use the directory or module containing the changed code.
2. **Generate characterization tests:** drive each surface member with realistic inputs including boundary cases (empty, null, max-size, unicode, boundary numerics). Record the ACTUAL outputs — whatever the code returns today — as expected values. When current behavior appears incorrect (e.g., off-by-one, wrong default, silent swallow of an error), STILL assert it; tag the test with the comment `// characterization: documents current behavior, not intent` and raise a Category B finding (`needs-approval`) so the user decides fix-vs-keep before refactoring.
3. **Run to green:** a failing characterization test means the captured expectation is wrong — fix the TEST to match actual output, never modify the source. Repeat until all pass.
4. **Report:** surface-coverage % (ratio of public surface members with at least one characterization test — compute from the two counted lists via `wc -l`, never by estimate) + list of oddities raised as Category B findings.

**Note — not assertion-weakening:** asserting observed behavior (even when it looks incorrect) with a `characterization: documents current behavior, not intent` tag and a Category B finding is the correct pattern — documented capture + user decision gate, never silent acceptance of a relaxed assertion.
