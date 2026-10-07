---
description: Queue all tasks from a design doc - mark each TODO as next
argument-hint: <doc-number-or-filename>
---

# Queue Design Doc

Queue all tasks from design document **$ARGUMENTS**: mark each `TODO` task in it as one the team has said is next.

There is no backlog file. `bin/backlog` computes the backlog from the task headings, and a queued task is a `TODO` heading with a `:QUEUED:` property.

## Process

### 1. Resolve Document

Find the design document from the identifier:

- If number (e.g., `007`, `7`): Look for `docs/design/007-*.org`
- If filename (e.g., `007-queue-design-doc.org`): Use directly
- If path: Use as provided

Read the document and extract title from `#+TITLE:`.

### 2. Pre-flight Checks

Before queuing tasks, validate the document is ready:

#### 2a. Status Check

Read `#+STATUS:` header:

| Status   | Action |
|----------|--------|
| Accepted | Proceed, will set to Active |
| Active   | Proceed with note "already in progress" |
| Draft    | Warn: "Document is still Draft. Queue anyway?" |
| Review   | Warn: "Document is in Review. Queue anyway?" |
| Complete | Abort: "Document already Complete, no tasks to queue" |
| Archived | Abort: "Document was Archived" |

#### 2b. Open Questions Check

Scan `* Questions` section for `** OPEN` headings.

If any found:
1. List each open question with its body text
2. For each question, help the user decide:
   - Show any options mentioned in the question body
   - Ask for their decision
   - Update the heading to `** DECIDED` with `:DECIDED: [YYYY-MM-DD]` property
   - Add decision rationale
3. After all resolved, continue

#### 2c. Decision Commentary Check

Scan `* Decision` and `* Design` sections for:
- Sub-headings: `*** Comment`, `*** Note`, `*** TODO`, `*** FIXME`
- Inline markers: `TODO:`, `FIXME:`, `NOTE:`, `XXX:`

If found:
1. Surface each comment/note with context
2. Ask: "Address this before proceeding? (yes/no/skip all)"
3. If yes: help resolve and update document
4. If no/skip: continue

### 3. Task Discovery

Find `* Tasks` section and collect all `** TODO` headings:

- Extract task ID from heading (pattern: `[PROJECT-NNN-XX]`)
- Extract title (rest of heading after ID)
- Read `:EFFORT:` property
- Read body text as description

Skip headings with states: `DONE`, `HOLD`, `WIP`

### 4. Mark Each Task Queued

For each discovered `TODO` task, add `:QUEUED: [YYYY-MM-DD]` to its property drawer (create the drawer if it has none). Leave a task that already has `:QUEUED:` alone.

```org
** TODO [DAB-007-01] Task title                                      :p1:
:PROPERTIES:
:EFFORT: M
:QUEUED: [2026-10-07]
:END:
```

Nothing is copied anywhere: the heading is the task.

### 5. Create Claude Task List

For each queued task:
- Create a Claude Task with matching ID and title
- Add `:CLAUDE_TASK:` to the task heading in the doc (working state; `/backlog:design-complete` removes it)
- Set dependencies if task order implies them (sequential tasks depend on previous)

This creates the coordination layer for multi-session/subagent work.

### 6. Update Document Status

After queuing tasks:
- If `#+STATUS:` was `Accepted` (or `Draft`/`Review` and user confirmed), set to `Active`
- Update `docs/design/README.org` index to reflect new status
- Work has begun on this design doc

### 7. Enter Plan Mode

Present the tasks as a plan for execution:

```
## Plan: Implement [Document Title]

Based on design doc [NNN], executing these tasks:

- [ ] [DAB-NNN-01] First task
- [ ] [DAB-NNN-02] Second task
- [ ] [DAB-NNN-03] Third task

Claude Task List ID: <list-id>

Proceed with plan?
```

The plan, the queued headings, and the Claude Tasks now represent the same work.

Commit the doc and README on their own (`chore: queue NNN`) before starting, so the other developer sees what is queued the next time they pull.

### 8. Summary Output

Display results:

```
## Queued: NNN - Document Title

**Pre-flight:**
- Status: Accepted ✓
- Questions: 2 DECIDED, 0 OPEN ✓
- Comments: None found ✓

**Tasks queued:**
- [DAB-007-01] Task title
- [DAB-007-02] Another task (already queued)

**Skipped:**
- [DAB-007-03] Completed task (DONE)

**Claude Tasks:**
- Task List ID: <list-id>
- Tasks created: 2
- Plan mode: Active
```

## Examples

```
/queue-design-doc 007
/queue-design-doc 7
/queue-design-doc 007-queue-design-doc
/queue-design-doc docs/design/007-queue-design-doc.org
```

## Files

- Design docs: `docs/design/*.org`
- Index: `docs/design/README.org`
- View: `bin/backlog`
