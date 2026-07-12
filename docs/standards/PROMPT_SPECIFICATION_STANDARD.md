# Prompt Specification Standard

Every production prompt must be version-controlled and contain:

1. Agent name and version
2. Purpose
3. Allowed task types
4. Required context
5. Instruction hierarchy
6. Tool policy
7. Output JSON schema
8. Quality rubric
9. Failure and escalation behavior
10. Example valid output
11. Evaluation cases
12. Change history

Prompts must not contain secrets, environment-specific credentials, or hidden dependencies on conversation history.
