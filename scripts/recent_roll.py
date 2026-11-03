#!/usr/bin/env python3
"""recent_roll.py — 滚动收缩 RECENT.md：超过 N 天的条目外迁到 archive（原文不动）

用法:
  recent_roll.py                          # 默认 memory/RECENT.md + memory/RECENT-archive.md，7 天
  recent_roll.py --days 7 --max-tokens 2000
  recent_roll.py --dry-run                # 只报告，不写文件

规则:
  - RECENT 中形如 "### 2026-10-30（周五）" 的块 = 一条日条目
  - 块头之前的内容（说明/待办之前的正文）保持不动
  - 超过 --days 的条目整块搬到 archive 的 "## 条目" 段末（只增，不改原稿）
  - 若剩余内容估算 token 仍 > --max-tokens，从最老的一天开始继续外迁
  - token 估算：中日韩字符按 1 字 ≈ 0.7 token，其他字符按 4 字符 ≈ 1 token
"""
from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path

DATE_RE = re.compile(r"^###\s+(\d{4}-\d{2}-\d{2})")


def est_tokens(text: str) -> int:
    cjk = sum(1 for ch in text if "\u4e00" <= ch <= "\u9fff" or "\u3040" <= ch <= "\u30ff")
    other = len(text) - cjk
    return int(cjk * 0.7 + other / 4)


def split_entries(text: str):
    """返回 (head, [(date_str, block_text), ...], tail)"""
    lines = text.splitlines(keepends=True)
    idxs = [i for i, ln in enumerate(lines) if DATE_RE.match(ln)]
    if not idxs:
        return text, [], ""
    head = "".join(lines[: idxs[0]])
    entries = []
    for n, start in enumerate(idxs):
        end = idxs[n + 1] if n + 1 < len(idxs) else len(lines)
        block = "".join(lines[start:end])
        # 尾部若含有 "## " 段（如待办），截出来留给 tail
        entries.append((DATE_RE.match(lines[start]).group(1), block))
    # 处理最后一个块里可能夹带的 "## " 段
    tail = ""
    if entries:
        last_date, last_block = entries[-1]
        m = re.search(r"^## ", last_block, flags=re.M)
        if m:
            tail = last_block[m.start():]
            entries[-1] = (last_date, last_block[: m.start()])
    return head, entries, tail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--recent", default="memory/RECENT.md")
    ap.add_argument("--archive", default="memory/RECENT-archive.md")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--max-tokens", type=int, default=2000)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    recent_p = Path(args.recent)
    archive_p = Path(args.archive)
    if not recent_p.exists():
        # 零配置：没有记忆目录就建一个空架子，不报错
        recent_p.parent.mkdir(parents=True, exist_ok=True)
        recent_p.write_text(
            "# RECENT.md — 近 7 天要事摘要（热层）\n\n"
            "> 硬上限：≤2000 token；超了按「最旧优先」外迁到 RECENT-archive.md\n\n"
            "## 📌 近 7 天要事\n",
            encoding="utf-8",
        )
        print(f"→ 已创建骨架文件 {recent_p}")

    text = recent_p.read_text(encoding="utf-8")
    head, entries, tail = split_entries(text)
    if not entries:
        print("✓ RECENT 里没有日条目，无需滚动")
        return 0

    today = dt.date.today()
    cutoff = today - dt.timedelta(days=args.days)
    keep, drop = [], []
    for date_str, block in entries:
        try:
            d = dt.date.fromisoformat(date_str)
        except ValueError:
            keep.append((date_str, block))
            continue
        (drop if d < cutoff else keep).append((date_str, block))

    def rebuild(k):
        return head + "".join(b for _, b in k) + tail

    # 容量触发：仍超限则继续从最老的开始外迁（7 天内的也迁）
    while keep and est_tokens(rebuild(keep)) > args.max_tokens:
        keep_sorted = sorted(keep, key=lambda x: x[0])
        drop.append(keep_sorted[0])
        keep = [e for e in keep if e is not keep_sorted[0]]

    if not drop:
        print(f"✓ 无需外迁（{len(keep)} 条，估算 {est_tokens(rebuild(keep))} token）")
        return 0

    print(f"外迁 {len(drop)} 条：" + "、".join(d for d, _ in drop))
    print(f"保留 {len(keep)} 条，估算 {est_tokens(rebuild(keep))} token（上限 {args.max_tokens}）")

    if args.dry_run:
        print("（dry-run，未写文件）")
        return 0

    recent_p.write_text(rebuild(keep), encoding="utf-8")

    archive_p.parent.mkdir(parents=True, exist_ok=True)
    arch = archive_p.read_text(encoding="utf-8") if archive_p.exists() else "# RECENT-archive.md\n\n## 条目\n"
    add = []
    for date_str, block in drop:
        body = block.strip()
        body = re.sub(r"^###\s+", f"### {date_str} ← 归档 ", body, count=1)
        add.append(body + "\n")
    if "## 条目" in arch:
        arch = arch.rstrip() + "\n\n" + "\n".join(add)
    else:
        arch = arch.rstrip() + "\n\n## 条目\n\n" + "\n".join(add)
    archive_p.write_text(arch, encoding="utf-8")
    print(f"✓ 已写入 {recent_p} 与 {archive_p}（原文 memory/YYYY-MM-DD.md 未动）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
