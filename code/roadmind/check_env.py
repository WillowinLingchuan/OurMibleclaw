"""
环境自检 —— 装完跑这个，全绿才算配好。

    uv run python check_env.py

对应方案文档 JUDGMENT-DATA.md 第一节「装完验证」：
    文书栈能 import / 语料目录在位 / 路径无单引号

注：输出刻意全用 ASCII —— 本机控制台编码是 gbk，中文在 Git Bash / 管道 /
    复制粘贴时会变乱码，而这份输出经常要被贴进聊天或 issue 里。
"""

import importlib
import os
import sys
from pathlib import Path

OK = "  [ok]  "
BAD = "  [!!]  "
SKIP = "  [--]  "
RULE = "-" * 46

HERE = Path(__file__).resolve().parent


def main() -> int:
    failures = 0
    w = sys.stdout.write

    w(f"\n{RULE}\n  RoadMind env check\n{RULE}\n")

    print("\n[ Python ]")
    print(f"{OK}interpreter   {sys.executable}")
    print(f"{OK}version       {sys.version.split()[0]}")
    if sys.version_info < (3, 12):
        print(f"{BAD}version       needs >= 3.12")
        failures += 1

    print("\n[ core deps  (uv sync --extra core) ]")
    for mod, note in [
        ("numpy", "arrays"),
        ("pandas", "tabular"),
        ("jieba", "chinese tokenizer"),
        ("pypdf", "PDF parsing"),
        ("docx", "DOCX parsing (python-docx)"),
        ("openpyxl", "XLSX parsing"),
        ("rank_bm25", "lexical retrieval"),
    ]:
        try:
            m = importlib.import_module(mod)
            print(f"{OK}{mod:<12} {getattr(m, '__version__', '') or note}")
        except ImportError:
            print(f"{BAD}{mod:<12} NOT INSTALLED - run: uv sync --extra core")
            failures += 1

    print("\n[ optional layers ]")
    for mod, extra in [
        ("langgraph", "agents"),
        ("pydantic", "agents"),
        ("streamlit", "ui"),
    ]:
        try:
            m = importlib.import_module(mod)
            print(f"{OK}{mod:<12} {getattr(m, '__version__', '') or extra}")
        except ImportError:
            print(f"{SKIP}{mod:<12} not installed - uv sync --extra {extra}")

    print("\n[ corpus dirs ]")
    for sub, what in [
        ("raw", "original documents (versioned)"),
        ("split", "three-way split output (versioned)"),
        ("truth", "clause-element ground truth (versioned)"),
        ("cache", "intermediate artifacts (gitignored)"),
    ]:
        d = HERE / "corpus" / sub
        if d.is_dir():
            n = sum(1 for _ in d.iterdir())
            print(f"{OK}corpus/{sub:<6} {n} entries  ({what})")
        else:
            print(f"{SKIP}corpus/{sub:<6} missing - mkdir when you start ({what})")

    print("\n[ path rule  (this machine) ]")
    if "'" in str(HERE):
        print(f"{BAD}project path contains a single quote.")
        print(f"{BAD}keep everything under D:\\GIT\\ , never under C:\\Users\\")
        failures += 1
    else:
        print(f"{OK}path safe     no single quote in {HERE}")

    print(f"\n{RULE}")
    if failures:
        print(f"  {failures} problem(s). See [!!] above.\n")
    else:
        print("  All good. Ready to build the document pipeline.")
        print("  Next: JUDGMENT-DATA.md section 2 (three-way split)")
        print(f"{RULE}\n")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
