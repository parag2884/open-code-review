// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { Body1, Button } from "@fluentui/react-components";
import { api, Finding, Job } from "../api";
import { FindingCard, StatusPill } from "../components/FindingCard";

export function JobDetail() {
  const { id } = useParams();
  const [job, setJob] = useState<Job | null>(null);
  const [findings, setFindings] = useState<Finding[]>([]);
  const [logs, setLogs] = useState<string[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;
    let source: EventSource | null = null;
    api
      .job(id)
      .then((payload) => {
        setJob(payload.job);
        setFindings(payload.findings);
        setLogs((payload.logs || []).map((item) => item.line));
      })
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));

    source = new EventSource(`/api/jobs/${id}/events`);
    source.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "log") {
        setLogs((current) => [...current, data.line]);
      }
      if (data.type === "complete") {
        setJob(data.job);
        api.job(id).then((payload) => setFindings(payload.findings));
        source?.close();
      }
    };
    source.onerror = () => source?.close();
    return () => source?.close();
  }, [id]);

  if (!id) return null;

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Review {id.slice(0, 8)}</h1>
          {job ? (
            <p>
              <StatusPill status={job.status} /> {job.mode} · {job.source} · {job.actor}
              {job.elapsed ? ` · ${job.elapsed}` : ""}
              {job.comments != null ? ` · ${job.comments} finding(s)` : ""}
            </p>
          ) : (
            <p>Loading run details...</p>
          )}
        </div>
      </div>
      {error ? <Body1 style={{ color: "#c4314b" }}>{error}</Body1> : null}
      {job?.error ? <Body1 style={{ color: "#c4314b" }}>{job.error}</Body1> : null}
      <div className="toolbar">
        <Button appearance="primary" onClick={() => window.open(`/api/jobs/${id}/json`, "_blank")}>
          Download JSON
        </Button>
        <Button onClick={() => window.open(`/api/jobs/${id}/sarif`, "_blank")}>Download SARIF</Button>
      </div>
      <div className="log-pane">{logs.join("\n") || "Waiting for progress..."}</div>
      <div className="stack" style={{ marginTop: 18 }}>
        {findings.map((finding) => (
          <FindingCard key={finding.id} finding={finding} />
        ))}
      </div>
    </>
  );
}
