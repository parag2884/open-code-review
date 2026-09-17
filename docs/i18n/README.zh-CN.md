## Open Code Review 是什么？

Open Code Review 是一款 AI 驱动的代码审查 CLI 工具。本仓库是该 Apache-2.0 项目的衍生版本，并附带面向 Azure OpenAI 的企业 Fluent 门户。只需配置一个模型端点即可使用。

它读取 Git diff，通过具备工具调用能力的 Agent 将变更文件发送至可配置的 LLM，生成具有行级精度的结构化审查意见。Agent 可以读取完整文件内容、搜索代码库、检查其他变更文件以获取上下文，从而进行深度审查——而非仅停留在表面的 diff 反馈。除了 diff 审查，`ocr scan` 可以审查整个文件，适用于审计不熟悉的代码库或没有有意义 diff 的目录。

## 企业门户

Microsoft 风格的审查控制台，封装 `ocr` CLI。粘贴 Git HTTPS URL 或本地文件夹，使用 Azure OpenAI 运行审查并浏览结果。

在仓库根目录的 PowerShell 中：

```powershell
.\portal\start.ps1
```

API、UI 与配置详见 [portal/README.md](../../portal/README.md)。

## 如何使用

### 前置条件

- **Git >= 2.41** — Open Code Review 依赖 Git 进行 diff 生成、代码搜索和仓库操作。

### CLI

从本仓库构建：

```bash
make build
```

`ocr` 二进制文件输出到 `dist/`。

**开始审查**

```bash
cd your-project

# 工作区模式 —— 审查所有暂存、未暂存和未跟踪的变更
ocr review

# 分支范围 —— 评审 feature-branch 与 main 分叉后的变更（合并基准模式）
ocr review --from main --to feature-branch

# 单个提交
ocr review --commit abc123

# 恢复中断的区间或单 commit 评审
ocr session list
ocr review --from main --to feature-branch --resume <session-id>

# 全量文件扫描 —— 审查整个文件而非 diff（无需 git 历史）
ocr scan                          # 扫描整个仓库
ocr scan --path internal/agent    # 扫描指定目录或文件
ocr scan --resume <session-id>   # 恢复中断的全量文件扫描

# 将结果输出到文件（AI 宿主 agent 推荐）
ocr review --format json --output result.json

# 委托模式 — 让你的 AI 编程 agent 自己执行评审
# OCR 负责文件选择和规则解析；无需配置 LLM
ocr delegate preview
ocr delegate rule src/main.go src/handler.go
```

## 许可证

[Apache-2.0](../../LICENSE)。原始项目归属见 [NOTICE](../../NOTICE)。
