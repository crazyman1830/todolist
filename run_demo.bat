@echo off
chcp 65001 > nul
title 할일 관리 프로그램 - 데모 실행

echo.
echo ============================================================
echo              📋 할일 관리 프로그램 - 데모 메뉴
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

:MENU
echo 실행할 데모를 선택하세요:
echo.
echo   1️⃣  GUI 데모 (권장)
echo   2️⃣  자동 저장 및 백업 데모
echo   3️⃣  진행률 컴포넌트 데모
echo   4️⃣  할일 트리 구조 데모
echo   5️⃣  모든 데모 순차 실행
echo   0️⃣  종료
echo.
echo ============================================================
set /p choice="선택 (0-5): "

if "%choice%"=="1" goto GUI_DEMO
if "%choice%"=="2" goto BACKUP_DEMO
if "%choice%"=="3" goto PROGRESS_DEMO
if "%choice%"=="4" goto TREE_DEMO
if "%choice%"=="5" goto ALL_DEMOS
if "%choice%"=="0" goto EXIT
echo.
echo ❌ 잘못된 선택입니다. 다시 선택해주세요.
echo.
goto MENU

:GUI_DEMO
echo.
echo 🚀 GUI 데모를 시작합니다...
echo.
python demo/demo_gui.py
goto DEMO_END

:BACKUP_DEMO
echo.
echo 🚀 자동 저장 및 백업 데모를 시작합니다...
echo.
python demo/demo_auto_save_backup.py
goto DEMO_END

:PROGRESS_DEMO
echo.
echo 🚀 진행률 컴포넌트 데모를 시작합니다...
echo.
python demo/demo_progress_components.py
goto DEMO_END

:TREE_DEMO
echo.
echo 🚀 할일 트리 구조 데모를 시작합니다...
echo.
python demo/demo_todo_tree.py
goto DEMO_END

:ALL_DEMOS
echo.
echo 🚀 모든 데모를 순차적으로 실행합니다...
echo.
echo [1/4] GUI 데모 실행 중...
python demo/demo_gui.py
echo.
echo [2/4] 자동 저장 및 백업 데모 실행 중...
python demo/demo_auto_save_backup.py
echo.
echo [3/4] 진행률 컴포넌트 데모 실행 중...
python demo/demo_progress_components.py
echo.
echo [4/4] 할일 트리 구조 데모 실행 중...
python demo/demo_todo_tree.py
echo.
echo ✅ 모든 데모가 완료되었습니다.
goto DEMO_END

:DEMO_END
echo.
echo ============================================================
echo.
set /p continue="다른 데모를 실행하시겠습니까? (y/N): "
if /i "%continue%"=="y" goto MENU
if /i "%continue%"=="yes" goto MENU

:EXIT
echo.
echo 👋 데모를 종료합니다.
echo    자세한 데모 사용법은 demo/README.md를 참조하세요.
echo.
pause