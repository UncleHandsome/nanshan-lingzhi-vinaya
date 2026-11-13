param([switch]$Apply)

$ErrorActionPreference = 'Stop'
$enc = New-Object System.Text.UTF8Encoding($false)
$planPath = Join-Path $PSScriptRoot 'plan.json'
$reportPath = Join-Path $PSScriptRoot 'report.txt'
$plan = [System.IO.File]::ReadAllText($planPath, [System.Text.Encoding]::UTF8) | ConvertFrom-Json

$rel = $plan.root.Replace('/', '\')
$ws = $PSScriptRoot
while (-not (Test-Path -LiteralPath (Join-Path $ws $rel))) {
    $ws = Split-Path $ws -Parent
    if (-not $ws) { throw 'workspace root not found' }
}
$dir = Join-Path $ws $rel
$bak = Join-Path $ws ($plan.backup.Replace('/', '\'))
$log = New-Object System.Collections.Generic.List[string]

function L($s) { $log.Add($s); Write-Output $s }

L ("workspace : " + $ws)
L ("chunk dir : " + $dir)
L ("backup dir: " + $bak)
L ("mode      : " + $(if ($Apply) { 'APPLY' } else { 'CHECK-ONLY' }))
L ""

# ---------- pass 1: validate against untouched originals ----------
$orig = @{}
foreach ($f in $plan.files) {
    $p = Join-Path $dir ($f.file + '.txt')
    if (-not (Test-Path -LiteralPath $p)) { throw ("missing file: " + $p) }
    $t = [System.IO.File]::ReadAllText($p, [System.Text.Encoding]::UTF8)
    $orig[$f.file] = $t
    foreach ($e in $f.edits) {
        $c = ([regex]::Matches($t, [regex]::Escape($e.old))).Count
        $c2 = ([regex]::Matches($t, [regex]::Escape($e.new))).Count
        L ("check {0,2} {1} {2,-16} old-count={3} (want {4})  new-preseen={5}" -f $e.id, $e.case, $e.chan, $c, $e.expect, $c2)
        if ($c -ne $e.expect) { throw ("count mismatch for id=" + $e.id) }
        if ($c2 -ne 0) { throw ("new string already present, id=" + $e.id) }
    }
}
L ""

# ---------- pass 2: apply + write ----------
$changed = 0
foreach ($f in $plan.files) {
    $p   = Join-Path $dir ($f.file + '.txt')
    $t   = $orig[$f.file]
    $new = $t
    foreach ($e in $f.edits) { $new = $new.Replace($e.old, $e.new) }

    # integrity assertions
    $lf0 = ([regex]::Matches($t, "`n")).Count
    $lf1 = ([regex]::Matches($new, "`n")).Count
    if ($lf0 -ne $lf1) { throw ("LF count changed in " + $f.file) }
    $cr0 = ([regex]::Matches($t, "`r`n")).Count
    $cr1 = ([regex]::Matches($new, "`r`n")).Count
    if ($cr0 -ne $cr1) { throw ("CRLF count changed in " + $f.file) }
    $pa0 = ($t -split "`n" | Where-Object { $_.Trim().Length -gt 0 }).Count
    $pa1 = ($new -split "`n" | Where-Object { $_.Trim().Length -gt 0 }).Count
    if ($pa0 -ne $pa1) { throw ("paragraph count changed in " + $f.file) }
    if (-not $new.EndsWith("`r`n")) { throw ("tail CRLF lost in " + $f.file) }

    # backup must equal the pre-edit original
    $bp = Join-Path $bak ($f.file + '.txt')
    if (-not (Test-Path -LiteralPath $bp)) { throw ("backup missing: " + $bp) }
    $bt = [System.IO.File]::ReadAllText($bp, [System.Text.Encoding]::UTF8)
    if ($bt -ne $t) { throw ("backup is not the pre-edit pre-image: " + $f.file) }

    # per-line diff detail
    $la = $t -split "`n"
    $lb = $new -split "`n"
    $diffs = 0
    $para = 0
    for ($i = 0; $i -lt $la.Length; $i++) {
        if ($la[$i].Trim().Length -gt 0) { $para++ }
        if ($la[$i] -cne $lb[$i]) {
            $diffs++
            $a = $la[$i]; $b = $lb[$i]
            $pre = 0
            $min = [Math]::Min($a.Length, $b.Length)
            while ($pre -lt $min -and $a[$pre] -eq $b[$pre]) { $pre++ }
            $suf = 0
            while ($suf -lt ($min - $pre) -and $a[$a.Length - 1 - $suf] -eq $b[$b.Length - 1 - $suf]) { $suf++ }
            $ctxA = $a.Substring([Math]::Max(0, $pre - 14), [Math]::Min($a.Length, $pre + ($a.Length - $pre - $suf) + 14) - [Math]::Max(0, $pre - 14))
            $ctxB = $b.Substring([Math]::Max(0, $pre - 14), [Math]::Min($b.Length, $pre + ($b.Length - $pre - $suf) + 14) - [Math]::Max(0, $pre - 14))
            L ("  diff {0} line {1} para#{2}" -f $f.file, ($i + 1), $para)
            L ("    old: ..." + $ctxA + "...")
            L ("    new: ..." + $ctxB + "...")
        }
    }
    if ($diffs -ne 0) {
        L ("{0,-16} paras {1} ({2}) changed-lines={3} bytes {4} -> {5}" -f $f.file, $pa0, $pa1, $diffs, [System.Text.Encoding]::UTF8.GetByteCount($t), [System.Text.Encoding]::UTF8.GetByteCount($new))
        $changed++
        if ($Apply) { [System.IO.File]::WriteAllBytes($p, $enc.GetBytes($new)) }
    } else {
        L ("{0,-16} NOTHING CHANGED" -f $f.file)
    }
}

L ""
L ("files changed: " + $changed + " / " + $plan.files.Count)
[System.IO.File]::WriteAllText($reportPath, ($log -join "`r`n") + "`r`n", $enc)
