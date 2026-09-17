// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button, Dropdown, Field, Input, Option, Switch, Body1 } from "@fluentui/react-components";
import { api, ReviewRequest } from "../api";

export function NewReview() {
  const navigate = useNavigate();
  const [sourceType, setSourceType] = useState<"git" | "local">("git");
  const [source, setSource] = useState("https://github.com/parag2884/VERA");
  const [branch, setBranch] = useState("");
  const [fromRef, setFromRef] = useState("");
  const [toRef, setToRef] = useState("HEAD");
  const [pythonOnly, setPythonOnly] = useState(true);
  const [effort, setEffort] = useState<"low" | "medium" | "high">("low");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  function onSource(value: "git" | "local") {
    setSourceType(value);
    setSource(value === "local" ? defaultLocalPath() : "https://github.com/parag2884/VERA");
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const payload: ReviewRequest = {
      source_type: sourceType,
      source,
      python_only: pythonOnly,
      effort,
    };
    if (branch.trim()) payload.branch = branch.trim();
    if (fromRef.trim()) payload.from_ref = fromRef.trim();
    if (toRef.trim()) payload.to_ref = toRef.trim();
    try {
      const job = await api.createReview(payload);
      navigate(`/jobs/${job.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <section className="page-hero">
        <h1>Review with precision</h1>
        <p>
          Point this portal at a Git repository or a local folder. Open Code Review handles file
          selection and line-accurate comments; Azure OpenAI supplies the judgment.
        </p>
      </section>
      <div className="surface">
        <div className="source-grid">
          <button type="button" className={`source-card ${sourceType === "git" ? "active" : ""}`} onClick={() => onSource("git")}>
            <strong>Git repository</strong>
            <span>HTTPS URL on GitHub, GitLab, Azure Repos, or Bitbucket</span>
          </button>
          <button type="button" className={`source-card ${sourceType === "local" ? "active" : ""}`} onClick={() => onSource("local")}>
            <strong>Local folder</strong>
            <span>A directory on this workstation, no clone required</span>
          </button>
        </div>
        <form onSubmit={onSubmit} className="form-grid">
          <Field label={sourceType === "git" ? "Git HTTPS URL" : "Local folder path"} required>
            <Input size="large" value={source} onChange={(_, d) => setSource(d.value)} />
          </Field>
          {sourceType === "git" ? (
            <Field label="Branch (optional)">
              <Input value={branch} onChange={(_, d) => setBranch(d.value)} placeholder="main" />
            </Field>
          ) : null}
          <Field label="Diff base — leave empty to scan the whole tree">
            <Input value={fromRef} onChange={(_, d) => setFromRef(d.value)} placeholder="main" />
          </Field>
          <Field label="Diff target">
            <Input value={toRef} onChange={(_, d) => setToRef(d.value)} />
          </Field>
          <Field label="Effort">
            <Dropdown
              value={effort}
              selectedOptions={[effort]}
              onOptionSelect={(_, data) => setEffort((data.optionValue as typeof effort) || "low")}
            >
              <Option value="low">Low — faster, fewer rounds</Option>
              <Option value="medium">Medium</Option>
              <Option value="high">High — deeper recall</Option>
            </Dropdown>
          </Field>
          <Switch checked={pythonOnly} onChange={(_, d) => setPythonOnly(d.checked)} label="Python only" />
          {error ? <Body1 style={{ color: "#c4314b" }}>{error}</Body1> : null}
          <Button appearance="primary" size="large" type="submit" disabled={busy}>
            {busy ? "Starting review..." : "Start review"}
          </Button>
        </form>
      </div>
    </>
  );
}

function defaultLocalPath() {
  return "C:\\Parag-Personal\\Open-Code-Review\\portal\\fixtures\\sample-python";
}
