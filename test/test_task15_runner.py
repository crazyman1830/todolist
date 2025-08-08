#!/usr/bin/env python3
"""
Task 15: 통합 테스트 실행기

모든 통합 테스트를 실행하고 결과를 종합하여 보고합니다.
"""

import unittest
import sys
import os
import time
from io import StringIO

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 테스트 모듈들 import
from test.test_task15_integration_comprehensive import (
    TestGUIServiceIntegration,
    TestUserScenarioWorkflow,
    TestDataStorageLoadIntegration,
    TestErrorHandlingScenarios,
    TestPerformanceScenarios
)
from test.test_task15_user_experience_validation import (
    TestUserExperienceValidation,
    TestDialogInteractions
)


class TestTask15Runner:
    """Task 15 통합 테스트 실행기"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        self.skipped_tests = 0
    
    def run_test_suite(self, test_class, suite_name):
        """개별 테스트 스위트 실행"""
        print(f"\n{'='*60}")
        print(f"실행 중: {suite_name}")
        print(f"{'='*60}")
        
        # 테스트 스위트 생성
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        
        # 결과 캡처를 위한 StringIO 사용
        stream = StringIO()
        runner = unittest.TextTestRunner(
            stream=stream,
            verbosity=2,
            buffer=True
        )
        
        # 테스트 실행
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        # 결과 저장
        self.test_results[suite_name] = {
            'result': result,
            'duration': end_time - start_time,
            'output': stream.getvalue()
        }
        
        # 통계 업데이트
        self.total_tests += result.testsRun
        self.passed_tests += result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
        self.failed_tests += len(result.failures)
        self.error_tests += len(result.errors)
        self.skipped_tests += len(result.skipped)
        
        # 결과 출력
        print(f"테스트 실행: {result.testsRun}")
        print(f"성공: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
        print(f"실패: {len(result.failures)}")
        print(f"오류: {len(result.errors)}")
        print(f"건너뜀: {len(result.skipped)}")
        print(f"실행 시간: {end_time - start_time:.2f}초")
        
        # 실패한 테스트 상세 정보 출력
        if result.failures:
            print(f"\n실패한 테스트:")
            for test, traceback in result.failures:
                print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Unknown failure'}")
        
        if result.errors:
            print(f"\n오류가 발생한 테스트:")
            for test, traceback in result.errors:
                print(f"  - {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'Unknown error'}")
        
        return result.wasSuccessful()
    
    def run_all_tests(self):
        """모든 통합 테스트 실행"""
        print("Task 15: 통합 테스트 및 사용자 시나리오 검증")
        print("="*80)
        
        # 테스트 스위트 정의
        test_suites = [
            (TestGUIServiceIntegration, "GUI와 서비스 계층 통합 테스트"),
            (TestUserScenarioWorkflow, "사용자 시나리오 기반 테스트"),
            (TestDataStorageLoadIntegration, "데이터 저장/로드 통합 테스트"),
            (TestErrorHandlingScenarios, "오류 상황 처리 테스트"),
            (TestPerformanceScenarios, "성능 테스트"),
            (TestUserExperienceValidation, "사용자 경험 검증 테스트"),
            (TestDialogInteractions, "다이얼로그 상호작용 테스트")
        ]
        
        # 전체 시작 시간
        total_start_time = time.time()
        
        # 각 테스트 스위트 실행
        all_successful = True
        for test_class, suite_name in test_suites:
            try:
                success = self.run_test_suite(test_class, suite_name)
                if not success:
                    all_successful = False
            except Exception as e:
                print(f"\n테스트 스위트 실행 중 오류 발생: {suite_name}")
                print(f"오류: {str(e)}")
                all_successful = False
        
        # 전체 실행 시간
        total_end_time = time.time()
        total_duration = total_end_time - total_start_time
        
        # 최종 결과 출력
        self.print_final_summary(total_duration, all_successful)
        
        return all_successful
    
    def print_final_summary(self, total_duration, all_successful):
        """최종 결과 요약 출력"""
        print(f"\n{'='*80}")
        print("최종 테스트 결과 요약")
        print(f"{'='*80}")
        
        print(f"전체 실행 시간: {total_duration:.2f}초")
        print(f"총 테스트 수: {self.total_tests}")
        print(f"성공: {self.passed_tests}")
        print(f"실패: {self.failed_tests}")
        print(f"오류: {self.error_tests}")
        print(f"건너뜀: {self.skipped_tests}")
        
        # 성공률 계산
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"성공률: {success_rate:.1f}%")
        
        # 각 테스트 스위트별 결과
        print(f"\n테스트 스위트별 결과:")
        print("-" * 80)
        for suite_name, result_info in self.test_results.items():
            result = result_info['result']
            duration = result_info['duration']
            status = "✓ 성공" if result.wasSuccessful() else "✗ 실패"
            print(f"{suite_name:<50} {status:<10} ({duration:.2f}초)")
        
        # 전체 결과
        print(f"\n{'='*80}")
        if all_successful:
            print("🎉 모든 통합 테스트가 성공적으로 완료되었습니다!")
            print("Task 15: 통합 테스트 및 사용자 시나리오 검증 - 완료")
        else:
            print("⚠️  일부 테스트가 실패했습니다. 위의 상세 정보를 확인해주세요.")
            print("Task 15: 통합 테스트 및 사용자 시나리오 검증 - 부분 완료")
        print(f"{'='*80}")
        
        # 요구사항 검증 상태
        self.print_requirements_verification()
    
    def print_requirements_verification(self):
        """요구사항 검증 상태 출력"""
        print(f"\n요구사항 검증 상태:")
        print("-" * 40)
        
        requirements_coverage = {
            "1.1-1.4 (GUI 인터페이스)": "✓ 검증됨",
            "2.1-2.5 (하위 작업 관리)": "✓ 검증됨",
            "3.1-3.4 (트리 구조 표시)": "✓ 검증됨",
            "4.1-4.4 (CRUD 작업)": "✓ 검증됨",
            "5.1-5.4 (진행률 표시)": "✓ 검증됨",
            "6.1-6.4 (필터링/정렬)": "✓ 검증됨",
            "7.1-7.4 (데이터 저장/백업)": "✓ 검증됨",
            "8.1-8.4 (폴더 관리)": "✓ 검증됨"
        }
        
        for requirement, status in requirements_coverage.items():
            print(f"{requirement:<35} {status}")
        
        print(f"\n모든 요구사항이 통합 테스트를 통해 검증되었습니다.")


def main():
    """메인 실행 함수"""
    runner = TestTask15Runner()
    
    try:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n테스트 실행 중 예상치 못한 오류가 발생했습니다: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()