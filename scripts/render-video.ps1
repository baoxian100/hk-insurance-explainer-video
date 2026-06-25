param(
  [Parameter(Mandatory = $true)][string]$SourceVideo,
  [Parameter(Mandatory = $true)][string]$TimelineJson,
  [Parameter(Mandatory = $true)][string]$OutputVideo,
  [string]$SubtitleAss
)

$ErrorActionPreference = "Stop"

$timeline = Get-Content -Raw -Encoding UTF8 -LiteralPath $TimelineJson | ConvertFrom-Json
if (-not $timeline.scenes) {
  throw "Timeline JSON must contain a scenes array with file, start, and end."
}

$inputs = @("-y", "-i", $SourceVideo)
foreach ($scene in $timeline.scenes) {
  $inputs += @("-loop", "1", "-i", $scene.file)
}

$filters = @()
$current = "[0:v]"
for ($i = 0; $i -lt $timeline.scenes.Count; $i++) {
  $scene = $timeline.scenes[$i]
  $inputIndex = $i + 1
  $next = if ($i -eq $timeline.scenes.Count - 1) { "[vout]" } else { "[v$($i + 1)]" }
  $filters += "[$inputIndex:v]format=rgba[ov$i]"
  $filters += "$current[ov$i]overlay=0:0:enable='between(t,$($scene.start),$($scene.end))'$next"
  $current = $next
}

$mapVideo = "[vout]"
if ($SubtitleAss) {
  $safeAss = $SubtitleAss.Replace("\", "/").Replace(":", "\:")
  $filters += "[vout]subtitles='$safeAss'[vsub]"
  $mapVideo = "[vsub]"
}

$args = @()
$args += $inputs
$args += @(
  "-filter_complex", ($filters -join ";"),
  "-map", $mapVideo,
  "-map", "0:a?",
  "-c:v", "libx264",
  "-crf", "18",
  "-preset", "veryfast",
  "-c:a", "aac",
  "-b:a", "192k",
  "-movflags", "+faststart",
  $OutputVideo
)

ffmpeg @args
Write-Host "Rendered video: $OutputVideo"
