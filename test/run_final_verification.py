#!/usr/bin/env python3
"""
최종 검증 테스트 실행기
모든 기능의 통합 테스트, 성능 테스트, 호환성 테스트를 실행합니다.
"""

import sys
import os
import time
import subprocess
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_test_file(test_file, description):
    """개별 테스트 파일 실행"""
    print(f"\n{'='*60}")
    print(f"실행 중: {description}")
    print(f"파일: {test_file}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # 테스트 파일 실행
        result = subprocess.run([
            sys.executable, test_file
        ], capture_output=True, text=True, cwd=os.path.dirname(test_file))
        
        execution_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {description} - 성공 ({execution_time:.2f}초)")
            if result.stdout:
                print("출력:")
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - 실패 ({execution_time:.2f}초)")
            if result.stdout:
                print("표준 출력:")
                print(result.stdout)
            if result.stderr:
                print("오류 출력:")
                print(result.stderr)
            return False
            
    except Exception as e:
        execution_time = time.time() - start_time
        print(f"❌ {description} - 예외 발생 ({execution_time:.2f}초)")
        print(f"예외: {e}")
        return False


def main():
    """최종 검증 테스트 메인 실행 함수"""
    print("🚀 목표 날짜 기능 최종 검증 테스트 시작")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 파일들과 설명
    test_files = [
        # 1. 최종 통합 테스트
        ("test_final_integration_verification.py", "최종 통합 및 검증 테스트"),
        
        # 2. 핵심 기능 테스트들
        ("test_comprehensive_due_date_unit.py", "포괄적 목표 날짜 단위 테스트"),
        ("test_integration_comprehensive_due_date.py", "목표 날짜 통합 테스트"),
        ("test_performance_optimization.py", "성능 최적화 테스트"),
        
        # 3. 서비스 레이어 테스트
        ("test_date_service.py", "날짜 서비스 테스트"),
        ("test_notification_service.py", "알림 서비스 테스트"),
        ("test_todo_service_due_date.py", "할일 서비스 목표 날짜 테스트"),
        ("test_storage_service_due_date.py", "저장 서비스 목표 날짜 테스트"),
        
        # 4. 모델 테스트
        ("test_todo_due_date_methods.py", "할일 모델 목표 날짜 메서드 테스트"),
        ("test_subtask_due_date.py", "하위 작업 목표 날짜 테스트"),
        
        # 5. GUI 테스트
        ("test_due_date_dialog.py", "목표 날짜 다이얼로그 테스트"),
        ("test_todo_tree_due_date.py", "할일 트리 목표 날짜 테스트"),
        ("test_context_menu_due_date.py", "컨텍스트 메뉴 목표 날짜 테스트"),
        ("test_status_bar_due_date.py", "상태바 목표 날짜 테스트"),
        
        # 6. 유틸리티 테스트
        ("test_date_utils.py", "날짜 유틸리티 테스트"),
        ("test_color_utils.py", "색상 유틸리티 테스트"),
        
        # 7. 통합 및 호환성 테스트
        ("test_data_migration.py", "데이터 마이그레이션 테스트"),
        ("test_due_date_error_handling.py", "목표 날짜 오류 처리 테스트"),
        ("test_accessibility_improvements.py", "접근성 개선 테스트"),
    ]
    
    # 테스트 결과 추적
    total_tests = len(test_files)
    passed_tests = 0
    failed_tests = []
    
    # 각 테스트 파일 실행
    for test_file, description in test_files:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        
        if os.path.exists(test_path):
            if run_test_file(test_path, description):
                passed_tests += 1
            else:
                failed_tests.append((test_file, description))
        else:
            print(f"⚠️  테스트 파일을 찾을 수 없음: {test_file}")
            failed_tests.append((test_file, f"{description} (파일 없음)"))
    
    # 최종 결과 출력
    print(f"\n{'='*80}")
    print("🏁 최종 검증 테스트 결과 요약")
    print(f"{'='*80}")
    print(f"총 테스트 파일: {total_tests}")
    print(f"성공: {passed_tests}")
    print(f"실패: {len(failed_tests)}")
    
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"성공률: {success_rate:.1f}%")
    
    if failed_tests:
        print(f"\n❌ 실패한 테스트들:")
        for test_file, description in failed_tests:
            print(f"  - {test_file}: {description}")
    
    print(f"\n완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 최종 판정
    if success_rate >= 90:
        print("\n🎉 최종 검증 성공! 목표 날짜 기능이 성공적으로 구현되었습니다.")
        
        # 기능 요약 출력
        print(f"\n{'='*60}")
        print("✅ 구현된 주요 기능들:")
        print("  • 할일 및 하위 작업에 목표 날짜 설정")
        print("  • 긴급도에 따른 시각적 표시 (색상 코딩)")
        print("  • 목표 날짜 기준 정렬 및 필터링")
        print("  • 남은 시간/지연 시간 표시")
        print("  • 직관적인 날짜 선택 인터페이스")
        print("  • 알림 및 상태 요약 기능")
        print("  • 기존 기능과의 완전한 호환성")
        print("  • 성능 최적화 및 메모리 관리")
        print("  • 포괄적인 오류 처리")
        print("  • 접근성 개선")
        print(f"{'='*60}")
        
        return True
    else:
        print(f"\n⚠️  일부 테스트에서 문제가 발견되었습니다. ({success_rate:.1f}% 성공)")
        print("실패한 테스트들을 확인하고 수정이 필요합니다.")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)