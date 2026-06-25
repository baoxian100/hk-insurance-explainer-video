---
name: hk-insurance-explainer-video
description: Package Hong Kong insurance product talking-head videos from a user-provided voiceover video and Chinese full script. Use when the user provides an MP4/MOV口播视频 plus 口播稿_完整版/录制稿 and wants data tables, product explainer visuals, subtitles, HyperFrames/HTML overlays, layout planning, or a finished rough-cut/final vertical video for 港险产品讲解、储蓄险测评、收益拆解、保司安全性、汇率风险、退保点、缴费/折扣/IRR/保证收益说明.
---

# 港险产品讲解视频

## Goal

Turn a filmed talking-head video plus a Chinese full script into a vertical product explainer video with clean subtitles, data cards, tables, and timed visual overlays.

Keep the output flexible: choose the best visual form for the script instead of forcing a fixed template. Use full-screen or upper-screen information cards, table overlays, comparison rows, number callouts, screenshots, flow cards, and lightweight chart motion as needed.

## Workflow

1. Gather source files:
   - Voiceover video: MP4/MOV/MKV.
   - Full script: Markdown/TXT, usually `口播稿_完整版.md`.
   - Optional: recording script, product PDFs, screenshots, reference videos, brand assets.
   - On Windows, read Chinese text with explicit UTF-8.

2. Create a working project:
   - Prefer a new folder beside the source video or under the current workspace.
   - Run `scripts/prepare-video-project.ps1` when useful to copy sources into an ASCII-safe `assets/` folder and create video metadata/poster.
   - Keep generated previews, overlays, subtitles, and final renders in separate output folders.

3. Analyze the script:
   - Break it into spoken beats of 5-15 seconds.
   - Identify claims that need visual support: rate comparisons, guarantee terms, cash values, surrender years, exchange-rate cases, company safety metrics, deadline/CTA.
   - Extract every table-like data set into structured rows before designing the picture.
   - Mark legal/financial caveats without overloading the screen.

4. Design visual scenes:
   - Read `references/layout-guide.md` before designing scenes.
   - For each scene, define: time range, headline, data rows, emphasis line, whether the face should remain visible, and where subtitles sit.
   - Prefer HTML/CSS/HyperFrames-style overlays for editable tables and precise typography.
   - Export transparent PNG overlays when compositing onto the real video.

5. Add subtitles:
   - Default subtitle style: white bold Chinese text, dark gray-green outline, light shadow, no solid black background.
   - Keep black or dark translucent bars only for data emphasis strips, not normal spoken subtitles.
   - Use `scripts/generate-ass-subtitles.js` to create a rough ASS subtitle file from the script when no timed subtitles exist.

6. Render:
   - Use transparent overlays plus ASS subtitles.
   - Use `scripts/render-video.ps1` for ffmpeg composition when overlays are already exported as PNG files.
   - Render a short 15-30 second sample first if the design is still being validated.

7. QA before final delivery:
   - Extract still frames at every data-heavy scene.
   - Check no production notes remain on screen.
   - Check Chinese line breaks do not split numbers, percentages, product names, or short labels.
   - Check subtitles are readable on face, shirt, and bright wall backgrounds.
   - Check data emphasis bars do not cover the mouth for too long.
   - State clearly when timing is rough and what still needs manual fine-tuning.

## Visual Decisions

- Use the real person as the anchor. Do not make the video feel like a generic corporate slide deck unless the user asks for that.
- Keep data cards large enough to read on mobile.
- Put complete tables on screen when the user wants completeness; use row highlights and a short emphasis strip to guide attention.
- Use soft warm white cards, dark gray-green table headers, muted peach highlights, and yellow number emphasis by default. Adapt colors to the actual video background.
- Keep normal subtitles near the lower third. Move them only when a table or emphasis strip needs that space.
- Use subtle motion: fade/slide-in, row highlight, number pop, table scroll only if needed. Avoid excessive animation for financial explainers.

## Reusable Resources

- `references/layout-guide.md`: detailed layout and typography rules for 港险口播数据画面.
- `scripts/prepare-video-project.ps1`: create a reusable project folder from a video and script.
- `scripts/generate-ass-subtitles.js`: create rough ASS subtitles with white text and outline from a Chinese script.
- `scripts/render-video.ps1`: composite transparent PNG overlays and subtitles onto the source video.
- `assets/design-tokens.json`: default colors and typography tokens.

## Example Invocation

Use `$hk-insurance-explainer-video` with:

```text
这是口播视频和口播稿_完整版。请按港险产品讲解视频做一版，表格和数据完整呈现，字幕用白字描边，先给我粗剪效果。
```
