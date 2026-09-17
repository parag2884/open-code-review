// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { Badge, Body1 } from "@fluentui/react-components";
import { Finding } from "../api";

export function FindingCard({ finding }: { finding: Finding }) {
  const severity = (finding.severity || "info").toLowerCase();
  return (
    <article className="finding-card">
      <div className={`finding-accent ${severity}`} />
      <div className="finding-body">
        <div className="finding-meta">
          <Badge appearance="tint" color={severityColor(severity)}>
            {severity} · {finding.category || "review"}
          </Badge>
          <span className="finding-path">
            {finding.path}:{finding.start_line}-{finding.end_line}
          </span>
        </div>
        <Body1 block>{finding.content}</Body1>
        {finding.existing_code ? <pre className="snippet">{finding.existing_code}</pre> : null}
        {finding.suggestion_code ? <pre className="snippet">{finding.suggestion_code}</pre> : null}
      </div>
    </article>
  );
}

export function StatusPill({ status }: { status: string }) {
  return <span className={`status-pill status-${status}`}>{status}</span>;
}

function severityColor(severity: string): "danger" | "warning" | "informative" | "success" {
  if (severity === "critical" || severity === "high") return "danger";
  if (severity === "medium") return "warning";
  if (severity === "low") return "informative";
  return "success";
}
