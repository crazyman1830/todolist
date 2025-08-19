"""
성능 최적화 및 메모리 관리 유틸리티

긴급도 계산 캐싱, 배치 업데이트, 실시간 업데이트 최적화 등의 기능을 제공합니다.
"""

import time
import threading
import weakref
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Set
from functools import wraps, lru_cache
import gc
import os

# psutil은 선택적 의존성
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


class UrgencyCache:
    """긴급도 계산 결과 캐싱 클래스"""
    
    def __init__(self, max_size: int = 1000, ttl_seconds: int = 60):
        """
        긴급도 캐시 초기화
        
        Args:
            max_size: 최대 캐시 크기
            ttl_seconds: 캐시 유효 시간 (초)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._access_times: Dict[str, float] = {}
        self._lock = threading.RLock()
    
    def _generate_key(self, due_date: Optional[datetime], completed_at: Optional[datetime] = None) -> str:
        """캐시 키 생성"""
        if due_date is None:
            return "no_due_date"
        
        # 분 단위로 반올림하여 캐시 효율성 증대
        rounded_due = due_date.replace(second=0, microsecond=0)
        key = f"due_{rounded_due.isoformat()}"
        
        if completed_at is not None:
            key += f"_completed_{completed_at.isoformat()}"
        
        return key
    
    def get_urgency_level(self, due_date: Optional[datetime], completed_at: Optional[datetime] = None) -> Optional[str]:
        """캐시에서 긴급도 레벨 조회"""
        if due_date is None:
            return 'normal'
        
        key = self._generate_key(due_date, completed_at)
        current_time = time.time()
        
        with self._lock:
            if key in self._cache:
                cache_entry = self._cache[key]
                
                # TTL 체크
                if current_time - cache_entry['timestamp'] < self.ttl_seconds:
                    self._access_times[key] = current_time
                    return cache_entry['urgency_level']
                else:
                    # 만료된 캐시 제거
                    del self._cache[key]
                    if key in self._access_times:
                        del self._access_times[key]
        
        return None
    
    def set_urgency_level(self, due_date: Optional[datetime], urgency_level: str, 
                         completed_at: Optional[datetime] = None) -> None:
        """긴급도 레벨을 캐시에 저장"""
        if due_date is None:
            return
        
        key = self._generate_key(due_date, completed_at)
        current_time = time.time()
        
        with self._lock:
            # 캐시 크기 제한 확인
            if len(self._cache) >= self.max_size:
                self._evict_oldest()
            
            self._cache[key] = {
                'urgency_level': urgency_level,
                'timestamp': current_time
            }
            self._access_times[key] = current_time
    
    def _evict_oldest(self) -> None:
        """가장 오래된 캐시 항목 제거 (LRU)"""
        if not self._access_times:
            return
        
        oldest_key = min(self._access_times.keys(), key=lambda k: self._access_times[k])
        
        if oldest_key in self._cache:
            del self._cache[oldest_key]
        if oldest_key in self._access_times:
            del self._access_times[oldest_key]
    
    def clear(self) -> None:
        """캐시 전체 삭제"""
        with self._lock:
            self._cache.clear()
            self._access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """캐시 통계 정보 반환"""
        with self._lock:
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'ttl_seconds': self.ttl_seconds,
                'hit_rate': getattr(self, '_hit_count', 0) / max(getattr(self, '_total_requests', 1), 1)
            }


class BatchUpdateManager:
    """배치 업데이트 관리 클래스"""
    
    def __init__(self, batch_size: int = 50, flush_interval: float = 0.5):
        """
        배치 업데이트 매니저 초기화
        
        Args:
            batch_size: 배치 크기
            flush_interval: 자동 플러시 간격 (초)
        """
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self._pending_updates: List[Dict[str, Any]] = []
        self._update_callbacks: Dict[str, Callable] = {}
        self._lock = threading.RLock()
        self._last_flush = time.time()
        self._timer: Optional[threading.Timer] = None
    
    def register_update_callback(self, update_type: str, callback: Callable) -> None:
        """업데이트 콜백 등록"""
        self._update_callbacks[update_type] = callback
    
    def queue_update(self, update_type: str, item_id: Any, data: Dict[str, Any]) -> None:
        """업데이트를 큐에 추가"""
        with self._lock:
            self._pending_updates.append({
                'type': update_type,
                'item_id': item_id,
                'data': data,
                'timestamp': time.time()
            })
            
            # 배치 크기 도달 시 즉시 플러시
            if len(self._pending_updates) >= self.batch_size:
                self._flush_updates()
            else:
                # 타이머 설정
                self._schedule_flush()
    
    def _schedule_flush(self) -> None:
        """자동 플러시 스케줄링"""
        if self._timer is not None:
            self._timer.cancel()
        
        self._timer = threading.Timer(self.flush_interval, self._flush_updates)
        self._timer.start()
    
    def _flush_updates(self) -> None:
        """대기 중인 업데이트들을 배치로 처리"""
        with self._lock:
            if not self._pending_updates:
                return
            
            # 업데이트 타입별로 그룹화
            updates_by_type: Dict[str, List[Dict[str, Any]]] = {}
            
            for update in self._pending_updates:
                update_type = update['type']
                if update_type not in updates_by_type:
                    updates_by_type[update_type] = []
                updates_by_type[update_type].append(update)
            
            # 각 타입별로 배치 처리
            for update_type, updates in updates_by_type.items():
                if update_type in self._update_callbacks:
                    try:
                        self._update_callbacks[update_type](updates)
                    except Exception as e:
                        print(f"배치 업데이트 실패 ({update_type}): {e}")
            
            # 처리된 업데이트 제거
            self._pending_updates.clear()
            self._last_flush = time.time()
            
            # 타이머 정리
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
    
    def force_flush(self) -> None:
        """강제 플러시"""
        self._flush_updates()
    
    def shutdown(self) -> None:
        """배치 매니저 종료"""
        self.force_flush()
        if self._timer is not None:
            self._timer.cancel()


class RealTimeUpdateOptimizer:
    """실시간 업데이트 최적화 클래스"""
    
    def __init__(self, update_interval: float = 1.0, max_updates_per_second: int = 30):
        """
        실시간 업데이트 최적화기 초기화
        
        Args:
            update_interval: 업데이트 간격 (초)
            max_updates_per_second: 초당 최대 업데이트 수
        """
        self.update_interval = update_interval
        self.max_updates_per_second = max_updates_per_second
        self._update_queue: Set[str] = set()
        self._update_callbacks: Dict[str, Callable] = {}
        self._last_update_times: Dict[str, float] = {}
        self._lock = threading.RLock()
        self._timer: Optional[threading.Timer] = None
        self._is_running = False
    
    def register_update_callback(self, component_id: str, callback: Callable) -> None:
        """업데이트 콜백 등록"""
        self._update_callbacks[component_id] = callback
    
    def request_update(self, component_id: str) -> None:
        """업데이트 요청"""
        current_time = time.time()
        
        with self._lock:
            # 업데이트 빈도 제한 확인
            last_update = self._last_update_times.get(component_id, 0)
            if current_time - last_update < (1.0 / self.max_updates_per_second):
                return
            
            self._update_queue.add(component_id)
            
            if not self._is_running:
                self._start_update_cycle()
    
    def _start_update_cycle(self) -> None:
        """업데이트 사이클 시작"""
        self._is_running = True
        self._schedule_next_update()
    
    def _schedule_next_update(self) -> None:
        """다음 업데이트 스케줄링"""
        if self._timer is not None:
            self._timer.cancel()
        
        self._timer = threading.Timer(self.update_interval, self._process_updates)
        self._timer.start()
    
    def _process_updates(self) -> None:
        """대기 중인 업데이트들 처리"""
        with self._lock:
            if not self._update_queue:
                self._is_running = False
                return
            
            current_time = time.time()
            components_to_update = list(self._update_queue)
            self._update_queue.clear()
            
            # 각 컴포넌트 업데이트
            for component_id in components_to_update:
                if component_id in self._update_callbacks:
                    try:
                        self._update_callbacks[component_id]()
                        self._last_update_times[component_id] = current_time
                    except Exception as e:
                        print(f"실시간 업데이트 실패 ({component_id}): {e}")
            
            # 다음 사이클 스케줄링
            if self._update_queue:
                self._schedule_next_update()
            else:
                self._is_running = False
    
    def stop(self) -> None:
        """업데이트 최적화기 중지"""
        with self._lock:
            self._is_running = False
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
            self._update_queue.clear()


class MemoryMonitor:
    """메모리 사용량 모니터링 클래스"""
    
    def __init__(self, warning_threshold: float = 0.8, critical_threshold: float = 0.9):
        """
        메모리 모니터 초기화
        
        Args:
            warning_threshold: 경고 임계값 (0.0 ~ 1.0)
            critical_threshold: 위험 임계값 (0.0 ~ 1.0)
        """
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self._callbacks: Dict[str, Callable] = {}
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        메모리 이벤트 콜백 등록
        
        Args:
            event_type: 'warning', 'critical', 'normal'
            callback: 콜백 함수
        """
        self._callbacks[event_type] = callback
    
    def start_monitoring(self, interval: float = 5.0) -> None:
        """메모리 모니터링 시작"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._stop_event.clear()
        self._monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(interval,),
            daemon=True
        )
        self._monitor_thread.start()
    
    def stop_monitoring(self) -> None:
        """메모리 모니터링 중지"""
        if not self._monitoring:
            return
        
        self._monitoring = False
        self._stop_event.set()
        
        if self._monitor_thread and self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
    
    def _monitor_loop(self, interval: float) -> None:
        """메모리 모니터링 루프"""
        last_status = 'normal'
        
        while not self._stop_event.wait(interval):
            try:
                memory_info = self.get_memory_info()
                usage_ratio = memory_info['usage_ratio']
                
                # 상태 결정
                if usage_ratio >= self.critical_threshold:
                    current_status = 'critical'
                elif usage_ratio >= self.warning_threshold:
                    current_status = 'warning'
                else:
                    current_status = 'normal'
                
                # 상태 변경 시 콜백 호출
                if current_status != last_status and current_status in self._callbacks:
                    try:
                        self._callbacks[current_status](memory_info)
                    except Exception as e:
                        print(f"메모리 모니터 콜백 실패: {e}")
                
                last_status = current_status
                
            except Exception as e:
                print(f"메모리 모니터링 오류: {e}")
    
    def get_memory_info(self) -> Dict[str, Any]:
        """현재 메모리 사용량 정보 반환"""
        try:
            if HAS_PSUTIL:
                # psutil을 사용한 정확한 메모리 정보
                system_memory = psutil.virtual_memory()
                process = psutil.Process(os.getpid())
                process_memory = process.memory_info()
                
                return {
                    'system_total': system_memory.total,
                    'system_available': system_memory.available,
                    'system_used': system_memory.used,
                    'system_usage_ratio': system_memory.percent / 100.0,
                    'process_rss': process_memory.rss,
                    'process_vms': process_memory.vms,
                    'usage_ratio': system_memory.percent / 100.0,
                    'gc_stats': self._get_gc_stats()
                }
            else:
                # psutil이 없는 경우 기본 정보만 제공
                process_memory = 0
                try:
                    import resource
                    # 프로세스 메모리 사용량 (근사치)
                    process_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
                    # Linux에서는 KB, Windows/macOS에서는 bytes
                    if os.name == 'posix':
                        process_memory *= 1024  # KB to bytes
                except ImportError:
                    # resource 모듈이 없는 경우 (일부 Windows 환경)
                    process_memory = 50 * 1024 * 1024  # 50MB 가정
                except:
                    process_memory = 0
                
                return {
                    'system_total': 8 * 1024**3,  # 8GB 가정
                    'system_available': 4 * 1024**3,  # 4GB 가정
                    'system_used': 4 * 1024**3,  # 4GB 가정
                    'system_usage_ratio': 0.5,  # 50% 가정
                    'process_rss': process_memory,
                    'process_vms': process_memory,
                    'usage_ratio': 0.5,  # 50% 가정
                    'gc_stats': self._get_gc_stats()
                }
                
        except Exception as e:
            print(f"메모리 정보 수집 실패: {e}")
            return {
                'system_total': 0,
                'system_available': 0,
                'system_used': 0,
                'system_usage_ratio': 0.0,
                'process_rss': 0,
                'process_vms': 0,
                'usage_ratio': 0.0,
                'gc_stats': {}
            }
    
    def _get_gc_stats(self) -> Dict[str, Any]:
        """가비지 컬렉션 통계 반환"""
        try:
            return {
                'counts': gc.get_count(),
                'stats': gc.get_stats() if hasattr(gc, 'get_stats') else [],
                'threshold': gc.get_threshold()
            }
        except Exception:
            return {}
    
    def force_gc(self) -> Dict[str, int]:
        """강제 가비지 컬렉션 실행"""
        collected = {}
        for generation in range(3):
            collected[f'gen_{generation}'] = gc.collect(generation)
        
        return collected


class PerformanceOptimizer:
    """통합 성능 최적화 관리자"""
    
    def __init__(self):
        """성능 최적화기 초기화"""
        self.urgency_cache = UrgencyCache()
        self.batch_manager = BatchUpdateManager()
        self.realtime_optimizer = RealTimeUpdateOptimizer()
        self.memory_monitor = MemoryMonitor()
        
        # 메모리 모니터 콜백 등록
        self.memory_monitor.register_callback('warning', self._on_memory_warning)
        self.memory_monitor.register_callback('critical', self._on_memory_critical)
        
        self._is_initialized = False
    
    def initialize(self) -> None:
        """성능 최적화기 초기화"""
        if self._is_initialized:
            return
        
        # 메모리 모니터링 시작
        self.memory_monitor.start_monitoring()
        
        self._is_initialized = True
    
    def shutdown(self) -> None:
        """성능 최적화기 종료"""
        if not self._is_initialized:
            return
        
        # 각 컴포넌트 종료
        self.batch_manager.shutdown()
        self.realtime_optimizer.stop()
        self.memory_monitor.stop_monitoring()
        
        self._is_initialized = False
    
    def _on_memory_warning(self, memory_info: Dict[str, Any]) -> None:
        """메모리 경고 시 처리"""
        print(f"메모리 사용량 경고: {memory_info['usage_ratio']:.1%}")
        
        # 캐시 크기 축소
        self.urgency_cache.clear()
        
        # 배치 업데이트 강제 플러시
        self.batch_manager.force_flush()
        
        # 가비지 컬렉션 실행
        collected = self.memory_monitor.force_gc()
        print(f"가비지 컬렉션 완료: {collected}")
    
    def _on_memory_critical(self, memory_info: Dict[str, Any]) -> None:
        """메모리 위험 시 처리"""
        print(f"메모리 사용량 위험: {memory_info['usage_ratio']:.1%}")
        
        # 모든 캐시 클리어
        self.urgency_cache.clear()
        
        # 강제 플러시
        self.batch_manager.force_flush()
        
        # 강제 가비지 컬렉션
        self.memory_monitor.force_gc()
        
        # 실시간 업데이트 일시 중지
        self.realtime_optimizer.stop()
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 정보 반환"""
        return {
            'urgency_cache': self.urgency_cache.get_stats(),
            'memory_info': self.memory_monitor.get_memory_info(),
            'batch_pending': len(self.batch_manager._pending_updates),
            'realtime_queue': len(self.realtime_optimizer._update_queue)
        }


# 전역 성능 최적화기 인스턴스
_performance_optimizer: Optional[PerformanceOptimizer] = None


def get_performance_optimizer() -> PerformanceOptimizer:
    """전역 성능 최적화기 인스턴스 반환"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = PerformanceOptimizer()
        _performance_optimizer.initialize()
    return _performance_optimizer


def cached_urgency_calculation(func: Callable) -> Callable:
    """긴급도 계산 캐싱 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs) -> str:
        optimizer = get_performance_optimizer()
        
        # 인자에서 due_date와 completed_at 추출
        due_date = args[0] if args else kwargs.get('due_date')
        completed_at = kwargs.get('completed_at')
        
        # 캐시에서 조회
        cached_result = optimizer.urgency_cache.get_urgency_level(due_date, completed_at)
        if cached_result is not None:
            return cached_result
        
        # 캐시 미스 시 계산
        result = func(*args, **kwargs)
        
        # 결과를 캐시에 저장
        optimizer.urgency_cache.set_urgency_level(due_date, result, completed_at)
        
        return result
    
    return wrapper


def batch_update(update_type: str):
    """배치 업데이트 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_performance_optimizer()
            
            # 배치 업데이트 콜백 등록 (한 번만)
            if not hasattr(wrapper, '_callback_registered'):
                optimizer.batch_manager.register_update_callback(update_type, func)
                wrapper._callback_registered = True
            
            # 업데이트 큐에 추가
            item_id = kwargs.get('item_id') or (args[0] if args else None)
            data = kwargs.get('data', {})
            
            optimizer.batch_manager.queue_update(update_type, item_id, data)
        
        return wrapper
    
    return decorator


def optimized_realtime_update(component_id: str):
    """실시간 업데이트 최적화 데코레이터"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = get_performance_optimizer()
            
            # 실시간 업데이트 콜백 등록 (한 번만)
            if not hasattr(wrapper, '_callback_registered'):
                optimizer.realtime_optimizer.register_update_callback(component_id, func)
                wrapper._callback_registered = True
            
            # 업데이트 요청
            optimizer.realtime_optimizer.request_update(component_id)
        
        return wrapper
    
    return decorator