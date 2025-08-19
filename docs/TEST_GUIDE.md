# 테스트 구조 가이드

이 문서는 Todo List 애플리케이션의 모든 테스트를 체계적으로 구성하고 실행하는 방법을 안내합니다.

## 테스트 디렉토리 구조

```
test/
├── unit/                    # 단위 테스트
│   ├── test_models.py      # 모델 클래스 테스트 (Todo, SubTask)
│   ├── test_services.py    # 서비스 클래스 테스트
│   ├── test_utils.py       # 유틸리티 함수 테스트
│   ├── test_todo.py        # Todo 모델 상세 테스트
│   ├── test_subtask.py     # SubTask 모델 상세 테스트
│   ├── test_*_service.py   # 개별 서비스 테스트
│   └── test_*_utils.py     # 개별 유틸리티 테스트
├── integration/             # 통합 테스트
│   ├── test_dialog_integration.py        # 다이얼로그 통합 테스트
│   ├── test_startup_notification_integration.py  # 시작 알림 통합 테스트
│   ├── test_*_dialog*.py   # 다이얼로그 관련 테스트
│   ├── test_*integration*.py  # 통합 테스트
│   └── test_*_gui*.py      # GUI 통합 테스트
├── verification/            # 작업 검증 테스트
│   ├── test_task9_verification.py   # Task 9 검증
│   ├── test_task10_verification.py  # Task 10 검증
│   ├── test_task13_verification.py  # Task 13 검증
│   ├── test_task14_verification.py  # Task 14 검증
│   ├── test_task15_*.py    # Task 15 관련 검증
│   └── test_task16_*.py    # Task 16 관련 검증
├── data/                    # 테스트 데이터
├── todo_folders/           # 테스트용 폴더
├── run_all_tests_organized.py  # 통합 테스트 실행기
├── run_all_tests.py        # 기존 테스트 실행기
├── run_final_verification.py   # 최종 검증 실행기
├── final_system_verification.py  # 시스템 검증
├── *_SUMMARY.md           # 테스트 요약 문서
└── README.md              # 테스트별 상세 가이드
```

## 테스트 실행 방법

### 1. 전체 테스트 실행 (권장)
```bash
python test/run_all_tests_organized.py
```

### 2. 카테고리별 테스트 실행

#### 단위 테스트만 실행
```bash
python -m unittest discover test/unit -v
```

#### 통합 테스트만 실행
```bash
python -m unittest discover test/integration -v
```

#### 검증 테스트만 실행
```bash
python -m unittest discover test/verification -v
```

### 3. 개별 테스트 파일 실행
```bash
python -m unittest test.unit.test_models -v
python -m unittest test.integration.test_dialog_integration -v
python -m unittest test.verification.test_task14_verification -v
```

### 4. 최종 시스템 검증
```bash
python test/final_system_verification.py
```

## 테스트 카테고리 설명

### Unit Tests (단위 테스트)
- **목적**: 개별 클래스와 함수의 기능을 독립적으로 테스트
- **범위**: 모델, 서비스, 유틸리티 클래스
- **특징**: 빠른 실행, 외부 의존성 최소화

### Integration Tests (통합 테스트)
- **목적**: 여러 컴포넌트 간의 상호작용을 테스트
- **범위**: GUI와 서비스 통합, 다이얼로그 기능, 데이터 흐름
- **특징**: 실제 사용 시나리오 시뮬레이션

### Verification Tests (검증 테스트)
- **목적**: 특정 작업(Task)의 완료 여부를 검증
- **범위**: 요구사항 구현 확인, 기능 완성도 검증
- **특징**: 비즈니스 요구사항과 직접 연결

## 테스트 작성 가이드라인

### 1. 명명 규칙
- 테스트 파일: `test_[모듈명].py`
- 테스트 클래스: `Test[클래스명]`
- 테스트 메서드: `test_[기능명]`

### 2. 테스트 구조
```python
class TestClassName(unittest.TestCase):
    def setUp(self):
        """테스트 환경 설정"""
        pass
    
    def tearDown(self):
        """테스트 환경 정리"""
        pass
    
    def test_specific_functionality(self):
        """특정 기능 테스트"""
        # Arrange
        # Act
        # Assert
        pass
```

### 3. 모킹 사용
- 외부 의존성은 `unittest.mock`을 사용하여 모킹
- 파일 시스템 작업은 임시 디렉토리 사용
- GUI 테스트는 실제 창을 표시하지 않도록 설정

### 4. 테스트 데이터
- `test/data/` 디렉토리에 테스트용 데이터 파일 저장
- 각 테스트는 독립적인 데이터 사용
- 테스트 후 임시 데이터 정리

## 지속적 통합 (CI)

테스트는 다음 상황에서 자동으로 실행됩니다:
1. 코드 커밋 시
2. Pull Request 생성 시
3. 릴리스 준비 시

## 테스트 커버리지

목표 커버리지: 80% 이상
- 단위 테스트: 90% 이상
- 통합 테스트: 70% 이상
- 전체 시스템: 80% 이상

## 문제 해결

### 테스트 실패 시
1. 실패한 테스트의 오류 메시지 확인
2. 관련 로그 파일 검토
3. 테스트 환경 설정 확인
4. 필요시 개별 테스트 실행으로 디버깅

### 성능 이슈
- 테스트 실행 시간이 너무 길면 병렬 실행 고려
- 무거운 통합 테스트는 별도 실행
- 모킹을 통한 외부 의존성 제거

## 기여 가이드

새로운 기능 추가 시:
1. 해당 기능의 단위 테스트 작성
2. 필요시 통합 테스트 추가
3. 기존 테스트가 통과하는지 확인
4. 테스트 커버리지 유지

테스트 관련 질문이나 제안사항은 이슈로 등록해 주세요.