---
description: Mark a task complete in its design doc
argument-hint: <task-id> [version]
---

# Task Complete

Mark task **$1** as DONE in its design doc.

## Process

1. **Find the task** in `docs/design/*.org` by the heading containing `[$1]`. Note `:WORKED_BY:`.

2. **Gather attribution**:
   - Ask: "Who completed this task? (claude-code / human / both)" unless it is obvious from the session

3. **Update the heading**:
   - Change `TODO`/`WIP`/`HOLD` to `DONE`
   - Add `CLOSED: [YYYY-MM-DD]` on the line after the heading
   - If version provided ($2), add `:VERSION:`
   - Add `:COMPLETED_BY:` from step 2
   - Keep `:WORKED_BY:`
   - Remove `:QUEUED:`, `:HANDOFF:` and `:REASON:` — they described work in progress
   - Leave the `:working:` subtree for now; `/backlog:design-complete` decides what in it is a finding

4. **Prompt for CHANGELOG.md** (if the project has one):
   - Ask: "Add to CHANGELOG.md? (Added/Changed/Fixed/Removed/Skip)"
   - If not Skip, add an entry under `## [Unreleased]`

5. **Commit** the doc (and CHANGELOG) with the task ID in the message, e.g. `feat: <what it does> (PROJECT-NNN-XX)`. `/reconcile-design-docs` finds tasks by their ID in the log.

6. **Check for document completion**:
   - Count remaining `TODO`, `WIP` and `HOLD` task headings in the doc
   - If none remain, ask: "All tasks in this design doc are complete. Mark it Complete and clear its working state?"
   - If yes, run `/backlog:design-complete <doc>`

7. **Confirm** with `bin/backlog`.

## Example

```
/task-complete DAB-001-01 v1.0
```

## Format in the Doc

Before:
```org
** WIP [DAB-001-01] Task title
:PROPERTIES:
:EFFORT: M
:QUEUED: [2026-01-02]
:HANDOFF: Tests written, implementation half done
:WORKED_BY: claude-code, human
:END:
```

After:
```org
** DONE [DAB-001-01] Task title
CLOSED: [2026-01-04]
:PROPERTIES:
:EFFORT: M
:VERSION: v1.0
:COMPLETED_BY: claude-code
:WORKED_BY: claude-code, human
:END:
```

## Files

- Design docs: `docs/design/*.org`
- Changelog: `CHANGELOG.md`
