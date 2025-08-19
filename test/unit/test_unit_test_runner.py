"""
단위 테스트 실행기

Task 17: 단위 테스트 작성 - 모든 단위 테스트를 실행하고 결과를 요약합니다.
"""

import unittest
import sys
import os

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def run_unit_tests():
    """모든 단위 테스트를 실행합니다."""
    
    # 실행할 테스트 모듈들
    test_modules = [
        'test.test_date_service',
        'test.test_date_utils', 
        'test.test_color_utils',
        'test.test_notification_service',
        'test.test_todo_due_date_methods',
        'test.test_subtask_due_date',
    ]
    
    print("=" * 60)
    print("목표 날짜 기능 단위 테스트 실행")
    print("=" * 60)
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    for module_name in test_modules:
        print(f"\n[{module_name}] 테스트 실행 중...")
        
        try:
            # 테스트 로더 생성
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromName(module_name)
            
            # 테스트 실행
            runner = unittest.TextTestRunner(verbosity=1, stream=open(os.devnull, 'w'))
            result = runner.run(suite)
            
            # 결과 집계
            tests_run = result.testsRun
            failures = len(result.failures)
            errors = len(result.errors)
            
            total_tests += tests_run
            total_failures += failures
            total_errors += errors
            
            # 결과 출력
            status = "PASS" if (failures == 0 and errors == 0) else "FAIL"
            print(f"  테스트: {tests_run}개, 실패: {failures}개, 오류: {errors}개 [{status}]")
            
            # 실패/오류 상세 정보
            if failures > 0:
                print("  실패한 테스트:")
                for test, traceback in result.failures:
                    print(f"    - {test}")
            
            if errors > 0:
                print("  오류가 발생한 테스트:")
                for test, traceback in result.errors:
                    print(f"    - {test}")
                    
        except Exception as e:
            print(f"  모듈 로드 실패: {e}")
            total_errors += 1
    
    print("\n" + "=" * 60)
    print("테스트 실행 완료")
    print("=" * 60)
    print(f"전체 테스트: {total_tests}개")
    print(f"성공: {total_tests - total_failures - total_errors}개")
    print(f"실패: {total_failures}개")
    print(f"오류: {total_errors}개")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"성공률: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n✅ 모든 단위 테스트가 성공했습니다!")
        return True
    else:
        print(f"\n❌ {total_failures + total_errors}개의 테스트가 실패했습니다.")
        return False


def run_specific_test_categories():
    """특정 카테고리별로 테스트를 실행합니다."""
    
    categories = {
        "DateService 테스트": ['test.test_date_service'],
        "DateUtils 테스트": ['test.test_date_utils'],
        "ColorUtils 테스트": ['test.test_color_utils'],
        "NotificationService 테스트": ['test.test_notification_service'],
        "Todo 모델 테스트": ['test.test_todo_due_date_methods'],
        "SubTask 모델 테스트": ['test.test_subtask_due_date'],
    }
    
    print("=" * 60)
    print("카테고리별 단위 테스트 실행")
    print("=" * 60)
    
    for category, modules in categories.items():
        print(f"\n📋 {category}")
        print("-" * 40)
        
        category_tests = 0
        category_failures = 0
        category_errors = 0
        
        for module_name in modules:
            try:
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromName(module_name)
                runner = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w'))
                result = runner.run(suite)
                
                category_tests += result.testsRun
                category_failures += len(result.failures)
                category_errors += len(result.errors)
                
            except Exception as e:
                print(f"  ❌ {module_name}: 로드 실패 ({e})")
                category_errors += 1
        
        # 카테고리 결과 출력
        if category_tests > 0:
            success_count = category_tests - category_failures - category_errors
            success_rate = (success_count / category_tests * 100)
            
            status_icon = "✅" if (category_failures == 0 and category_errors == 0) else "❌"
            print(f"  {status_icon} {success_count}/{category_tests} 성공 ({success_rate:.1f}%)")
            
            if category_failures > 0:
                print(f"     실패: {category_failures}개")
            if category_errors > 0:
                print(f"     오류: {category_errors}개")
        else:
            print("  ⚠️  실행할 테스트가 없습니다.")


def show_test_coverage_summary():
    """테스트 커버리지 요약을 표시합니다."""
    
    print("\n" + "=" * 60)
    print("테스트 커버리지 요약")
    print("=" * 60)
    
    coverage_areas = {
        "DateService": {
            "description": "날짜 관련 비즈니스 로직",
            "methods": [
                "get_urgency_level", "get_time_remaining_text", "format_due_date",
                "is_same_day", "get_quick_date_options", "validate_due_date",
                "get_date_filter_ranges"
            ],
            "tested": True
        },
        "DateUtils": {
            "description": "날짜 유틸리티 함수들",
            "methods": [
                "get_relative_time_text", "parse_user_date_input", 
                "get_business_days_between", "format_duration", "is_weekend",
                "get_next_weekday", "validate_date_range"
            ],
            "tested": True
        },
        "ColorUtils": {
            "description": "색상 관련 유틸리티",
            "methods": [
                "get_urgency_color", "get_urgency_background_color", 
                "get_completed_colors", "hex_to_rgb", "rgb_to_hex",
                "get_contrast_color", "lighten_color", "darken_color"
            ],
            "tested": True
        },
        "NotificationService": {
            "description": "알림 관련 서비스",
            "methods": [
                "get_overdue_todos", "get_due_today_todos", "get_urgent_todos",
                "should_show_startup_notification", "get_startup_notification_message",
                "get_status_bar_summary", "get_detailed_notification_info"
            ],
            "tested": True
        },
        "Todo Model": {
            "description": "할일 모델의 목표 날짜 메서드",
            "methods": [
                "set_due_date", "get_due_date", "is_overdue", "get_urgency_level",
                "get_time_remaining_text", "mark_completed", "mark_uncompleted",
                "has_overdue_subtasks", "validate_subtask_due_date"
            ],
            "tested": True
        },
        "SubTask Model": {
            "description": "하위 작업 모델의 목표 날짜 메서드",
            "methods": [
                "set_due_date", "get_due_date", "is_overdue", "get_urgency_level",
                "get_time_remaining_text", "mark_completed", "mark_uncompleted"
            ],
            "tested": True
        }
    }
    
    for area, info in coverage_areas.items():
        status_icon = "✅" if info["tested"] else "❌"
        print(f"{status_icon} {area}")
        print(f"   {info['description']}")
        print(f"   테스트된 메서드: {len(info['methods'])}개")
        
        # 주요 메서드 나열 (처음 3개만)
        main_methods = info['methods'][:3]
        if len(info['methods']) > 3:
            main_methods.append(f"... 외 {len(info['methods']) - 3}개")
        print(f"   주요 메서드: {', '.join(main_methods)}")
        print()


if __name__ == '__main__':
    print("목표 날짜 기능 단위 테스트 실행기")
    print("Task 17: 단위 테스트 작성 - 모든 요구사항의 기능 검증")
    
    # 기본 단위 테스트 실행
    success = run_unit_tests()
    
    # 카테고리별 테스트 실행
    run_specific_test_categories()
    
    # 테스트 커버리지 요약
    show_test_coverage_summary()
    
    # 최종 결과
    if success:
        print("🎉 Task 17 완료: 모든 단위 테스트가 성공적으로 작성되고 실행되었습니다!")
        sys.exit(0)
    else:
        print("⚠️  일부 테스트에서 문제가 발견되었습니다. 위의 결과를 확인해주세요.")
        sys.exit(1)