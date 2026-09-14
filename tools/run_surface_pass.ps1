<#
.SYNOPSIS
  Drive the Dragonslayer / Nether surface pass: one qwen3.8-flash session per piece, sequentially.

.DESCRIPTION
  Each piece gets its OWN session and its own Blockbench window, because both halves of a
  session's bridge derive identity from the parent process (see the qwen-launcher notes) and
  two sessions in one window race on the active tab.

  Per piece: find a free window by IDENTITY (GET /hello says app:blockbench + the bridge
  plugin - an open port proves nothing, 25599 is the Minecraft client), pin BOTH
  MCPTK_BLOCKBENCH and ARMORPIECES_BB_URL to it, share one MCPTK_SESSION so the two halves
  bind the same project, run, then archive the transcript.

  Every model slot is pinned to qwen3.8-flash so nothing can quietly escalate to a max model.

.EXAMPLE
  pwsh tools/run_surface_pass.ps1 -Pieces magma_cops,wither_ribs
  pwsh tools/run_surface_pass.ps1 -All
#>
[CmdletBinding()]
param(
    [string[]]$Pieces,
    [switch]$All,
    [string]$Model = 'qwen3.8-flash',
    # Take an EMPTY window even though its claim looks live. The claim-age guard exists to stop
    # two authoring sessions landing in one window, but an idle INTERACTIVE session (the one
    # driving this batch) refreshes its own claim forever and so locks out every window it has
    # ever touched. Pass this only when you know the fresh claim is the driver's own and the
    # driver will not touch Blockbench while the batch runs.
    [switch]$AllowClaimed,
    [int]$TimeoutSec = 900
)

$ErrorActionPreference = 'Stop'
$repo = 'C:\Users\Matthijs\ArmorPieces'
$briefDir = Join-Path $repo 'docs\plans\briefs'
$logDir = Join-Path $repo '.mcptoolkit\runs\surface'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null

if ($All) {
    $Pieces = Get-ChildItem "$briefDir\*_surface.md" | ForEach-Object {
        $_.BaseName -replace '_surface$', ''
    }
}
if (-not $Pieces) { Write-Error 'Give -Pieces or -All.' }

# --- credentials and model pinning -------------------------------------------------------
$cfg = Join-Path $HOME '.claude-qwen'
if (-not (Test-Path (Join-Path $cfg 'settings.json'))) { Write-Error "No $cfg" }
$env:CLAUDE_CONFIG_DIR = $cfg
$env:ANTHROPIC_AUTH_TOKEN = (Import-Clixml (Join-Path $cfg 'credential.xml')).GetNetworkCredential().Password
foreach ($slot in 'ANTHROPIC_MODEL', 'ANTHROPIC_DEFAULT_OPUS_MODEL',
    'ANTHROPIC_DEFAULT_SONNET_MODEL', 'ANTHROPIC_DEFAULT_HAIKU_MODEL',
    'CLAUDE_CODE_SUBAGENT_MODEL') { Set-Item "env:$slot" $Model }
$env:CLAUDE_CODE_MAX_CONTEXT_TOKENS = '983616'
Remove-Item env:ANTHROPIC_API_KEY -ErrorAction SilentlyContinue

$claude = (Get-Command claude -CommandType Application | Select-Object -First 1).Source

function Get-DockWindow {
    param([string]$SessionId)
    # THE DOCK IS THE FRONT DOOR (plugin 0.10.0, toolkit 0.147.0). Since plugin 0.7.0 a window is the
    # person's unless it was opened FOR an agent, so the scan below can no longer just take an empty
    # one: 25803 is the dock and 25804 the person's window, both of which refuse a claim. The dock
    # reuses an empty agent window before making another and answers with the PORT, and asking it
    # under the SAME session id every time is a rejoin, so one batch holds one window throughout
    # instead of piling up a new one per piece while the last one's claim goes stale.
    foreach ($port in 25801..25816) {
        try { $r = Invoke-RestMethod "http://127.0.0.1:$port/hello" -TimeoutSec 1 -ErrorAction Stop }
        catch { continue }
        if ($r.app -ne 'blockbench' -or $r.plugin -ne 'mcptoolkit_bridge' -or $r.role -ne 'dock') { continue }
        $body = @{ session = @{ id = $SessionId; client = 'armorpieces'; profile = 'kit' } } | ConvertTo-Json -Compress
        try {
            $a = Invoke-RestMethod "http://127.0.0.1:$port/dock/window" -Method Post -ContentType 'application/json' `
                -Body $body -TimeoutSec 40 -ErrorAction Stop
        } catch { Write-Host "  dock on $port did not answer: $_" -ForegroundColor Yellow; return $null }
        if ($a.ok -and $a.port) {
            $how = if ($a.made) { 'made' } elseif ($a.rejoined) { 'rejoined' } else { 'reused' }
            Write-Host "  dock on $port gave window $($a.window) port $($a.port) ($how)" -ForegroundColor DarkGray
            return [int]$a.port
        }
        Write-Host "  dock on $port refused: $($a.error) $($a.hint)" -ForegroundColor Yellow
        return $null
    }
    return $null
}

function Get-AskedWindow {
    param([string]$SessionId)
    # NO DOCK OPEN (2026-09-13: the dock is a window a person opens from the menu, and there was
    # none). `POST /window` on any bridge window is the same front door the shim itself uses: it
    # rejoins a window this session already holds, else hands over an empty agent window that no
    # live session holds, else opens a new one pre-claimed for this session (up to the plugin's
    # agent-window ceiling). Asked under ONE session id for the whole batch, every later ask is a
    # rejoin, so one window serves the batch the way the dock would have.
    $asker = $null
    foreach ($port in 25801..25816) {
        try { $r = Invoke-RestMethod "http://127.0.0.1:$port/hello" -TimeoutSec 1 -ErrorAction Stop }
        catch { continue }
        if ($r.app -eq 'blockbench' -and $r.plugin -eq 'mcptoolkit_bridge') { $asker = $port; break }
    }
    if (-not $asker) { return $null }
    $body = @{ session = @{ id = $SessionId; client = 'armorpieces'; profile = 'kit' } } | ConvertTo-Json -Compress
    try {
        $a = Invoke-RestMethod "http://127.0.0.1:$asker/window" -Method Post -ContentType 'application/json' `
            -Body $body -TimeoutSec 40 -ErrorAction Stop
    } catch { Write-Host "  /window on $asker did not answer: $_" -ForegroundColor Yellow; return $null }
    # Only a REUSED answer names another window's port. An `opened` answer carries the asking
    # window's own block (its `port` is the asker's - 2026-09-13 the driver pinned the person's
    # window that way and died on it); the new window has to be found by its claim.
    if ($a.ok -and $a.reused -and $a.port) {
        Write-Host "  /window on $asker gave port $($a.port) ($(if ($a.rejoined) { 'rejoined' } else { 'reused' }))" -ForegroundColor DarkGray
        return [int]$a.port
    }
    if (-not $a.ok) { Write-Host "  /window on $asker refused: $($a.error) $($a.hint)" -ForegroundColor Yellow; return $null }
    # opened (or opening): the new window registers on the next free port in a few seconds
    for ($i = 0; $i -lt 30; $i++) {
        Start-Sleep -Seconds 2
        foreach ($port in 25801..25816) {
            try { $h = Invoke-RestMethod "http://127.0.0.1:$port/hello" -TimeoutSec 1 -ErrorAction Stop }
            catch { continue }
            if ($h.claimed_by -and $h.claimed_by.session -eq $SessionId) {
                Write-Host "  /window on $asker opened window $($h.window) port $port" -ForegroundColor DarkGray
                return [int]$port
            }
        }
    }
    Write-Host "  /window on $asker said it opened a window, but none registered for $SessionId" -ForegroundColor Yellow
    return $null
}

function Get-FreeWindow {
    # NOTE: `$AllowClaimed is read from the enclosing script scope.
    # IDENTITY, not liveness. A claim seen under 120 s ago is a live session.
    # This is the pre-dock path, kept for a Blockbench whose plugin has no dock.
    foreach ($port in 25801..25816) {
        try { $r = Invoke-RestMethod "http://127.0.0.1:$port/hello" -TimeoutSec 1 -ErrorAction Stop }
        catch { continue }
        if ($r.app -ne 'blockbench' -or $r.plugin -ne 'mcptoolkit_bridge') { continue }
        if ($r.projects -ne 0) { continue }
        $seen = if ($r.claimed_by) { [double]$r.claimed_by.seen_s_ago } else { [double]::MaxValue }
        if ($seen -lt 120 -and -not $AllowClaimed) { continue }
        return $port
    }
    return $null
}

$results = @()
$registered = $false
# One identity for the whole batch, so every ask to the dock is a rejoin of the same window.
$batchSession = "mcptk-batch-" + (Get-Date -Format 'yyyyMMdd-HHmmss')
foreach ($piece in $Pieces) {
    # A retrofit is <piece>_surface.md; a full authoring brief is just <piece>.md.
    $brief = Join-Path $briefDir "$piece`_surface.md"
    if (-not (Test-Path $brief)) { $brief = Join-Path $briefDir "$piece.md" }
    if (-not (Test-Path $brief)) { Write-Host "  no brief for $piece - skipped" -ForegroundColor Yellow; continue }

    $port = Get-DockWindow -SessionId $batchSession
    $sessionId = $batchSession
    if (-not $port) { $port = Get-AskedWindow -SessionId $batchSession }
    if (-not $port) {
        $port = Get-FreeWindow
        $sessionId = "mcptk-surface-$piece"
    }
    if (-not $port) {
        Write-Host "  no free Blockbench window for $piece - stopping" -ForegroundColor Red
        break
    }
    try {
        $h = Invoke-RestMethod "http://127.0.0.1:$port/hello" -TimeoutSec 2 -ErrorAction Stop
        if ([int]$h.projects -gt 0) {
            Write-Host ("  !! window {0} still holds {1} tab(s), active '{2}' - the last session did not close its tab" -f
                $port, $h.projects, $h.active) -ForegroundColor Yellow
        }
    } catch { }
    if (-not $registered) {
        # The plugin's pack list is per Blockbench install and does not follow the repo (RUNNING.md).
        $prevEap = $ErrorActionPreference; $ErrorActionPreference = 'Continue'
        try { & python (Join-Path $repo 'tools/register_packs.py') $port $sessionId } catch { Write-Host "  register_packs failed: $_" -ForegroundColor Yellow }
        $ErrorActionPreference = $prevEap
        $registered = $true
    }
    $env:MCPTK_BLOCKBENCH = "http://127.0.0.1:$port"
    $env:ARMORPIECES_BB_URL = "http://127.0.0.1:$port"
    $env:MCPTK_SESSION = $sessionId

    $out = Join-Path $logDir "$piece.json"
    $prompt = "Build the piece specified in $brief. Read the brief first, then follow its order of work exactly. Ask me before you force any check line."

    Write-Host ("-> {0,-18} window {1}" -f $piece, $port) -ForegroundColor Cyan
    $t0 = Get-Date
    # NO `2>&1` HERE. PowerShell 5.1 wraps a native command's stderr in ErrorRecords
    # (NativeCommandError) and, under ErrorActionPreference=Stop, that KILLS the batch - even
    # though the only thing claude.exe writes there is a harmless
    # `[claude-code:unrecognized_model] ... generate_session_title` notice about the session
    # title model. stdout is what carries the result JSON, so stderr is simply let through.
    $prev = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $prompt | & $claude --agent part-author-qwen --model haiku -p --output-format json |
        Out-File -FilePath $out -Encoding utf8
    $ErrorActionPreference = $prev
    $mins = ((Get-Date) - $t0).TotalMinutes

    $sid = $null; $cost = $null; $err = $true
    try {
        $raw = Get-Content $out -Raw
        $i = $raw.IndexOf('{"duration_api_ms"')
        if ($i -ge 0) {
            $j = $raw.Substring($i) | ConvertFrom-Json
            $sid = $j.session_id; $cost = $j.total_cost_usd; $err = $j.is_error
        }
    } catch { }

    $results += [pscustomobject]@{
        Piece = $piece; Window = $port; Minutes = [math]::Round($mins, 1)
        Cost = $cost; Error = $err; Session = $sid
    }
    Write-Host ("   {0,-18} {1,5:N1} min  {2}  {3}" -f $piece, $mins,
        $(if ($cost) { '${0:N4}' -f $cost } else { '-' }),
        $(if ($err) { 'ERROR' } else { 'ok' })) -ForegroundColor $(if ($err) { 'Red' } else { 'Green' })

    if ($sid) { & python (Join-Path $repo 'tools\archive_qwen_run.py') $sid --piece $piece | Out-Null }
}

$results | Format-Table -AutoSize
$results | ConvertTo-Json | Out-File (Join-Path $logDir ("batch-" + (Get-Date -Format 'yyyyMMdd-HHmmss') + ".json")) -Encoding utf8
