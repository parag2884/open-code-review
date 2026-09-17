// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

/* Docs content index — imports English markdown files and provides a lookup by slug. */

import type { Language } from '../../i18n/types';

import enQuickstart from './en/quickstart.md';
import enInstallation from './en/installation.md';
import enConfiguration from './en/configuration.md';
import enCliReference from './en/cli-reference.md';
import enReviewRules from './en/review-rules.md';
import enArchitecture from './en/architecture.md';
import enTools from './en/tools.md';
import enMcp from './en/mcp.md';
import enViewer from './en/viewer.md';
import enTelemetry from './en/telemetry.md';
import enAgentSkill from './en/integrations/agent-skill.md';
import enClaudeCode from './en/integrations/claude-code.md';
import enCicd from './en/integrations/ci.md';
import enDelegate from './en/integrations/delegate.md';
import enFaq from './en/faq.md';

export type DocSlug =
  | 'quickstart'
  | 'installation'
  | 'configuration'
  | 'cli-reference'
  | 'review-rules'
  | 'architecture'
  | 'tools'
  | 'mcp'
  | 'viewer'
  | 'telemetry'
  | 'agent-skill'
  | 'claude-code'
  | 'cicd'
  | 'delegate'
  | 'faq';

type LocalizedDocs = Partial<Record<DocSlug, string>>;

const enDocs: Record<DocSlug, string> = {
  'quickstart': enQuickstart,
  'installation': enInstallation,
  'configuration': enConfiguration,
  'cli-reference': enCliReference,
  'review-rules': enReviewRules,
  'architecture': enArchitecture,
  'tools': enTools,
  'mcp': enMcp,
  'viewer': enViewer,
  'telemetry': enTelemetry,
  'agent-skill': enAgentSkill,
  'claude-code': enClaudeCode,
  'cicd': enCicd,
  'delegate': enDelegate,
  'faq': enFaq,
};

const docsMap: Record<Language, LocalizedDocs> = {
  en: enDocs,
};

function stripFrontmatter(md: string): string {
  if (md.startsWith('---')) {
    const end = md.indexOf('---', 3);
    if (end !== -1) {
      return md.slice(end + 3).trim();
    }
  }
  return md;
}

function getRawContent(slug: DocSlug, language: string): string {
  const langDocs = docsMap[language as Language] || docsMap.en;
  return langDocs[slug] ?? enDocs[slug] ?? '';
}

export function getDocContent(slug: DocSlug, language: string): string {
  return stripFrontmatter(getRawContent(slug, language));
}

export function getDocTitle(slug: DocSlug, language: string): string {
  const raw = getRawContent(slug, language);
  if (raw.startsWith('---')) {
    const end = raw.indexOf('---', 3);
    if (end !== -1) {
      const fm = raw.slice(3, end);
      const match = fm.match(/title:\s*(.+)/);
      if (match) return match[1].trim();
    }
  }
  return slug;
}

export function searchDocs(query: string, language: string): { slug: DocSlug; title: string; snippet: string }[] {
  if (!query.trim()) return [];
  const langDocs = docsMap[language as Language] || docsMap.en;
  const results: { slug: DocSlug; title: string; snippet: string }[] = [];
  const lowerQuery = query.toLowerCase();
  const slugs = Object.keys(enDocs) as DocSlug[];
  for (const slug of slugs) {
    const raw = langDocs[slug] ?? enDocs[slug] ?? '';
    const content = stripFrontmatter(raw);
    const lowerContent = content.toLowerCase();
    const idx = lowerContent.indexOf(lowerQuery);
    if (idx !== -1) {
      const start = Math.max(0, idx - 30);
      const end = Math.min(content.length, idx + query.length + 60);
      let snippet = content.slice(start, end).replace(/[#*_`[\]()]/g, '').replace(/\n/g, ' ').trim();
      if (start > 0) snippet = '...' + snippet;
      if (end < content.length) snippet = snippet + '...';
      const title = getDocTitle(slug, language);
      results.push({ slug, title, snippet });
    }
  }
  return results;
}
