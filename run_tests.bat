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

echo 사용 가능한 테스트 옵션:
echo   1️⃣  전체 테스트 (권장)
echo   2️⃣  단위 테스트만
echo   3️⃣  통합 테스트만
echo   4️⃣  검증 테스트만
echo   5️⃣  최종 시스템 검증
echo.
set /p test_choice="선택 (1-5, 기본값: 1): "

if "%test_choice%"=="" set test_choice=1
if "%test_choice%"=="1" goto FULL_TEST
if "%test_choice%"=="2" goto UNIT_TEST
if "%test_choice%"=="3" goto INTEGRATION_TEST
if "%test_choice%"=="4" goto VERIFICATION_TEST
if "%test_choice%"=="5" goto SYSTEM_TEST

:FULL_TEST
echo.
echo 🚀 전체 테스트를 실행합니다...
if exist "test\run_all_tests_organized.py" (
    python test\run_all_tests_organized.py
) else if exist "test\run_all_tests.py" (
    python test\run_all_tests.py
) else (
    echo ❌ 테스트 실행 파일을 찾을 수 없습니다.
)
goto TEST_END

:UNIT_TEST
echo.
echo 🧪 단위 테스트를 실행합니다...
python -m unittest discover test\unit -v
goto TEST_END

:INTEGRATION_TEST
echo.
echo 🔗 통합 테스트를 실행합니다...
python -m unittest discover test\integration -v
goto TEST_END

:VERIFICATION_TEST
echo.
echo ✅ 검증 테스트를 실행합니다...
python -m unittest discover test\verification -v
goto TEST_END

:SYSTEM_TEST
echo.
echo 🎯 최종 시스템 검증을 실행합니다...
if exist "test\final_system_verification.py" (
    python test\final_system_verification.py
) else (
    echo ❌ 시스템 검증 파일을 찾을 수 없습니다.
)
goto TEST_END

:TEST_END
echo.
echo ✅ 테스트가 완료되었습니다.
echo.

pause