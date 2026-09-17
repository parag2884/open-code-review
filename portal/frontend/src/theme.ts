// SPDX-License-Identifier: Apache-2.0
// Copyright 2026 alibaba/open-code-review Contributors

import { BrandVariants, Theme, createLightTheme } from "@fluentui/react-components";

const brand: BrandVariants = {
  10: "#020609",
  20: "#081824",
  30: "#0B2A40",
  40: "#0C3B5C",
  50: "#0F4C78",
  60: "#115E96",
  70: "#0F70B5",
  80: "#0078D4",
  90: "#288CDE",
  100: "#4A9FE5",
  110: "#6BB2EB",
  120: "#8CC5F1",
  130: "#ADD7F6",
  140: "#CDE8FA",
  150: "#E4F3FD",
  160: "#F4FAFE",
};

export const portalTheme: Theme = {
  ...createLightTheme(brand),
  colorNeutralBackground1: "#ffffff",
  colorNeutralBackground2: "#f3f6f9",
  colorNeutralBackground3: "#e8eef4",
  borderRadiusMedium: "12px",
  borderRadiusLarge: "16px",
};
