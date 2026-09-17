## Open Code Review란?

Open Code Review는 AI 기반 코드 리뷰 CLI 도구입니다. 이 저장소는 Apache-2.0 Open Code Review 프로젝트의 파생본이며, Azure OpenAI용 엔터프라이즈 Fluent 포털을 포함합니다. 모델 endpoint만 설정하면 바로 사용할 수 있습니다.

이 도구는 Git diff를 읽고, 변경 파일을 tool-use 기능을 가진 agent를 통해 설정 가능한 LLM으로 전달한 뒤, 라인 단위 위치 정보가 포함된 구조화된 리뷰 코멘트를 생성합니다. agent는 전체 파일 내용 읽기, 코드베이스 검색, 다른 변경 파일 확인 등을 통해 맥락을 확보하고 표면적인 diff 피드백이 아닌 깊이 있는 리뷰를 수행할 수 있습니다. diff 리뷰 외에도 `ocr scan`은 전체 파일을 리뷰할 수 있어, 익숙하지 않은 코드베이스를 감사하거나 의미 있는 diff가 없는 디렉터리를 검토하는 데 유용합니다.

## 엔터프라이즈 포털

`ocr` CLI를 감싼 Microsoft 스타일 리뷰 콘솔입니다. Git HTTPS URL 또는 로컬 폴더를 넣고 Azure OpenAI로 리뷰를 실행한 뒤 결과를 확인합니다.

저장소 루트에서 PowerShell:

```powershell
.\portal\start.ps1
```

API, UI, 설정은 [portal/README.md](../../portal/README.md)를 참고하세요.

## 사용 방법

### 사전 요구 사항

- **Git >= 2.41** — Open Code Review는 diff 생성, 코드 검색, 저장소 작업에 Git을 사용합니다.

### CLI

이 저장소에서 빌드합니다:

```bash
make build
```

`ocr` 바이너리는 `dist/`에 생성됩니다.

**리뷰 실행**

```bash
cd your-project

# Workspace mode: staged, unstaged, untracked 변경을 모두 리뷰
ocr review

# 브랜치 범위 — main에서 분기된 이후 feature-branch의 변경 사항을 리뷰합니다 (머지베이스 모드)
ocr review --from main --to feature-branch

# 단일 commit
ocr review --commit abc123

# 중단된 range 또는 단일 commit review 재개
ocr session list
ocr review --from main --to feature-branch --resume <session-id>

# 전체 파일 스캔 — diff 대신 파일 전체를 리뷰 (git 이력 불필요)
ocr scan                          # 전체 repository 스캔
ocr scan --path internal/agent    # 디렉터리 또는 특정 파일 스캔
ocr scan --resume <session-id>   # 중단된 전체 파일 스캔 재개

# 결과를 파일로 저장 (AI 호스트 에이전트 권장)
ocr review --format json --output result.json

# 위임 모드 — AI 코딩 에이전트가 직접 리뷰 수행
# OCR은 파일 선택과 규칙 해석만 담당; LLM 설정 불필요
ocr delegate preview
ocr delegate rule src/main.go src/handler.go
```
