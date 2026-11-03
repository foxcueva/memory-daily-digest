---
name: memory-daily-digest
description: 每日记忆总结与三层记忆维护（热/温/冷）。Use when the user asks for 每日小结/记忆总结/整理 memory/滚动 RECENT/蒸馏流水账/记忆仓库清理, or when running an end-of-day routine that must append a diary entry, roll memory/RECENT.md, archive stale entries, and check pointer consistency.
---

# Memory Daily Digest

把一天的工作收敛进「日记 → 摘要 → 归档」三层，并保证指针不腐烂。

## 安装（三步，零配置）

1. 解压或克隆，得到 `memory-daily-digest/` 目录（里面有 SKILL.md）
2. 整个目录放进工作区的 `skills/` 下：`~/.openclaw/workspace/skills/memory-daily-digest/`
3. 新开一个会话（让 skill 元数据重新加载），之后说「做个每日小结」就会触发

- 也可以 `git clone` 仓库后，把里面的目录直接挖过去；不需要改任何路径
- 安装后验证：确认 `<工作区>/skills/memory-daily-digest/SKILL.md` 存在，再新开一个会话

## 零配置

- 所有路径都是**相对当前工作目录**的：`memory/RECENT.md`、`memory/RECENT-archive.md`、`MEMORY.md`
- 目录不存在时脚本**自动建骨架**，直接跑就行：`python3 scripts/recent_roll.py --dry-run`
- 用户已有自己的记忆目录？加 `--recent <路径> --archive <路径>` 指过去即可
- 不需要 API key、不需要联网、不依赖其他 skill

## 文件约定（可改，改前先问用户路径）

| 层 | 路径 | 规则 |
|---|---|---|
| 日记（冷） | `memory/YYYY-MM-DD.md` | **只增不改**；头部 3 行：`> 一句话 / > 话题 / > 随想` || 摘要（热） | `memory/RECENT.md` | 近 7 天，每日一条，**≤2000 token** |
| 归档（温） | `memory/RECENT-archive.md` | 从 RECENT 外迁的旧条目，顶部维护主题目录 |
| 长期 | `MEMORY.md` | 只放「能改变行为」的结论，细节留指针 |

## 每晚流程（按序执行，别跳步）

1. **查当天日记**：读 `memory/YYYY-MM-DD.md`；不存在就新建，头部写 3 行（一句话/话题/随想要说真话，别写套话）。
2. **补写细节**：把当天发生的事按时间段落写清楚——做了什么、结论是什么、踩了什么坑、留下的待办。宁可细，不要概括。
3. **追加当晚总结段**：在日记末尾加 `## 🌙 全天小结`，3–6 行，讲结果与教训，不讲流水。
4. **滚动 RECENT**：跑 `scripts/recent_roll.py --days 7 --max-tokens 2000`（先 `--dry-run` 看一眼），超过 7 天或超容量的条目自动外迁到 archive。
5. **更新 RECENT 当日条目**：3–6 条要点，每条一行、带文件指针 `Source: memory/YYYY-MM-DD.md`。
6. **指针一致性**：如果今天修改过旧的日记内容，检查 RECENT / archive 里指向它的行，同步更新或标 `⚠stale`。
7. **沉淀判断**：今天有没有产生「以后还会用」的结论？
   - 会 → 改写 `MEMORY.md` 对应段（每条必须能改变行为），或写进 `knowledge/` 条目并在索引登记
   - 不会 → 什么都不做，别为了写而写
8. **报用户**：3–5 行摘要 + 一句话点出今天的教训。不要贴日志原文。

## 月度流程

- `scripts/recent_roll.py --days 30` 先把 RECENT 压到 30 天；再人工把 archive 里同主题合并成一段。
- 扫 `knowledge/00-索引.md`：>90 天无访问的条目标 `休眠`（只改索引，不动原稿）。
- 给用户一份「休眠清单」，由他决定去留——自动化只提议，不裁决。

## 季度流程

- 把 3 个月前的日记压成一篇 `notes/memory-distill-<季度>.md`：
  - 只留**会反复用到**的结论；一次性事件剔除
  - 分主题成章（成本、环境、家人、金融、业务、行为准则…）
  - 单列「反复出现 ≥2 次的问题」与「已废止的旧口径」两节——这两节最值钱
- 原日记不动，蒸馏稿只是索引层。

## 硬纪律

- **原文永不删**：只换读取方式。归档 ≠ 删除，休眠 ≠ 删除。
- **两层删除策略分开**：`memory/` 是历史（只增不改）；`knowledge/`、`data/` 是活文档（可替换，旧值进「沿革」留一行）。
- **普通流水的失效模式**：漏一天总结是良性洞（摘要偏冷一天），不要为它设计补记机制——补记的成本比洞贵。
- **别把摘要塞进常驻注入文件**：`MEMORY.md`、`AGENTS.md` 这类每轮都读的文件，只放结论和指针，详细内容进 `memory/` 或 `knowledge/`。
- **成本**：写文件、跑脚本都是真实开销。能一次写清的不要分三次；能在日记里带过的不要另开文件。

## 参考

- 完整规则与踩坑：`references/rules.md`
- 模板：`assets/RECENT-template.md`、`assets/archive-template.md`、`assets/diary-template.md`
