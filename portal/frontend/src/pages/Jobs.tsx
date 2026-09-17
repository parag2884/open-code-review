// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Body1 } from "@fluentui/react-components";
import { api, Job } from "../api";
import { StatusPill } from "../components/FindingCard";

export function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .jobs()
      .then(setJobs)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, []);

  const succeeded = jobs.filter((job) => job.status === "succeeded").length;
  const findings = jobs.reduce((sum, job) => sum + (job.comments || 0), 0);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Jobs</h1>
          <p>Every review is recorded with actor, source, and outcome.</p>
        </div>
      </div>
      <div className="metrics">
        <div className="metric">
          <span>Runs</span>
          <strong>{jobs.length}</strong>
        </div>
        <div className="metric">
          <span>Succeeded</span>
          <strong>{succeeded}</strong>
        </div>
        <div className="metric">
          <span>Findings</span>
          <strong>{findings}</strong>
        </div>
      </div>
      <div className="surface">
        {error ? <Body1 style={{ color: "#c4314b" }}>{error}</Body1> : null}
        <table className="jobs-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Source</th>
              <th>Actor</th>
              <th>Findings</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            {jobs.map((job) => (
              <tr key={job.id}>
                <td>
                  <StatusPill status={job.status} />
                </td>
                <td>
                  <Link to={`/jobs/${job.id}`}>{job.source}</Link>
                </td>
                <td>{job.actor}</td>
                <td>{job.comments ?? "—"}</td>
                <td>{job.created_at.replace("T", " ").replace("+00:00", " UTC")}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {jobs.length === 0 ? <Body1>No jobs yet. Start a review from the workspace.</Body1> : null}
      </div>
    </>
  );
}
