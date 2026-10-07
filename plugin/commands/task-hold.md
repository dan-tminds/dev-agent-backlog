---
description: Move a task to HOLD with a reason, in its design doc
argument-hint: <task-id> <reason>
---

# Task Hold

Put task **$1** on hold, with reason: **$2**

## Process

1. **Find the task** in `docs/design/*.org` by the heading containing `[$1]`.

2. **Change its state** to `HOLD` and add `:REASON:` to its property drawer:

Before:
```org
** WIP [DAB-001-01] Task title
:PROPERTIES:
:EFFORT: M
:QUEUED: [2026-10-01]
:END:
```

After:
```org
** HOLD [DAB-001-01] Task title
:PROPERTIES:
:EFFORT: M
:QUEUED: [2026-10-01]
:REASON: Waiting for dependency release
:END:
```

3. If the task was `WIP`, update `:HANDOFF:` with whatever the next person needs to pick it back up.

4. **Commit** the doc on its own: `chore: hold DAB-001-01`.

5. **Confirm** by showing `bin/backlog`; the task is now under *On hold*.

To release a hold, set the state back to `TODO` (or `WIP` via `/task-start`) and delete `:REASON:`.

## Example

```
/task-hold DAB-001-01 Waiting for dependency release
```

## Files

- Design docs: `docs/design/*.org`
