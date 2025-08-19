@echo off
chcp 65001 > nul
title 할일 관리 프로그램 - 성능 테스트

echo.
echo ============================================================
echo            🚀 할일 관리 프로그램 - 성능 테스트
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
echo 성능 테스트를 선택하세요:
echo.
echo   1️⃣  성능 최적화 데모
echo   2️⃣  대량 데이터 처리 테스트
echo   3️⃣  메모리 사용량 테스트
echo   4️⃣  응답 시간 벤치마크
echo   5️⃣  전체 성능 테스트 실행
echo   0️⃣  종료
echo.
echo ============================================================
set /p choice="선택 (0-5): "

if "%choice%"=="1" goto OPTIMIZATION_DEMO
if "%choice%"=="2" goto BULK_TEST
if "%choice%"=="3" goto MEMORY_TEST
if "%choice%"=="4" goto BENCHMARK_TEST
if "%choice%"=="5" goto ALL_TESTS
if "%choice%"=="0" goto EXIT
echo.
echo ❌ 잘못된 선택입니다. 다시 선택해주세요.
echo.
goto MENU

:OPTIMIZATION_DEMO
echo.
echo 🚀 성능 최적화 데모를 시작합니다...
echo    - 대량 할일 처리
echo    - 배치 업데이트
echo    - 메모리 사용량 모니터링
echo    - 캐싱 시스템
echo.
if exist "demo\performance\demo_performance_optimization.py" (
    python demo\performance\demo_performance_optimization.py
) else (
    echo ❌ 성능 최적화 데모 파일을 찾을 수 없습니다.
)
goto TEST_END

:BULK_TEST
echo.
echo 🚀 대량 데이터 처리 테스트를 시작합니다...
echo    - 1000개 할일 생성 테스트
echo    - 대량 검색 성능 테스트
echo    - 정렬 성능 테스트
echo.
if exist "test\test_performance_bulk.py" (
    python test\test_performance_bulk.py
) else (
    echo ❌ 대량 데이터 테스트 파일을 찾을 수 없습니다.
    echo    성능 최적화 데모로 대체 실행합니다...
    if exist "demo\performance\demo_performance_optimization.py" (
        python demo\performance\demo_performance_optimization.py
    )
)
goto TEST_END

:MEMORY_TEST
echo.
echo 🚀 메모리 사용량 테스트를 시작합니다...
echo    - 메모리 누수 검사
echo    - 가비지 컬렉션 테스트
echo    - 메모리 효율성 분석
echo.
if exist "test\test_memory_usage.py" (
    python test\test_memory_usage.py
) else (
    echo ❌ 메모리 테스트 파일을 찾을 수 없습니다.
    echo    성능 최적화 데모로 대체 실행합니다...
    if exist "demo\performance\demo_performance_optimization.py" (
        python demo\performance\demo_performance_optimization.py
    )
)
goto TEST_END

:BENCHMARK_TEST
echo.
echo 🚀 응답 시간 벤치마크를 시작합니다...
echo    - 할일 생성 속도 측정
echo    - 검색 응답 시간 측정
echo    - UI 렌더링 성능 측정
echo.
if exist "test\test_response_time.py" (
    python test\test_response_time.py
) else (
    echo ❌ 벤치마크 테스트 파일을 찾을 수 없습니다.
    echo    최종 시스템 검증으로 대체 실행합니다...
    if exist "test\final_system_verification.py" (
        python test\final_system_verification.py
    )
)
goto TEST_END

:ALL_TESTS
echo.
echo 🚀 전체 성능 테스트를 실행합니다...
echo.
echo [1/4] 성능 최적화 데모...
if exist "demo\performance\demo_performance_optimization.py" (
    python demo\performance\demo_performance_optimization.py
)
echo.
echo [2/4] 최종 시스템 검증...
if exist "test\final_system_verification.py" (
    python test\final_system_verification.py
)
echo.
echo [3/4] 성능 관련 단위 테스트...
python -m unittest discover test\unit -k "performance" -v 2>nul
echo.
echo [4/4] 성능 관련 통합 테스트...
python -m unittest discover test\integration -k "performance" -v 2>nul
echo.
echo ✅ 전체 성능 테스트가 완료되었습니다.
goto TEST_END

:TEST_END
echo.
echo ============================================================
echo.
set /p continue="다른 성능 테스트를 실행하시겠습니까? (y/N): "
if /i "%continue%"=="y" goto MENU
if /i "%continue%"=="yes" goto MENU

:EXIT
echo.
echo 👋 성능 테스트를 종료합니다.
echo    자세한 성능 정보는 docs/FINAL_INTEGRATION_SUMMARY.md를 참조하세요.
echo.
pause