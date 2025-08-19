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
echo 📱 GUI 데모:
echo   1️⃣  메인 GUI 데모 (권장)
echo   2️⃣  기본 GUI 데모
echo   3️⃣  진행률 컴포넌트 데모
echo   4️⃣  할일 트리 구조 데모
echo.
echo 🎯 기능별 데모:
echo   5️⃣  목표 날짜 기능 종합 데모
echo   6️⃣  목표 날짜 다이얼로그 데모
echo   7️⃣  날짜 필터링 데모
echo   8️⃣  자동 저장 및 백업 데모
echo.
echo 🔗 통합 데모:
echo   9️⃣  시작 알림 통합 데모
echo   A️⃣  성능 최적화 데모
echo.
echo   0️⃣  종료
echo.
echo ============================================================
set /p choice="선택 (0-9, A): "

if "%choice%"=="1" goto MAIN_GUI_DEMO
if "%choice%"=="2" goto GUI_DEMO
if "%choice%"=="3" goto PROGRESS_DEMO
if "%choice%"=="4" goto TREE_DEMO
if "%choice%"=="5" goto DUE_DATE_DEMO
if "%choice%"=="6" goto DUE_DATE_DIALOG_DEMO
if "%choice%"=="7" goto FILTERING_DEMO
if "%choice%"=="8" goto BACKUP_DEMO
if "%choice%"=="9" goto NOTIFICATION_DEMO
if /i "%choice%"=="A" goto PERFORMANCE_DEMO
if "%choice%"=="0" goto EXIT
echo.
echo ❌ 잘못된 선택입니다. 다시 선택해주세요.
echo.
goto MENU

:MAIN_GUI_DEMO
echo.
echo 🚀 메인 GUI 데모를 시작합니다...
echo.
if exist "demo\gui\demo_main_gui.py" (
    python demo\gui\demo_main_gui.py
) else (
    echo ❌ 메인 GUI 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:GUI_DEMO
echo.
echo 🚀 기본 GUI 데모를 시작합니다...
echo.
if exist "demo\gui\demo_gui.py" (
    python demo\gui\demo_gui.py
) else if exist "demo\demo_gui.py" (
    python demo\demo_gui.py
) else (
    echo ❌ GUI 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:PROGRESS_DEMO
echo.
echo 🚀 진행률 컴포넌트 데모를 시작합니다...
echo.
if exist "demo\gui\demo_progress_components.py" (
    python demo\gui\demo_progress_components.py
) else if exist "demo\demo_progress_components.py" (
    python demo\demo_progress_components.py
) else (
    echo ❌ 진행률 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:TREE_DEMO
echo.
echo 🚀 할일 트리 구조 데모를 시작합니다...
echo.
if exist "demo\gui\demo_todo_tree.py" (
    python demo\gui\demo_todo_tree.py
) else if exist "demo\demo_todo_tree.py" (
    python demo\demo_todo_tree.py
) else (
    echo ❌ 트리 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:DUE_DATE_DEMO
echo.
echo 🚀 목표 날짜 기능 종합 데모를 시작합니다...
echo.
if exist "demo\features\demo_due_date_features.py" (
    python demo\features\demo_due_date_features.py
) else (
    echo ❌ 목표 날짜 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:DUE_DATE_DIALOG_DEMO
echo.
echo 🚀 목표 날짜 다이얼로그 데모를 시작합니다...
echo.
if exist "demo\demo_due_date_dialog.py" (
    python demo\demo_due_date_dialog.py
) else (
    echo ❌ 목표 날짜 다이얼로그 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:FILTERING_DEMO
echo.
echo 🚀 날짜 필터링 데모를 시작합니다...
echo.
if exist "demo\demo_due_date_filtering.py" (
    python demo\demo_due_date_filtering.py
) else (
    echo ❌ 필터링 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:BACKUP_DEMO
echo.
echo 🚀 자동 저장 및 백업 데모를 시작합니다...
echo.
if exist "demo\features\demo_auto_save_backup.py" (
    python demo\features\demo_auto_save_backup.py
) else if exist "demo\demo_auto_save_backup.py" (
    python demo\demo_auto_save_backup.py
) else (
    echo ❌ 백업 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:NOTIFICATION_DEMO
echo.
echo 🚀 시작 알림 통합 데모를 시작합니다...
echo.
if exist "demo\integration\demo_startup_notification_integration.py" (
    python demo\integration\demo_startup_notification_integration.py
) else (
    echo ❌ 알림 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:PERFORMANCE_DEMO
echo.
echo 🚀 성능 최적화 데모를 시작합니다...
echo.
if exist "demo\performance\demo_performance_optimization.py" (
    python demo\performance\demo_performance_optimization.py
) else (
    echo ❌ 성능 데모 파일을 찾을 수 없습니다.
)
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
echo    자세한 데모 사용법은 docs/DEMO_GUIDE.md를 참조하세요.
echo.
pause