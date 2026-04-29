$repoPath = "."
$branch   = "develop"
$interval = 30
$logFile  = "$repoPath\git-pull.log"

while ($true) {
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $result = git -C $repoPath pull origin $branch 2>&1

    if ($LASTEXITCODE -ne 0) {
        $msg = "[$timestamp] ERROR: $result"
        Write-Host $msg -ForegroundColor Red
    } elseif ($result -match "Already up to date") {
        Write-Host "[$timestamp] Sin cambios" -ForegroundColor Gray
    } else {
        $msg = "[$timestamp] ACTUALIZADO: $result"
        Write-Host $msg -ForegroundColor Green
        Add-Content $logFile $msg
    }

    Start-Sleep -Seconds $interval
}