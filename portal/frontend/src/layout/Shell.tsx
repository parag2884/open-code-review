// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { Avatar } from "@fluentui/react-components";
import {
  AddRegular,
  BugRegular,
  DocumentChevronDoubleRegular,
  SettingsRegular,
} from "@fluentui/react-icons";
import { api } from "../api";

export function Shell() {
  const [actor, setActor] = useState("Signing in");

  useEffect(() => {
    api
      .me()
      .then((me) => setActor(me.name))
      .catch(() => setActor("Guest"));
  }, []);

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">
          <div className="brand-mark" aria-hidden="true" />
          <div className="brand-copy">
            <strong>Code Review</strong>
            <span>Enterprise portal</span>
          </div>
        </div>
        <div className="persona">
          <Avatar name={actor} size={28} color="brand" />
          <div className="persona-name">{actor}</div>
        </div>
      </header>
      <div className="workspace">
        <nav className="rail">
          <div className="rail-label">Workspace</div>
          <NavLink to="/" end>
            <AddRegular /> New review
          </NavLink>
          <NavLink to="/jobs">
            <DocumentChevronDoubleRegular /> Jobs
          </NavLink>
          <NavLink to="/findings">
            <BugRegular /> Findings
          </NavLink>
          <NavLink to="/settings">
            <SettingsRegular /> Settings
          </NavLink>
        </nav>
        <main className="canvas">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
