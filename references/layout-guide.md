# 港险口播数据画面指南

## Core Style

- Keep the host visible as the trust anchor. Let data cards occupy the upper half or middle of the frame, not the entire frame for too long.
- Use vertical 9:16 composition first. Standard canvas: 1080 x 1920.
- Use a soft dim layer over the real video only when a table needs readability.
- Default palette:
  - Card: warm off-white `#f8f5ee`
  - Table header: dark gray-green `#435b5d`
  - Body text: deep ink `#172b33`
  - Accent yellow: `#f2cf4a`
  - Risk/callout orange-red: `#e8664c`
  - Row highlight: pale peach `#f3e1d9`
  - Subtitle outline: `#252c2e`

## Subtitles

- Prefer white bold Chinese text with dark gray-green outline and light shadow.
- Do not use a full black subtitle box by default.
- Use ASS style similar to:
  - Font: Microsoft YaHei UI Bold
  - Size: 54-60 on 1080 x 1920
  - Primary: white
  - Outline: dark gray-green / near black
  - Outline width: 3-5
  - Shadow: 1-2
- Avoid splitting numbers, percentages, product names, and short financial labels.

## Data Cards

- Use complete tables when the user's goal is trust and proof. Do not reduce tables to vague big numbers unless the script only needs a quick point.
- Highlight the spoken row or cell with a pale background and a slim orange-red left border.
- Put one short emphasis strip just below the table when useful. This strip may use dark translucent background with white/yellow text.
- Keep emphasis strips separate from normal subtitles.

## Scene Types

Use these as flexible building blocks:

- Bank rate comparison: table or compact cards showing mainland deposits, bonds, whole life savings, and the HK product.
- Yield calculation: two-column process table showing nominal premium, discount, actual payment, surrender value, interest, annualized simple return.
- Premium tier table: amount tier, discount, actual annualized return.
- Exchange-rate scenario: scenario rows for extreme depreciation, unchanged rate, appreciation, plus breakeven rate callout.
- Holding-year strategy: full row table for year 2, 5, 6, 10, 20 with guarantee and projected simple annualized return.
- Company safety: paired cards for premium growth and solvency/dividend/AM Best metrics.
- Asset allocation: simple stacked bar or two-column allocation table; avoid pretending projected return is guaranteed.
- Deadline/CTA: concise bottom card; no exaggerated urgency beyond the script.

## QA Checklist

- No production notes, editor comments, or layout hints are visible.
- Tables are readable on a phone screen.
- Important labels remain on one line when possible.
- Numbers such as `200%`, `5.01%`, `232,500美元`, `39亿港元` are not split awkwardly.
- Data cards do not cover the mouth for long sections.
- Subtitle and emphasis strip do not overlap.
- Colors fit the actual background and clothing, not only the product category.
