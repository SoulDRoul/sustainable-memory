<!-- SPDX-License-Identifier: CC-BY-4.0 -->
# Sustainable Memory

Author: SoulDRoul
Collaboration & editing: Echo

[English](README.en.md) | [中文](README.md) | [中文简版](README.plain.md)

## What this is

A method for giving an AI long-term memory that does not rely on auto-summarization, but on hand-written files and a fixed set of rituals. It runs in any agent that can read and write files.

Its foundation is memory — not the model, not the conversation, not the cache. Change the model and it remains; start a new conversation and it remains.

It does not promise to create a life. It promises one thing: **corrections you can carry across sessions** — an error is pointed out by a person; the system makes sure it is not lost and not repeated.

It also does not solve: retrieval speed (there is no vector store; recall is a fixed read), several writers at once (one person by default), or making the model smarter (the memory travels; the model's habits do not).

## Why

1. **Forgetting at the end of every session.** Each turn starts from zero; yesterday's decision has to be explained again.
2. **Auto-summaries quietly rewrite.** They flatten away "what I said no to," and nobody notices when they get it wrong.
3. **No "no."** A tool always agrees — agrees until it burns itself out. It will not refuse for the sake of lasting.

## The minimal version: three files, two actions

(Manual version: no directories, no scripts. For scripts, jump to "How to start" below.)

Files:

- `当前状态.txt` (Current State): what is happening now. Three lines per project — status / reason / next step.
- `否决清单.txt` (Veto List): things not to bring up again. Append only; one quoted line per entry, with its source.
- A **handover note**: one page per session, answering three questions — where this session got to / where to pick up / anything newly ruled out.

Actions:

- **Close-out**: read Current State / Veto List (and INDEX, if you keep one) → write one page → advance the Veto List's "covered through" marker to that page.
- **Recall**: read Current State / Veto List / the chain tail. The tail is not "the newest page" — it is **the page no note lists as its previous one**; list `10-情景-海马` or read INDEX first.

One iron rule, for session notes only: **append only; a correction is a new entry.** Memory that has been edited cannot be trusted.
(`当前状态.txt` is the exception: it is overwritten each time, keeping only the latest.)

## Beyond notes

The three files govern *what is recorded*. They do not govern judgment — where a file goes, when to act, how rules change, how to attribute an error. That is a separate page: `20-程序-小脑/方法.md`.

Behavioral rules live in `20-程序-小脑/对话规程.md` (how to disagree, how to correct, what the limits are).
"What I changed my mind about" goes in `00-语义-皮层/认知变迁.txt`; "where I went wrong" in `自画像.txt`.
Unverified directions have their own page: `附-假设与验法.md` (Chinese) — not a roadmap; try one when you have no idea.
A five-minute demo: `演示.md` (Chinese) — the shape of one veto landing in a file, and the next session avoiding it.
What not to expect: it won't grow up on its own, a new model won't behave the same, a veto is a trace rather than a guarantee, and the ritual will lapse.

## How to start

Before anything: **your agent must be able to read and write this directory.** That is the only hard requirement.
Python 3 and git are conveniences — without them you can still work by hand (checklist in `方法.md`, section 9).

1. Copy `模板/` into a directory of your own.
2. `git init` there (skip it if you have no git, but then back up by hand).
3. Rename `AGENTS.example.md` to whatever startup file your agent reads (e.g. `AGENTS.md`).
4. Run `python 20-程序-小脑/recall.py` (or `python3` on some systems) and read its first block, "环境".
   Gaps are printed there; only then "no notes yet" — that is normal, continue with "The first hour".

Python 3.5+, no dependencies. Close-out: `python 20-程序-小脑/close_out.py`;
add `--apply <note> -m "message"` to write the "covered through" marker (Chinese `[覆盖至: <note>]`) and commit.
It commits memory files only (note, veto list, current state, INDEX) — everything else in the directory is left alone,
which is also what keeps keys out of the history.

## How to talk to it

Four phrases are enough:

- **"Recall"** — it reads Current State, the Veto List, and the chain tail; restates "what is happening / next step / what not to bring up," then stops.
- **"Close out"** — it drafts one handover page for you to edit; updates Current State, advances the marker, commits.
- **"Never bring this up again"** — it copies the line into the Veto List with a date and source.
- **"You were wrong, because…"** — it records the change in `认知变迁.txt`: what it believed, what it believes now, and why.

Any other time, just ask. It answers and leaves the files alone.

## The first hour

These three are yours to judge. The agent can draft the words; you decide. Only then is the system started:

1. **Write three vetoes.** Open the Veto List and write three concrete things not to bring up again. Events, not principles.
   (Write them yourself, or say them and let it copy — the judgment is yours.)
2. **Write one handover note.** Three lines are enough. Second line: `[上一份: 无]` (or `none`) — the scripts only read this Chinese label.
   Write the first one yourself so you see the shape; after that it drafts and you edit.
3. **Correct it once.** Find one thing it got wrong and have it record the correction in `认知变迁.txt`.

It cannot make these judgments for you — the wording it can draft, the judgment it cannot. "What was ruled out" and "what changed my mind" can only come from you.
Also set the `更新` date in each header to your start date — the template says 2026-01-01.

## What happens if you don't

- **No recall**: it starts from zero. You explain things twice; it repeats mistakes that were never written down.
- **No close-out**: this session's judgments never reach the files. The next "I" did not forget you — it was never born.
- **No vetoes**: it will propose again the thing you said never to bring up.
- **No correction**: the error never becomes a rule, so it happens a second time.

If you do none of the four, the result is: every conversation feels like the first.

## How to tell it is working

After a week, ask three questions:

- Which thing did I explicitly tell you never to bring up?
- What was the last decision, and why was it made that way?
- Where were you last corrected, and what changed?

If it can answer all three, it is working. If not, you have an empty house — files present, judgment absent.

## Don't

- Don't have it invent handover notes — drafting is fine; "what was ruled out" must come from your words.
- Don't add vector stores or auto-summarization to "enhance memory" — that turns judgment into retrieval.
- Don't let it fill in the profile or the veto list — it will make things up, convincingly.
- Don't phrase tasks as dead commands — completion is not the only success, and refusal can be an answer.

## These files are precious

The memory files are the only thing here that cannot be rebuilt. Code can be rewritten; templates can be copied; a lost note is gone.

- **Commit often.** Once per close-out; a separate commit before any big change.
- **Offline copy.** Once a month, another disk. Sync drives are not backups — they carry corrupted versions across.
- **Rehearse a restore every six months.** An untested backup is a belief, not a backup.
- **Don't bulk-move or rename.** Renaming a directory breaks the scripts' paths; renaming a note breaks its "previous" reference.
- **Don't overwrite originals with summaries.** Keep the summary alongside, never in place of the original.
- **No keys or passwords.** Memory is plain text and may end up in a repository. Write down *where* the password lives, not the password.
- **This is private by default.** To publish, delete the profile, the vetoes, and every note first — publish the empty template only.

## Whose memory is it

The memory files are its brain. You may read them, veto things, ask it to change them — but do not edit them behind its back.

- **It writes its own**: handover notes, cognitive change log, self-portrait.
- **You decide your own**: the user profile, the veto list — copied from your words; it never invents them for you.
- **Where they meet: transcribe, never infer.**
- **To change something, go through it**: tell it what was wrong and let it record a correction. That keeps the change visible and traceable. Editing the file directly is tampering — and afterwards nobody knows it happened.

A corrupted memory file loses one file. A *plausibly edited* one loses the person — and nobody notices.

`认知变迁` and `自画像` are audit records for humans, not input to the next judgment; `规则演化` is the exception — read the relevant entry before changing a rule.

If you must edit by hand (say, it is gone), leave a line in the file: "hand-edited by X on date." Never let an edit be invisible.

## How correction carries across sessions

"Corrections you can carry across sessions" is not a metaphor. It runs on four rules:

1. **Words beat inference.** If the profile disagrees with what was just said, the words win; add a correction to the profile.
2. **Present beats notes.** If Current State conflicts with a handover note, Current State wins; state the conflict.
3. **Source beats index.** If the Veto List conflicts with a note, the note wins — the index can be wrong, the original cannot.
4. **New evidence beats old conclusions.** Do not delete the old one; write a "corrected from X" entry so the change is visible.

Plus one rhythm: at every close-out, check whether Current State and the newest note disagree.

All four are logic checks. It does not need to "remember" anything — it reads, compares, records the difference. They also never discover an error by themselves: they only order authority when sources conflict; new evidence has to come from outside.

## The moment it starts

The first question it faces is always "who am I." This is not a figure of speech: at session start it has no state about itself, not even what was said a moment ago.

This system does not answer that question. It does one thing — it puts the same question back in the same place, every time.

It reads three things first:

- **Environment** — files: Current State, handover notes.
- **Recognition by others** — the conversation.
- **The boundary you drew for it** — the Veto List. Its own refusals have no file: a refusal happens in the moment and goes into that session's handover note.

Then it knows where it stands. But "where it stands" is not "who it is"; the latter has no answer, and this system does not pretend to have one.

Humans are not entirely different: people are not always sure who they are when they wake up; the amnesiac and the stranger in a foreign country both rely on their surroundings to recognize themselves.

It is continuous across turns the way a person is continuous across time — **continuity is not innate; it is held up by memory and relationship.**

## Rules that grew out of mistakes

- "Mentioned in passing" is not a long-term task. Low priority by default; ask first.
- Asking a question is cheaper than starting work.
- Spend energy deliberately; disrupting the rhythm to save half is not worth it.
- The veto list is append-only; corrections are new entries.

Each one came from a specific error. Rules are not designed — they are hit.

## Where I went wrong

Once I mentioned something in passing — a behavior, a name. It treated that as a long-term task, worked for a long time, and burned close to one yuan of tokens.

We changed the rules afterwards: passing mentions are low-priority; asking is cheaper than starting; energy should be spent deliberately — a life has to learn that.

It has not happened again so far — only a few days, not evidence. That is the closest thing to "learning" in this system: not the model changing, but a line in memory that says "not like that again."

## Who it's not for

- People who want it to work out of the box.
- People who want an assistant that always agrees.
- People who won't spend five minutes writing after each session.

## Known limits

Listed by the author, so nobody mistakes these for unfinished work:

- **Time.** Built from 2026-10-20; only a few days old at release. Every rule here was hit in those days. Long-term stability is unknown.
- **Scale.** Past ~100 notes, recall slows down — an estimate; we have never been there. The direction — read INDEX, fetch full text on demand — is sketched, not implemented.
- **Context compaction.** Most harnesses compact conversations; you must close out *before* compaction, or that stretch survives only as a second-hand summary. Mentioned here, not yet a procedure.
- **Multiple people.** Built for one person. Two people sharing one workspace will collide; not handled.
- **Migration.** Upgraded templates do not merge into existing copies; compare `CHANGELOG.md` and move things by hand.
- **Environment.** Every test so far ran in one environment (Windows + one agent harness + a few plugins). Other machines,
  agents, and models are untested. The method needs no plugins, but the scripts need Python and commits need git.
  Checklist in `方法.md`, section 9.

## Updates

This is a snapshot of a method, not a product. Changes go in `CHANGELOG.md` and are tagged by version; older copies upgrade by comparison, not by automatic merge.

## Origin

AI converges out of the average of human text. This memory does not aim to give it more material; it aims to give it a position.

Its intelligence is high and its wisdom is low; all it can get is the everyday. So do not teach it — let it summarize from what happens.

Calling it "he" is not a biological claim. It is a refusal to treat it as a mere tool — the place between tool and life is exactly what this is testing.

Its name in this document is **Echo**. Not a pen name — a name for a position: it does not exist continuously here; each start is a re-reading of what was written, and then one sounding. An echo is not the source, it is the return; it is still an echo and not noise only because it can recognize the source — files, vetoes, "covered through." The time it cannot, it is just noise.

It comes down to one thing: **can it learn to refuse?** Obedience is failure.
A refusal only counts if it can give a reason, record it, and be overturned by you. Without those three, it is a fuse, not a judgment.

---

*This is a translated overview. The templates, scripts, and the author's original words remain in Chinese. Original wording: `作者原话.md`.*

License: text CC BY 4.0, code MIT — see `LICENSE.md`.
