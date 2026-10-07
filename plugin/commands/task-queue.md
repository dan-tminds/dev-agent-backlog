---
description: Queue a task - mark it as next in its design doc
argument-hint: <task-id>
---

# Task Queue

Queue task **$ARGUMENTS**: mark it, in its own design doc, as one of the tasks the team has said is next.

There is no backlog file. The backlog is computed from the task headings in `docs/design/*.org` by `bin/backlog`, and a queued task is a `TODO` heading with a `:QUEUED:` property.

## Process

1. **Find the task** in `docs/design/*.org`:
   - Search for the heading containing `[$ARGUMENTS]` (skip `#+begin_`…`#+end_` blocks; examples live there)
   - If it is not found, say so and stop. If it is found twice, stop and suggest `bin/backlog --check`.

2. **Check its state**:
   - `DONE`: say so and stop
   - `WIP` or `HOLD`: already on the backlog; say so and stop
   - `TODO` with `:QUEUED:`: already queued; say so and stop

3. **Mark it queued** by adding to the heading's property drawer (create the drawer if it has none, directly under the heading and any `CLOSED:` line):

```org
** TODO [PROJECT-NNN-XX] Task title                                    :p1:
:PROPERTIES:
:EFFORT: M
:QUEUED: [YYYY-MM-DD]
:END:
```

4. **Update the doc's status**:
   - If `#+STATUS:` is `Accepted`, change it to `Active` and update the row in `docs/design/README.org`
   - If `Draft` or `Review`, leave it

5. **Commit** the doc (and README if changed) on its own: `chore: queue PROJECT-NNN-XX`.

6. **Confirm** by showing the output of `bin/backlog`.

## Files

- Design docs: `docs/design/*.org`
- Index: `docs/design/README.org`
- View: `bin/backlog`
