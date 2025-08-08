@echo off
chcp 65001 > nul
title 할일 관리 프로그램

echo.
echo ============================================================
echo                    📝 할일 관리 프로그램
echo ============================================================
echo.
echo GUI 버전을 시작합니다...
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

REM 필요한 디렉토리 생성
if not exist "data" mkdir data
if not exist "logs" mkdir logs
if not exist "todo_folders" mkdir todo_folders

REM GUI 프로그램 실행
echo 🚀 프로그램을 시작합니다...
echo.
python main_gui.py

REM 프로그램 종료 후 처리
if errorlevel 1 (
    echo.
    echo ❌ 프로그램 실행 중 오류가 발생했습니다.
    echo    로그 파일을 확인해주세요: logs/app.log
    echo.
) else (
    echo.
    echo ✅ 프로그램이 정상적으로 종료되었습니다.
    echo.
)

pause