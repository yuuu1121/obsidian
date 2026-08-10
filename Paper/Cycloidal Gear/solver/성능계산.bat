@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================================
echo  사이클로이드 감속기 성능 계산
echo  (전달오차 / 백래시 / 접촉력)
echo ============================================================
echo.
echo 엑셀 파일이 열려 있으면 저장에 실패합니다. 먼저 닫아주세요.
echo.
pause
echo.
python run_performance.py
echo.
if errorlevel 1 (
  echo ---- 계산에 실패했습니다. 위 메시지를 확인하세요. ----
) else (
  echo ---- 완료. 엑셀을 열어 [6.성능계산] 시트를 보세요. ----
)
echo.
pause
