# Vocabulary

Generated from vocab.json.

## moment

- admission: Plan admission before execution.
- step: Self reports and host expectations for one step.
- final: Checks used for judgement, sealing or verification.

## outcome

- PASS: Checked and satisfied within the stated scope.
- FAIL: Checked and contradicted within the stated scope.
- UNKNOWN: Not determined because evidence or execution was unavailable.
- NOT_APPLICABLE: Inapplicable for a stated reason backed by evidence.

## scope

- content_model: Computational content and domain consistency.
- preparation_model: Preparation feasibility within the stated model.
- file: Faithfulness and integrity of files and records.
- user_goal: Coverage of the declared computable requirements.

## issuer

- check_capability: A registered CHECK capability.
- tool_self_report: A capability reporting on its own output.
- host_expectation: A host-provided expectation evaluated by the runtime.

## role

- ACTION: A capability that performs a planned action.
- CHECK: A read-only checking capability.

## output_role

- construct: A construct requiring preparation-model checks.
- component: A component with material checks when applicable.
- primer_set: Primers requiring quality, order and reaction checks.
- analysis: An analytical output; domain checks come from declarations.

## run_state

- PLANNED: An admitted plan has not begun execution.
- RUNNING: The run is executing or has pending work.
- HALTED: A failed step awaits revision or abandonment.
- COMPLETED: No pending steps remain and failed steps have replacements.
- ABANDONED: The run was abandoned and is terminal.

## step_state

- PENDING: No execution event exists for the step.
- RUNNING: The step has started without a terminal event.
- COMPLETED: Execution and required host expectations completed.
- FAILED: Execution or a host expectation failed.

## effects

- pure: No external side effect is declared.
- reads_files: Reads declared files.
- writes_files: Writes only in the supplied work directory.
- external_process: Runs a local process through the execution context.

## status

- draft: A rule is in draft form.
- active: A rule is in use.
- retired: A rule is no longer in use.

## verification_status

- unverified: The source has no recorded human verification.
- verified: A human source-verification receipt is recorded.

## review

- none: No review record exists.
- draft: Changes were requested or the record is incomplete.
- reviewed: An approval record matches the reviewed content.
- stale: The content differs from the review record.

## actor

- program: A program-observed fact.
- ai_host: A declaration submitted by the host.
- human: An interactive human declaration.
- unknown: The information origin is unknown.

## origin

- plan_declared: A reason supplied with a plan or revision.
- original_statement: A statement matching recorded source text.
- organized_summary: A later organized summary.
- later_interpretation: A later interpretation.
- unknown: The origin is not established.

## relation_basis

- hash_equal: An explicit input binding has equal content hashes.
- declared: The relationship is declared rather than program-verified.

## input_origin

- user_file: A local file supplied by the user.
- researcher_observation: An observation reported by a researcher.

## source_class

- literature: A cited research publication.
- official_method: An official method or documentation source.
- project_contract: A declared project boundary or requirement.
- lab_protocol: A laboratory protocol or experience record.
- database_record: An identified database record.

## laboratory_label

- PLANNED: A laboratory operation is planned.
- NOT_PERFORMED: A laboratory operation has not been performed.

## error_category

- INVALID_INPUT: An operation was not admitted because input is invalid.
- CAPABILITY_FAILURE: A capability failed to execute its contract.
- ENVIRONMENT: A local runtime dependency or resource is unavailable.
- POLICY: An operation violates the declared policy.
- INTEGRITY: Content or history does not match its recorded identity.
- INTERNAL: An unexpected implementation failure occurred.

## exit_code

- 0: The command completed; scientific outcomes are separate.
- 1: The command returned an error.
- 10: Mandatory checks refused sealing; this is not an execution error.
