# SatQuery AI - Mission Control PowerShell Launcher
Write-Host "========================================================" -ForegroundColor Red
Write-Host "  SatQuery AI - Autonomous Vision-Language Assistant" -ForegroundColor White
Write-Host "  Smart India Hackathon 2026 | PS 26167 | ISRO / SAC" -ForegroundColor Yellow
Write-Host "========================================================" -ForegroundColor Red
Write-Host "Starting Mission Control Dashboard on http://localhost:8000 ..." -ForegroundColor Cyan

python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
