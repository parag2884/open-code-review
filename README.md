## What is Open Code Review?

Open Code Review is an AI-powered code review CLI tool. This repository is a derivative of the Apache-2.0 Open Code Review project, with an enterprise Fluent portal for Azure OpenAI. Simply configure a model endpoint to get started.

It reads Git diffs, sends changed files to a configurable LLM via an agent with tool-use capabilities, and generates structured review comments with line-level precision. The agent can read full file contents, search the codebase, inspect other changed files for context, and produce deep reviews — not just surface-level diff feedback. Beyond diff review, `ocr scan` reviews entire files for auditing unfamiliar codebases or directories that have no meaningful diff.

## Enterprise portal

Microsoft-style review console wrapping the `ocr` CLI. Paste a Git HTTPS URL or a local folder, run a review with Azure OpenAI, and browse findings.

From the repository root, in PowerShell:

```powershell
.\portal\start.ps1
```

See [portal/README.md](portal/README.md) for API, UI, and configuration details.

## How to Use

### Prerequisites

- **Git >= 2.41** — Open Code Review relies on Git for diff generation, code search, and repository operations.

### CLI

Build from this repository:

```bash
make build
```

The `ocr` binary is written to `dist/`.

**Review**

```bash
cd your-project

# Workspace mode — review all staged, unstaged, and untracked changes
ocr review

# Branch range — reviews feature-branch's changes since it diverged from main (merge-base mode)
ocr review --from main --to feature-branch

# Single commit
ocr review --commit abc123

# Resume an interrupted range or commit review
ocr session list
ocr review --from main --to feature-branch --resume <session-id>

# Full-file scan — review whole files instead of a diff (no git history needed)
ocr scan                          # scan the entire repository
ocr scan --path internal/agent    # scan a directory or specific files
ocr scan --resume <session-id>   # resume an interrupted full-file scan

# Save results to a file (recommended for AI host agents)
ocr review --format json --output result.json

# Delegation mode — let your AI coding agent perform the review itself
# OCR handles file selection and rule resolution; no LLM configuration needed
ocr delegate preview
ocr delegate rule src/main.go src/handler.go
```

## License

[Apache-2.0](LICENSE). See [NOTICE](NOTICE) for original-project attribution.
