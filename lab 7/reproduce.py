"""Replay the original failure and fixed runs. Author: Vishal H."""

import argparse
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=["buggy-demo", "buggy-tests",
                                         "fixed-demo", "fixed-tests"])
    stage = parser.parse_args().stage
    with tempfile.TemporaryDirectory(prefix="lab7-") as directory:
        work = Path(directory)
        original = stage.startswith("buggy")
        source = (ROOT / "evidence" / "original_parking_fee.py"
                  if original else ROOT / "parking_fee.py")
        shutil.copyfile(source, work / "parking_fee.py")
        shutil.copyfile(ROOT / "test_parking_fee.py", work / "test_parking_fee.py")
        shutil.copyfile(ROOT / "pytest.ini", work / "pytest.ini")
        print(f"Lab 7 - {stage} | Vishal H", flush=True)
        if stage.endswith("tests"):
            command = [sys.executable, "-m", "pytest", "test_parking_fee.py"]
            if original:
                command += ["-k", "no_crash", "--tb=short", "-q"]
            else:
                command += ["-q", "--tb=short"]
            print("$ python -m pytest test_parking_fee.py"
                  + (" -k no_crash --tb=short -q" if original else " -q --tb=short"),
                  flush=True)
            result = subprocess.run(command, cwd=work, text=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            output = result.stdout
            status = result.returncode
        else:
            # Keep the original interactive script unmodified. Input is piped
            # to make these demonstration runs repeatable on any platform.
            samples = (["09:30-11:45\ncar\n\n"] if original else
                       ["09:30-11:45\n CAR \nka01ab1234\n",
                        "24:00-25:00\nbus\nA\n"])
            output, status = "", 0
            for sample in samples:
                output += "$ python parking_fee.py\n"
                output += "Piped inputs: " + repr(sample.splitlines()) + "\n"
                result = subprocess.run([sys.executable, "parking_fee.py"],
                                        cwd=work, input=sample, text=True,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT)
                output += result.stdout + f"Exit code: {result.returncode}\n"
                status = max(status, result.returncode)
        print(output, end="", flush=True)
        (ROOT / "evidence" / (stage + ".txt")).write_text(output, encoding="utf-8")
        return status


if __name__ == "__main__":
    sys.exit(main())
