import argparse
import json
import math
import re
from bisect import bisect_left, bisect_right
from difflib import SequenceMatcher
from pathlib import Path


DEFAULT_PROTECTED_TERMS = [
    "友邦财富盈活",
    "财富盈活",
    "环宇盈活",
    "永明星河尊享二",
    "3331未来心愿安排",
    "未来心愿安排",
    "复归红利",
    "终期分红",
    "终期红利",
    "分红实现率",
    "保证现金价值",
    "预期现金价值",
    "预期IRR",
    "保证IRR",
    "第20年",
    "第27年",
    "第30年",
    "7月31号",
    "7月31日",
    "4.3%",
    "4.0%",
    "3.8%",
    "6.50%",
    "5.83%",
    "332.5万",
    "2746.4万",
    "107年历史",
    "港险市场",
    "各家保司",
    "拼命迭代",
    "传承功能",
    "友邦实力",
    "长期收益",
    "取钱表现",
    "缴费方式",
    "五年交",
    "趸交",
    "0岁宝宝",
    "总保费",
    "预缴保费",
    "保证利率",
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate ASS subtitles aligned to real speech timing while preserving the provided Chinese script."
    )
    parser.add_argument("--video", required=True, help="Source talking-head video.")
    parser.add_argument("--script", required=True, help="Full script, usually 口播稿_完整版.md.")
    parser.add_argument("--output", required=True, help="Output ASS subtitle file.")
    parser.add_argument("--cache-json", help="Optional ASR JSON cache path.")
    parser.add_argument("--model", default="small", help="faster-whisper model name or local model path.")
    parser.add_argument("--duration", type=float, help="Video duration in seconds. Probed by ASR when omitted.")
    parser.add_argument("--prompt", default="", help="Initial prompt with product names and financial terms.")
    parser.add_argument("--font-size", type=int, default=58)
    parser.add_argument("--margin-v", type=int, default=315)
    parser.add_argument("--max-chars", type=int, default=24)
    return parser.parse_args()


def normalize_text(text):
    return re.sub(r"\s+", "", text)


def normalize_for_match(text):
    chars = []
    mapping = []
    for index, ch in enumerate(text):
        if re.match(r"[\u4e00-\u9fffA-Za-z0-9]", ch):
            chars.append(ch.lower())
            mapping.append(index)
    return "".join(chars), mapping


def extract_spoken_text(script_path):
    text = Path(script_path).read_text(encoding="utf-8").replace("\r", "")
    lines = text.split("\n")
    blocks = []
    capture = False
    current = []

    def flush():
        nonlocal current
        value = "".join(x.strip() for x in current if x.strip())
        if value:
            blocks.append(value)
        current = []

    for line in lines:
        if re.search(r"〔\s*口播\s*〕", line):
            flush()
            capture = True
            continue
        if re.search(r"〔\s*画面\s*〕", line) or re.match(r"^#{1,6}\s*", line) or re.match(r"^-{3,}\s*$", line):
            flush()
            capture = False
            continue
        if capture:
            stripped = line.strip()
            if not stripped or stripped.startswith("|") or stripped.startswith("高亮"):
                continue
            current.append(stripped)
    flush()
    return "".join(blocks) if blocks else text


def sentence_spans(script_text):
    spans = []
    start = 0
    for index, ch in enumerate(script_text):
        if ch in "。！？!?；;":
            end = index + 1
            value = script_text[start:end].strip()
            if value:
                spans.append((start, end, value))
            start = end
    if start < len(script_text):
        value = script_text[start:].strip()
        if value:
            spans.append((start, len(script_text), value))
    return spans


def tokenize(text, protected_terms):
    protected = "|".join(re.escape(x) for x in sorted(protected_terms, key=len, reverse=True))
    pattern = rf"{protected}|[A-Za-z0-9,.%+~·/%（）()\"：:-]+|[\u4e00-\u9fff]|[^\s]"
    return re.findall(pattern, text)


def split_long_text(text, protected_terms, max_len=24):
    rough_parts = []
    current_part = ""
    for token in re.split(r"([，、。！？；,.!?;])", text):
        if not token:
            continue
        trial = current_part + token
        if current_part and len(normalize_text(trial)) > max_len and token not in "，、。！？；,.!?;":
            rough_parts.append(current_part)
            current_part = token
        else:
            current_part = trial
            if token in "。！？；!?;":
                rough_parts.append(current_part)
                current_part = ""
    if current_part:
        rough_parts.append(current_part)

    chunks = []
    for part in rough_parts:
        if len(normalize_text(part)) <= max_len:
            chunks.append(part)
            continue
        current = ""
        for token in tokenize(part, protected_terms):
            if current and len(normalize_text(current + token)) > max_len:
                chunks.append(current)
                current = token
            else:
                current += token
        if current:
            chunks.append(current)

    for index in range(len(chunks) - 1):
        if len(normalize_text(chunks[index + 1])) <= 2:
            chunks[index] += chunks[index + 1]
            chunks[index + 1] = ""
    return [c for c in chunks if normalize_text(c)]


def transcribe(video_path, model_name, prompt, cache_json):
    if cache_json and Path(cache_json).exists():
        return json.loads(Path(cache_json).read_text(encoding="utf-8"))

    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise SystemExit(
            "Missing dependency: faster-whisper. Install it in the active Python environment, "
            "or fall back to generate-ass-subtitles.js for rough subtitles."
        ) from exc

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        str(video_path),
        language="zh",
        task="transcribe",
        initial_prompt=prompt,
        beam_size=5,
        vad_filter=True,
        vad_parameters={"min_silence_duration_ms": 350},
        word_timestamps=True,
    )
    data = {"language": info.language, "duration": info.duration, "segments": []}
    for seg in segments:
        data["segments"].append({"start": float(seg.start), "end": float(seg.end), "text": seg.text.strip()})
    if cache_json:
        Path(cache_json).parent.mkdir(parents=True, exist_ok=True)
        Path(cache_json).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def map_asr_to_script_positions(asr_norm, script_norm):
    matcher = SequenceMatcher(None, asr_norm, script_norm, autojunk=False)
    pairs = []
    for a_start, b_start, size in matcher.get_matching_blocks():
        for offset in range(size):
            pairs.append((a_start + offset, b_start + offset))
    pairs.sort()
    compact = []
    last_a = -1
    for a_pos, b_pos in pairs:
        if a_pos != last_a:
            compact.append((a_pos, b_pos))
            last_a = a_pos
    return compact


def estimate_asr_pos(anchor_pairs, script_pos, asr_len):
    if not anchor_pairs:
        return int(script_pos)
    inverse = sorted((b, a) for a, b in anchor_pairs)
    b_values = [p[0] for p in inverse]
    idx = bisect_left(b_values, script_pos)
    if idx < len(inverse) and inverse[idx][0] == script_pos:
        return inverse[idx][1]
    prev_pair = inverse[idx - 1] if idx > 0 else None
    next_pair = inverse[idx] if idx < len(inverse) else None
    if prev_pair and next_pair and next_pair[0] != prev_pair[0]:
        ratio = (script_pos - prev_pair[0]) / (next_pair[0] - prev_pair[0])
        return int(round(prev_pair[1] + ratio * (next_pair[1] - prev_pair[1])))
    if prev_pair:
        return min(asr_len, prev_pair[1] + max(0, script_pos - prev_pair[0]))
    if next_pair:
        return max(0, next_pair[1] - max(0, next_pair[0] - script_pos))
    return min(asr_len, int(script_pos))


def norm_index_for_original(script_norm_map, original_pos, side="left"):
    if side == "right":
        return bisect_right(script_norm_map, original_pos)
    return bisect_left(script_norm_map, original_pos)


def build_time_lookup(asr_ranges, asr_segments):
    starts = [r[0] for r in asr_ranges]

    def asr_pos_to_time(asr_pos):
        idx = bisect_right(starts, asr_pos) - 1
        idx = max(0, min(idx, len(asr_ranges) - 1))
        a0, a1 = asr_ranges[idx]
        seg = asr_segments[idx]
        if a1 <= a0:
            return seg["start"]
        ratio = max(0.0, min(1.0, (asr_pos - a0) / (a1 - a0)))
        return seg["start"] + ratio * (seg["end"] - seg["start"])

    return asr_pos_to_time


def build_events(script_text, asr_data, duration, protected_terms, max_chars):
    script_norm, script_norm_map = normalize_for_match(script_text)
    asr_segments = [s for s in asr_data["segments"] if s["end"] > s["start"] and normalize_text(s["text"])]
    if not asr_segments:
        raise SystemExit("ASR returned no usable speech segments.")

    asr_norm_parts = []
    asr_ranges = []
    cursor = 0
    for seg in asr_segments:
        norm, _ = normalize_for_match(seg["text"])
        asr_ranges.append((cursor, cursor + len(norm)))
        asr_norm_parts.append(norm)
        cursor += len(norm)
    asr_norm = "".join(asr_norm_parts)
    anchor_pairs = map_asr_to_script_positions(asr_norm, script_norm)
    asr_pos_to_time = build_time_lookup(asr_ranges, asr_segments)

    events = []
    last_end = 0.0
    for original_start, original_end, sentence in sentence_spans(script_text):
        norm_start = norm_index_for_original(script_norm_map, original_start, "left")
        norm_end = norm_index_for_original(script_norm_map, original_end - 1, "right")
        if norm_end <= norm_start:
            continue
        asr_start = estimate_asr_pos(anchor_pairs, norm_start, len(asr_norm))
        asr_end = estimate_asr_pos(anchor_pairs, norm_end, len(asr_norm))
        start_time = max(last_end + 0.02, asr_pos_to_time(asr_start))
        end_time = min(duration - 0.1, max(start_time + 0.85, asr_pos_to_time(asr_end)))

        chunks = split_long_text(sentence, protected_terms, max_chars)
        total = sum(max(1, len(normalize_text(c))) for c in chunks)
        span = end_time - start_time
        cursor_time = start_time
        for chunk_index, chunk in enumerate(chunks):
            weight = max(1, len(normalize_text(chunk)))
            chunk_span = max(0.72, span * weight / total)
            start = cursor_time
            end = end_time if chunk_index == len(chunks) - 1 else min(end_time, cursor_time + chunk_span)
            if end > start:
                events.append({"start": start, "end": end, "text": chunk})
            cursor_time = end + 0.03
        if events:
            last_end = events[-1]["end"]
    return events


def ass_time(seconds):
    seconds = max(0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - math.floor(seconds)) * 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def ass_wrap(text, protected_terms, max_len=17):
    lines = []
    current = ""
    for token in tokenize(text, protected_terms):
        if current and len(normalize_text(current + token)) > max_len:
            lines.append(current)
            current = token
        else:
            current += token
    if current:
        lines.append(current)
    return "\\N".join(lines[:2])


def write_ass(events, output_path, font_size, margin_v, protected_terms):
    lines = [
        "[Script Info]",
        "ScriptType: v4.00+",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "ScaledBorderAndShadow: yes",
        "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        f"Style: Default,Microsoft YaHei UI,{font_size},&H00FFFFFF,&H000000FF,&H00252C2E,&H00000000,-1,0,0,0,100,100,0,0,1,4,1,2,70,70,{margin_v},1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
    ]
    for event in events:
        lines.append(
            f"Dialogue: 0,{ass_time(event['start'])},{ass_time(event['end'])},Default,,0,0,0,,{ass_wrap(event['text'], protected_terms)}"
        )
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    args = parse_args()
    protected_terms = DEFAULT_PROTECTED_TERMS[:]
    prompt = args.prompt or " ".join(protected_terms[:30])
    asr_data = transcribe(args.video, args.model, prompt, args.cache_json)
    duration = args.duration or float(asr_data.get("duration") or 0)
    if not duration:
        raise SystemExit("Duration is required when ASR metadata does not include duration.")
    script_text = extract_spoken_text(args.script)
    events = build_events(script_text, asr_data, duration, protected_terms, args.max_chars)
    write_ass(events, args.output, args.font_size, args.margin_v, protected_terms)
    print(f"Generated {len(events)} speech-aligned subtitle events: {args.output}")
    if args.cache_json:
        print(f"ASR cache: {args.cache_json}")


if __name__ == "__main__":
    main()
