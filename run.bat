@echo off
title SatQuery AI - Mission Control Dashboard
echo ========================================================
echo   SatQuery AI - Autonomous Vision-Language Assistant
echo   Smart India Hackathon 2026 | PS 26167 | ISRO / SAC
echo ========================================================
echo Starting Mission Control Dashboard on http://localhost:8000 ...
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
pause
