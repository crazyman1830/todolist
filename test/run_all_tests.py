#!/usr/bin/env python3
"""
모든 테스트를 실행하는 스크립트

통합 테스트 및 오류 처리 강화 검증을 위한 전체 테스트 실행
"""

import unittest
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def run_all_tests():
    """모든 테스트를 실행합니다."""
    
    # 현재 디렉토리를 test 디렉토리로 변경
    test_dir = os.path.dirname(os.path.abspath(__file__))
    original_dir = os.getcwd()
    os.chdir(test_dir)
    
    try:
        # 테스트 파일 목록
        test_files = [
            'test_validators.py',
            'test_storage_service.py', 
            'test_file_service.py',
            'test_subtask.py',
            'test_todo.py',
            'test_todo_service.py',
            'test_todo_service_subtasks.py',
            'test_menu.py',
            'test_main.py',
            'test_main_integration.py',
            'test_menu_integration.py',
            'test_integration_comprehensive.py',
            'test_user_experience.py'
        ]
        
        print("="*60)
        print("           할일 관리 프로그램 전체 테스트 실행")
        print("="*60)
        
        total_tests = 0
        total_failures = 0
        total_errors = 0
        total_skipped = 0
        
        for test_file in test_files:
            if not os.path.exists(test_file):
                print(f"⚠️  테스트 파일을 찾을 수 없습니다: {test_file}")
                continue
                
            print(f"\n📋 실행 중: {test_file}")
            print("-" * 40)
            
            # 테스트 로더 생성
            loader = unittest.TestLoader()
            
            try:
                # 테스트 모듈 로드
                module_name = test_file[:-3]  # .py 제거
                suite = loader.loadTestsFromName(module_name)
                
                # 테스트 실행
                runner = unittest.TextTestRunner(verbosity=1, stream=sys.stdout)
                result = runner.run(suite)
                
                # 결과 집계
                total_tests += result.testsRun
                total_failures += len(result.failures)
                total_errors += len(result.errors)
                total_skipped += len(result.skipped)
                
                # 개별 결과 출력
                if result.wasSuccessful():
                    print(f"✅ {test_file}: 성공 ({result.testsRun}개 테스트)")
                else:
                    print(f"❌ {test_file}: 실패 ({len(result.failures)}개 실패, {len(result.errors)}개 오류)")
                    
            except Exception as e:
                print(f"❌ {test_file}: 로드 실패 - {e}")
                total_errors += 1
        
        # 전체 결과 요약
        print("\n" + "="*60)
        print("                    테스트 결과 요약")
        print("="*60)
        print(f"총 테스트 수: {total_tests}")
        print(f"성공: {total_tests - total_failures - total_errors}")
        print(f"실패: {total_failures}")
        print(f"오류: {total_errors}")
        print(f"건너뜀: {total_skipped}")
        
        if total_failures == 0 and total_errors == 0:
            print("\n🎉 모든 테스트가 성공적으로 통과했습니다!")
            return True
        else:
            print(f"\n⚠️  {total_failures + total_errors}개의 테스트가 실패했습니다.")
            return False
    
    finally:
        # 원래 디렉토리로 복원
        os.chdir(original_dir)

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)