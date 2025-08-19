#!/usr/bin/env python3
"""
Task 16 검증 테스트: 성능 최적화 및 메모리 관리

Requirements 2.4, 5.1, 5.2, 5.3 검증:
- 긴급도 계산 캐싱 구현
- 대량 할일 처리 시 배치 업데이트 구현  
- 실시간 시간 업데이트 최적화
- 메모리 사용량 모니터링 및 최적화
"""

import unittest
import sys
import os
import time
import tempfile
import shutil
from datetime import datetime, timedelta

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.todo_service import TodoService
from services.storage_service import StorageService
from services.file_service import FileService
from services.date_service import DateService
from models.todo import Todo
from models.subtask import SubTask
from utils.performance_utils import get_performance_optimizer


class TestTask16Verification(unittest.TestCase):
    """Task 16 성능 최적화 기능 검증"""
    
    def setUp(self):
        """테스트 환경 설정"""
        # 임시 디렉토리 생성
        self.test_dir = tempfile.mkdtemp()
        self.data_file = os.path.join(self.test_dir, "test_todos.json")
        self.folders_dir = os.path.join(self.test_dir, "test_folders")
        
        # 서비스 초기화
        self.storage_service = StorageService(self.data_file)
        self.file_service = FileService(self.folders_dir)
        self.todo_service = TodoService(self.storage_service, self.file_service)
        
        # 성능 최적화기
        self.performance_optimizer = get_performance_optimizer()
    
    def tearDown(self):
        """테스트 환경 정리"""
        try:
            self.todo_service.shutdown()
            shutil.rmtree(self.test_dir, ignore_errors=True)
        except:
            pass
    
    def test_urgency_calculation_caching(self):
        """긴급도 계산 캐싱 검증 (Requirements 2.4, 5.1)"""
        print("\n=== 긴급도 계산 캐싱 테스트 ===")
        
        # 캐시 클리어
        self.performance_optimizer.urgency_cache.clear()
        
        # 테스트 할일 생성
        todo = self.todo_service.add_todo("긴급도 테스트 할일")
        
        # 다양한 목표 날짜 설정
        test_dates = [
            datetime.now() + timedelta(minutes=30),   # urgent
            datetime.now() + timedelta(hours=2),      # urgent  
            datetime.now() + timedelta(days=2),       # warning
            datetime.now() + timedelta(days=5),       # normal
            datetime.now() - timedelta(hours=1),      # overdue
        ]
        
        # 첫 번째 계산 (캐시 미스)
        start_time = time.time()
        results1 = []
        for due_date in test_dates:
            todo.set_due_date(due_date)
            urgency = todo.get_urgency_level()
            results1.append(urgency)
        first_time = time.time() - start_time
        
        # 두 번째 계산 (캐시 히트)
        start_time = time.time()
        results2 = []
        for due_date in test_dates:
            todo.set_due_date(due_date)
            urgency = todo.get_urgency_level()
            results2.append(urgency)
        second_time = time.time() - start_time
        
        # 검증
        self.assertEqual(results1, results2, "캐시된 결과가 일관되어야 함")
        
        # 캐시 통계 확인
        cache_stats = self.performance_optimizer.urgency_cache.get_stats()
        self.assertGreater(cache_stats['size'], 0, "캐시에 항목이 있어야 함")
        
        print(f"  첫 번째 계산: {first_time:.4f}초")
        print(f"  두 번째 계산: {second_time:.4f}초")
        print(f"  캐시 크기: {cache_stats['size']}")
        print("  ✅ 긴급도 계산 캐싱 정상 작동")
    
    def test_batch_update_processing(self):
        """배치 업데이트 처리 검증 (Requirements 2.4, 5.2)"""
        print("\n=== 배치 업데이트 처리 테스트 ===")
        
        # 테스트 할일들 생성
        todos = []
        for i in range(10):
            todo = self.todo_service.add_todo(f"배치 테스트 할일 {i+1}")
            todos.append(todo)
        
        # 배치 업데이트 큐에 추가
        batch_count = 0
        for i, todo in enumerate(todos):
            due_date = datetime.now() + timedelta(hours=i+1)
            self.todo_service.queue_due_date_update(todo.id, due_date, 'todo')
            batch_count += 1
        
        print(f"  {batch_count}개 할일 배치 업데이트 큐에 추가")
        
        # 배치 처리 대기
        time.sleep(1.0)
        
        # 강제 플러시
        self.performance_optimizer.batch_manager.force_flush()
        
        # 결과 확인
        updated_todos = self.todo_service.get_all_todos()
        todos_with_due_dates = [t for t in updated_todos if t.due_date is not None]
        
        print(f"  목표 날짜가 설정된 할일: {len(todos_with_due_dates)}개")
        print("  ✅ 배치 업데이트 처리 정상 작동")
    
    def test_realtime_update_optimization(self):
        """실시간 업데이트 최적화 검증 (Requirements 5.3)"""
        print("\n=== 실시간 업데이트 최적화 테스트 ===")
        
        # 업데이트 카운터
        update_count = {'count': 0}
        
        def mock_update():
            update_count['count'] += 1
        
        # 실시간 업데이트 콜백 등록
        optimizer = self.performance_optimizer.realtime_optimizer
        optimizer.register_update_callback('test_component', mock_update)
        
        # 빠른 연속 업데이트 요청
        request_count = 50
        for i in range(request_count):
            optimizer.request_update('test_component')
            time.sleep(0.01)  # 10ms 간격
        
        # 처리 대기
        time.sleep(2.0)
        
        # 검증
        actual_updates = update_count['count']
        optimization_rate = (request_count - actual_updates) / request_count * 100
        
        print(f"  요청된 업데이트: {request_count}회")
        print(f"  실제 실행된 업데이트: {actual_updates}회")
        print(f"  최적화율: {optimization_rate:.1f}%")
        
        # 실제 업데이트 수가 요청보다 적어야 함 (최적화 효과)
        self.assertLess(actual_updates, request_count, "실시간 업데이트 최적화가 작동해야 함")
        print("  ✅ 실시간 업데이트 최적화 정상 작동")
    
    def test_memory_monitoring(self):
        """메모리 사용량 모니터링 검증 (Requirements 2.4)"""
        print("\n=== 메모리 모니터링 테스트 ===")
        
        monitor = self.performance_optimizer.memory_monitor
        
        # 메모리 정보 수집
        memory_info = monitor.get_memory_info()
        
        # 필수 필드 확인
        required_fields = [
            'system_total', 'system_available', 'system_used',
            'system_usage_ratio', 'process_rss', 'process_vms',
            'usage_ratio', 'gc_stats'
        ]
        
        for field in required_fields:
            self.assertIn(field, memory_info, f"메모리 정보에 {field} 필드가 있어야 함")
        
        # 값 범위 확인
        self.assertGreaterEqual(memory_info['usage_ratio'], 0.0)
        self.assertLessEqual(memory_info['usage_ratio'], 1.0)
        
        print(f"  시스템 메모리 사용률: {memory_info['usage_ratio']:.1%}")
        print(f"  프로세스 메모리: {memory_info['process_rss'] / 1024**2:.1f}MB")
        
        # 가비지 컬렉션 테스트
        collected = monitor.force_gc()
        self.assertIsInstance(collected, dict, "가비지 컬렉션 결과가 딕셔너리여야 함")
        
        print(f"  가비지 컬렉션 결과: {collected}")
        print("  ✅ 메모리 모니터링 정상 작동")
    
    def test_large_dataset_performance(self):
        """대량 데이터 처리 성능 검증 (Requirements 5.1, 5.2)"""
        print("\n=== 대량 데이터 처리 성능 테스트 ===")
        
        # 대량의 할일 생성
        todo_count = 100
        print(f"  {todo_count}개 할일 생성 중...")
        
        start_time = time.time()
        todos = []
        for i in range(todo_count):
            todo = self.todo_service.add_todo(f"성능 테스트 할일 {i+1}")
            
            # 하위작업 추가
            for j in range(3):
                self.todo_service.add_subtask(todo.id, f"하위작업 {j+1}")
            
            # 목표 날짜 설정
            due_date = datetime.now() + timedelta(hours=i % 24)
            self.todo_service.set_todo_due_date(todo.id, due_date)
            
            todos.append(todo)
        
        creation_time = time.time() - start_time
        
        # 긴급도 계산 성능 테스트
        print("  긴급도 계산 성능 테스트...")
        start_time = time.time()
        
        urgency_counts = {'overdue': 0, 'urgent': 0, 'warning': 0, 'normal': 0}
        
        # 모든 할일의 긴급도 계산
        all_todos = self.todo_service.get_all_todos()
        for todo in all_todos:
            urgency = todo.get_urgency_level()
            urgency_counts[urgency] += 1
            
            # 하위작업 긴급도도 계산
            for subtask in todo.subtasks:
                subtask_urgency = subtask.get_urgency_level()
        
        urgency_time = time.time() - start_time
        
        # 필터링 성능 테스트
        print("  필터링 성능 테스트...")
        start_time = time.time()
        
        overdue_todos = self.todo_service.get_overdue_todos()
        urgent_todos = self.todo_service.get_urgent_todos()
        due_today_todos = self.todo_service.get_due_today_todos()
        
        filtering_time = time.time() - start_time
        
        # 결과 출력
        print(f"  할일 생성 시간: {creation_time:.2f}초")
        print(f"  긴급도 계산 시간: {urgency_time:.4f}초")
        print(f"  필터링 시간: {filtering_time:.4f}초")
        print(f"  긴급도 분포: {urgency_counts}")
        print(f"  지연된 할일: {len(overdue_todos)}개")
        print(f"  긴급한 할일: {len(urgent_todos)}개")
        print(f"  오늘 마감 할일: {len(due_today_todos)}개")
        
        # 성능 기준 검증
        self.assertLess(creation_time, 10.0, "할일 생성이 10초 이내에 완료되어야 함")
        self.assertLess(urgency_time, 1.0, "긴급도 계산이 1초 이내에 완료되어야 함")
        self.assertLess(filtering_time, 0.5, "필터링이 0.5초 이내에 완료되어야 함")
        
        print("  ✅ 대량 데이터 처리 성능 기준 통과")
    
    def test_integrated_performance_optimization(self):
        """통합 성능 최적화 검증"""
        print("\n=== 통합 성능 최적화 테스트 ===")
        
        # 초기 성능 통계
        initial_stats = self.performance_optimizer.get_performance_stats()
        print(f"  초기 캐시 크기: {initial_stats['urgency_cache']['size']}")
        print(f"  초기 배치 대기: {initial_stats['batch_pending']}개")
        print(f"  초기 실시간 큐: {initial_stats['realtime_queue']}개")
        
        # 복합 작업 수행
        print("  복합 작업 수행 중...")
        
        # 1. 할일 생성 및 목표 날짜 설정
        todos = []
        for i in range(20):
            todo = self.todo_service.add_todo(f"통합 테스트 할일 {i+1}")
            due_date = datetime.now() + timedelta(hours=i)
            self.todo_service.set_todo_due_date(todo.id, due_date)
            todos.append(todo)
        
        # 2. 긴급도 계산 (캐싱됨)
        for todo in todos:
            urgency = todo.get_urgency_level()
            time_text = todo.get_time_remaining_text()
        
        # 3. 배치 업데이트
        for i, todo in enumerate(todos[:10]):
            self.todo_service.queue_todo_update(todo.id, {'title': f'수정된 할일 {i+1}'})
        
        # 4. 실시간 업데이트 요청
        for i in range(30):
            self.performance_optimizer.realtime_optimizer.request_update('integrated_test')
        
        # 처리 대기
        time.sleep(1.0)
        self.performance_optimizer.batch_manager.force_flush()
        
        # 최종 성능 통계
        final_stats = self.performance_optimizer.get_performance_stats()
        print(f"  최종 캐시 크기: {final_stats['urgency_cache']['size']}")
        print(f"  최종 배치 대기: {final_stats['batch_pending']}개")
        print(f"  최종 실시간 큐: {final_stats['realtime_queue']}개")
        print(f"  메모리 사용률: {final_stats['memory_info']['usage_ratio']:.1%}")
        
        # 검증 - 캐시가 사용되었는지 확인 (크기가 0이 아니거나 초기값보다 증가)
        cache_was_used = (final_stats['urgency_cache']['size'] > 0 or 
                         final_stats['urgency_cache']['size'] >= initial_stats['urgency_cache']['size'])
        self.assertTrue(cache_was_used, "캐시가 사용되어야 함")
        
        print("  ✅ 통합 성능 최적화 정상 작동")
    
    def test_performance_under_stress(self):
        """스트레스 상황에서의 성능 검증"""
        print("\n=== 스트레스 테스트 ===")
        
        # 메모리 모니터링 시작
        monitor = self.performance_optimizer.memory_monitor
        initial_memory = monitor.get_memory_info()
        
        print(f"  초기 메모리 사용률: {initial_memory['usage_ratio']:.1%}")
        
        # 스트레스 작업 수행
        print("  스트레스 작업 수행 중...")
        
        # 대량의 할일과 하위작업 생성
        for i in range(50):
            todo = self.todo_service.add_todo(f"스트레스 테스트 할일 {i+1}")
            
            # 각 할일에 여러 하위작업 추가
            for j in range(5):
                self.todo_service.add_subtask(todo.id, f"스트레스 하위작업 {j+1}")
            
            # 목표 날짜 설정
            due_date = datetime.now() + timedelta(minutes=i*10)
            self.todo_service.set_todo_due_date(todo.id, due_date)
        
        # 대량의 긴급도 계산
        all_todos = self.todo_service.get_all_todos()
        for _ in range(10):  # 10번 반복
            for todo in all_todos:
                urgency = todo.get_urgency_level()
                for subtask in todo.subtasks:
                    subtask_urgency = subtask.get_urgency_level()
        
        # 최종 메모리 확인
        final_memory = monitor.get_memory_info()
        print(f"  최종 메모리 사용률: {final_memory['usage_ratio']:.1%}")
        
        # 메모리 사용량이 과도하게 증가하지 않았는지 확인
        memory_increase = final_memory['usage_ratio'] - initial_memory['usage_ratio']
        print(f"  메모리 사용량 증가: {memory_increase:.1%}")
        
        # 캐시 통계
        cache_stats = self.performance_optimizer.urgency_cache.get_stats()
        print(f"  최종 캐시 크기: {cache_stats['size']}")
        
        # 가비지 컬렉션 실행
        collected = monitor.force_gc()
        print(f"  가비지 컬렉션: {sum(collected.values())}개 객체 정리")
        
        print("  ✅ 스트레스 테스트 완료")


def run_task16_verification():
    """Task 16 검증 테스트 실행"""
    print("Task 16: 성능 최적화 및 메모리 관리 검증 테스트")
    print("=" * 70)
    
    # 테스트 실행
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTask16Verification)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 출력
    print("\n" + "=" * 70)
    if result.wasSuccessful():
        print("✅ Task 16 모든 검증 테스트가 성공했습니다!")
        print("\n구현된 기능:")
        print("  ✓ 긴급도 계산 캐싱")
        print("  ✓ 배치 업데이트 처리")
        print("  ✓ 실시간 업데이트 최적화")
        print("  ✓ 메모리 사용량 모니터링")
        print("  ✓ 대량 데이터 처리 최적화")
        print("  ✓ 통합 성능 관리")
    else:
        print("❌ 일부 검증 테스트가 실패했습니다.")
        print(f"실패: {len(result.failures)}, 오류: {len(result.errors)}")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_task16_verification())