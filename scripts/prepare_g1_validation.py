"""Prepare the Phase 0 G1 manual validation bundle for the original Sourcetrail GUI."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import uuid
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
POC_RUNNER = ROOT / "poc" / "01_jedi_to_sqlite" / "run.py"
ARTIFACT_DIR = ROOT / "poc" / "01_jedi_to_sqlite" / "artifacts"
PROJECT_FILE = ARTIFACT_DIR / "sample-minimal.srctrlprj"
DATABASE_FILE = ARTIFACT_DIR / "sample-minimal.srctrldb"
REPORT_FILE = ARTIFACT_DIR / "report.json"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "sample-minimal"
DEFAULT_SOURCETRAIL_EXE = Path(r"C:\Program Files\Sourcetrail\Sourcetrail.exe")
SOURCE_GROUP_ID = uuid.uuid5(uuid.NAMESPACE_URL, "sourcetrail-remake/sample-minimal")


def make_project_xml() -> str:
    source_path = os.path.relpath(FIXTURE_DIR, ARTIFACT_DIR).replace("\\", "/")
    return (
        '<?xml version="1.0" encoding="utf-8" ?>\n'
        "<config>\n"
        "    <description>Phase 0 G1 manual validation fixture for sample-minimal.</description>\n"
        "    <source_groups>\n"
        f"        <source_group_{SOURCE_GROUP_ID}>\n"
        "            <name>Sample Minimal Source Group</name>\n"
        "            <source_extensions>\n"
        "                <source_extension>.py</source_extension>\n"
        "            </source_extensions>\n"
        "            <source_paths>\n"
        f"                <source_path>{escape(source_path)}</source_path>\n"
        "            </source_paths>\n"
        "            <status>enabled</status>\n"
        "            <type>Python Source Group</type>\n"
        f"        </source_group_{SOURCE_GROUP_ID}>\n"
        "    </source_groups>\n"
        "    <version>8</version>\n"
        "</config>\n"
    )


def regenerate_database() -> None:
    subprocess.run([sys.executable, str(POC_RUNNER)], cwd=ROOT, check=True)


def write_project_file() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    project_xml = make_project_xml()
    if PROJECT_FILE.exists() and PROJECT_FILE.read_text(encoding="utf-8") == project_xml:
        return
    PROJECT_FILE.write_text(project_xml, encoding="utf-8")


def align_project_timestamp() -> None:
    if not PROJECT_FILE.exists() or not DATABASE_FILE.exists():
        return
    target_time = DATABASE_FILE.stat().st_mtime - 1
    os.utime(PROJECT_FILE, (target_time, target_time))


def launch_sourcetrail(sourcetrail_exe: Path) -> None:
    subprocess.Popen(
        [str(sourcetrail_exe), "--project-file", str(PROJECT_FILE)],
        cwd=ARTIFACT_DIR,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare sample-minimal.srctrlprj and optionally launch Sourcetrail."
    )
    parser.add_argument(
        "--sourcetrail-exe",
        type=Path,
        default=DEFAULT_SOURCETRAIL_EXE,
        help="Path to the original Sourcetrail.exe.",
    )
    parser.add_argument(
        "--skip-db-regen",
        action="store_true",
        help="Do not rerun poc/01_jedi_to_sqlite/run.py before preparing the project file.",
    )
    parser.add_argument(
        "--launch",
        action="store_true",
        help="Launch the original Sourcetrail GUI with the generated project file.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    write_project_file()

    if not args.skip_db_regen:
        regenerate_database()

    if not DATABASE_FILE.exists():
        raise SystemExit(
            "Missing sample-minimal.srctrldb. "
            "Run without --skip-db-regen or generate the PoC first."
        )

    align_project_timestamp()

    print(f"project_file={PROJECT_FILE}")
    print(f"database_file={DATABASE_FILE}")
    print(f"report_file={REPORT_FILE}")
    print(f"sourcetrail_exe={args.sourcetrail_exe}")
    print("validation_checks=SessionManager, Session, cleanup_expired, missing_cleanup_handler")

    if args.launch:
        if not args.sourcetrail_exe.exists():
            raise SystemExit(f"Sourcetrail executable not found: {args.sourcetrail_exe}")
        launch_sourcetrail(args.sourcetrail_exe)
        print("launch=started")
    else:
        print(f'launch_command="{args.sourcetrail_exe}" --project-file "{PROJECT_FILE}"')

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
