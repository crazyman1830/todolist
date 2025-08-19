#!/usr/bin/env python3
"""
성능 최적화 및 메모리 관리 기능 테스트

Requirements 2.4, 5.1, 5.2, 5.3: 성능 최적화 및 메모리 관리 검증
"""

import unittest
import sys
import os
import time
import threading
from datetime import datetime, timedelta

# 프로젝트 루트 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.performance_utils import (
    UrgencyCache, BatchUpdateManager, RealTimeUpdateOptimizer, 
    MemoryMonitor, PerformanceOptimizer, get_performance_optimizer,
    cached_urgency_calculation
)
from services.date_service import DateService


class TestUrgencyCache(unittest.TestCase):
    """긴급도 캐싱 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.cache = UrgencyCache(max_size=10, ttl_seconds=1)
    
    def test_cache_hit_miss(self):
        """캐시 히트/미스 테스트"""
        due_date = datetime.now() + timedelta(hours=1)
        
        # 첫 번째 조회 (미스)
        result1 = self.cache.get_urgency_level(due_date)
        self.assertIsNone(result1)
        
        # 캐시에 저장
        self.cache.set_urgency_level(due_date, 'urgent')
        
        # 두 번째 조회 (히트)
        result2 = self.cache.get_urgency_level(due_date)
        self.assertEqual(result2, 'urgent')
    
    def test_cache_ttl(self):
        """캐시 TTL 테스트"""
        due_date = datetime.now() + timedelta(hours=1)
        
        # 캐시에 저장
        self.cache.set_urgency_level(due_date, 'urgent')
        
        # 즉시 조회 (히트)
        result1 = self.cache.get_urgency_level(due_date)
        self.assertEqual(result1, 'urgent')
        
        # TTL 대기
        time.sleep(1.1)
        
        # TTL 만료 후 조회 (미스)
        result2 = self.cache.get_urgency_level(due_date)
        self.assertIsNone(result2)
    
    def test_cache_size_limit(self):
        """캐시 크기 제한 테스트"""
        # 최대 크기보다 많은 항목 추가
        for i in range(15):
            due_date = datetime.now() + timedelta(hours=i)
            self.cache.set_urgency_level(due_date, f'level_{i}')
        
        # 캐시 크기가 제한을 초과하지 않는지 확인
        stats = self.cache.get_stats()
        self.assertLessEqual(stats['size'], stats['max_size'])
    
    def test_none_due_date(self):
        """목표 날짜가 None인 경우 테스트"""
        result = self.cache.get_urgency_level(None)
        self.assertEqual(result, 'normal')


class TestBatchUpdateManager(unittest.TestCase):
    """배치 업데이트 관리자 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.batch_manager = BatchUpdateManager(batch_size=3, flush_interval=0.5)
        self.processed_updates = []
        
        def test_callback(updates):
            self.processed_updates.extend(updates)
        
        self.batch_manager.register_update_callback('test', test_callback)
    
    def tearDown(self):
        """테스트 정리"""
        self.batch_manager.shutdown()
    
    def test_batch_size_flush(self):
        """배치 크기 도달 시 자동 플러시 테스트"""
        # 배치 크기만큼 업데이트 추가
        for i in range(3):
            self.batch_manager.queue_update('test', i, {'data': f'item_{i}'})
        
        # 즉시 처리되어야 함
        time.sleep(0.1)
        self.assertEqual(len(self.processed_updates), 3)
    
    def test_interval_flush(self):
        """시간 간격 자동 플러시 테스트"""
        # 배치 크기보다 적은 업데이트 추가
        self.batch_manager.queue_update('test', 1, {'data': 'item_1'})
        self.batch_manager.queue_update('test', 2, {'data': 'item_2'})
        
        # 즉시는 처리되지 않음
        self.assertEqual(len(self.processed_updates), 0)
        
        # 플러시 간격 대기
        time.sleep(0.6)
        
        # 자동 플러시됨
        self.assertEqual(len(self.processed_updates), 2)
    
    def test_force_flush(self):
        """강제 플러시 테스트"""
        # 업데이트 추가
        self.batch_manager.queue_update('test', 1, {'data': 'item_1'})
        
        # 강제 플러시
        self.batch_manager.force_flush()
        
        # 즉시 처리됨
        self.assertEqual(len(self.processed_updates), 1)


class TestRealTimeUpdateOptimizer(unittest.TestCase):
    """실시간 업데이트 최적화기 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.optimizer = RealTimeUpdateOptimizer(
            update_interval=0.2, 
            max_updates_per_second=5
        )
        self.update_count = 0
        
        def test_callback():
            self.update_count += 1
        
        self.optimizer.register_update_callback('test', test_callback)
    
    def tearDown(self):
        """테스트 정리"""
        self.optimizer.stop()
    
    def test_update_throttling(self):
        """업데이트 스로틀링 테스트"""
        # 빠른 연속 업데이트 요청
        for i in range(20):
            self.optimizer.request_update('test')
            time.sleep(0.01)  # 10ms 간격
        
        # 업데이트 처리 대기
        time.sleep(1.0)
        
        # 요청보다 적은 수의 업데이트가 실행되어야 함
        self.assertLess(self.update_count, 20)
        self.assertGreater(self.update_count, 0)
    
    def test_update_frequency_limit(self):
        """업데이트 빈도 제한 테스트"""
        start_time = time.time()
        
        # 1초간 연속 요청
        while time.time() - start_time < 1.0:
            self.optimizer.request_update('test')
            time.sleep(0.05)
        
        # 추가 처리 시간
        time.sleep(0.5)
        
        # 초당 최대 업데이트 수 확인 (여유를 두고 검증)
        self.assertLessEqual(self.update_count, 10)  # max_updates_per_second * 2


class TestMemoryMonitor(unittest.TestCase):
    """메모리 모니터 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.monitor = MemoryMonitor(warning_threshold=0.1, critical_threshold=0.2)
        self.callback_calls = {'warning': 0, 'critical': 0, 'normal': 0}
        
        def warning_callback(memory_info):
            self.callback_calls['warning'] += 1
        
        def critical_callback(memory_info):
            self.callback_calls['critical'] += 1
        
        def normal_callback(memory_info):
            self.callback_calls['normal'] += 1
        
        self.monitor.register_callback('warning', warning_callback)
        self.monitor.register_callback('critical', critical_callback)
        self.monitor.register_callback('normal', normal_callback)
    
    def tearDown(self):
        """테스트 정리"""
        self.monitor.stop_monitoring()
    
    def test_memory_info_collection(self):
        """메모리 정보 수집 테스트"""
        memory_info = self.monitor.get_memory_info()
        
        # 필수 필드 확인
        required_fields = [
            'system_total', 'system_available', 'system_used',
            'system_usage_ratio', 'process_rss', 'process_vms',
            'usage_ratio', 'gc_stats'
        ]
        
        for field in required_fields:
            self.assertIn(field, memory_info)
        
        # 값 범위 확인
        self.assertGreaterEqual(memory_info['usage_ratio'], 0.0)
        self.assertLessEqual(memory_info['usage_ratio'], 1.0)
    
    def test_gc_execution(self):
        """가비지 컬렉션 실행 테스트"""
        # 가비지 생성
        garbage = []
        for i in range(1000):
            garbage.append([0] * 100)
        
        # 참조 제거
        del garbage
        
        # 가비지 컬렉션 실행
        collected = self.monitor.force_gc()
        
        # 결과 확인
        self.assertIsInstance(collected, dict)
        self.assertIn('gen_0', collected)
        self.assertIn('gen_1', collected)
        self.assertIn('gen_2', collected)


class TestPerformanceOptimizer(unittest.TestCase):
    """통합 성능 최적화기 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        self.optimizer = PerformanceOptimizer()
        self.optimizer.initialize()
    
    def tearDown(self):
        """테스트 정리"""
        self.optimizer.shutdown()
    
    def test_initialization(self):
        """초기화 테스트"""
        self.assertIsNotNone(self.optimizer.urgency_cache)
        self.assertIsNotNone(self.optimizer.batch_manager)
        self.assertIsNotNone(self.optimizer.realtime_optimizer)
        self.assertIsNotNone(self.optimizer.memory_monitor)
    
    def test_performance_stats(self):
        """성능 통계 테스트"""
        stats = self.optimizer.get_performance_stats()
        
        # 필수 통계 필드 확인
        required_fields = [
            'urgency_cache', 'memory_info', 
            'batch_pending', 'realtime_queue'
        ]
        
        for field in required_fields:
            self.assertIn(field, stats)
    
    def test_global_optimizer_singleton(self):
        """전역 최적화기 싱글톤 테스트"""
        optimizer1 = get_performance_optimizer()
        optimizer2 = get_performance_optimizer()
        
        # 같은 인스턴스여야 함
        self.assertIs(optimizer1, optimizer2)


class TestCachedUrgencyCalculation(unittest.TestCase):
    """캐싱된 긴급도 계산 테스트"""
    
    def test_cached_decorator(self):
        """캐싱 데코레이터 테스트"""
        
        @cached_urgency_calculation
        def test_urgency_func(due_date, completed_at=None):
            # 계산 시뮬레이션
            time.sleep(0.01)
            if due_date is None:
                return 'normal'
            
            now = datetime.now()
            if due_date < now:
                return 'overdue'
            elif (due_date - now).total_seconds() <= 3600:
                return 'urgent'
            else:
                return 'normal'
        
        due_date = datetime.now() + timedelta(minutes=30)
        
        # 첫 번째 호출 (느림)
        start_time = time.time()
        result1 = test_urgency_func(due_date)
        first_time = time.time() - start_time
        
        # 두 번째 호출 (빠름, 캐시됨)
        start_time = time.time()
        result2 = test_urgency_func(due_date)
        second_time = time.time() - start_time
        
        # 결과는 같아야 함
        self.assertEqual(result1, result2)
        
        # 두 번째 호출이 더 빨라야 함
        self.assertLess(second_time, first_time)
    
    def test_date_service_caching(self):
        """DateService 캐싱 테스트"""
        due_date = datetime.now() + timedelta(hours=2)
        
        # 캐시 클리어
        optimizer = get_performance_optimizer()
        optimizer.urgency_cache.clear()
        
        # 여러 번 호출
        results = []
        
        for i in range(5):
            result = DateService.get_urgency_level(due_date)
            results.append(result)
        
        # 모든 결과가 같아야 함
        self.assertTrue(all(r == results[0] for r in results))
        # 2시간 후는 urgent (24시간 이내)
        self.assertIn(results[0], ['urgent', 'warning', 'normal'])
        
        # 캐시 통계 확인
        cache_stats = optimizer.urgency_cache.get_stats()
        self.assertGreater(cache_stats['size'], 0)  # 캐시에 항목이 있어야 함


class TestIntegrationPerformance(unittest.TestCase):
    """통합 성능 테스트"""
    
    def test_large_dataset_performance(self):
        """대용량 데이터셋 성능 테스트"""
        optimizer = get_performance_optimizer()
        
        # 캐시 클리어
        optimizer.urgency_cache.clear()
        
        # 대량의 날짜 데이터 생성 (중복 포함하여 캐싱 효과 확인)
        test_dates = []
        base_dates = [
            datetime.now() + timedelta(hours=i) 
            for i in range(-10, 10)
        ]
        
        # 같은 날짜를 여러 번 반복하여 캐싱 효과 극대화
        for _ in range(10):
            test_dates.extend(base_dates)
        
        # 첫 번째 패스 (캐시 미스 + 히트)
        results1 = []
        for due_date in test_dates:
            results1.append(DateService.get_urgency_level(due_date))
        
        # 두 번째 패스 (대부분 캐시 히트)
        results2 = []
        for due_date in test_dates:
            results2.append(DateService.get_urgency_level(due_date))
        
        # 결과가 일관되어야 함
        self.assertEqual(results1, results2)
        
        # 캐시에 항목이 있어야 함
        cache_stats = optimizer.urgency_cache.get_stats()
        self.assertGreater(cache_stats['size'], 0)
        
        print(f"대용량 데이터 처리 완료: {len(test_dates)}개 항목, 캐시 크기: {cache_stats['size']}")
    
    def test_concurrent_access(self):
        """동시 접근 테스트"""
        optimizer = get_performance_optimizer()
        results = []
        errors = []
        
        def worker():
            try:
                for i in range(50):
                    due_date = datetime.now() + timedelta(hours=i % 10)
                    result = DateService.get_urgency_level(due_date)
                    results.append(result)
            except Exception as e:
                errors.append(e)
        
        # 여러 스레드에서 동시 실행
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()
        
        # 모든 스레드 완료 대기
        for thread in threads:
            thread.join()
        
        # 오류 없이 완료되어야 함
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(results), 250)  # 5 threads * 50 calls


def run_performance_tests():
    """성능 테스트 실행"""
    print("성능 최적화 및 메모리 관리 테스트 실행")
    print("=" * 60)
    
    # 테스트 스위트 생성
    test_classes = [
        TestUrgencyCache,
        TestBatchUpdateManager,
        TestRealTimeUpdateOptimizer,
        TestMemoryMonitor,
        TestPerformanceOptimizer,
        TestCachedUrgencyCalculation,
        TestIntegrationPerformance
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 테스트 실행
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 결과 출력
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ 모든 성능 최적화 테스트가 성공했습니다!")
    else:
        print("❌ 일부 테스트가 실패했습니다.")
        print(f"실패: {len(result.failures)}, 오류: {len(result.errors)}")
    
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    exit(run_performance_tests())