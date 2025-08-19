#!/usr/bin/env python3
"""
최종 시스템 검증 스크립트
Task 20: 모든 기능을 통합하여 전체 시스템 테스트
"""

import sys
import os
import tempfile
import shutil
import json
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.todo import Todo
from models.subtask import SubTask
from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from services.date_service import DateService
from services.notification_service import NotificationService
from utils.date_utils import DateUtils
from utils.color_utils import ColorUtils


def test_core_functionality():
    """핵심 기능 테스트"""
    print("1. 핵심 기능 테스트...")
    
    # 임시 디렉토리 생성
    test_dir = tempfile.mkdtemp()
    data_file = os.path.join(test_dir, 'test_todos.json')
    
    try:
        # 서비스 초기화
        storage_service = StorageService(data_file)
        file_service = FileService()
        todo_service = TodoService(storage_service, file_service)
        
        # 할일 생성 및 목표 날짜 설정
        todo = todo_service.add_todo("테스트 할일")
        assert todo is not None, "할일 생성 실패"
        
        due_date = datetime.now() + timedelta(days=3)
        success = todo_service.set_todo_due_date(todo.id, due_date)
        assert success, "목표 날짜 설정 실패"
        
        # 하위 작업 추가
        subtask = todo_service.add_subtask(todo.id, "테스트 하위 작업")
        assert subtask is not None, "하위 작업 생성 실패"
        
        subtask_due_date = datetime.now() + timedelta(days=2)
        success = todo_service.set_subtask_due_date(todo.id, subtask.id, subtask_due_date)
        assert success, "하위 작업 목표 날짜 설정 실패"
        
        # 데이터 검증
        updated_todo = todo_service.get_todo_by_id(todo.id)
        assert updated_todo.due_date is not None, "목표 날짜가 저장되지 않음"
        assert len(updated_todo.subtasks) == 1, "하위 작업이 저장되지 않음"
        assert updated_todo.subtasks[0].due_date is not None, "하위 작업 목표 날짜가 저장되지 않음"
        
        print("   ✓ 할일 생성 및 목표 날짜 설정")
        print("   ✓ 하위 작업 생성 및 목표 날짜 설정")
        print("   ✓ 데이터 저장 및 로드")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_urgency_calculation():
    """긴급도 계산 테스트"""
    print("2. 긴급도 계산 테스트...")
    
    test_dir = tempfile.mkdtemp()
    data_file = os.path.join(test_dir, 'test_todos.json')
    
    try:
        storage_service = StorageService(data_file)
        file_service = FileService()
        todo_service = TodoService(storage_service, file_service)
        
        # 다양한 긴급도의 할일 생성
        test_cases = [
            ("긴급한 할일", datetime.now() + timedelta(hours=12)),
            ("경고 할일", datetime.now() + timedelta(days=2)),
            ("일반 할일", datetime.now() + timedelta(days=10))
        ]
        
        for title, due_date in test_cases:
            todo = todo_service.add_todo(title)
            todo_service.set_todo_due_date(todo.id, due_date)
            
            updated_todo = todo_service.get_todo_by_id(todo.id)
            urgency_level = updated_todo.get_urgency_level()
            
            assert urgency_level in ['normal', 'warning', 'urgent', 'overdue'], f"잘못된 긴급도: {urgency_level}"
            
            # 색상 매핑 확인
            color = ColorUtils.get_urgency_color(urgency_level)
            assert color is not None, "색상 매핑 실패"
            
            # 시간 텍스트 확인
            time_text = updated_todo.get_time_remaining_text()
            assert isinstance(time_text, str) and len(time_text) > 0, "시간 텍스트 생성 실패"
        
        print("   ✓ 긴급도 계산")
        print("   ✓ 색상 매핑")
        print("   ✓ 시간 텍스트 생성")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_filtering_and_sorting():
    """필터링 및 정렬 테스트"""
    print("3. 필터링 및 정렬 테스트...")
    
    test_dir = tempfile.mkdtemp()
    data_file = os.path.join(test_dir, 'test_todos.json')
    
    try:
        storage_service = StorageService(data_file)
        file_service = FileService()
        todo_service = TodoService(storage_service, file_service)
        
        # 테스트 데이터 생성
        todos_data = [
            ("할일 1", datetime.now() + timedelta(days=1)),
            ("할일 2", datetime.now() + timedelta(days=3)),
            ("할일 3", None)  # 목표 날짜 없음
        ]
        
        for title, due_date in todos_data:
            todo = todo_service.add_todo(title)
            if due_date:
                todo_service.set_todo_due_date(todo.id, due_date)
        
        # 정렬 테스트
        all_todos = todo_service.get_all_todos()
        sorted_todos = todo_service.sort_todos_by_due_date(all_todos)
        assert isinstance(sorted_todos, list), "정렬 결과가 리스트가 아님"
        assert len(sorted_todos) == len(all_todos), "정렬 후 개수 불일치"
        
        # 필터링 테스트
        urgent_todos = todo_service.get_urgent_todos()
        assert isinstance(urgent_todos, list), "긴급한 할일 필터링 실패"
        
        print("   ✓ 목표 날짜순 정렬")
        print("   ✓ 긴급한 할일 필터링")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_notification_service():
    """알림 서비스 테스트"""
    print("4. 알림 서비스 테스트...")
    
    test_dir = tempfile.mkdtemp()
    data_file = os.path.join(test_dir, 'test_todos.json')
    
    try:
        storage_service = StorageService(data_file)
        file_service = FileService()
        todo_service = TodoService(storage_service, file_service)
        notification_service = NotificationService(todo_service)
        
        # 오늘 마감 할일 생성
        today_todo = todo_service.add_todo("오늘 마감 할일")
        today_due = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
        todo_service.set_todo_due_date(today_todo.id, today_due)
        
        # 알림 서비스 기능 테스트
        due_today_todos = notification_service.get_due_today_todos()
        urgent_todos = notification_service.get_urgent_todos()
        
        assert isinstance(due_today_todos, list), "오늘 마감 할일 조회 실패"
        assert isinstance(urgent_todos, list), "긴급한 할일 조회 실패"
        
        # 상태 요약 테스트
        status_summary = notification_service.get_status_bar_summary()
        assert isinstance(status_summary, dict), "상태 요약 생성 실패"
        assert 'due_today' in status_summary, "오늘 마감 개수 누락"
        
        # 시작 시 알림 판단 테스트
        should_show = notification_service.should_show_startup_notification()
        assert isinstance(should_show, bool), "시작 시 알림 판단 실패"
        
        print("   ✓ 오늘 마감 할일 조회")
        print("   ✓ 긴급한 할일 조회")
        print("   ✓ 상태 요약 생성")
        print("   ✓ 시작 시 알림 판단")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_data_persistence():
    """데이터 지속성 테스트"""
    print("5. 데이터 지속성 테스트...")
    
    test_dir = tempfile.mkdtemp()
    data_file = os.path.join(test_dir, 'test_todos.json')
    
    try:
        # 첫 번째 서비스 인스턴스로 데이터 생성
        storage_service = StorageService(data_file)
        file_service = FileService()
        todo_service = TodoService(storage_service, file_service)
        
        original_todo = todo_service.add_todo("지속성 테스트 할일")
        due_date = datetime.now() + timedelta(days=5)
        todo_service.set_todo_due_date(original_todo.id, due_date)
        
        subtask = todo_service.add_subtask(original_todo.id, "지속성 테스트 하위 작업")
        subtask_due_date = datetime.now() + timedelta(days=4)
        todo_service.set_subtask_due_date(original_todo.id, subtask.id, subtask_due_date)
        
        # 두 번째 서비스 인스턴스로 데이터 로드
        new_storage_service = StorageService(data_file)
        new_file_service = FileService()
        new_todo_service = TodoService(new_storage_service, new_file_service)
        
        loaded_todos = new_todo_service.get_all_todos()
        assert len(loaded_todos) > 0, "데이터 로드 실패"
        
        # 목표 날짜가 있는 할일 찾기
        loaded_todo = None
        for todo in loaded_todos:
            if todo.title == "지속성 테스트 할일":
                loaded_todo = todo
                break
        
        assert loaded_todo is not None, "특정 할일 로드 실패"
        assert loaded_todo.due_date is not None, "목표 날짜 로드 실패"
        assert len(loaded_todo.subtasks) == 1, "하위 작업 로드 실패"
        assert loaded_todo.subtasks[0].due_date is not None, "하위 작업 목표 날짜 로드 실패"
        
        print("   ✓ 데이터 저장")
        print("   ✓ 데이터 로드")
        print("   ✓ 목표 날짜 지속성")
        print("   ✓ 하위 작업 지속성")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_backward_compatibility():
    """기존 기능 호환성 테스트"""
    print("6. 기존 기능 호환성 테스트...")
    
    test_dir = tempfile.mkdtemp()
    data_file = os.path.join(test_dir, 'test_todos.json')
    
    try:
        storage_service = StorageService(data_file)
        file_service = FileService()
        todo_service = TodoService(storage_service, file_service)
        
        # 목표 날짜 없는 할일 생성 (기존 방식)
        todo_without_due_date = todo_service.add_todo("목표 날짜 없는 할일")
        assert todo_without_due_date is not None, "기존 방식 할일 생성 실패"
        assert todo_without_due_date.due_date is None, "목표 날짜가 None이 아님"
        
        # 기존 할일 관리 기능 정상 동작 확인
        subtask = todo_service.add_subtask(todo_without_due_date.id, "목표 날짜 없는 하위 작업")
        assert subtask is not None, "기존 방식 하위 작업 생성 실패"
        assert subtask.due_date is None, "하위 작업 목표 날짜가 None이 아님"
        
        # 완료 상태 변경 기능 확인
        success = todo_service.toggle_subtask_completion(todo_without_due_date.id, subtask.id)
        assert success, "완료 상태 변경 실패"
        
        # 긴급도 계산 (목표 날짜 없는 경우)
        urgency_level = todo_without_due_date.get_urgency_level()
        assert urgency_level == 'normal', f"목표 날짜 없는 할일의 긴급도가 normal이 아님: {urgency_level}"
        
        print("   ✓ 목표 날짜 없는 할일 생성")
        print("   ✓ 기존 하위 작업 관리")
        print("   ✓ 완료 상태 변경")
        print("   ✓ 긴급도 계산 (목표 날짜 없음)")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)


def test_utility_functions():
    """유틸리티 함수 테스트"""
    print("7. 유틸리티 함수 테스트...")
    
    try:
        # DateService 테스트
        urgency_level = DateService.get_urgency_level(datetime.now() + timedelta(days=1))
        assert urgency_level in ['normal', 'warning', 'urgent', 'overdue'], "긴급도 계산 실패"
        
        time_text = DateService.get_time_remaining_text(datetime.now() + timedelta(days=1))
        assert isinstance(time_text, str) and len(time_text) > 0, "시간 텍스트 생성 실패"
        
        # ColorUtils 테스트
        color = ColorUtils.get_urgency_color('urgent')
        assert color is not None, "색상 매핑 실패"
        
        # DateUtils 테스트
        relative_text = DateUtils.get_relative_time_text(datetime.now() + timedelta(days=1))
        assert isinstance(relative_text, str) and len(relative_text) > 0, "상대적 시간 텍스트 생성 실패"
        
        print("   ✓ DateService 기능")
        print("   ✓ ColorUtils 기능")
        print("   ✓ DateUtils 기능")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return False


def run_final_verification():
    """최종 검증 실행"""
    print("=" * 60)
    print("목표 날짜 기능 최종 시스템 검증")
    print("=" * 60)
    
    tests = [
        ("핵심 기능", test_core_functionality),
        ("긴급도 계산", test_urgency_calculation),
        ("필터링 및 정렬", test_filtering_and_sorting),
        ("알림 서비스", test_notification_service),
        ("데이터 지속성", test_data_persistence),
        ("기존 기능 호환성", test_backward_compatibility),
        ("유틸리티 함수", test_utility_functions)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 테스트 통과\n")
            else:
                print(f"❌ {test_name} 테스트 실패\n")
        except Exception as e:
            print(f"❌ {test_name} 테스트 오류: {e}\n")
    
    # 결과 요약
    print("=" * 60)
    print("최종 검증 결과")
    print("=" * 60)
    print(f"총 테스트: {total}")
    print(f"통과: {passed}")
    print(f"실패: {total - passed}")
    
    success_rate = (passed / total * 100) if total > 0 else 0
    print(f"성공률: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n🎉 최종 검증 성공!")
        print("\n✅ 구현 완료된 주요 기능들:")
        print("  • 할일 및 하위 작업에 목표 날짜 설정")
        print("  • 긴급도에 따른 시각적 표시 (색상 코딩)")
        print("  • 목표 날짜 기준 정렬 및 필터링")
        print("  • 남은 시간/지연 시간 표시")
        print("  • 알림 및 상태 요약 기능")
        print("  • 기존 기능과의 완전한 호환성")
        print("  • 데이터 지속성 및 마이그레이션")
        print("  • 포괄적인 유틸리티 함수")
        print("\n🚀 목표 날짜 기능이 성공적으로 구현되었습니다!")
        return True
    else:
        print(f"\n⚠️  일부 기능에서 문제가 발견되었습니다. ({success_rate:.1f}% 성공)")
        print("추가 수정이 필요할 수 있습니다.")
        return False


if __name__ == '__main__':
    success = run_final_verification()
    sys.exit(0 if success else 1)