param(
  [Parameter(Mandatory = $true)][string]$VideoPath,
  [Parameter(Mandatory = $true)][string]$ScriptPath,
  [Parameter(Mandatory = $true)][string]$OutputDir
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path -LiteralPath $OutputDir -ErrorAction SilentlyContinue)
if (-not $root) {
  New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
  $root = Resolve-Path -LiteralPath $OutputDir
}

$assetDir = Join-Path $root "assets"
$overlayDir = Join-Path $root "overlays"
$previewDir = Join-Path $root "previews"
$outputDir = Join-Path $root "output"
New-Item -ItemType Directory -Force -Path $assetDir, $overlayDir, $previewDir, $outputDir | Out-Null

$sourceVideo = Join-Path $assetDir "source.mp4"
$sourceScript = Join-Path $assetDir "script.md"
Copy-Item -LiteralPath $VideoPath -Destination $sourceVideo -Force
Copy-Item -LiteralPath $ScriptPath -Destination $sourceScript -Force

$metadataPath = Join-Path $assetDir "metadata.json"
$posterPath = Join-Path $assetDir "poster.jpg"

ffprobe -v error -show_format -show_streams -of json $sourceVideo | Set-Content -Encoding UTF8 -LiteralPath $metadataPath
ffmpeg -y -ss 00:00:02 -i $sourceVideo -frames:v 1 $posterPath | Out-Null

Write-Host "Prepared video project: $root"
Write-Host "Source video: $sourceVideo"
Write-Host "Source script: $sourceScript"
