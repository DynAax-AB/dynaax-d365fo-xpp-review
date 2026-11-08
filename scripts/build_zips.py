"""Builds one zip per skill in dist/, ready to upload to Claude.

Run from the repository folder:

    python3 scripts/build_zips.py

Each zip holds the skill folder at the top level. test-questions.md is left
out: it is for reviewers, not for the AI assistant.
"""

import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"
LEAVE_OUT = {"test-questions.md"}


def main():
    DIST.mkdir(exist_ok=True)
    for folder in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        target = DIST / f"{folder.name}.zip"
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in sorted(folder.rglob("*")):
                if file.is_file() and file.name not in LEAVE_OUT and not file.name.startswith("."):
                    archive.write(file, file.relative_to(SKILLS))
        print(f"wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
