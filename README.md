# memory-daily-digest

OpenClaw skill：**每日记忆总结与三层记忆维护**。把一天的工作收敛进「日记 → 近 7 天摘要 → 归档」三层，并保证指针不腐烂。

An OpenClaw skill for daily memory distillation and 3-tier memory maintenance (diary → rolling 7-day summary → archive), with pointer consistency checks. Zero config, no API key.

## 它解决什么

长期记忆最容易烂在两处：**RECENT 越滚越长**（每轮都注入，烧 token）、**指针过期**（记了路径但文件已挪走）。这个 skill 每晚跑一遍固定流程：

1. 查/建当天日记 `memory/YYYY-MM-DD.md`，补写细节（只增不改）
2. 末尾追加 `## 🌙 全天小结`（3–6 行，讲结果与教训）
3. 滚动 `memory/RECENT.md`：超过 7 天或超 token 上限的条目自动外迁到 `RECENT-archive.md`
4. 更新 RECENT 当日条目（3–6 条，带 `Source:` 指针）
5. 检查指针一致性，报告失效项

## 安装（三步，零配置）

1. `git clone` 或下载 zip，得到本目录
2. 整个目录放进工作区 `skills/` 下：`~/.openclaw/workspace/skills/memory-daily-digest/`
3. 新开会话让 skill 元数据重新加载；之后说「做个每日小结」即可触发

- 所有路径都相对**当前工作目录**：`memory/RECENT.md`、`memory/RECENT-archive.md`、`MEMORY.md`
- 目录不存在时脚本自动建骨架；已有自己的记忆目录可加 `--recent <路径> --archive <路径>`
- 不需要 API key、不联网、不依赖其他 skill

## 目录

```
SKILL.md              技能说明（触发词、流程、约定）
scripts/recent_roll.py  滚动 RECENT 的实现（先 --dry-run 预览）
references/           流程细节与检查清单
assets/               模板与示例
```

## 快速验证

```bash
python3 scripts/recent_roll.py --dry-run
```

不改任何文件，只打印「哪些条目会被外迁」。

## License

MIT
