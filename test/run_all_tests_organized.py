#!/usr/bin/env python3
"""
통합 테스트 실행기 - 정리된 테스트 구조

테스트 카테고리:
- unit: 단위 테스트 (모델, 서비스, 유틸리티)
- integration: 통합 테스트 (GUI, 서비스 통합)
- verification: 작업 검증 테스트 (Task 검증)
"""

import sys
import os
import unittest
import time
from io import StringIO

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def discover_and_run_tests(test_dir, pattern="test_*.py"):
    """지정된 디렉토리에서 테스트를 발견하고 실행"""
    loader = unittest.TestLoader()
    suite = loader.discover(test_dir, pattern=pattern)
    
    # 테스트 실행
    stream = StringIO()
    runner = unittest.TextTestRunner(stream=stream, verbosity=2)
    result = runner.run(suite)
    
    return result, stream.getvalue()


def run_unit_tests():
    """단위 테스트 실행"""
    print("=" * 60)
    print("단위 테스트 (Unit Tests) 실행")
    print("=" * 60)
    
    test_dir = os.path.join(os.path.dirname(__file__), "unit")
    result, output = discover_and_run_tests(test_dir)
    
    print(output)
    print(f"단위 테스트 결과: {result.testsRun}개 실행, {len(result.failures)}개 실패, {len(result.errors)}개 오류")
    
    return result.wasSuccessful()


def run_integration_tests():
    """통합 테스트 실행"""
    print("\n" + "=" * 60)
    print("통합 테스트 (Integration Tests) 실행")
    print("=" * 60)
    
    test_dir = os.path.join(os.path.dirname(__file__), "integration")
    result, output = discover_and_run_tests(test_dir)
    
    print(output)
    print(f"통합 테스트 결과: {result.testsRun}개 실행, {len(result.failures)}개 실패, {len(result.errors)}개 오류")
    
    return result.wasSuccessful()


def run_verification_tests():
    """검증 테스트 실행"""
    print("\n" + "=" * 60)
    print("검증 테스트 (Verification Tests) 실행")
    print("=" * 60)
    
    test_dir = os.path.join(os.path.dirname(__file__), "verification")
    result, output = discover_and_run_tests(test_dir)
    
    print(output)
    print(f"검증 테스트 결과: {result.testsRun}개 실행, {len(result.failures)}개 실패, {len(result.errors)}개 오류")
    
    return result.wasSuccessful()


def run_remaining_tests():
    """남은 테스트들 실행"""
    print("\n" + "=" * 60)
    print("기타 테스트 실행")
    print("=" * 60)
    
    test_dir = os.path.dirname(__file__)
    # 하위 디렉토리는 제외하고 루트 레벨 테스트만 실행
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    for file in os.listdir(test_dir):
        if file.startswith("test_") and file.endswith(".py"):
            module_name = file[:-3]  # .py 제거
            try:
                module = __import__(f"test.{module_name}", fromlist=[module_name])
                suite.addTests(loader.loadTestsFromModule(module))
            except ImportError as e:
                print(f"모듈 {module_name} 로드 실패: {e}")
    
    if suite.countTestCases() > 0:
        stream = StringIO()
        runner = unittest.TextTestRunner(stream=stream, verbosity=2)
        result = runner.run(suite)
        
        print(stream.getvalue())
        print(f"기타 테스트 결과: {result.testsRun}개 실행, {len(result.failures)}개 실패, {len(result.errors)}개 오류")
        
        return result.wasSuccessful()
    else:
        print("실행할 기타 테스트가 없습니다.")
        return True


def main():
    """메인 테스트 실행 함수"""
    print("Todo List 애플리케이션 - 전체 테스트 실행")
    print("=" * 80)
    
    start_time = time.time()
    
    # 각 카테고리별 테스트 실행
    results = []
    
    try:
        results.append(("단위 테스트", run_unit_tests()))
    except Exception as e:
        print(f"단위 테스트 실행 중 오류: {e}")
        results.append(("단위 테스트", False))
    
    try:
        results.append(("통합 테스트", run_integration_tests()))
    except Exception as e:
        print(f"통합 테스트 실행 중 오류: {e}")
        results.append(("통합 테스트", False))
    
    try:
        results.append(("검증 테스트", run_verification_tests()))
    except Exception as e:
        print(f"검증 테스트 실행 중 오류: {e}")
        results.append(("검증 테스트", False))
    
    try:
        results.append(("기타 테스트", run_remaining_tests()))
    except Exception as e:
        print(f"기타 테스트 실행 중 오류: {e}")
        results.append(("기타 테스트", False))
    
    # 전체 결과 요약
    end_time = time.time()
    execution_time = end_time - start_time
    
    print("\n" + "=" * 80)
    print("전체 테스트 결과 요약")
    print("=" * 80)
    
    all_passed = True
    for test_category, passed in results:
        status = "✅ 통과" if passed else "❌ 실패"
        print(f"{test_category}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n실행 시간: {execution_time:.2f}초")
    
    if all_passed:
        print("\n🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return 0
    else:
        print("\n❌ 일부 테스트가 실패했습니다. 로그를 확인해주세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())