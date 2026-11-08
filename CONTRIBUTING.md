# Contributing

Thanks for helping. A review rule is only useful if it's right, so every
change is checked by someone who writes X++ every day.

## Ways to help

- **Report a wrong review.** Open an issue with a small made-up example, what
  the review said and what it should have said. Never paste customer code or
  secrets.
- **Improve a rule.** Sharpen what to look for, fix a reason or a code
  example, or correct a severity.
- **Add a rule.** Open an issue first to agree on it, so it fits the list
  and doesn't repeat another rule.
- **Add a sample.** A small diff that breaks one or two rules, or a good
  one that shouldn't trigger any.

## Rule format

Rules live in `skills/xpp-code-review/references/rules.md`, grouped by area.
Each area starts with a `Source:` line linking to Microsoft Learn. Each rule
looks like this:

```markdown
### DAT-05 No select inside a loop

**Severity:** Major

**Look for:** what the reviewer sees in the diff.

**Why it matters:** what goes wrong in production.

**Fix:** what to do instead, with a short code example if it helps.
```

- IDs are the area prefix and a two-digit number. Never reuse or renumber
  an ID; mark an old rule as replaced instead.
- Severity is Blocker, Major, Minor or Question. See
  `references/severity-and-verdict.md`.
- If you add a rule at the end of an area, update the range in the table in
  `SKILL.md` (for example `DAT-01 to DAT-10`). The checks catch it if you
  forget.

## Samples

Samples are in `samples/`, one `.diff` file each, with an entry in
`samples/expected-findings.md` listing the verdict and the rules it must
trigger. Names start with `bad-` or `good-`. Use the made-up model
`ContosoExtensions` and the prefix `CON`.

## Rules for content

- **Your own words.** Don't copy text from Microsoft Learn, blogs, books or
  other review checklists. Link to the source instead.
- **No customer code.** Samples and examples are made up. No customer names,
  environment names, tenant IDs or real secrets, even fake-looking ones from
  a real system.
- **Say when you're not sure.** Leave a comment in the file:
  `<!-- REVIEW: what needs checking -->`.
- **No product promotion.** No links to paid products or services.

## Check your changes

With Python 3 installed:

```bash
python3 tests/check_skills.py
```

This checks the skill frontmatter and sections, the test questions, the rule
format, that every rule ID used anywhere exists, and that every sample has
expected findings. To also check that every link still opens:

```bash
python3 tests/check_skills.py --online
```

The same checks run on every pull request.

## Review

The maintainer reviews every pull request and may run the samples through
the skill. When the rules have been checked, the skill's status changes to
`reviewed` and `checked-against` names the F&O version.
