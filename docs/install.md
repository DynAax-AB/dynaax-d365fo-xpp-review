# Install the skill

Pick the tool you use. The skill is the folder `skills/xpp-code-review/`, with a
`SKILL.md` file and a `references/` folder.

<!-- REVIEW: Nurlin to walk through each method once and update the screen names if they've moved. -->

- [Claude on the web or desktop app](#claude-on-the-web-or-desktop-app)
- [Claude Code](#claude-code)
- [Microsoft Copilot Studio](#microsoft-copilot-studio)
- [Other AI assistants](#other-ai-assistants)

---

## Claude on the web or desktop app

Skills work in claude.ai and the Claude desktop app on plans where Skills are
available. Code execution must be switched on in your settings.

1. Download `xpp-code-review.zip` from the repository's **Releases** page. Or
   build it yourself (see [Build the zip file](#build-the-zip-file)).
2. In Claude, open **Settings > Capabilities > Skills** and choose **Upload skill**.
3. Upload the zip. The skill shows in the list and can be switched on or off.
4. Start a new chat, paste a diff (or one of the files in `samples/`) and ask:
   *"Review this X++ change."* Claude picks the skill by itself.

Team and Enterprise admins can also add the skill for everyone in the
organization.

### Build the zip file

The zip must contain the skill folder at the top level
(`xpp-code-review/SKILL.md`).

With Python 3 installed, from the repository folder:

```bash
python3 scripts/build_zips.py
```

The zip is written to `dist/`.

Without Python, on Windows PowerShell:

```powershell
Get-ChildItem skills -Directory | ForEach-Object {
  Compress-Archive -Path $_.FullName -DestinationPath "dist\$($_.Name).zip" -Force
}
```

(Create the `dist` folder first.)

---

## Claude Code

### As a plugin (recommended)

In Claude Code, run:

```text
/plugin marketplace add DynAax-AB/dynaax-d365fo-xpp-review
/plugin install d365fo-xpp-review@d365fo-xpp-review
```

Restart Claude Code if the skill doesn't show straight away.

Then open your F&O repository in Claude Code and ask, for example:
*"Review the changes on this branch against main"* or
*"Review pull request 1234"* (with the GitHub or Azure DevOps CLI signed in).
Claude reads the diff and reviews it; it doesn't change any files unless you
ask it to.

### By copying the folder

Copy the `skills/xpp-code-review` folder to one of these places:

- `~/.claude/skills/` to use it in every project, or
- `.claude/skills/` inside your F&O repository, so the whole team gets it.

On Windows, `~` is your user folder, for example `C:\Users\you\.claude\skills\`.

---

## Microsoft Copilot Studio

Copilot Studio doesn't read skill files as skills, but it can use them as
knowledge. This works well for a code-review agent in Teams that developers
paste changes into.

1. In Copilot Studio, create an agent (or open an existing one).
2. Under **Knowledge**, choose **Add knowledge > Files** and upload:
   - `SKILL.md` (rename it `xpp-code-review.md`), and
   - every file in the `references/` folder.
   If your tenant doesn't accept `.md` files, rename them to `.txt`.
3. Paste the text below into the agent's **Instructions**.
4. Test with the questions in `test-questions.md` and the diffs in `samples/`.

Instructions to paste:

```text
You review X++ code changes for Dynamics 365 Finance and Supply Chain
Management like a senior F&O developer.

Follow the xpp-code-review guide in your knowledge files: check the change
against the rules in the rules file, area by area. For each finding give the
rule ID, where it is, why it matters, the fix and the severity (Blocker,
Major, Minor or Question). List what you can't see in the change, then give
a verdict: Ready to merge, Merge after small fixes, or Needs changes before
merge, using the severity and verdict file.

Never say the code compiles or is safe to deploy. Never repeat secrets you
find in the code. Review only what the change adds or changes.
```

---

## Other AI assistants

Any assistant that accepts custom instructions or uploaded documents can use the
skill the same way as Copilot Studio: upload the `SKILL.md` and `references/`
files as documents, and paste the instructions above.

---

## Updating

When a new version is released, upload the new zip (Claude), pull the plugin
update (Claude Code: `/plugin marketplace update`), or replace the knowledge
files (Copilot Studio).
