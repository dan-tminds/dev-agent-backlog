---
name: claude-tasks-sync
description: Ensures Claude Tasks that do design-doc work are cross-referenced from the task heading in the doc. Triggers when creating Claude Tasks, using TodoWrite, or when subagents create tasks for work on a design doc task. Keeps the design doc as the human-readable record while agents use their native primitives.
---

# Claude Tasks Sync

This skill ensures a Claude Task doing the work of a design doc task is linked from that task's heading. The doc is where humans look; agents follow the link to their native primitive.

## Prerequisites

**Before triggering, check that `docs/design/` exists in the project root.** If it does not, silently skip; Claude Tasks work normally without it.

## Core Principle

**Sync means cross-references, not content replication.**

- When a Claude Task is created for a design doc task, add `:CLAUDE_TASK:` to that task's heading
- Don't copy descriptions either way
- Don't mirror status automatically
- A Claude Task with no design doc task behind it stays session-local. It is not tracked anywhere else, and that is fine: there is no backlog file to add it to. If the work turns out to matter beyond this session, it is either a task in a doc or a loose end (`/backlog:loose-end`).

## When to Trigger

- Creating Claude Tasks (via TodoWrite or task management) for a design doc task
- Spawning subagents that will create their own Tasks for one
- After `/queue-design-doc` creates a Task List

## Workflow

### 1. Find the Heading

The design doc task is the one being worked: usually `WIP` under *In progress* in `bin/backlog`, or named by ID in the request.

### 2. Add the Link

```org
** WIP [DAB-012-08] Create sync skill
:PROPERTIES:
:QUEUED: [2026-10-01]
:CLAUDE_TASK: <task-list-id>/<task-id>
:END:
```

Or, for a whole doc's Task List, `:CLAUDE_TASK_LIST: <task-list-id>` on each task heading it covers.

Both are working state: `/backlog:design-complete` removes them when the doc is finished.

### 3. When Subagents Create Tasks

After a subagent completes, check for new Tasks that correspond to design doc tasks and link them the same way.

## What NOT To Do

- Don't create task headings in a design doc just to hold a Claude Task
- Don't remove existing properties
- Don't create duplicate links - one per task

## Related Skills

| Skill | Relationship |
|-------|--------------|
| `backlog-update` | Records progress on the same heading |
| `backlog-resume` | Reads `:CLAUDE_TASK:` on session start |
