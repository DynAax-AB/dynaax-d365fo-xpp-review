# Severity and verdict

> **Draft: Nurlin to review.**

## Severity

Each rule in `rules.md` has a usual severity. Raise or lower it when the
case calls for it, and say why in the finding.

| Severity | Label | Meaning | Examples |
|---|---|---|---|
| Blocker | 🔴 | Breaks data, security or upgrades, or fails at run time. Must be fixed before merge. | Overlayering, `next` not called, unbalanced transaction, dialog inside a transaction, a secret in code |
| Major | 🟠 | Will cause a performance, support or upgrade problem. Should be fixed before merge. | Row-by-row updates, select in a loop, hard-coded text, a menu item without a privilege |
| Minor | 🟡 | Naming, style or readability. Fix now or in a follow-up. | Missing prefix on a new class, `firstonly` missing, extension class naming |
| Question | 🔵 | You can't tell from the change. Ask the author. | Is the privilege in another commit? Is this table large? |

When to change the usual severity:

- **Raise** when the code runs on large tables, in posting, in batch for all
  companies, or in an integration that many users depend on.
- **Lower** when the code is clearly a one-off (an upgrade or data script
  that runs once), or the table is small and stays small. Say so.
- A Major that you're not sure applies becomes a **Question**. Don't guess.

<!-- REVIEW: check these severities match how you'd rate them in a real review. -->

## Verdict

| Verdict | When |
|---|---|
| **Needs changes before merge** | Any Blocker, or two or more Majors |
| **Merge after small fixes** | One Major, or only Minors |
| **Ready to merge** | No findings, or only Questions that don't change the code |

<!-- REVIEW: is "two or more Majors" the right line for "Needs changes"? -->

Always give a one-sentence reason with the verdict, naming the finding that
decided it.

The verdict is about the code in front of you. It doesn't replace the build,
the Best Practice check, testing in a sandbox or the lead developer's
approval. Say so if the user treats it as a sign-off.
