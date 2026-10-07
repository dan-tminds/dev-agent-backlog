---
name: backlog-resume
description: Check for in-progress work on session start. Use when beginning a new session in a project with docs/design/. Triggers automatically at session start or when user says "what was I working on?", "resume", "continue", or "where did I leave off?". Surfaces WIP tasks and handoff notes from the design docs to enable seamless session continuity.
---

# Backlog Resume

This skill checks for in-progress work when starting a new session, implementing the "hook pattern" from gastown - if there's work on your hook, you should run it.

## Prerequisites

**Before triggering, check that `docs/design/` exists in the project root.**

If it does not, do NOT trigger this skill. The project hasn't been set up with the backlog system. Silently skip.

If the project still has a committed `backlog.org` with a `* Current WIP` section, it predates design doc 017: mention once that `/backlog:migrate-backlog` moves it into the docs, then read it the old way.

## Where the State Is

There is no backlog file. Every task's state is on its heading in its design doc, and `bin/backlog` prints the view:

- *In progress* — `WIP` headings
- *On hold* — `HOLD` headings, with `:REASON:`
- *Queued* — `TODO` headings with `:QUEUED:`
- *Loose ends* — files in `docs/loose-ends/`, notes that belong to no doc

## Workflow

### 1. Pull, Then Read

If the repo has a remote and the working tree is clean, `git pull --ff-only` first: the other developer's started and finished tasks arrive as commits to the docs. Don't pull over uncommitted work; just say the view may be behind.

Run `bin/backlog`. (If `bin/backlog` is missing, run the plugin's `scripts/backlog.py` directly and suggest `/backlog:setup` to install it.)

### 2. Surface WIP Tasks

For each task under *In progress*:
- Read `:HANDOFF:` and `:WORKED_BY:` from the heading
- Read the last entry or two of its `:working:` subtree
- If `:CLAUDE_TASK:` is set, note the Task List ID
- If `:WORKED_BY:` doesn't include the current person, it may be the other developer's: check `git log -3 --format='%an %ar' -- <doc>` and say whose it looks like before offering it

### 3. Present Resume Option

```
## Work in Progress

### [TASK-ID] Task Title  (docs/design/NNN-doc.org:LINE)

**Handoff notes:**
> <:HANDOFF:>

**Recent progress:**
> <last working note>

Continue working on this task?
```

### 4. Quick Consistency Check

Run `bin/backlog --check`. It is fast and reports:
- two docs with one number (suggest `/backlog:renumber-design-doc`)
- one task ID in two places
- a task whose ID doesn't match its doc's number
- working state left in a `Complete` or `Superseded` doc (suggest `/backlog:design-complete`)

Mention what it finds in one or two lines; don't fix anything unasked.

### 5. If No WIP Tasks

Show *Queued* and *Loose ends* from `bin/backlog`:

```
## Ready to Start

No work in progress. Queued:

1. [TASK-ID-1] Task title
2. [TASK-ID-2] Task title

Start one of these tasks?
```

### 6. Handle Response

- Continue: run `/task-start <task-id>`
- A different task: `/task-queue` or `/task-start` it
- Declines: proceed with whatever they want to do

## Related Commands

| Command | When to use |
|---------|-------------|
| `/task-start <id>` | Resume the WIP task |
| `/task-queue <id>` | Queue a new task |
| `/task-hold <id> <reason>` | If task is blocked |
