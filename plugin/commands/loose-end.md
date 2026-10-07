---
description: Record a note that belongs to no design doc, as its own file in docs/loose-ends/
argument-hint: <note> | --resolve <slug> | --move <slug> <doc>
---

# Loose End

Record, resolve, or move a loose end: **$ARGUMENTS**

## What a Loose End Is

A note that matters beyond this session and belongs to no design doc — "lint is red in three files", "the stylesheet is overdue for a restructure", "the e2e server boots from scratch on every run". Each one is its own file in `docs/loose-ends/`, so two developers conflict only when they edit the same note. `bin/backlog` lists them under *Loose ends*.

If the note belongs to a doc, it goes in that doc (as a task, an `OPEN` question, or a finding), not here.

## Record (default)

1. Pick a short slug from the note: `lint-is-red`, `css-restructure`.
2. Write `docs/loose-ends/<slug>.org`:

```org
#+TITLE: Lint is red
#+CREATED: [2026-10-07]

=ruff check .= finds five errors in three files. Two are =--fix=-able; =DJ006= on the household admin form is a real question.

Checked [2026-10-07].
```

   Title is the claim, not a category. Body says what is true and how it was checked, dated, so the next reader knows how stale it is.
3. Commit the file alone: `docs: loose end, <title>`.

## `--resolve <slug>`

Delete the file and commit: `docs: resolve loose end, <title>` with one line on how. Git keeps the note.

## `--move <slug> <doc>`

The loose end turned out to belong to a doc. Add it there — as a `TODO` task with the next free ID, an `OPEN` question, or a finding, whichever it is — delete the file, and commit both together.

## Files

- Loose ends: `docs/loose-ends/*.org`
- View: `bin/backlog`
