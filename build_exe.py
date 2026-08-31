from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
NAME = "sv.autoclick"
VERSION = "1.1.0"
DIST = os.path.join(ROOT, "release")
WORK = os.path.join(ROOT, "build")

EXCLUDES = ("matplotlib", "scipy", "pandas", "IPython", "notebook", "pytest",
            "PySide6", "PyQt5", "torch")


def build(clean: bool) -> int:
    args = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",
        "--name", NAME,
        "--icon", os.path.join(ROOT, "logo.ico"),
        "--distpath", DIST,
        "--workpath", WORK,
        "--specpath", WORK,
        "--add-data", f"{os.path.join(ROOT, 'logo.ico')}{os.pathsep}.",
        "--collect-all", "customtkinter",
    ]
    if clean:
        args.append("--clean")
    for module in EXCLUDES:
        args += ["--exclude-module", module]
    args.append(os.path.join(ROOT, "main.py"))

    print(f"Собираю {NAME} {VERSION}")
    print("Занимает пару минут: PyInstaller упаковывает OpenCV.\n")

    started = time.time()
    result = subprocess.run(args, cwd=ROOT)
    if result.returncode != 0:
        print("\nСборка не удалась.")
        return result.returncode

    exe = os.path.join(DIST, NAME + ".exe")
    print(f"\nГотово за {time.time() - started:.0f} с")
    print(f"Результат: {exe}")
    print(f"Размер: {os.path.getsize(exe) / 1024 / 1024:.0f} МБ")
    return 0


def main():
    p = argparse.ArgumentParser(description="Сборка sv.autoclick в exe")
    p.add_argument("--clean", action="store_true",
                   help="очистить кеш PyInstaller перед сборкой")
    args = p.parse_args()

    os.makedirs(DIST, exist_ok=True)
    return build(args.clean)


if __name__ == "__main__":
    sys.exit(main())
