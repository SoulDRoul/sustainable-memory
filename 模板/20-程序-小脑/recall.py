# -*- coding: utf-8 -*-
# SPDX-License-Identifier: MIT
"""回忆包：把“回忆”里的机械件一次打印出来。

只读。不写文件、不联网、不改 git。
用法：python recall.py [--root 工作区路径]

收缩条件（2026-10-22 定，现在不实现）：笔记过 100 份，或一次打出的
材料超过 120K，就改成“先给 INDEX + 每条一行摘要，再按需读全文”。
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


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return f.read()


def head_lines(path, n=3):
    with io.open(path, encoding="utf-8") as f:
        return [next(f, "") for _ in range(n)]


def section(no, title, body):
    print("")
    print("=" * 74)
    print("[%s] %s" % (no, title))
    print("=" * 74)
    print(body.rstrip("\n"))


def parse_root(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for i, a in enumerate(argv):
        if a == "--root" and i + 1 < len(argv):
            root = argv[i + 1]
    return root


def chain(root):
    """返回 (链尾候选列表, 上一份映射, 断链列表, 缺页眉列表)。"""
    d = os.path.join(root, "10-情景-海马")
    notes = sorted(f for f in os.listdir(d) if f.endswith(".txt") and f != "INDEX.txt")
    prev = {}
    nohdr = []
    for n in notes:
        text = "".join(head_lines(os.path.join(d, n)))
        m = re.search(r"\[上一份[:：]\s*([^\]\s]+)\s*\]", text)
        if not m:
            nohdr.append(n)
        ref = m.group(1) if m else None
        if ref in ("无", "none", "None", "-"):
            ref = None
        prev[n] = ref
    referenced = set(v for v in prev.values() if v and v in notes)
    broken = sorted(set(v for v in prev.values() if v and v not in notes))
    tails = [n for n in notes if n not in referenced]
    return tails, prev, broken, nohdr


def covered_chain(prev, cov, notes):
    """从“覆盖至”那份沿“上一份”往回走，走到的都算已覆盖。"""
    seen = []
    cur = cov
    while cur and cur in notes and cur not in seen:
        seen.append(cur)
        cur = prev.get(cur)
    return set(seen)


def coverage(root):
    p = os.path.join(root, "00-语义-皮层", "否决清单.txt")
    text = "".join(head_lines(p))
    m = re.search(r"\[覆盖至[:：]\s*([^\]\s]+)\s*\]", text)
    return m.group(1) if m else ""


def _git_run(root, *args):
    """用临时文件收输出，不用管道（Windows 沙箱禁子进程管道）。"""
    tmp = os.path.join(tempfile.gettempdir(), "dsh_git_out.txt")
    try:
        with io.open(tmp, "w", encoding="utf-8") as f:
            p = subprocess.run(
                ["git", "-C", root] + list(args),
                stdout=f,
                stderr=subprocess.STDOUT,
            )
    except OSError:
        return "<git 未安装>"
    with io.open(tmp, encoding="utf-8", errors="replace") as f:
        text = f.read().strip()
    if p.returncode != 0:
        return "<git 失败 rc=%d> %s" % (p.returncode, text[:200])
    return text


def messages(root):
    """留言只报条数，不报内容——它的规矩是“写了不必读”。"""
    p = os.path.join(root, "留言.txt")
    if not os.path.isfile(p):
        return "（没有 留言.txt）"
    n = 0
    with io.open(p, encoding="utf-8") as f:
        for line in f:
            if re.match(r"^\d{4}-\d{2}-\d{2}", line.strip()):
                n += 1
    return "留言：%d 条（未读；想翻再翻，内容不在这里打）" % n


def git(root):
    top = _git_run(root, "rev-parse", "--show-toplevel").strip()
    if top.startswith("<git 未安装"):
        return "（没找到 git：不提交也能用，但收尾前要手动备份）"
    if top.startswith("<git 失败") or not top:
        return "（未初始化 git：在工作区根目录执行 git init）"
    if os.path.normcase(os.path.abspath(top)) != os.path.normcase(os.path.abspath(root)):
        return "（这层目录不是独立仓库，被外层仓库 %s 接管；在工作区根目录 git init 后可用）" % top
    return "\n".join(
        [
            "HEAD   : %s" % _git_run(root, "log", "-1", "--format=%h %s"),
            "分支   : %s" % _git_run(root, "rev-parse", "--abbrev-ref", "HEAD"),
            "未提交 : %s" % (_git_run(root, "status", "--porcelain") or "（干净）"),
        ]
    )


def env_report(root):
    """环境自检：三项。缺了就降级，不是报错。"""
    py = sys.version.split()[0]
    gv = _git_run(root, "--version")
    if gv.startswith("<"):
        git_line = "未安装（脚本照跑，但不能提交；收尾前手动备份）"
    else:
        git_line = gv.replace("git version ", "").strip()
    d = os.path.join(root, "10-情景-海马")
    nn = len([f for f in os.listdir(d) if f.endswith(".txt") and f != "INDEX.txt"])
    return "\n".join([
        "Python : %s%s" % (py, "" if sys.version_info >= (3, 5) else "（需要 3.5 以上）"),
        "git    : %s" % git_line,
        "笔记   : %d 份" % nn,
        "说明   : 缺 git 不影响写，只影响提交与退回（方法 第九节）。",
    ])


def main():
    root = parse_root(sys.argv)
    now = datetime.datetime.now()
    print("回忆包 · %s · %s" % (now.strftime("%Y-%m-%d %H:%M"), root))
    print("只读：不写文件、不联网、不改 git。")

    for rel in ("当前状态.txt", os.path.join("00-语义-皮层", "否决清单.txt"),
                os.path.join("10-情景-海马", "INDEX.txt")):
        if not os.path.isfile(os.path.join(root, rel)):
            print("")
            print("缺 %s。" % rel)
            print("先把 模板/ 整个复制到工作区根目录，再跑（见 README 的“怎么开始”）。")
            return 2

    section("0", "环境", env_report(root))
    section("1", "当前状态.txt", read(os.path.join(root, "当前状态.txt")))
    section("2", "否决清单.txt", read(os.path.join(root, "00-语义-皮层", "否决清单.txt")))

    tails, prev, broken, nohdr = chain(root)
    cov = coverage(root)
    if len(tails) == 1:
        body = ["链尾（判据：没被任何笔记写成“上一份”）", "  %s" % tails[0], ""]
        body.append("上一份链（%d 份笔记）" % len(prev))
        for n in sorted(prev):
            body.append("  %s  ← %s" % (n, prev[n] or "无"))
        section("3a", "链尾", "\n".join(body))
        section("3b", "链尾正文 · %s" % tails[0], read(os.path.join(root, "10-情景-海马", tails[0])))
    elif tails:
        body = ["链尾并列 %d 份，需人工取舍：" % len(tails)]
        body += ["  %s" % t for t in tails]
        body += ["", "脚本不按日期替你挑。先定一份（或修链），再读正文。", ""]
        body.append("上一份链（%d 份笔记）" % len(prev))
        for n in sorted(prev):
            body.append("  %s  ← %s" % (n, prev[n] or "无"))
        section("3a", "链尾", "\n".join(body))
    else:
        section("3a", "链尾", "还没有笔记——先写第一条，页眉写 [上一份: 无]。")

    if broken:
        section("3c", "断链", "引用了不存在或改名后的笔记：\n  " + "\n  ".join(broken))

    if nohdr:
        section("3e", "缺页眉", "这些笔记没有 [上一份] 行，按链根算：\n  " + "\n  ".join(nohdr))

    d = os.path.join(root, "10-情景-海马")
    notes = sorted(f for f in os.listdir(d) if f.endswith(".txt") and f != "INDEX.txt")
    covset = covered_chain(prev, cov, notes)
    newer = [n for n in notes if n not in covset]
    body = ["覆盖至 : %s" % (cov or "（未写）")]
    if not notes:
        body.append("（还没有笔记，无所谓覆盖）")
    elif newer:
        body.append("不在覆盖链上的 %d 份（判断件：是否算新、是否要读）：" % len(newer))
        body += ["  %s" % n for n in newer]
    else:
        body.append("覆盖链已包含全部笔记。")
    section("3d", "覆盖检查", "\n".join(body))

    section("4", "INDEX.txt", read(os.path.join(d, "INDEX.txt")))
    section("5", "用户画像.txt", read(os.path.join(root, "00-语义-皮层", "用户画像.txt")))
    section("6", "git", git(root))
    section("7", "留言", messages(root))

    print("")
    print("完。判断件仍留给模型：同名取舍、覆盖之后的真新假新、要不要回读原文。")


if __name__ == "__main__":
    sys.exit(main())
