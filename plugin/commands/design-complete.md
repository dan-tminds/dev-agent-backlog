---
description: Mark a design doc Complete and clear its working state in its own commit
argument-hint: <doc-number-or-filename>
---

# Design Complete

Finish design doc **$ARGUMENTS**: mark it `Complete` and clear the working state out of it, so what's left reads as the record of a decision and what building it found, for people and for agents.

Clearing is lossless. It happens in its own commit, and the doc records the commit just before it, so the working notes are one `git show` away.

## 1. Resolve and Check

Find the doc as `/design-review` does (number, filename or path).

- Count `TODO`, `WIP` and `HOLD` task headings. If any remain, list them and stop: the doc isn't finished. (A `HOLD` that will never happen should become `DONE` with a note saying it was dropped, or move to another doc, before this runs.)
- If `#+STATUS:` is already `Complete`, carry on: this also cleans docs that were marked Complete before this command existed.
- `OPEN` questions may remain. List them so the user knows; they're not working state.

## 2. Separate Findings from Working Notes

The one judgement here. Read every `:working:` subtree (`*** Working notes  :working:` under a task) and every `:HANDOFF:`.

A **working note** describes the work in progress: "tests written, form half done", "stuck on the date picker", "picked back up after lunch". It goes.

A **finding** is something a later reader of the doc needs: a surprise, a constraint discovered, a decision made while building, a measurement. "Trix loaded the ordinary way draws its own toolbar over ours, which every Django test passed and a screenshot caught." It stays — moved into the doc's findings section (create `* What building it found` before `* Tasks` if the doc has none), rewritten as a sentence that stands on its own, without the date-stamped diary voice.

When you can't tell, ask. Show the user the findings you're about to move, as a list, before writing them.

## 3. Clear

Remove, from every task heading:
- the `:working:` subtrees
- `:QUEUED:`, `:HANDOFF:`, `:REASON:`, `:CLAUDE_TASK:`, `:CLAUDE_TASK_LIST:`, `:TRANSCRIPT:` (a path to one developer's machine)
- a property drawer left empty

Keep: the argument, the decisions, the findings, every task heading with its description, `CLOSED:`, `:EFFORT:`, `:VERSION:`, `:COMPLETED_BY:`, `:WORKED_BY:`, `:GITHUB:`, `:RECONCILED:`.

## 4. Mark Complete

Before editing the header, note `sha=$(git rev-parse --short HEAD)` — the last commit with the working state in it.

- `#+STATUS: Complete`
- `#+LAST_MODIFIED: [today]`
- `#+WORKING_STATE: <sha>` — where to look for what was cleared
- The doc's row in `docs/design/README.org`

## 5. Verify and Commit

`bin/backlog --check` must not report working state for this doc.

Commit the doc and README alone:

```
docs: NNN complete, working state cleared

Moved K findings out of working notes. The notes are in <sha>.
```

## 6. Report

- Findings moved, by task
- What was cleared (counts)
- `OPEN` questions still on the doc
- `git show <sha>:docs/design/NNN-slug.org` to see it as it was

## Files

- Design docs: `docs/design/*.org`
- Index: `docs/design/README.org`
- Check: `bin/backlog --check`
