---
description: Write a checkpoint - a design doc saying what we now believe, superseding the finished docs it summarizes
argument-hint: [doc-range e.g. 001-015] [--draft-only]
---

# Checkpoint

Write a checkpoint over design docs **$ARGUMENTS** (default: every finished doc not already superseded).

The design docs record where decisions were *made*. Over time, learning what is currently believed means reading several of them in order — 003 decided it, 008 revised it, 014 revised it again — and that costs agents context and people time. A checkpoint is a design doc whose subject is the other design docs: what we believe now, what we stopped believing, and what is still open. It goes through `/design-review` like any other doc, which is the point. Re-reading twenty docs and deciding what they add up to is a review the team should have every so often anyway.

## 1. Choose What It Covers

Candidates are docs with `#+STATUS:` `Complete`, `Living` or `Archived` and no `TODO`, `WIP` or `HOLD` tasks (`bin/backlog --all` shows which docs still have open tasks; they can't be covered yet). Skip docs already `Superseded`.

Include the previous checkpoint, if there is one: the new one supersedes it.

Show the user the list and the docs left out and why. Ask before going on.

## 2. Reserve a Number

Create the doc with `/new-design-doc Checkpoint <YYYY-MM>` — it reserves the number like any other. Use category `architecture` (or the project's nearest equivalent).

## 3. Read, Then Write

Read every covered doc in full, oldest first, along with each doc's findings section (often "What building it found"). Use subagents if there are many, one per few docs, each returning: decisions as they stand at the end of that doc, decisions it reversed or revised from earlier docs, findings, `OPEN` questions.

Write the checkpoint with these sections:

```org
* Summary
What this checkpoint covers (docs NNN–MMM) and the one-paragraph state of things.

* What we believe
** <A claim, in the present tense, as a heading>
Why, in a paragraph. Cites: [[file:003-record-schema.org][003]], revised by [[file:014-...org][014]].

* What we stopped believing
** <The old claim>
What replaced it, and what made us change our minds. Cites the docs.

* What is still open
** OPEN <Question carried forward>
Context. Originally [[file:015-...org::*Question heading][015]].

* What it supersedes
| Doc | Title | ID |
|-----+-------+----|
| 003 | [[file:003-record-schema.org][The Record Schema]] | <:ID:> |

* Tasks
(Usually none. If writing it surfaced work, it becomes tasks here or in a new doc.)
```

Rules for the claims:
- **One claim per heading**, short enough that the heading alone is useful in an outline
- **The current version only**; the history goes in the citation and, if it was a reversal, under *What we stopped believing*
- **Every claim cites** at least one doc. A claim nobody can trace is an opinion
- **Don't restate the code.** "Drafts are append-only" is a belief worth keeping; the name of the model that implements it is in the code
- **Carry every `OPEN` question forward** as an `OPEN` heading here, and add a line under the original: `Carried forward to [[file:NNN-checkpoint-...org][NNN]].`

Keep it short. A checkpoint as long as what it replaces has failed. Aim for a tenth.

## 4. Review

Leave it `Draft` and stop (`--draft-only` stops here too). Tell the user it's ready for `/design-review`, which is where the team argues with it.

## 5. When the Checkpoint Is Accepted

`/design-review` runs this step when it accepts a doc that has a *What it supersedes* section. For each covered doc:

- `#+STATUS: Superseded`
- `#+SUPERSEDED_BY: [[file:NNN-checkpoint-YYYY-MM.org][NNN - Checkpoint YYYY-MM]]`
- Its row in `docs/design/README.org`

The files stay where they are, so no link anywhere breaks. Agents are told (by the CLAUDE.md section `/backlog:setup` writes) to start from the newest checkpoint and the docs after it, and to open a superseded doc only to follow a citation.

Mark the checkpoint itself `Complete` (it has no tasks, or `/design-complete` once they're done). Commit the checkpoint and the status changes together: `docs: NNN checkpoint accepted, supersedes K docs`.

## Files

- Design docs: `docs/design/*.org`
- Index: `docs/design/README.org`
- View: `bin/backlog --all`
