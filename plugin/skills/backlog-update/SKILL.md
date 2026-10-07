---
name: backlog-update
description: Reminder to record progress in the design docs before commits or when finishing significant work. Use before committing changes, after completing implementation from plan mode, or when wrapping up a work session. Ensures each task heading in docs/design/ reflects actual progress. Trigger when about to commit, exiting plan mode, or when user says "done", "let's commit", "wrap up", or similar.
---

# Backlog Update Reminder

This skill reminds you to record progress on the task's heading in its design doc before a commit. The doc should reflect reality in the same commit as the work.

## Prerequisites

**Before triggering, check that `docs/design/` exists in the project root.** If it does not, silently skip and proceed with the commit normally.

## Where Things Go

There is no backlog file. Write to the place the note belongs:

| Note | Where |
|------|-------|
| Progress on a task | The `:working:` subtree under the task's heading |
| What the next person needs | `:HANDOFF:` on the task's heading |
| Something a later reader of the doc needs | The doc's findings section (e.g. "What building it found") |
| Something that belongs to no doc | A loose end: `/backlog:loose-end` |
| A status paragraph about the project as a whole | Nowhere. `bin/backlog` is the status; the docs are the narrative. |

That last row is deliberate. A running "where things stand" journal at the top of a shared file is what made two branches impossible to merge (design doc 017).

## Workflow

### 1. Find the Task

Run `bin/backlog` and look under *In progress* for the task this work belongs to. If none fits, ask whether the work belongs to a task that should be started (`/task-start`), to a loose end, or to nothing.

### 2. Add a Working Note

Under the task heading, in a child heading tagged `:working:` (create it if missing, as the last child of the task):

```org
** WIP [PROJECT-NNN-XX] Task title
:PROPERTIES:
:QUEUED: [2026-10-01]
:WORKED_BY: claude-code, dan
:END:

The task's description.

*** Working notes                                                  :working:
[2026-10-06] Earlier note.
[2026-10-07] What was done, what remains.
```

The `:working:` tag is what lets `/backlog:design-complete` clear these mechanically later, so keep progress chatter inside it and nowhere else in the doc.

If the note is something a later reader of the doc needs — a surprise, a constraint discovered, a decision made while building — write it in the doc's findings section instead, not under `:working:`.

### 3. Assess Task Status

- **Still in progress?** Leave as `WIP`
- **Blocked?** Suggest `/task-hold <id> <reason>`
- **Complete?** Suggest `/task-complete <id> [version]`

Do NOT mark complete automatically - that's an explicit user action.

### 4. Check CHANGELOG.md

If significant user-facing changes were made and the project has a `CHANGELOG.md`, suggest an entry under `## [Unreleased]` (Added / Changed / Fixed / Removed).

### 5. Check Design Doc Status

If every task in the doc is now `DONE`, prompt: "All tasks in [doc] are complete. Run `/backlog:design-complete`?"

### 6. Update Handoff Notes

If stopping mid-task, update `:HANDOFF:` on the heading: what was tried, where it's stuck, what to try next. Replace the old value rather than appending; history is in the working notes and in git.

### 7. Then Commit

Include the doc in the same commit as the work it describes, and put the task ID in the message. The other developer sees the progress on their next pull, and it merges like any other change to that doc.

## Related Commands

| Command | When to suggest |
|---------|-----------------|
| `/task-complete <id>` | Task is fully done |
| `/task-hold <id> <reason>` | Task is blocked |
| `/task-queue <id>` | A task should be next |
| `/backlog:loose-end <note>` | A note with no doc |

## Example

```
User: "Let's commit these changes"

Claude: "Before committing — [DAB-001-01] is WIP in 001. We just built
the directory structure. Should I:
1. Add a working note (still more to do)
2. Mark complete with /task-complete DAB-001-01
3. Proceed without updating (unrelated work)"
```
