#!/usr/bin/env python3
"""
통합 테스트 실행기 - 목표 날짜 기능 전체 통합 테스트

이 스크립트는 목표 날짜 기능의 모든 통합 테스트를 실행합니다:
- 전체 워크플로우 통합 테스트
- GUI 상호작용 테스트
- 데이터 워크플로우 테스트
"""

import sys
import os
import unittest
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 통합 테스트 모듈들 임포트
from test.test_integration_comprehensive_due_date import TestIntegrationComprehensiveDueDate
from test.test_gui_interaction_due_date import TestGUIInteractionDueDate
from test.test_data_workflow_integration import TestDataWorkflowIntegration


class IntegrationTestRunner:
    """통합 테스트 실행기"""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
        
    def run_all_tests(self):
        """모든 통합 테스트 실행"""
        print("=" * 80)
        print("목표 날짜 기능 통합 테스트 전체 실행")
        print("=" * 80)
        print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.start_time = time.time()
        
        # 테스트 스위트 목록
        test_suites = [
            ("전체 워크플로우 통합 테스트", TestIntegrationComprehensiveDueDate),
            ("GUI 상호작용 테스트", TestGUIInteractionDueDate),
            ("데이터 워크플로우 테스트", TestDataWorkflowIntegration)
        ]
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        
        # 각 테스트 스위트 실행
        for suite_name, test_class in test_suites:
            print(f"\n{'='*60}")
            print(f"실행 중: {suite_name}")
            print(f"{'='*60}")
            
            suite_start = time.time()
            
            # 테스트 스위트 생성 및 실행
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
            result = runner.run(suite)
            
            suite_time = time.time() - suite_start
            
            # 결과 저장
            self.results[suite_name] = {
                'tests': result.testsRun,
                'failures': len(result.failures),
                'errors': len(result.errors),
                'time': suite_time,
                'success': len(result.failures) == 0 and len(result.errors) == 0
            }
            
            # 누적 통계
            total_tests += result.testsRun
            total_failures += len(result.failures)
            total_errors += len(result.errors)
            
            # 스위트 결과 출력
            print(f"\n{suite_name} 결과:")
            print(f"  - 실행된 테스트: {result.testsRun}")
            print(f"  - 실패: {len(result.failures)}")
            print(f"  - 오류: {len(result.errors)}")
            print(f"  - 실행 시간: {suite_time:.2f}초")
            print(f"  - 결과: {'성공' if self.results[suite_name]['success'] else '실패'}")
            
            # 실패/오류 상세 정보
            if result.failures:
                print(f"\n  실패한 테스트:")
                for test, traceback in result.failures:
                    print(f"    - {test}")
                    print(f"      {traceback.split('AssertionError:')[-1].strip()}")
            
            if result.errors:
                print(f"\n  오류가 발생한 테스트:")
                for test, traceback in result.errors:
                    print(f"    - {test}")
                    print(f"      {traceback.split('Exception:')[-1].strip()}")
        
        # 전체 결과 요약
        total_time = time.time() - self.start_time
        self.print_final_summary(total_tests, total_failures, total_errors, total_time)
        
        return total_failures == 0 and total_errors == 0
    
    def print_final_summary(self, total_tests, total_failures, total_errors, total_time):
        """최종 결과 요약 출력"""
        print("\n" + "=" * 80)
        print("통합 테스트 전체 결과 요약")
        print("=" * 80)
        
        # 전체 통계
        print(f"총 실행된 테스트: {total_tests}")
        print(f"총 실패: {total_failures}")
        print(f"총 오류: {total_errors}")
        print(f"전체 실행 시간: {total_time:.2f}초")
        
        # 스위트별 결과
        print(f"\n스위트별 결과:")
        for suite_name, result in self.results.items():
            status = "✓ 성공" if result['success'] else "✗ 실패"
            print(f"  {status} {suite_name}")
            print(f"    테스트: {result['tests']}, 실패: {result['failures']}, 오류: {result['errors']}, 시간: {result['time']:.2f}초")
        
        # 성공률 계산
        success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
        print(f"\n성공률: {success_rate:.1f}%")
        
        # 최종 결과
        overall_success = total_failures == 0 and total_errors == 0
        print(f"최종 결과: {'✓ 전체 성공' if overall_success else '✗ 일부 실패'}")
        
        # 권장사항
        if not overall_success:
            print(f"\n권장사항:")
            print(f"  - 실패한 테스트를 개별적으로 실행하여 상세 오류 확인")
            print(f"  - 관련 코드 및 설정 검토")
            print(f"  - 필요시 테스트 환경 재설정")
        else:
            print(f"\n모든 통합 테스트가 성공적으로 완료되었습니다!")
            print(f"목표 날짜 기능이 올바르게 구현되었습니다.")
    
    def run_specific_suite(self, suite_name):
        """특정 테스트 스위트만 실행"""
        suite_map = {
            'comprehensive': TestIntegrationComprehensiveDueDate,
            'gui': TestGUIInteractionDueDate,
            'data': TestDataWorkflowIntegration
        }
        
        if suite_name not in suite_map:
            print(f"알 수 없는 테스트 스위트: {suite_name}")
            print(f"사용 가능한 스위트: {', '.join(suite_map.keys())}")
            return False
        
        test_class = suite_map[suite_name]
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return len(result.failures) == 0 and len(result.errors) == 0


def main():
    """메인 함수"""
    runner = IntegrationTestRunner()
    
    # 명령행 인수 처리
    if len(sys.argv) > 1:
        suite_name = sys.argv[1]
        success = runner.run_specific_suite(suite_name)
    else:
        success = runner.run_all_tests()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()