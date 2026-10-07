---
description: Add link properties to a task in its design doc
argument-hint: <task-id> --github <url> | --claude-task <id> | --bead <ref>
---

# Task Link

Add link properties to task **$ARGUMENTS**, on its heading in its design doc.

## Purpose

A task lives in one place — its design doc — and may also be represented elsewhere: a GitHub issue, a Claude Task, a bead. This command records those links on the task heading so either side can find the other.

## Usage

```
/task-link <task-id> --github <url>
/task-link <task-id> --claude-task <task-list-id>/<task-id>
/task-link <task-id> --bead <session>/<task>
```

Multiple links can be added at once:

```
/task-link DAB-012-02 --github https://github.com/org/repo/issues/15 --claude-task abc123/task-001
```

## Process

### 1. Find the Task

Find the heading containing `[<task-id>]` in `docs/design/*.org`. If it is not there, report the error: a task has to belong to a design doc before it can be linked. Work that belongs to no doc is a loose end (`/backlog:loose-end`).

### 2. Parse Link Arguments

| Flag | Property | Example Value |
|------|----------|---------------|
| `--github` | `:GITHUB:` | `https://github.com/org/repo/issues/15` |
| `--claude-task` | `:CLAUDE_TASK:` | `abc123/task-001` |
| `--bead` | `:BEAD:` | `session-xyz/task-002` |

### 3. Format Link Properties

```org
:GITHUB: [[https://github.com/org/repo/issues/15][#15]]
:CLAUDE_TASK: abc123/task-001
:BEAD: [[bead:session-xyz/task-002][bead ref]]
```

### 4. Update the Heading

Add the properties to the task's `:PROPERTIES:` drawer.

- If a property already exists, ask before overwriting
- Preserve all existing properties
- `:GITHUB:` and `:BEAD:` are permanent; `:CLAUDE_TASK:` is working state and `/backlog:design-complete` removes it

### 5. Commit and Confirm

Commit the doc on its own and show the updated drawer.

## Files

- Design docs: `docs/design/*.org`
