<#
.SYNOPSIS
    Author pieces from briefs: one headless `claude -p` per piece, N at a time, every transcript kept.

.DESCRIPTION
    This is the authoring workflow the part sessions actually run under, written down so a batch is
    reproducible instead of remembered. One piece is one `claude.exe` - never two subagents of one
    session, because both halves of a session's bridge derive their identity from the PARENT process
    and two subagents would share a binding.

    Everything here is a trap that has already cost a batch:

      * THE PROMPT GOES ON STDIN. `Start-Process -ArgumentList @(...)` joins an array with spaces and
        quotes nothing, so a multi-word prompt arrives as many argv entries and `claude -p` takes only
        the first word. Two sessions were once launched with the prompt "Build"; neither crashed, both
        went looking for something to do, and one built the wrong piece. The prompt is written to a
        file and handed over with -RedirectStandardInput.

      * DO NOT WATCH THE PID. `claude.exe` is a launcher shim: it exits immediately while the real
        session runs on. A run is finished when its stream-json log carries a `"type":"result"` line,
        and stalled when nothing has been written to it for -StallMinutes.

      * PIN BOTH HALVES TO ONE WINDOW, AND SHARE THE IDENTITY. Each Blockbench window's plugin takes
        the first free port at or above 25801, so the port names the window. `tools/mcp/server.mjs`
        (the piece tools) and the toolkit's shim (Blockbench itself) must be pinned to the SAME port
        AND given the same MCPTK_SESSION - left alone the proxy falls back to `mcptk-<parent pid>`
        while the shim lets the bridge assign it one, so the two halves bind in different windows and
        the toolkit truthfully reports "no project is open".

      * THE TRANSCRIPTS ARE NOT OURS. They live in ~/.claude/projects/<slug>/<session id>.jsonl,
        which nothing backs up and Claude Code prunes. Every finished run is copied into
        .mcptoolkit/runs/archive/E/ here, immediately, and the batch manifest records where each one
        went. `python tools/measure_sessions.py` reads the same archive.

.EXAMPLE
    .\tools\run_briefs.ps1 wither_mask wither_heads wither_ribs

.EXAMPLE
    .\tools\run_briefs.ps1 -MaxConcurrent 3 -Model sonnet (Get-Content batch.txt)

.EXAMPLE
    .\tools\run_briefs.ps1 -DryRun wither_mask        # print the plan, launch nothing
#>
[CmdletBinding()]
param(
    # Brief names (`wither_mask`) or paths. The piece name is the brief's file stem.
    [Parameter(Mandatory = $true, Position = 0, ValueFromRemainingArguments = $true)]
    [string[]]$Brief,

    # How many sessions may run at once. One Blockbench window is needed per concurrent session.
    [int]$MaxConcurrent = 3,

    [string]$Agent = 'part-author-kit',

    # Passed through to `claude --model`. Every part session so far has run on sonnet.
    [string]$Model = 'sonnet',

    # No write to a run's log for this long means finished-or-stalled; the run is given up on.
    [int]$StallMinutes = 12,

    # Claim a window that still has projects open in it (but is not claimed by a live session).
    # Off by default: a piece gets a window to itself, and a leftover tab is the active tab for
    # whoever claims the window next.
    [switch]$AllowBusyWindow,

    # Un-minimise each session's Blockbench window without stealing focus.
    [switch]$Raise,

    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'

# Directory constants carry a _DIR suffix on purpose: PowerShell variable names are
# case-insensitive, and `$runs` (the list of launched sessions) silently overwrote a `$RUNS`
# path constant with an array of run objects. The same collision hit $LIVE/$running.
$REPO = Split-Path -Parent $PSScriptRoot
$RUNS_DIR = Join-Path $REPO '.mcptoolkit\runs'
$ARCHIVE_DIR = Join-Path $RUNS_DIR 'archive\E'
$BRIEFS_DIR = Join-Path $REPO 'docs\plans\briefs'
$TRANSCRIPTS_DIR = Join-Path $HOME '.claude\projects\C--Users-Matthijs-ArmorPieces'
# Seconds: a claim seen more recently than this belongs to a running session. NOT named $LIVE -
# PowerShell variable names are case-insensitive, and a `$running` list of running sessions silently
# overwrote this constant with an empty array, which made every claim look stale.
$CLAIM_LIVE_S = 120

foreach ($d in @($RUNS_DIR, $ARCHIVE_DIR)) {
    if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d | Out-Null }
}

if ((Get-Location).Path -ne $REPO) {
    Write-Host "Working directory is not $REPO - the project agent and .mcp.json are found from it." -ForegroundColor Yellow
    Write-Error 'cd to the repository root first.'
}

$claude = Get-Command claude -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
if (-not $claude) { Write-Error 'claude executable not found on PATH.' }

# --- the briefs ------------------------------------------------------------------------------

$queue = @()
foreach ($b in $Brief) {
    $path = $b
    if (-not (Test-Path $path)) { $path = Join-Path $BRIEFS_DIR $b }
    if (-not (Test-Path $path)) { $path = Join-Path $BRIEFS_DIR "$b.md" }
    if (-not (Test-Path $path)) { Write-Error "Brief not found: $b" }
    $full = (Resolve-Path $path).Path
    $queue += [pscustomobject]@{
        Piece = [IO.Path]::GetFileNameWithoutExtension($full)
        Brief = $full
    }
}

# --- who is on the bridge --------------------------------------------------------------------

function Get-BlockbenchBridge {
    # IDENTITY, not liveness: an open port proves nothing about who is behind it, and 25599 in this
    # repo is the Minecraft dev client's bridge rather than Blockbench's.
    $found = @()
    foreach ($port in 25801..25816) {
        try {
            $r = Invoke-RestMethod -Uri "http://127.0.0.1:$port/hello" -TimeoutSec 1 -ErrorAction Stop
        }
        catch { continue }
        if ($r.app -eq 'blockbench' -and $r.plugin -eq 'mcptoolkit_bridge') {
            $seen = [double]::MaxValue
            $claim = $null
            if ($r.claimed_by) {
                $claim = $r.claimed_by.session
                $seen = [double]$r.claimed_by.seen_s_ago
            }
            $found += [pscustomobject]@{
                Port = $port; Window = $r.window; Active = $r.active; Projects = [int]$r.projects
                Version = $r.plugin_version; Claim = $claim; Seen = $seen
            }
        }
    }
    return $found
}

function Select-Window {
    param([string]$Piece, [string[]]$Taken)

    $bridges = @(Get-BlockbenchBridge) | Where-Object { $Taken -notcontains $_.Window }

    # In order: the window that already holds this piece (a relaunch), then an empty unclaimed one,
    # then - only with -AllowBusyWindow - any window no live session is sitting in.
    $hit = $bridges | Where-Object { $_.Active -eq $Piece } | Select-Object -First 1
    if ($hit) { return @{ Bridge = $hit; How = 'already holds this piece' } }

    $hit = $bridges |
        Where-Object { $_.Projects -eq 0 -and ($null -eq $_.Claim -or $_.Seen -ge $CLAIM_LIVE_S) } |
        Select-Object -First 1
    if ($hit) { return @{ Bridge = $hit; How = 'empty and unclaimed' } }

    if ($AllowBusyWindow) {
        $hit = $bridges | Where-Object { $null -eq $_.Claim -or $_.Seen -ge $CLAIM_LIVE_S } | Select-Object -First 1
        if ($hit) { return @{ Bridge = $hit; How = "unclaimed, but $($hit.Projects) project(s) still open" } }
    }

    return $null
}

# --- launching -------------------------------------------------------------------------------

$WinRaiseSource = @'
using System;
using System.Text;
using System.Runtime.InteropServices;
public class WinRaiseBriefs {
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc cb, IntPtr p);
  [DllImport("user32.dll")] static extern int GetWindowTextLength(IntPtr h);
  [DllImport("user32.dll", CharSet=CharSet.Unicode)] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] static extern bool ShowWindow(IntPtr h, int c);
  delegate bool EnumProc(IntPtr h, IntPtr p);
  public static string Show(string needle) {
    string hit = null;
    EnumWindows((h, p) => {
      int len = GetWindowTextLength(h);
      if (len == 0) return true;
      var sb = new StringBuilder(len + 1);
      GetWindowText(h, sb, sb.Capacity);
      string t = sb.ToString();
      if (t.Contains("Blockbench") && t.Contains(needle)) {
        if (IsIconic(h)) ShowWindow(h, 9);  // SW_RESTORE
        ShowWindow(h, 4);                   // SW_SHOWNOACTIVATE
        hit = t; return false;
      }
      return true;
    }, IntPtr.Zero);
    return hit;
  }
}
'@

function Start-PartSession {
    param([pscustomobject]$Item, $Bridge, [string]$How)

    $stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $stem = "$Agent-$($Item.Piece)-$stamp"
    $log = Join-Path $RUNS_DIR "$stem.jsonl"
    $err = Join-Path $RUNS_DIR "$stem.stderr.log"
    $promptFile = Join-Path $RUNS_DIR "$stem.prompt.txt"

    $prompt = @"
Build the piece specified in $($Item.Brief).

Read that brief first and follow it exactly. Then read docs/plans/briefs/LESSONS.md, which is the
current technique. Do not open any other brief for technique - open one only if your own brief names
a neighbouring piece and you need that piece's numbers.

Then follow your order of work: create the piece, block out the geometry, paint, set the part data,
save, run the checks the brief names, and fill in the brief's own Lessons section with what you
learned. Report what you built, every check line you accepted and why, and anything that should go to
LESSONS.md.

LEAVE THE WORKSPACE AS YOU FOUND IT. This is not tidiness - the next session claims this window, and
a tab you left open is the tab it finds active.

  * Finish with `armorpieces_close` on your piece. Always. It is the last tool call you make.
  * If you are giving up on the piece, close it anyway, with `discard: true`, and say in your report
    that you discarded it and what state the pack files were left in.
  * If you are stopping to ask a question, close the tab first and say so - a question does not
    entitle a session to hold a window open.
  * Do not open, edit, save or close any OTHER tab, and do not leave a project open that you created
    by mistake. If you created a piece you then abandoned, close it with `discard: true` and name the
    three starter files you left behind so they can be removed.

You are pinned to one Blockbench window and one piece. Do not touch any other tab, and do not force a
save past a check line the brief does not allow.
"@
    if (-not $DryRun) { Set-Content -Path $promptFile -Value $prompt -Encoding utf8 }

    # Both servers to the same window, and the same identity for both halves.
    #
    # MCPTK_BLOCKBENCH, *not* MCPTK_URL. The toolkit shim has two upstreams: MCPTK_URL is the
    # MINECRAFT bridge (default 25599) and MCPTK_BLOCKBENCH is the Blockbench one. A bare URL there
    # pins one window; left unset the adapter range-scans 25801-25816 and CLAIMS a window of its
    # own - which is how a session ends up with its armorpieces half in the pinned window and its
    # toolkit half in an empty one, answering "no project is open" to every geometry call. That cost
    # the wither_mask run of 2026-09-09 its whole turn budget; the piece could not be built at all.
    $env:MCPTK_BLOCKBENCH = "http://127.0.0.1:$($Bridge.Port)"
    $env:ARMORPIECES_BB_URL = "http://127.0.0.1:$($Bridge.Port)"
    if ($Bridge.Claim) {
        # Adopt the window's existing (dead) claim: minting a new identity needs a free window, and
        # windows stay claimed by sessions that have already exited.
        $env:MCPTK_SESSION = $Bridge.Claim
    }
    else {
        $env:MCPTK_SESSION = 'mcptk-batch-' + [Guid]::NewGuid().ToString('N').Substring(0, 8)
    }

    # ONE argument string, with nothing multi-word in it - the prompt is on stdin.
    $argLine = "-p --agent $Agent --model $Model --dangerously-skip-permissions " +
               "--output-format stream-json --verbose"

    Write-Host ("  -> {0}  window {1} port {2} ({3})" -f $Item.Piece, $Bridge.Window, $Bridge.Port, $How) -ForegroundColor Cyan
    Write-Host ("     session {0}   log {1}" -f $env:MCPTK_SESSION, (Split-Path $log -Leaf)) -ForegroundColor DarkGray

    if ($DryRun) {
        Write-Host "     (dry run - not launched)" -ForegroundColor DarkGray
        return $null
    }

    Start-Process -FilePath $claude.Source -ArgumentList $argLine `
        -RedirectStandardInput $promptFile -RedirectStandardOutput $log -RedirectStandardError $err `
        -WorkingDirectory $REPO -WindowStyle Hidden

    if ($Raise) {
        if (-not ('WinRaiseBriefs' -as [type])) { Add-Type -TypeDefinition $WinRaiseSource -ErrorAction SilentlyContinue }
        try { [WinRaiseBriefs]::Show($env:MCPTK_SESSION) | Out-Null } catch { }
    }

    return [pscustomobject]@{
        Piece = $Item.Piece; Brief = $Item.Brief; Log = $log; Stderr = $err; Prompt = $promptFile
        Port = $Bridge.Port; Window = $Bridge.Window; Session = $env:MCPTK_SESSION
        ProjectsAtLaunch = $Bridge.Projects
        Started = Get-Date; Ended = $null; SessionId = $null; Archived = $null
        Result = $null; State = 'running'; LeftOpen = $null; CleanExit = $null
    }
}

# --- finishing -------------------------------------------------------------------------------

function Get-RunResult {
    <# The stream-json log's last `result` event, or $null while the run is still going. #>
    param([string]$Log)
    if (-not (Test-Path $Log)) { return $null }
    $line = Select-String -Path $Log -Pattern '"type":"result"' -SimpleMatch | Select-Object -Last 1
    if (-not $line) { return $null }
    try { return $line.Line | ConvertFrom-Json } catch { return $null }
}

function Get-RunSessionId {
    param([string]$Log)
    if (-not (Test-Path $Log)) { return $null }
    foreach ($line in Get-Content $Log -TotalCount 40) {
        if ($line -notmatch '"session_id"') { continue }
        try { $o = $line | ConvertFrom-Json } catch { continue }
        if ($o.session_id) { return $o.session_id }
    }
    return $null
}

function Save-Transcript {
    <# Copy the child's own transcript out of ~/.claude/projects, which nothing backs up. #>
    param([pscustomobject]$Run)

    $sid = Get-RunSessionId -Log $Run.Log
    if (-not $sid) {
        Write-Host ("     !! no session id in {0} - transcript NOT archived" -f (Split-Path $Run.Log -Leaf)) -ForegroundColor Red
        return
    }
    $Run.SessionId = $sid
    $src = Join-Path $TRANSCRIPTS_DIR "$sid.jsonl"
    if (-not (Test-Path $src)) {
        Write-Host ("     !! transcript $sid.jsonl not found in $TRANSCRIPTS_DIR") -ForegroundColor Red
        return
    }
    $dst = Join-Path $ARCHIVE_DIR "$($Run.Piece)--$sid.jsonl"
    Copy-Item -Path $src -Destination $dst -Force
    $Run.Archived = $dst
    $kb = [int]((Get-Item $dst).Length / 1KB)
    Write-Host ("     transcript archived: {0} ({1} KB)" -f (Split-Path $dst -Leaf), $kb) -ForegroundColor DarkGray
}

function Test-WindowClean {
    <# Did the session close its tab? The window is about to be handed to the next piece, and a tab
       left open is the tab that session finds ACTIVE. Reported, and the window is not reused. #>
    param([pscustomobject]$Run)

    try {
        $r = Invoke-RestMethod -Uri "http://127.0.0.1:$($Run.Port)/hello" -TimeoutSec 2 -ErrorAction Stop
    }
    catch {
        Write-Host "     (window $($Run.Window) no longer answering - cannot check cleanup)" -ForegroundColor DarkGray
        return
    }
    $Run.LeftOpen = [int]$r.projects - [int]$Run.ProjectsAtLaunch
    $Run.CleanExit = ($Run.LeftOpen -le 0 -and $r.active -ne $Run.Piece)
    if ($Run.CleanExit) {
        Write-Host "     window clean: $($r.projects) tab(s), active '$($r.active)'" -ForegroundColor DarkGray
    }
    else {
        Write-Host ("     !! {0} did NOT close its tab - window {1} now holds {2} project(s), active '{3}'" -f
                    $Run.Piece, $Run.Window, $r.projects, $r.active) -ForegroundColor Yellow
        Write-Host "        that window will not be reused by this batch; close the tab by hand." -ForegroundColor Yellow
    }
}

# --- the batch -------------------------------------------------------------------------------

$batchStamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$manifest = Join-Path $RUNS_DIR "batch-$batchStamp.json"

Write-Host ''
Write-Host ("Batch of {0} piece(s), {1} at a time, agent {2} on {3}" -f $queue.Count, $MaxConcurrent, $Agent, $Model) -ForegroundColor Green
Write-Host ("  logs and prompts -> {0}" -f $RUNS_DIR) -ForegroundColor DarkGray
Write-Host ("  transcripts      -> {0}" -f $ARCHIVE_DIR) -ForegroundColor DarkGray
Write-Host ("  manifest         -> {0}" -f (Split-Path $manifest -Leaf)) -ForegroundColor DarkGray
Write-Host ''

$bridges = @(Get-BlockbenchBridge)
if ($bridges.Count -eq 0) {
    Write-Host 'Bridge preflight FAILED - no Blockbench bridge on 25801-25816.' -ForegroundColor Red
    Write-Host '  Start Blockbench with the mcptoolkit bridge plugin loaded. One window per' -ForegroundColor Yellow
    Write-Host '  concurrent session. (A listener on 25599 is the Minecraft dev client, not this.)' -ForegroundColor Yellow
    Write-Error 'No Blockbench bridge.'
}
Write-Host 'Blockbench windows:' -ForegroundColor DarkGray
foreach ($b in $bridges) {
    $state = 'free'
    if ($b.Projects -gt 0) { $state = "$($b.Projects) project(s) open, active '$($b.Active)'" }
    if ($b.Claim -and $b.Seen -lt $CLAIM_LIVE_S) { $state = "CLAIMED by $($b.Claim), seen $([int]$b.Seen)s ago" }
    Write-Host ("  {0}  {1}  plugin {2}  {3}" -f $b.Port, $b.Window, $b.Version, $state) -ForegroundColor DarkGray
}
Write-Host ''

$runs = @()
$pending = [System.Collections.ArrayList]@($queue)

while ($pending.Count -gt 0 -or ($runs | Where-Object { $_.State -eq 'running' })) {

    # Finish what has finished.
    foreach ($r in ($runs | Where-Object { $_.State -eq 'running' })) {
        $res = Get-RunResult -Log $r.Log
        $idle = (New-TimeSpan -Start (Get-Item $r.Log -ErrorAction SilentlyContinue).LastWriteTime -End (Get-Date)).TotalMinutes
        if ($res) {
            $r.State = 'done'
            $r.Ended = Get-Date
            $r.Result = $res
            $mins = [math]::Round(((New-TimeSpan -Start $r.Started -End $r.Ended).TotalMinutes), 1)
            $cost = 0.0
            if ($res.total_cost_usd) { $cost = [math]::Round([double]$res.total_cost_usd, 2) }
            $flag = 'ok'
            if ($res.is_error) { $flag = 'ERROR' }
            Write-Host ("  <- {0}  {1}  {2} min, {3} turns, `$${4}" -f $r.Piece, $flag, $mins, $res.num_turns, $cost) -ForegroundColor Green
            Save-Transcript -Run $r
            Test-WindowClean -Run $r
        }
        elseif ($idle -gt $StallMinutes) {
            $r.State = 'stalled'
            $r.Ended = Get-Date
            Write-Host ("  <- {0}  STALLED - no log write for {1:N0} min" -f $r.Piece, $idle) -ForegroundColor Red
            Save-Transcript -Run $r
            Test-WindowClean -Run $r
        }
    }

    # Start what can start.
    $running = @($runs | Where-Object { $_.State -eq 'running' })
    while ($pending.Count -gt 0 -and $running.Count -lt $MaxConcurrent) {
        # Windows in use, plus any a finished session left a tab open in: reusing one of those hands
        # the next piece somebody else's active tab.
        $taken = @($running | ForEach-Object { $_.Window }) +
                 @($runs | Where-Object { $_.CleanExit -eq $false } | ForEach-Object { $_.Window })
        $pick = Select-Window -Piece $pending[0].Piece -Taken $taken
        if (-not $pick) {
            if ($running.Count -eq 0) {
                Write-Host ''
                Write-Host ("No free Blockbench window for '{0}'." -f $pending[0].Piece) -ForegroundColor Red
                foreach ($b in (Get-BlockbenchBridge)) {
                    $why = 'free'
                    if ($b.Projects -gt 0) { $why = "holds $($b.Active) ($($b.Projects) tabs)" }
                    if ($b.Claim -and $b.Seen -lt $CLAIM_LIVE_S) { $why = "claimed by $($b.Claim), seen $([int]$b.Seen)s ago" }
                    Write-Host ("  {0}  {1}  {2}" -f $b.Port, $b.Window, $why) -ForegroundColor DarkGray
                }
                Write-Host '  Open another Blockbench window, close the leftover tabs, or pass -AllowBusyWindow.' -ForegroundColor Yellow
                Write-Error 'No free Blockbench window.'
            }
            break   # wait for a running session to release one
        }
        $item = $pending[0]
        $pending.RemoveAt(0)
        $run = Start-PartSession -Item $item -Bridge $pick.Bridge -How $pick.How
        if ($run) {
            $runs += $run
            $running = @($runs | Where-Object { $_.State -eq 'running' })
            Start-Sleep -Seconds 20   # let the session claim its window before the next preflight
        }
        elseif ($DryRun) {
            $running = @()   # nothing is really running
        }
    }

    if ($DryRun) { break }
    if ($pending.Count -gt 0 -or ($runs | Where-Object { $_.State -eq 'running' })) { Start-Sleep -Seconds 20 }
}

# --- the manifest ----------------------------------------------------------------------------

$rows = foreach ($r in $runs) {
    $res = $r.Result
    [pscustomobject]@{
        piece      = $r.Piece
        brief      = $r.Brief
        state      = $r.State
        agent      = $Agent
        model      = $Model
        window     = $r.Window
        port       = $r.Port
        mcptk      = $r.Session
        started    = $r.Started.ToString('s')
        ended      = $(if ($r.Ended) { $r.Ended.ToString('s') } else { $null })
        minutes    = $(if ($r.Ended) { [math]::Round((New-TimeSpan -Start $r.Started -End $r.Ended).TotalMinutes, 1) } else { $null })
        turns      = $(if ($res) { $res.num_turns } else { $null })
        cost_usd   = $(if ($res -and $res.total_cost_usd) { [math]::Round([double]$res.total_cost_usd, 3) } else { $null })
        is_error   = $(if ($res) { [bool]$res.is_error } else { $null })
        log        = $r.Log
        stderr     = $r.Stderr
        left_open  = $r.LeftOpen
        clean_exit = $r.CleanExit
        session_id = $r.SessionId
        transcript = $r.Archived
    }
}

if (-not $DryRun) {
    $rows | ConvertTo-Json -Depth 4 | Out-File -FilePath $manifest -Encoding utf8
    Write-Host ''
    Write-Host 'Batch finished.' -ForegroundColor Green
    $rows | Format-Table piece, state, minutes, turns, cost_usd, session_id -AutoSize | Out-String -Width 160 | Write-Host
    $missing = @($rows | Where-Object { -not $_.transcript })
    if ($missing.Count -gt 0) {
        Write-Host ("!! {0} run(s) have no archived transcript: {1}" -f $missing.Count, ($missing.piece -join ', ')) -ForegroundColor Red
    }
    Write-Host ("manifest: {0}" -f $manifest) -ForegroundColor DarkGray
    Write-Host 'Then: python tools/measure_sessions.py --archive' -ForegroundColor DarkGray
}
