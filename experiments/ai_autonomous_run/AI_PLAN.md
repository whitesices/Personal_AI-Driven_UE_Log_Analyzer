# AI Plan

## Objective

Use a bounded autonomous run to improve the analyzer while preserving project safety.

## Planned Steps

1. Inspect existing UE rule behavior.
2. Identify one false-positive or missing-rule risk.
3. Update the smallest relevant module.
4. Add focused tests.
5. Run quality gates.
6. Record result and residual risks.

## Acceptance Criteria

- Existing CLI still works.
- Existing tests still pass.
- New behavior has a test.
- No unsafe filesystem behavior is introduced.
- The change is documented in the experiment notes.

