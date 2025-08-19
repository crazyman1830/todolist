#!/usr/bin/env python3
"""
StorageService 목표 날짜 기능 데모

이 스크립트는 StorageService의 목표 날짜 관련 기능들을 시연합니다:
- 목표 날짜가 포함된 데이터 저장/로드
- 기존 데이터 자동 마이그레이션
- 데이터 무결성 검사 및 복구
- 백업 및 복원 기능
"""

import os
import sys
import json
import tempfile
from datetime import datetime, timedelta

# 상위 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from services.storage_service import StorageService
from models.todo import Todo
from models.subtask import SubTask


def create_sample_todos_with_due_dates():
    """목표 날짜가 포함된 샘플 할일들 생성"""
    todos = []
    
    # 1. 오늘 마감인 할일
    today_todo = Todo(
        id=1,
        title="오늘 마감 프로젝트 완료",
        created_at=datetime.now() - timedelta(days=3),
        folder_path="todo_folders/todo_1_오늘_마감_프로젝트_완료",
        due_date=datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
    )
    
    # 하위 작업 추가
    subtask1 = SubTask(
        id=1,
        todo_id=1,
        title="문서 작성",
        is_completed=True,
        created_at=datetime.now() - timedelta(days=2),
        due_date=datetime.now() - timedelta(days=1),
        completed_at=datetime.now() - timedelta(days=1)
    )
    
    subtask2 = SubTask(
        id=2,
        todo_id=1,
        title="최종 검토",
        is_completed=False,
        created_at=datetime.now() - timedelta(days=1),
        due_date=datetime.now().replace(hour=17, minute=0, second=0, microsecond=0)
    )
    
    today_todo.add_subtask(subtask1)
    today_todo.add_subtask(subtask2)
    todos.append(today_todo)
    
    # 2. 지연된 할일
    overdue_todo = Todo(
        id=2,
        title="지연된 중요 작업",
        created_at=datetime.now() - timedelta(days=7),
        folder_path="todo_folders/todo_2_지연된_중요_작업",
        due_date=datetime.now() - timedelta(days=2)
    )
    todos.append(overdue_todo)
    
    # 3. 미래 마감인 할일
    future_todo = Todo(
        id=3,
        title="다음 주 마감 계획",
        created_at=datetime.now(),
        folder_path="todo_folders/todo_3_다음_주_마감_계획",
        due_date=datetime.now() + timedelta(days=7)
    )
    todos.append(future_todo)
    
    # 4. 목표 날짜가 없는 할일
    no_due_date_todo = Todo(
        id=4,
        title="목표 날짜 없는 할일",
        created_at=datetime.now(),
        folder_path="todo_folders/todo_4_목표_날짜_없는_할일"
    )
    todos.append(no_due_date_todo)
    
    return todos


def create_legacy_data_file(file_path):
    """목표 날짜 필드가 없는 기존 데이터 파일 생성"""
    legacy_data = {
        "todos": [
            {
                "id": 1,
                "title": "기존 할일 1",
                "created_at": "2025-01-08T10:30:00",
                "folder_path": "todo_folders/todo_1_기존_할일_1",
                "subtasks": [
                    {
                        "id": 1,
                        "todo_id": 1,
                        "title": "기존 하위 작업",
                        "is_completed": False,
                        "created_at": "2025-01-08T10:35:00"
                    }
                ],
                "is_expanded": True
            },
            {
                "id": 2,
                "title": "기존 할일 2",
                "created_at": "2025-01-08T11:00:00",
                "folder_path": "todo_folders/todo_2_기존_할일_2",
                "subtasks": [],
                "is_expanded": True
            }
        ],
        "next_id": 3,
        "next_subtask_id": 2
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(legacy_data, f, ensure_ascii=False, indent=2)


def demo_basic_save_load():
    """기본 저장/로드 기능 데모"""
    print("=" * 60)
    print("1. 기본 저장/로드 기능 데모")
    print("=" * 60)
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        # StorageService 생성
        storage = StorageService(temp_file.name, auto_save_enabled=False)
        
        # 샘플 데이터 생성
        todos = create_sample_todos_with_due_dates()
        
        print(f"생성된 할일 수: {len(todos)}")
        for todo in todos:
            due_text = todo.get_time_remaining_text() if todo.due_date else "목표 날짜 없음"
            print(f"  - {todo.title}: {due_text}")
        
        # 데이터 저장
        print("\n데이터 저장 중...")
        success = storage.save_todos(todos)
        print(f"저장 결과: {'성공' if success else '실패'}")
        
        # 데이터 로드
        print("\n데이터 로드 중...")
        loaded_todos = storage.load_todos()
        print(f"로드된 할일 수: {len(loaded_todos)}")
        
        # 목표 날짜 검증
        print("\n목표 날짜 검증:")
        validation_result = storage.validate_due_date_fields(loaded_todos)
        print(f"  - 유효성: {'통과' if validation_result['valid'] else '실패'}")
        print(f"  - 목표 날짜가 있는 할일: {validation_result['statistics']['todos_with_due_date']}")
        print(f"  - 지연된 할일: {validation_result['statistics']['overdue_todos']}")
        
        if validation_result['warnings']:
            print("  - 경고:")
            for warning in validation_result['warnings']:
                print(f"    * {warning}")
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)


def demo_legacy_migration():
    """기존 데이터 마이그레이션 데모"""
    print("\n" + "=" * 60)
    print("2. 기존 데이터 마이그레이션 데모")
    print("=" * 60)
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        # 기존 데이터 파일 생성
        print("기존 형식의 데이터 파일 생성...")
        create_legacy_data_file(temp_file.name)
        
        # 파일 내용 확인
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        print("원본 데이터 구조:")
        print(f"  - 할일 수: {len(original_data['todos'])}")
        print(f"  - 첫 번째 할일에 due_date 필드: {'due_date' in original_data['todos'][0]}")
        print(f"  - data_version 필드: {'data_version' in original_data}")
        
        # StorageService로 로드 (자동 마이그레이션)
        print("\nStorageService로 데이터 로드 (자동 마이그레이션)...")
        storage = StorageService(temp_file.name, auto_save_enabled=False)
        todos = storage.load_todos()
        
        print(f"마이그레이션 후 할일 수: {len(todos)}")
        
        # 마이그레이션된 파일 내용 확인
        with open(temp_file.name, 'r', encoding='utf-8') as f:
            migrated_data = json.load(f)
        
        print("\n마이그레이션된 데이터 구조:")
        print(f"  - data_version: {migrated_data.get('data_version', '없음')}")
        print(f"  - settings 필드: {'settings' in migrated_data}")
        print(f"  - 첫 번째 할일에 due_date 필드: {'due_date' in migrated_data['todos'][0]}")
        print(f"  - 첫 번째 할일의 due_date 값: {migrated_data['todos'][0]['due_date']}")
        
        # 하위 작업도 확인
        if migrated_data['todos'][0]['subtasks']:
            subtask = migrated_data['todos'][0]['subtasks'][0]
            print(f"  - 첫 번째 하위작업에 due_date 필드: {'due_date' in subtask}")
            print(f"  - 첫 번째 하위작업의 due_date 값: {subtask['due_date']}")
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)
        # 마이그레이션 백업 파일도 삭제
        migration_backup = f"{temp_file.name}.migration_backup"
        if os.path.exists(migration_backup):
            os.remove(migration_backup)


def demo_data_integrity():
    """데이터 무결성 검사 및 복구 데모"""
    print("\n" + "=" * 60)
    print("3. 데이터 무결성 검사 및 복구 데모")
    print("=" * 60)
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        # 손상된 데이터 생성
        corrupted_data = {
            "todos": [
                {
                    "id": 1,
                    "title": "정상 할일",
                    "created_at": "2025-01-08T10:30:00",
                    "folder_path": "todo_folders/todo_1",
                    "subtasks": [],
                    "is_expanded": True,
                    "due_date": "2025-01-15T18:00:00",  # 문자열 (datetime이어야 함)
                    "completed_at": None
                },
                {
                    "id": 2,
                    "title": "손상된 할일",
                    "created_at": "2025-01-08T11:00:00",
                    "folder_path": "todo_folders/todo_2",
                    "subtasks": [
                        {
                            "id": 1,
                            "todo_id": 2,
                            "title": "손상된 하위작업",
                            "is_completed": True,
                            "created_at": "2025-01-08T11:05:00",
                            "due_date": "invalid_date",  # 잘못된 날짜 형식
                            "completed_at": "2025-01-08T12:00:00"
                        }
                    ],
                    "is_expanded": True,
                    "due_date": 12345,  # 숫자 (datetime이어야 함)
                    "completed_at": "not_a_date"  # 잘못된 형식
                }
            ],
            "next_id": 3,
            "next_subtask_id": 2
        }
        
        # 손상된 데이터 파일 생성
        with open(temp_file.name, 'w', encoding='utf-8') as f:
            json.dump(corrupted_data, f, ensure_ascii=False, indent=2)
        
        print("손상된 데이터 파일 생성 완료")
        print("  - 할일 1: due_date가 문자열")
        print("  - 할일 2: due_date가 숫자, completed_at이 잘못된 형식")
        print("  - 하위작업 1: due_date가 잘못된 형식")
        
        # StorageService로 로드 (자동 복구)
        print("\nStorageService로 데이터 로드 (자동 복구)...")
        storage = StorageService(temp_file.name, auto_save_enabled=False)
        todos = storage.load_todos()
        
        print(f"복구 후 할일 수: {len(todos)}")
        
        # 복구 결과 확인
        print("\n복구 결과:")
        for todo in todos:
            print(f"  할일 {todo.id}: {todo.title}")
            print(f"    - due_date: {todo.due_date} ({type(todo.due_date).__name__})")
            print(f"    - completed_at: {todo.completed_at} ({type(todo.completed_at).__name__})")
            
            for subtask in todo.subtasks:
                print(f"    하위작업 {subtask.id}: {subtask.title}")
                print(f"      - due_date: {subtask.due_date} ({type(subtask.due_date).__name__})")
                print(f"      - completed_at: {subtask.completed_at} ({type(subtask.completed_at).__name__})")
        
        # 유효성 검사
        validation_result = storage.validate_due_date_fields(todos)
        print(f"\n복구 후 유효성 검사: {'통과' if validation_result['valid'] else '실패'}")
        
        if validation_result['issues']:
            print("남은 문제:")
            for issue in validation_result['issues']:
                print(f"  - {issue}")
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)


def demo_backup_restore():
    """백업 및 복원 기능 데모"""
    print("\n" + "=" * 60)
    print("4. 백업 및 복원 기능 데모")
    print("=" * 60)
    
    # 임시 디렉토리 생성
    temp_dir = tempfile.mkdtemp()
    temp_file = os.path.join(temp_dir, 'todos.json')
    export_file = os.path.join(temp_dir, 'export.json')
    
    try:
        # StorageService 생성
        storage = StorageService(temp_file, auto_save_enabled=False)
        
        # 샘플 데이터 생성 및 저장
        todos = create_sample_todos_with_due_dates()
        storage.save_todos(todos)
        
        print(f"초기 데이터 저장 완료: {len(todos)}개 할일")
        
        # 데이터 내보내기
        print("\n데이터 내보내기...")
        export_success = storage.export_data_with_due_dates(export_file, todos)
        print(f"내보내기 결과: {'성공' if export_success else '실패'}")
        
        if export_success:
            # 내보낸 파일 크기 확인
            file_size = os.path.getsize(export_file)
            print(f"내보낸 파일 크기: {file_size} bytes")
            
            # 내보낸 파일 구조 확인
            with open(export_file, 'r', encoding='utf-8') as f:
                export_data = json.load(f)
            
            print("내보낸 데이터 구조:")
            print(f"  - 버전: {export_data['export_info']['version']}")
            print(f"  - 내보낸 날짜: {export_data['export_info']['export_date']}")
            print(f"  - 총 할일 수: {export_data['export_info']['total_todos']}")
            print(f"  - 총 하위작업 수: {export_data['export_info']['total_subtasks']}")
        
        # 원본 파일 삭제 (복원 테스트를 위해)
        os.remove(temp_file)
        print(f"\n원본 파일 삭제: {temp_file}")
        
        # 데이터 가져오기 (복원)
        print("데이터 가져오기 (복원)...")
        imported_todos = storage.import_data_with_due_dates(export_file)
        print(f"가져온 할일 수: {len(imported_todos)}")
        
        # 복원된 데이터 검증
        print("\n복원된 데이터 검증:")
        for todo in imported_todos:
            due_text = todo.get_time_remaining_text() if todo.due_date else "목표 날짜 없음"
            print(f"  - {todo.title}: {due_text}")
        
        # 백업 목록 확인
        print("\n백업 파일 목록:")
        backup_files = storage.list_backups()
        for backup_file in backup_files:
            file_size = os.path.getsize(backup_file)
            mod_time = datetime.fromtimestamp(os.path.getmtime(backup_file))
            print(f"  - {os.path.basename(backup_file)}: {file_size} bytes, {mod_time}")
        
    finally:
        # 임시 디렉토리 삭제
        import shutil
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def demo_data_statistics():
    """데이터 통계 및 상태 정보 데모"""
    print("\n" + "=" * 60)
    print("5. 데이터 통계 및 상태 정보 데모")
    print("=" * 60)
    
    # 임시 파일 생성
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    temp_file.close()
    
    try:
        # StorageService 생성
        storage = StorageService(temp_file.name, auto_save_enabled=False)
        
        # 샘플 데이터 생성 및 저장
        todos = create_sample_todos_with_due_dates()
        storage.save_todos(todos)
        
        # 데이터 무결성 상태 확인
        print("데이터 무결성 상태:")
        integrity_status = storage.get_data_integrity_status()
        
        print(f"  - 파일 존재: {integrity_status['file_exists']}")
        print(f"  - 파일 크기: {integrity_status['file_size']} bytes")
        print(f"  - 마지막 수정: {integrity_status['last_modified']}")
        print(f"  - 백업 파일 수: {integrity_status['backup_count']}")
        print(f"  - 데이터 유효성: {integrity_status['data_valid']}")
        print(f"  - 총 할일 수: {integrity_status['todo_count']}")
        print(f"  - 총 하위작업 수: {integrity_status['subtask_count']}")
        
        if integrity_status['integrity_issues']:
            print("  - 무결성 문제:")
            for issue in integrity_status['integrity_issues']:
                print(f"    * {issue}")
        else:
            print("  - 무결성 문제: 없음")
        
        # 목표 날짜 필드 유효성 검사
        print("\n목표 날짜 필드 통계:")
        validation_result = storage.validate_due_date_fields(todos)
        stats = validation_result['statistics']
        
        print(f"  - 총 할일 수: {stats['total_todos']}")
        print(f"  - 목표 날짜가 있는 할일: {stats['todos_with_due_date']}")
        print(f"  - 지연된 할일: {stats['overdue_todos']}")
        print(f"  - 총 하위작업 수: {stats['total_subtasks']}")
        print(f"  - 목표 날짜가 있는 하위작업: {stats['subtasks_with_due_date']}")
        print(f"  - 지연된 하위작업: {stats['overdue_subtasks']}")
        
        if validation_result['warnings']:
            print("  - 경고:")
            for warning in validation_result['warnings']:
                print(f"    * {warning}")
        
        # 긴급도별 분류
        print("\n긴급도별 할일 분류:")
        urgency_counts = {'overdue': 0, 'urgent': 0, 'warning': 0, 'normal': 0}
        
        for todo in todos:
            urgency = todo.get_urgency_level()
            urgency_counts[urgency] += 1
        
        for urgency, count in urgency_counts.items():
            urgency_names = {
                'overdue': '지연됨',
                'urgent': '긴급 (24시간 이내)',
                'warning': '주의 (3일 이내)',
                'normal': '일반'
            }
            print(f"  - {urgency_names[urgency]}: {count}개")
        
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file.name):
            os.remove(temp_file.name)


def main():
    """메인 함수"""
    print("StorageService 목표 날짜 기능 데모")
    print("=" * 60)
    print("이 데모는 StorageService의 목표 날짜 관련 기능들을 시연합니다.")
    print("Requirements 1.3, 1.4: 데이터 무결성 검사 및 백업/복원 기능")
    
    try:
        # 각 데모 실행
        demo_basic_save_load()
        demo_legacy_migration()
        demo_data_integrity()
        demo_backup_restore()
        demo_data_statistics()
        
        print("\n" + "=" * 60)
        print("모든 데모가 성공적으로 완료되었습니다!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n데모 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()