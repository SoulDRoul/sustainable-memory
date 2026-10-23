# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""收尾包：把“收尾”里能机器判的部分一次做完。

默认只读；加 --apply 才写，而且只写三处：否决清单的“覆盖至”、它的“更新”日期，和一次提交。
提交只含四样：新笔记、否决清单、当前状态、INDEX——工作区里别的文件不动。
交接笔记本身、当前状态、INDEX 星号，都还是模型写。

用法：
    python close_out.py
    python close_out.py --apply 2026-10-22-主题.txt -m "提交说明"
    python close_out.py --apply 2026-10-22-主题.txt -m "..." --dry-run
"""

import datetime
import io
import os
import re
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HPC = os.path.join(ROOT, "10-情景-海马")
VETO = os.path.join(ROOT, "00-语义-皮层", "否决清单.txt")


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def sh(*args):
    tmp = os.path.join(tempfile.gettempdir(), "dsh_git_out.txt")
    try:
        with io.open(tmp, "w", encoding="utf-8") as f:
            p = subprocess.run(["git", "-C", ROOT] + list(args), stdout=f, stderr=subprocess.STDOUT)
    except OSError:
        return "<git 未安装>"
    with io.open(tmp, encoding="utf-8", errors="replace") as f:
        text = f.read().rstrip()
    if p.returncode != 0:
        return "<git 失败 rc=%d> %s" % (p.returncode, text[:200])
    return text


def is_own_repo():
    """这个目录自己是不是 git 仓库的根（避免被外层仓库接管时误报）。"""
    top = sh("rev-parse", "--show-toplevel")
    if top.startswith("<git") or not top:
        return False
    return os.path.normcase(os.path.abspath(top)) == os.path.normcase(os.path.abspath(ROOT))


def notes():
    return sorted(f for f in os.listdir(HPC) if f.endswith(".txt") and f != "INDEX.txt")


def header(path, n=3):
    with io.open(path, encoding="utf-8") as f:
        return "".join(next(f, "") for _ in range(n))


def prev_of(name):
    m = re.search(r"\[上一份[:：]\s*([^\]\s]+)\s*\]", header(os.path.join(HPC, name)))
    ref = m.group(1) if m else None
    return None if ref in (None, "无", "none", "-") else ref


def tail_excluding(exclude=None):
    all_notes = [n for n in notes() if n != exclude]
    refs = set(p for p in (prev_of(n) for n in all_notes) if p)
    tails = [n for n in all_notes if n not in refs]
    return tails


def coverage():
    m = re.search(r"\[覆盖至[:：]\s*([^\]\s]+)\s*\]", header(VETO))
    return m.group(1) if m else ""


def section(no, title, body):
    print("")
    print("=" * 74)
    print("[%s] %s" % (no, title))
    print("=" * 74)
    print(body.rstrip("\n"))


def layout_ok():
    need = ["当前状态.txt",
            os.path.join("00-语义-皮层", "否决清单.txt"),
            os.path.join("10-情景-海马", "INDEX.txt")]
    missing = [p for p in need if not os.path.isfile(os.path.join(ROOT, p))]
    if missing:
        print("缺 %s。" % "、".join(missing))
        print("先把 模板/ 整个复制到工作区根目录，再跑（见 README 的“怎么开始”）。")
        return False
    return True


def plan(note_name=None):
    today = datetime.date.today().isoformat()
    tails = tail_excluding(note_name)
    print("收尾包 · %s" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("只读：默认不写、不提交。--apply 才动。")

    cov = coverage() or "（未写）"
    if len(tails) > 1:
        body = [
            "今天     : %s" % today,
            "链尾     : 并列 %d 份，需人工取舍" % len(tails),
            "           " + "、".join(tails),
            "覆盖至   : %s" % cov,
        ]
    elif tails:
        body = [
            "今天     : %s" % today,
            "链尾     : %s" % tails[0],
            "新笔记的“上一份”应写上面这份",
            "覆盖至   : %s" % cov,
        ]
    else:
        body = [
            "今天     : %s" % today,
            "链尾     : （还没有笔记）",
            "这是第一条：页眉写 [上一份: 无]，收尾时可以把覆盖至写成它",
            "覆盖至   : %s" % cov,
        ]
    section("0", "该写什么", "\n".join(body))

    section("1", "当前状态.txt", read(os.path.join(ROOT, "当前状态.txt")))
    section("2", "INDEX.txt", read(os.path.join(HPC, "INDEX.txt")))

    veto = read(VETO)
    section("3", "否决清单.txt", veto)

    if is_own_repo():
        git_info = "\n".join(
            [
                "未提交 : %s" % (sh("status", "--porcelain") or "（干净）"),
                "相对上次提交的改动 :",
                sh("diff", "--stat", "HEAD") or "（无）",
                "最近三条 :",
                sh("log", "-3", "--format=%h %s"),
            ]
        )
    else:
        git_info = "（没有 git 或未初始化：不提交也能用，但收尾前要手动备份；见方法第九节）"
    section("4", "git", git_info)


def apply(note, message, dry):
    if not is_own_repo():
        top = sh("rev-parse", "--show-toplevel")
        if top.startswith("<git 未安装"):
            print("没找到 git：--apply 靠它提交。可以手动改“覆盖至”，并自己备份。")
        else:
            print("这个目录不是独立 git 仓库，拒绝 --apply；先在工作区根目录 git init。")
        return 2
    path = os.path.join(HPC, note)
    if not os.path.isfile(path):
        print("找不到笔记：%s" % path)
        return 2

    tails = tail_excluding(note)
    if len(tails) > 1:
        print("链尾并列 %d 份：%s" % (len(tails), "、".join(tails)))
        print("先修链（或只留一条），再收尾；脚本不按日期替你挑。")
        return 2
    if tails:
        expect_prev = tails[0]
        if prev_of(note) != expect_prev:
            print("笔记页眉的上一份是 %r，应为 %r —— 先改页眉。" % (prev_of(note), expect_prev))
            return 2
    else:
        if prev_of(note) is not None:
            print("找不到链尾，而这份笔记的上一份写着 %r —— 先核对链。" % prev_of(note))
            return 2
        print("这是第一条笔记，允许把覆盖至写成它。")

    cov = coverage()
    if cov == note:
        print("覆盖至已经是这份，不重复写。")
        return 0

    text = read(VETO)
    new = re.sub(r"\[覆盖至[:：][^\]]*\]", "[覆盖至: %s]" % note, text, count=1)
    new = re.sub(r"\[更新[:：]\s*[^\]]*\]", "[更新: %s]" % datetime.date.today().isoformat(), new, count=1)
    if dry:
        print("[dry-run] 覆盖至 %s → %s" % (cov, note))
        print("[dry-run] 不写文件、不提交。")
        return 0

    write(VETO, new)
    print("覆盖至：%s → %s" % (cov, note))
    # 只提交记忆文件：工作区里别的东西不动，避免把无关文件（或密钥）带进历史。
    for rel in (os.path.join("10-情景-海马", note), os.path.relpath(VETO, ROOT),
                "当前状态.txt", os.path.join("10-情景-海马", "INDEX.txt")):
        sh("add", "--", rel.replace(os.sep, "/"))
    print("提交范围：笔记 + 否决清单 + 当前状态 + INDEX（别的文件不动）")
    out = sh("commit", "-m", message)
    print(out)
    print("")
    print("退回方式：git revert --no-edit HEAD（保留历史），或 git reset --hard HEAD~1（丢弃这次提交）。")
    return 0


def main():
    argv = sys.argv[1:]
    dry = "--dry-run" in argv
    if not layout_ok():
        return 2
    if "--apply" in argv:
        i = argv.index("--apply")
        if i + 1 >= len(argv):
            print("用法：--apply 笔记文件名 -m 提交说明")
            return 2
        note = argv[i + 1]
        msg = ""
        if "-m" in argv:
            j = argv.index("-m")
            msg = " ".join(argv[j + 1:])
        if not msg:
            print("缺 -m 提交说明。")
            return 2
        return apply(note, msg, dry)
    plan()
    print("")
    print("接下来（模型做）：写交接笔记 → 改当前状态 → 判 INDEX 星号 → 再 --apply。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
