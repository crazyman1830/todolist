@echo off
chcp 65001 > nul
title 할일 관리 프로그램 - 목표 날짜 기능 데모

echo.
echo ============================================================
echo          📅 할일 관리 프로그램 - 목표 날짜 기능 데모
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
echo 목표 날짜 기능 데모를 선택하세요:
echo.
echo   1️⃣  목표 날짜 기능 종합 데모 (권장)
echo   2️⃣  목표 날짜 다이얼로그 데모
echo   3️⃣  날짜 필터링 데모
echo   4️⃣  알림 서비스 데모
echo   5️⃣  시작 알림 통합 데모
echo   6️⃣  모든 목표 날짜 데모 실행
echo   0️⃣  종료
echo.
echo ============================================================
set /p choice="선택 (0-6): "

if "%choice%"=="1" goto COMPREHENSIVE_DEMO
if "%choice%"=="2" goto DIALOG_DEMO
if "%choice%"=="3" goto FILTERING_DEMO
if "%choice%"=="4" goto NOTIFICATION_DEMO
if "%choice%"=="5" goto STARTUP_DEMO
if "%choice%"=="6" goto ALL_DEMOS
if "%choice%"=="0" goto EXIT
echo.
echo ❌ 잘못된 선택입니다. 다시 선택해주세요.
echo.
goto MENU

:COMPREHENSIVE_DEMO
echo.
echo 🚀 목표 날짜 기능 종합 데모를 시작합니다...
echo    - 다양한 날짜 형식 파싱
echo    - 긴급도 자동 계산
echo    - 상대적 시간 표시
echo    - 날짜 기반 정렬/필터링
echo.
if exist "demo\features\demo_due_date_features.py" (
    python demo\features\demo_due_date_features.py
) else (
    echo ❌ 종합 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:DIALOG_DEMO
echo.
echo 🚀 목표 날짜 다이얼로그 데모를 시작합니다...
echo    - 달력 위젯 사용법
echo    - 빠른 날짜 선택
echo    - 유효성 검사
echo.
if exist "demo\demo_due_date_dialog.py" (
    python demo\demo_due_date_dialog.py
) else (
    echo ❌ 다이얼로그 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:FILTERING_DEMO
echo.
echo 🚀 날짜 필터링 데모를 시작합니다...
echo    - 오늘 마감 할일 필터
echo    - 지연된 할일 필터
echo    - 이번 주 할일 필터
echo.
if exist "demo\demo_due_date_filtering.py" (
    python demo\demo_due_date_filtering.py
) else (
    echo ❌ 필터링 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:NOTIFICATION_DEMO
echo.
echo 🚀 알림 서비스 데모를 시작합니다...
echo    - 상태바 요약 정보
echo    - 긴급한 할일 알림
echo    - 마감 임박 알림
echo.
if exist "demo\services\demo_notification_service.py" (
    python demo\services\demo_notification_service.py
) else (
    echo ❌ 알림 서비스 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:STARTUP_DEMO
echo.
echo 🚀 시작 알림 통합 데모를 시작합니다...
echo    - 애플리케이션 시작 시 알림
echo    - "다시 보지 않기" 기능
echo    - 설정 저장/복원
echo.
if exist "demo\integration\demo_startup_notification_integration.py" (
    python demo\integration\demo_startup_notification_integration.py
) else (
    echo ❌ 시작 알림 데모 파일을 찾을 수 없습니다.
)
goto DEMO_END

:ALL_DEMOS
echo.
echo 🚀 모든 목표 날짜 데모를 순차적으로 실행합니다...
echo.
echo [1/5] 목표 날짜 기능 종합 데모...
if exist "demo\features\demo_due_date_features.py" (
    python demo\features\demo_due_date_features.py
)
echo.
echo [2/5] 목표 날짜 다이얼로그 데모...
if exist "demo\demo_due_date_dialog.py" (
    python demo\demo_due_date_dialog.py
)
echo.
echo [3/5] 날짜 필터링 데모...
if exist "demo\demo_due_date_filtering.py" (
    python demo\demo_due_date_filtering.py
)
echo.
echo [4/5] 알림 서비스 데모...
if exist "demo\services\demo_notification_service.py" (
    python demo\services\demo_notification_service.py
)
echo.
echo [5/5] 시작 알림 통합 데모...
if exist "demo\integration\demo_startup_notification_integration.py" (
    python demo\integration\demo_startup_notification_integration.py
)
echo.
echo ✅ 모든 목표 날짜 데모가 완료되었습니다.
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
echo 👋 목표 날짜 기능 데모를 종료합니다.
echo    자세한 사용법은 docs/DEMO_GUIDE.md를 참조하세요.
echo.
pause