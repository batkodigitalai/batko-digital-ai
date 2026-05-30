# Přesune foto_01.jpg - foto_37.jpg z Downloads do img\ složky aukce
$src = "$env:USERPROFILE\Downloads"
$dst = "$PSScriptRoot\img"

New-Item -ItemType Directory -Force -Path $dst | Out-Null

$moved = 0
for ($i = 1; $i -le 37; $i++) {
    $fname = "foto_{0:D2}.jpg" -f $i
    $srcPath = Join-Path $src $fname
    $dstPath = Join-Path $dst $fname
    if (Test-Path $srcPath) {
        Move-Item $srcPath $dstPath -Force
        Write-Host "OK: $fname"
        $moved++
    } else {
        Write-Host "CHYBÍ: $fname"
    }
}
Write-Host "`nPřesunuto: $moved/37 fotek do $dst"
