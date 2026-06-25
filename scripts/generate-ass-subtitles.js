const fs = require("fs");
const path = require("path");

function usage() {
  console.error("Usage: node generate-ass-subtitles.js <script.md> <durationSeconds> <output.ass>");
  process.exit(1);
}

const [, , scriptPath, durationArg, outputPath] = process.argv;
if (!scriptPath || !durationArg || !outputPath) usage();

const duration = Number(durationArg);
if (!Number.isFinite(duration) || duration <= 0) usage();

function extractSpokenText(text) {
  const lines = text.replace(/\r/g, "").split("\n");
  const blocks = [];
  let capture = false;
  let current = [];

  function flush() {
    const value = current.join("\n").trim();
    if (value) blocks.push(value);
    current = [];
  }

  for (const line of lines) {
    if (/〔\s*口播\s*〕/.test(line)) {
      flush();
      capture = true;
      const rest = line.replace(/.*〔\s*口播\s*〕\s*/, "").trim();
      if (rest) current.push(rest);
      continue;
    }
    if (/〔\s*画面\s*〕/.test(line) || /^#{1,6}\s*/.test(line) || /^-{3,}\s*$/.test(line)) {
      flush();
      capture = false;
      continue;
    }
    if (capture) current.push(line);
  }
  flush();
  return blocks.length ? blocks.join("\n\n") : text;
}

function cleanMarkdown(text) {
  return text
    .replace(/\r/g, "")
    .split("\n")
    .filter((line) => {
      const trimmed = line.trim();
      if (!trimmed) return true;
      if (trimmed.startsWith("|")) return false;
      if (trimmed.startsWith(">")) return false;
      if (/^:?-{2,}:?(\s*\|\s*:?-{2,}:?)+$/.test(trimmed)) return false;
      return true;
    })
    .join("\n")
    .replace(/\r/g, "")
    .replace(/```[\s\S]*?```/g, "")
    .replace(/^#{1,6}\s*/gm, "")
    .replace(/^\s*[-*+]\s+/gm, "")
    .replace(/\*\*|__/g, "")
    .replace(/\[[^\]]+\]\([^)]+\)/g, (m) => m.match(/\[([^\]]+)\]/)?.[1] || "")
    .replace(/[ \t]+/g, " ")
    .trim();
}

function splitSentences(text) {
  const parts = text
    .split(/(?<=[。！？!?；;])\s*/g)
    .map((s) => s.trim())
    .filter(Boolean);
  return parts.length ? parts : [text];
}

function tokenize(text) {
  return text.match(/[A-Za-z0-9,.%]+|[\u4e00-\u9fff]|[^\s]/g) || [];
}

function splitLongText(text, max = 30) {
  const out = [];
  let current = "";
  for (const token of tokenize(text)) {
    if ((current + token).length > max && current) {
      out.push(current);
      current = token;
    } else {
      current += token;
    }
  }
  if (current) out.push(current);
  return out;
}

function wrapLine(text, max = 18) {
  const lines = [];
  let current = "";
  for (const token of tokenize(text)) {
    if ((current + token).length > max && current) {
      lines.push(current);
      current = token;
    } else {
      current += token;
    }
  }
  if (current) lines.push(current);
  return lines.slice(0, 2).join("\\N");
}

function assTime(seconds) {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  const cs = Math.floor((seconds - Math.floor(seconds)) * 100);
  return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(cs).padStart(2, "0")}`;
}

const raw = fs.readFileSync(scriptPath, "utf8");
const sentences = splitSentences(cleanMarkdown(extractSpokenText(raw))).flatMap((s) => splitLongText(s));
const totalChars = sentences.reduce((sum, s) => sum + Math.max(1, s.length), 0);
let cursor = 0;

const events = sentences.map((text, index) => {
  const weight = Math.max(1, text.length);
  const span = Math.max(1.2, (duration * weight) / totalChars);
  const start = cursor;
  const end = index === sentences.length - 1 ? duration : Math.min(duration, cursor + span);
  cursor = end;
  return `Dialogue: 0,${assTime(start)},${assTime(end)},Default,,0,0,0,,${wrapLine(text)}`;
});

const ass = `[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Microsoft YaHei UI,56,&H00FFFFFF,&H000000FF,&H00252C2E,&H00000000,-1,0,0,0,100,100,0,0,1,4,1,2,70,70,440,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
${events.join("\n")}
`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, ass, "utf8");
console.log(`Generated ${events.length} subtitle events: ${outputPath}`);
