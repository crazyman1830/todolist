"""
자동 저장 및 백업 시스템 데모

Task 12: 데이터 자동 저장 및 백업 시스템 구현 데모
이 스크립트는 구현된 자동 저장 및 백업 기능을 시연합니다.
"""

import os
import time
from datetime import datetime

from services.storage_service import StorageService
from services.todo_service import TodoService
from services.file_service import FileService
from models.todo import Todo
from models.subtask import SubTask


def demo_auto_save_backup():
    """자동 저장 및 백업 시스템 데모"""
    print("=" * 60)
    print("자동 저장 및 백업 시스템 데모")
    print("=" * 60)
    
    # 데모용 임시 파일 경로
    demo_data_file = "demo/data/demo_todos.json"
    demo_folder_path = "demo/data/todo_folders"
    
    # 데모 디렉토리 생성
    os.makedirs("demo/data", exist_ok=True)
    os.makedirs(demo_folder_path, exist_ok=True)
    
    try:
        # 서비스 초기화 (자동 저장 활성화)
        print("\n1. 서비스 초기화 (자동 저장 활성화)")
        storage_service = StorageService(demo_data_file, auto_save_enabled=True)
        file_service = FileService(base_folder_path=demo_folder_path)
        todo_service = TodoService(storage_service, file_service)
        
        print(f"   - 데이터 파일: {demo_data_file}")
        print(f"   - 자동 저장: 활성화")
        print(f"   - 백업 관리: 최대 5개 유지")
        
        # 초기 데이터 상태 확인
        print("\n2. 초기 데이터 상태 확인")
        status = todo_service.get_data_status()
        print(f"   - 파일 존재: {status['file_exists']}")
        print(f"   - 데이터 유효: {status['data_valid']}")
        print(f"   - 할일 개수: {status['todo_count']}")
        print(f"   - 백업 개수: {status['backup_count']}")
        
        # 할일 추가 (자동 저장 테스트)
        print("\n3. 할일 추가 및 자동 저장 테스트")
        todo1 = todo_service.add_todo("데모 할일 1 - 자동 저장 테스트")
        print(f"   - 할일 추가: {todo1.title}")
        
        todo2 = todo_service.add_todo("데모 할일 2 - 백업 테스트")
        print(f"   - 할일 추가: {todo2.title}")
        
        # 하위 작업 추가
        subtask1 = todo_service.add_subtask(todo1.id, "하위 작업 1")
        subtask2 = todo_service.add_subtask(todo1.id, "하위 작업 2")
        print(f"   - 하위 작업 추가: {subtask1.title}, {subtask2.title}")
        
        # 백업 상태 확인
        print("\n4. 백업 생성 확인")
        backups = todo_service.list_available_backups()
        print(f"   - 자동 백업 개수: {len(backups)}")
        for i, backup in enumerate(backups[:3]):  # 최대 3개만 표시
            backup_name = os.path.basename(backup)
            print(f"     {i+1}. {backup_name}")
        
        # 수동 백업 생성
        print("\n5. 수동 백업 생성")
        backup_name = f"manual_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        success = todo_service.create_backup(backup_name)
        print(f"   - 수동 백업 생성: {'성공' if success else '실패'}")
        if success:
            print(f"   - 백업 이름: {backup_name}")
        
        # 데이터 수정 (자동 저장 트리거)
        print("\n6. 데이터 수정 및 자동 저장")
        todo_service.update_todo(todo1.id, "수정된 데모 할일 1")
        todo_service.toggle_subtask_completion(todo1.id, subtask1.id)
        print("   - 할일 제목 수정")
        print("   - 하위 작업 완료 상태 변경")
        print("   - 자동 저장 실행됨")
        
        # 진행률 확인
        updated_todo = todo_service.get_todo_by_id(todo1.id)
        completion_rate = updated_todo.get_completion_rate()
        print(f"   - 할일 진행률: {completion_rate:.1%}")
        
        # 데이터 무결성 검사
        print("\n7. 데이터 무결성 검사")
        status = todo_service.get_data_status()
        print(f"   - 무결성 문제: {len(status['integrity_issues'])}개")
        if status['integrity_issues']:
            for issue in status['integrity_issues']:
                print(f"     - {issue}")
        else:
            print("   - 데이터 무결성 양호")
        
        # 강제 저장 테스트
        print("\n8. 강제 저장 테스트")
        save_success = todo_service.force_save()
        print(f"   - 강제 저장: {'성공' if save_success else '실패'}")
        
        # 최종 상태 확인
        print("\n9. 최종 데이터 상태")
        final_status = todo_service.get_data_status()
        print(f"   - 할일 개수: {final_status['todo_count']}")
        print(f"   - 하위 작업 개수: {final_status['subtask_count']}")
        print(f"   - 파일 크기: {final_status['file_size']} bytes")
        print(f"   - 백업 개수: {final_status['backup_count']}")
        print(f"   - 마지막 수정: {final_status['last_modified']}")
        
        # 백업 복구 데모 (선택사항)
        print("\n10. 백업 복구 데모 (선택사항)")
        backups = todo_service.list_available_backups()
        if backups:
            print("    사용 가능한 백업:")
            for i, backup in enumerate(backups[:3]):
                backup_name = os.path.basename(backup)
                print(f"      {i+1}. {backup_name}")
            
            # 첫 번째 백업에서 복구 시뮬레이션 (실제로는 하지 않음)
            print("    (실제 복구는 수행하지 않음 - 데모 데이터 보존)")
        
        # 서비스 정상 종료
        print("\n11. 서비스 정상 종료")
        todo_service.shutdown()
        print("   - 자동 저장 타이머 정리")
        print("   - 대기 중인 저장 작업 완료")
        print("   - 복구 파일 정리")
        
        print("\n" + "=" * 60)
        print("자동 저장 및 백업 시스템 데모 완료!")
        print("=" * 60)
        
        # 데모 파일 정리 여부 확인
        print(f"\n데모 파일들이 생성되었습니다:")
        print(f"  - 데이터 파일: {demo_data_file}")
        print(f"  - 폴더: {demo_folder_path}")
        print("이 파일들을 유지하시겠습니까? (y/N): ", end="")
        
        try:
            keep_files = input().lower().startswith('y')
            if not keep_files:
                import shutil
                if os.path.exists("demo/data"):
                    shutil.rmtree("demo/data")
                print("데모 파일들이 삭제되었습니다.")
            else:
                print("데모 파일들이 유지되었습니다.")
        except KeyboardInterrupt:
            print("\n데모 파일들이 유지되었습니다.")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 정리 작업
        try:
            if 'todo_service' in locals():
                todo_service.shutdown()
        except:
            pass


def demo_recovery_simulation():
    """비정상 종료 복구 시뮬레이션 데모"""
    print("\n" + "=" * 60)
    print("비정상 종료 복구 시뮬레이션 데모")
    print("=" * 60)
    
    demo_data_file = "demo/data/recovery_test.json"
    os.makedirs("demo/data", exist_ok=True)
    
    try:
        # 1단계: 정상적인 데이터 생성
        print("\n1. 정상적인 데이터 생성")
        storage_service = StorageService(demo_data_file, auto_save_enabled=True)
        
        # 테스트 데이터 생성
        test_todos = [
            Todo(
                id=1,
                title="복구 테스트 할일",
                created_at=datetime.now(),
                folder_path="demo/data/todo_1",
                subtasks=[
                    SubTask(id=1, todo_id=1, title="복구 테스트 하위 작업", is_completed=False)
                ]
            )
        ]
        
        storage_service.save_todos_with_auto_save(test_todos)
        print("   - 테스트 데이터 저장 완료")
        
        # 2단계: 복구 파일 생성 시뮬레이션
        print("\n2. 비정상 종료 시뮬레이션")
        recovery_file = f"{demo_data_file}.recovery"
        
        # 복구 파일 수동 생성
        import json
        recovery_data = {
            "todos": [todo.to_dict() for todo in test_todos],
            "next_id": 2,
            "next_subtask_id": 2,
            "timestamp": time.time(),
            "original_file": demo_data_file
        }
        
        with open(recovery_file, 'w', encoding='utf-8') as f:
            json.dump(recovery_data, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"   - 복구 파일 생성: {recovery_file}")
        
        # 메인 파일 삭제 (비정상 종료 시뮬레이션)
        if os.path.exists(demo_data_file):
            os.remove(demo_data_file)
        print("   - 메인 데이터 파일 삭제 (비정상 종료 시뮬레이션)")
        
        # 3단계: 복구 테스트
        print("\n3. 복구 프로세스 실행")
        new_storage = StorageService(demo_data_file, auto_save_enabled=False)
        
        # 복구된 데이터 확인
        recovered_todos = new_storage.load_todos()
        print(f"   - 복구된 할일 개수: {len(recovered_todos)}")
        if recovered_todos:
            print(f"   - 복구된 할일: {recovered_todos[0].title}")
            print(f"   - 하위 작업 개수: {len(recovered_todos[0].subtasks)}")
        
        print("   - 복구 완료!")
        
        # 정리
        new_storage.shutdown()
        
    except Exception as e:
        print(f"\n복구 데모 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 기본 자동 저장 및 백업 데모
    demo_auto_save_backup()
    
    # 복구 시뮬레이션 데모
    demo_recovery_simulation()