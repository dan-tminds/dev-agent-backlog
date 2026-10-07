# Backlog Plugin for Claude Code

Design doc driven task management for human-agent collaboration.

For full documentation, see the [GitHub repository](https://github.com/farra/dev-agent-backlog).

## Quick Start

```bash
# Set up your project (interactive)
/backlog:setup

# Or just say: "Set up design docs for this project"
```

## Commands

| Command                                  | Description                                         |
|------------------------------------------|-----------------------------------------------------|
| `/backlog:setup`                         | Initialize design doc system in a project           |
| `/backlog:new-design-doc <title>`        | Reserve a number on main and create a design doc    |
| `/backlog:design-review <doc>`           | Guide doc through review workflow                   |
| `/backlog:queue-design-doc <doc>`        | Mark all of a doc's tasks queued                    |
| `/backlog:task-queue <id>`               | Mark a task queued                                  |
| `/backlog:task-start <id>`               | Begin work on a task                                |
| `/backlog:task-complete <id>`            | Mark a task as done                                 |
| `/backlog:task-hold <id> <reason>`       | Put a task on hold                                  |
| `/backlog:task-link <id> <flags>`        | Add link properties to a task                       |
| `/backlog:loose-end <note>`              | Record a note that belongs to no doc                |
| `/backlog:design-complete <doc>`         | Mark a doc Complete and clear its working state     |
| `/backlog:renumber-design-doc [doc]`     | Repair two docs with one number                     |
| `/backlog:checkpoint [range]`            | Write what we now believe; supersede the old docs   |
| `/backlog:reconcile-backlog`             | Find stale working state across the docs            |
| `/backlog:reconcile-design-docs`         | Find tasks that are done but not marked             |
| `/backlog:migrate-backlog`               | Move an old backlog.org into the docs               |

## The Backlog Is a View

There is no backlog file. Every task's state is on its heading in its design doc, and `bin/backlog` (installed by setup, stdlib Python) computes the view:

```bash
bin/backlog                 # in progress, on hold, queued, loose ends
bin/backlog --all           # and every unqueued TODO
bin/backlog --questions     # OPEN questions
bin/backlog --org > backlog.org
bin/backlog --next-number   # counts origin/main
bin/backlog --check         # collisions and stale working state
```

See design doc 017, *Two Developers, One Repo*, for why.

## Skills (Auto-triggered)

| Skill            | Triggers when...                                 |
|------------------|--------------------------------------------------|
| `backlog-resume` | Session starts; shows WIP and handoff notes      |
| `backlog-update` | Before commits; records progress in the doc      |
| `new-design-doc` | Architectural discussions suggest creating a doc |
| `setup`          | User wants to initialize design doc system       |

## Task ID Format

```
[PREFIX-NNN-XX]
   │      │   └── Task sequence (01, 02, ...)
   │      └────── Design doc number
   └───────────── Project prefix (e.g., ACME)
```

## Learn More

- [Full Documentation](https://github.com/farra/dev-agent-backlog)
- [Design Doc Pattern](https://github.com/farra/dev-agent-backlog/blob/main/docs/design/002-design-docs.org)
- [Backlog Workflow](https://github.com/farra/dev-agent-backlog/blob/main/docs/design/003-backlog-workflow.org)
