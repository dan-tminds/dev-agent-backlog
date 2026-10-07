---
description: Start or resume work on a task. Reviews context and prepares an implementation plan.
argument-hint: <task-id>
---

# Start Task

Start or resume work on task **$ARGUMENTS**.

All of a task's state lives on its heading in its design doc. There is no backlog file to update.

## Process

### 1. Find the Task

Find the heading containing `[$ARGUMENTS]` in `docs/design/*.org` (skip `#+begin_`…`#+end_` blocks).

- `DONE`: say so and stop.
- `HOLD`: show `:REASON:` and ask whether the hold is over before going on. If it is, delete `:REASON:`.
- `TODO` or `WIP`: go on.

### 2. Read the Handoff

From the task heading:
- `:HANDOFF:`, the note left for whoever picks this up
- The `:working:` subtree under it, if there is one (`*** Working notes  :working:`), newest entries last
- `:WORKED_BY:`, to see who has been on it

**If `:HANDOFF:` has content, display it prominently:**

```
## Resuming [$ARGUMENTS]

**Handoff from last session:**
> <handoff notes here>
```

**If `:WORKED_BY:` names someone other than the current person and the task is already `WIP`**, say so: someone else may be partway through it. On a shared repo, `git log -5 --format='%h %an %ar %s' -- <doc>` shows whether that work is recent. Ask before carrying on.

### 2a. Mark It Started

- Change the state to `WIP`
- Add `:QUEUED: [today]` if it was never queued
- Add the current worker (`claude-code`, and the person's name if known) to `:WORKED_BY:`
- Commit the doc on its own (`chore: start PROJECT-NNN-XX`), so the other developer sees it the next time they pull

### 2b. Create a Claude Task (optional)

If the work will span sessions or subagents, create a Claude Task with the task ID as its subject, and add `:CLAUDE_TASK: <task-list-id>/<task-id>` to the heading. It is working state: `/backlog:design-complete` removes it.

### 3. Gather Related Context

Read the full design doc containing the task:
- Motivation (why this matters)
- Design (how it should work)
- Related tasks (dependencies, sequence)
- Open questions (blockers, decisions needed)

If the doc is `Superseded`, also read the checkpoint named in its `#+SUPERSEDED_BY:`, which is the current statement of what was decided.

### 4. Prepare Implementation Plan

Create a plan with:
- **Goal**: What we're trying to achieve
- **Approach**: How we'll implement it
- **Files to modify**: List of files we'll touch
- **Steps**: Ordered implementation steps
- **Open questions**: Anything that needs clarification

### 5. Present Plan for Review

Present the plan to the user for approval before beginning implementation.

## Example

```
/task-start DAB-001-01
```

## Files

- Design docs: `docs/design/*.org`
- View: `bin/backlog`
