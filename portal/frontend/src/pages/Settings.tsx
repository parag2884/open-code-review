// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { useEffect, useState } from "react";
import { Body1, Button } from "@fluentui/react-components";
import { api } from "../api";

export function Settings() {
  const [settings, setSettings] = useState<Record<string, unknown> | null>(null);
  const [testOutput, setTestOutput] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .settings()
      .then(setSettings)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  async function onTest() {
    setBusy(true);
    setError("");
    try {
      const result = await api.llmTest();
      setTestOutput((result.ok ? "OK\n" : "FAILED\n") + result.output);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Settings</h1>
          <p>LLM configuration is read from .env. The API key is never shown here.</p>
        </div>
      </div>
      <div className="surface">
        {error ? (
          <Body1 block style={{ color: "#c4314b" }}>
            {error}
          </Body1>
        ) : null}
        {settings ? (
          <dl className="settings-grid">
            {Object.entries(settings).map(([key, value]) => (
              <div key={key} style={{ display: "contents" }}>
                <dt>{key}</dt>
                <dd>{Array.isArray(value) ? value.join(", ") : String(value)}</dd>
              </div>
            ))}
          </dl>
        ) : null}
        <Button appearance="primary" onClick={onTest} disabled={busy}>
          {busy ? "Testing..." : "Test Azure OpenAI"}
        </Button>
        {testOutput ? <pre className="snippet">{testOutput}</pre> : null}
      </div>
    </>
  );
}
