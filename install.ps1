# MeetionRC modpack installer (Windows PowerShell)
# Called by install.bat. Can also be run directly:
#   powershell -ExecutionPolicy Bypass -File install.ps1
#   powershell -ExecutionPolicy Bypass -File install.ps1 1.21.8
[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$RequestedVersions
)

$ErrorActionPreference = 'Stop'
$ProgressPreference    = 'SilentlyContinue'   # speeds up Invoke-WebRequest a lot

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Config    = Join-Path $ScriptDir 'modpack.json'

if (-not (Test-Path $Config)) {
    Write-Error "modpack.json not found next to install.ps1"
    exit 1
}

$Pack    = Get-Content -Raw $Config | ConvertFrom-Json
$UA      = $Pack.user_agent
$Loader  = $Pack.loader
$AllVers = $Pack.versions

if ($RequestedVersions -and $RequestedVersions.Count -gt 0) {
    $Versions = $RequestedVersions
} else {
    $Versions = $AllVers
}

$Headers = @{ 'User-Agent' = $UA }

function Resolve-Modrinth {
    param(
        [string]$Slug,
        [string]$McVersion,
        [string]$LoaderFilter = 'fabric'   # or 'none'
    )

    $u = "https://api.modrinth.com/v2/project/$Slug/version?game_versions=%5B%22$McVersion%22%5D"
    if ($LoaderFilter -eq 'fabric') {
        $u += '&loaders=%5B%22fabric%22%5D'
    }

    try {
        $resp = Invoke-RestMethod -Uri $u -Headers $Headers -TimeoutSec 30
    } catch {
        return $null
    }

    if (-not $resp -or $resp.Count -eq 0) { return $null }

    # Prefer "release" type, sorted newest first
    $releases = @($resp | Where-Object { $_.version_type -eq 'release' })
    if ($releases.Count -eq 0) { $releases = @($resp) }
    $best = $releases | Sort-Object date_published -Descending | Select-Object -First 1
    if (-not $best) { return $null }

    $primary = $best.files | Where-Object { $_.primary } | Select-Object -First 1
    if (-not $primary) { $primary = $best.files | Select-Object -First 1 }
    if (-not $primary) { return $null }

    return [pscustomobject]@{
        Url      = $primary.url
        Filename = $primary.filename
    }
}

function Download-File {
    param([string]$Url, [string]$OutPath)
    if (Test-Path $OutPath) {
        Write-Host "    SKIP  (already downloaded) $(Split-Path $OutPath -Leaf)"
        return $true
    }
    try {
        $tmp = "$OutPath.part"
        Invoke-WebRequest -Uri $Url -Headers $Headers -OutFile $tmp -TimeoutSec 120
        Move-Item -Force $tmp $OutPath
        return $true
    } catch {
        Write-Host "      ! download failed: $_"
        return $false
    }
}

function Install-Version {
    param([string]$McVersion)

    Write-Host ''
    Write-Host '================================================================'
    Write-Host " Installing for Minecraft $McVersion (loader: $Loader)"
    Write-Host '================================================================'

    $modsDir = Join-Path $ScriptDir "$McVersion\mods"
    $rpDir   = Join-Path $ScriptDir "$McVersion\resourcepacks"
    New-Item -ItemType Directory -Force -Path $modsDir | Out-Null
    New-Item -ItemType Directory -Force -Path $rpDir   | Out-Null

    Write-Host ''
    Write-Host "[$McVersion] Mods:"
    $total = 0; $ok = 0; $skipped = 0
    foreach ($m in $Pack.mods) {
        $total++
        $info = Resolve-Modrinth -Slug $m.slug -McVersion $McVersion -LoaderFilter 'fabric'
        if ($null -eq $info) {
            Write-Host ("  {0,-28} [{1}] -- no compatible version, skipped" -f $m.slug, $m.category)
            $skipped++
            continue
        }
        Write-Host ("  {0,-28} [{1}] -> {2}" -f $m.slug, $m.category, $info.Filename)
        if (Download-File -Url $info.Url -OutPath (Join-Path $modsDir $info.Filename)) {
            $ok++
        }
    }
    Write-Host "  --- mods: $ok installed, $skipped skipped, of $total ---"

    Write-Host ''
    Write-Host "[$McVersion] Resource packs:"
    $rtotal = 0; $rok = 0; $rskipped = 0
    foreach ($p in $Pack.resourcepacks) {
        $rtotal++
        $info = Resolve-Modrinth -Slug $p.slug -McVersion $McVersion -LoaderFilter 'none'
        if ($null -eq $info) {
            Write-Host ("  {0,-32} -- no compatible version, skipped" -f $p.slug)
            $rskipped++
            continue
        }
        Write-Host ("  {0,-32} -> {1}" -f $p.slug, $info.Filename)
        if (Download-File -Url $info.Url -OutPath (Join-Path $rpDir $info.Filename)) {
            $rok++
        }
    }
    Write-Host "  --- resourcepacks: $rok installed, $rskipped skipped, of $rtotal ---"
}

foreach ($v in $Versions) {
    Install-Version -McVersion $v
}

Write-Host ''
Write-Host '================================================================'
Write-Host ' Done.'
Write-Host ' Move the contents of <version>\mods\ into your Minecraft mods folder:'
Write-Host '   Windows:  %APPDATA%\.minecraft\mods'
Write-Host ''
Write-Host ' And <version>\resourcepacks\ into:'
Write-Host '   %APPDATA%\.minecraft\resourcepacks'
Write-Host ''
Write-Host ' Make sure you have Fabric Loader installed for the same MC version'
Write-Host ' (https://fabricmc.net/use/installer/).'
Write-Host '================================================================'
