// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { useEffect, useState } from "react";
import { Body1, Dropdown, Option } from "@fluentui/react-components";
import { Finding } from "../api";
import { FindingCard } from "../components/FindingCard";

export function Findings() {
  const [items, setItems] = useState<Finding[]>([]);
  const [severity, setSeverity] = useState<string>("");
  const [error, setError] = useState("");

  useEffect(() => {
    const query = severity ? `/api/findings?severity=${encodeURIComponent(severity)}` : "/api/findings";
    fetch(query)
      .then(async (response) => {
        const raw = await response.text();
        if (!response.ok) throw new Error(raw || response.statusText);
        return JSON.parse(raw);
      })
      .then(setItems)
      .catch((err) => setError(err instanceof Error ? err.message : String(err)));
  }, [severity]);

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Findings</h1>
          <p>Line-accurate comments across every completed review.</p>
        </div>
        <Dropdown
          placeholder="All severities"
          value={severity}
          selectedOptions={severity ? [severity] : []}
          onOptionSelect={(_, data) => setSeverity(data.optionValue || "")}
        >
          <Option value="">All severities</Option>
          <Option value="critical">Critical</Option>
          <Option value="high">High</Option>
          <Option value="medium">Medium</Option>
          <Option value="low">Low</Option>
        </Dropdown>
      </div>
      {error ? <Body1 style={{ color: "#c4314b" }}>{error}</Body1> : null}
      <div className="stack">
        {items.map((finding) => (
          <FindingCard key={finding.id} finding={finding} />
        ))}
        {items.length === 0 ? <div className="surface">No findings yet.</div> : null}
      </div>
    </>
  );
}
