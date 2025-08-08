@echo off
chcp 65001 > nul
title 할일 관리 프로그램 - 테스트 실행

echo.
echo ============================================================
echo              📝 할일 관리 프로그램 - 테스트 실행
echo ============================================================
echo.

REM Python이 설치되어 있는지 확인
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되어 있지 않습니다.
    echo    Python 3.7 이상을 설치해주세요.
    echo    https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 현재 디렉토리를 스크립트 위치로 변경
cd /d "%~dp0"

REM 테스트 실행
echo 🧪 테스트를 시작합니다...
echo.

if exist "test\run_all_tests.py" (
    python test\run_all_tests.py
) else (
    echo ❌ 테스트 파일을 찾을 수 없습니다.
    echo    test\run_all_tests.py 파일이 존재하는지 확인해주세요.
)

echo.
echo ✅ 테스트가 완료되었습니다.
echo.

pause