## Open Code Reviewとは？

Open Code ReviewはAIを活用したコードレビューCLIツールです。本リポジトリは Apache-2.0 の Open Code Review プロジェクトの派生版であり、Azure OpenAI 向けのエンタープライズ Fluent ポータルを含みます。モデルのエンドポイントを設定するだけで使い始められます。

Gitのdiffを読み取り、変更されたファイルをツール利用機能を持つエージェント経由で設定可能なLLMに送信し、行レベルの精度で構造化されたレビューコメントを生成します。エージェントはファイル全体の内容を読み取り、コードベースを検索し、コンテキストのために他の変更ファイルを参照し、深いレビューを生成できます — 単なる表面的なdiffへのフィードバックではありません。diffレビュー以外にも、`ocr scan` はファイル全体をレビューできます。不慣れなコードベースの監査や、意味のあるdiffがないディレクトリの検査に便利です。

## エンタープライズポータル

`ocr` CLI をラップする Microsoft スタイルのレビューコンソールです。Git HTTPS URL またはローカルフォルダを指定し、Azure OpenAI でレビューを実行して結果を確認できます。

リポジトリルートで PowerShell から:

```powershell
.\portal\start.ps1
```

API、UI、設定の詳細は [portal/README.md](../../portal/README.md) を参照してください。

## 使い方

### 前提条件

- **Git >= 2.41** — Open Code Review は diff 生成、コード検索、リポジトリ操作に Git を利用します。

### CLI

このリポジトリからビルドします:

```bash
make build
```

`ocr` バイナリは `dist/` に出力されます。

**レビュー**

```bash
cd your-project

# ワークスペースモード — ステージ済み・未ステージ・未追跡のすべての変更をレビュー
ocr review

# ブランチ範囲 — main から分岐した後の feature-branch の変更をレビュー（マージベースモード）
ocr review --from main --to feature-branch

# 単一コミット
ocr review --commit abc123

# 中断した範囲または単一 commit レビューを再開
ocr session list
ocr review --from main --to feature-branch --resume <session-id>

# フルファイルスキャン — diffではなくファイル全体をレビュー（git履歴不要）
ocr scan                          # リポジトリ全体をスキャン
ocr scan --path internal/agent    # ディレクトリまたは特定のファイルをスキャン
ocr scan --resume <session-id>   # 中断したフルファイルスキャンを再開

# 結果をファイルに出力（AI ホストエージェント推奨）
ocr review --format json --output result.json

# デリゲートモード — AI コーディングエージェントが自らレビューを実行
# OCR はファイル選択とルール解決を担当。LLM 設定不要
ocr delegate preview
ocr delegate rule src/main.go src/handler.go
```

## ライセンス

[Apache-2.0](../../LICENSE)。元プロジェクトの帰属は [NOTICE](../../NOTICE) を参照してください。
