# Getting a diff to review

The skill works best with a diff: it shows what was there before and what
changed. Here's how to get one from the usual places. All of these only read.

Before you paste a diff into a chat, check it has no secrets or customer
data in it.

## From a Git repository

Changes on your branch compared with `main`:

```bash
git diff main...HEAD
```

Only the X++ and metadata files:

```bash
git diff main...HEAD -- '*.xml' '*.txt'
```

Save it to a file to upload or paste:

```bash
git diff main...HEAD > my-change.diff
```

In Claude Code you don't need to copy anything. Open the repository and ask:
*"Review the changes on this branch against main."*

## From an Azure DevOps pull request

**In the browser:** open the pull request, go to **Files**, and copy the
changes of the files you want reviewed. For a full diff, use Git (above)
after fetching the pull request's branch.

**With the Azure CLI** (with the `azure-devops` extension):

```bash
az repos pr show --id 1234 --query "{source:sourceRefName, target:targetRefName}"
```

Then fetch both branches and use `git diff target...source`.

## From a GitHub pull request

```bash
gh pr diff 1234
```

Or add `.diff` to the end of the pull request's web address.

## From Visual Studio (Team Foundation Version Control)

<!-- REVIEW: Nurlin to check the TFVC steps on a dev VM. -->

Some F&O teams still use TFVC. In Visual Studio, open **Source Control
Explorer**, right-click the folder or changeset, choose **Compare**, and
copy the result. Or, from a Developer Command Prompt:

```bash
tf diff /recursive /format:unified Metadata\ContosoExtensions > my-change.diff
```

## No diff?

Paste the changed files or the X++ methods. The review still works, but it
can't tell what was already there, so it will say so.
