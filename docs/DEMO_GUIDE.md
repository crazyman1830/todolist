# 데모 가이드

이 문서는 Todo List 애플리케이션의 다양한 기능을 시연하는 데모 스크립트들에 대한 종합 가이드입니다.

## 데모 디렉토리 구조

```
demo/
├── gui/                     # GUI 관련 데모
│   ├── demo_main_gui.py    # 메인 GUI 종합 데모
│   ├── demo_gui.py         # 기본 GUI 데모
│   ├── demo_progress_components.py  # 진행률 컴포넌트 데모
│   └── demo_todo_tree.py   # TodoTree 컴포넌트 데모
├── features/               # 기능별 데모
│   ├── demo_due_date_features.py    # 목표 날짜 기능 종합 데모
│   ├── demo_date_features.py        # 날짜 기능 데모
│   ├── demo_context_menu_due_date.py # 컨텍스트 메뉴 데모
│   ├── demo_due_date_dialog.py      # 목표 날짜 다이얼로그 데모
│   ├── demo_due_date_filtering.py   # 날짜 필터링 데모
│   ├── demo_status_bar_due_date.py  # 상태바 데모
│   ├── demo_subtask_due_date.py     # 하위작업 날짜 데모
│   ├── demo_todo_due_date_methods.py # Todo 날짜 메서드 데모
│   └── demo_auto_save_backup.py     # 자동 저장 데모
├── services/               # 서비스 데모
│   ├── demo_notification_service.py # 알림 서비스 데모
│   ├── demo_storage_service_due_date.py # 저장 서비스 데모
│   └── demo_todo_service_due_date.py    # Todo 서비스 데모
├── integration/            # 통합 데모
│   └── demo_startup_notification_integration.py # 시작 알림 통합 데모
├── performance/            # 성능 데모
│   └── demo_performance_optimization.py # 성능 최적화 데모
├── accessibility/          # 접근성 데모
│   └── demo_accessibility_improvements.py # 접근성 개선 데모
├── data/                   # 데모용 데이터
└── README.md              # 데모별 상세 가이드
```

## 주요 데모 실행 방법

### 1. 메인 GUI 데모 (추천)
전체 애플리케이션의 모든 기능을 체험할 수 있는 종합 데모입니다.

```bash
python demo/gui/demo_main_gui.py
```

**포함 기능:**
- 할일 추가, 수정, 삭제
- 하위작업 관리
- 목표 날짜 설정
- 진행률 표시
- 컨텍스트 메뉴
- 키보드 단축키
- 드래그 앤 드롭
- 폴더 관리
- 알림 기능

### 2. 목표 날짜 기능 종합 데모
목표 날짜 관련 모든 기능을 콘솔에서 확인할 수 있습니다.

```bash
python demo/features/demo_due_date_features.py
```

**포함 기능:**
- 다양한 날짜 형식 파싱
- 긴급도 자동 계산
- 상대적 시간 표시
- 날짜 기반 정렬/필터링
- 알림 서비스

### 3. 시작 알림 통합 데모
애플리케이션 시작 시 알림 기능을 테스트합니다.

```bash
python demo/integration/demo_startup_notification_integration.py
```

**포함 기능:**
- 지연된 할일 감지
- 시작 알림 다이얼로그
- "다시 보지 않기" 옵션
- 설정 저장/복원

### 4. 성능 최적화 데모
대량 데이터 처리 및 성능 최적화 기능을 확인합니다.

```bash
python demo/performance/demo_performance_optimization.py
```

**포함 기능:**
- 대량 할일 처리
- 배치 업데이트
- 메모리 사용량 모니터링
- 캐싱 시스템

## 카테고리별 데모 설명

### GUI 데모
실제 그래픽 사용자 인터페이스를 통해 기능을 시연합니다.
- 마우스와 키보드 상호작용
- 시각적 피드백
- 사용자 경험 확인

### 기능 데모
특정 기능의 동작을 집중적으로 보여줍니다.
- 콘솔 출력으로 결과 확인
- 단계별 기능 설명
- 다양한 시나리오 테스트

### 서비스 데모
백엔드 서비스 계층의 기능을 시연합니다.
- API 호출 시뮬레이션
- 데이터 처리 과정
- 오류 처리 확인

### 통합 데모
여러 컴포넌트가 함께 동작하는 시나리오를 보여줍니다.
- 전체 워크플로우
- 컴포넌트 간 상호작용
- 실제 사용 사례

## 데모 실행 시 주의사항

### 1. 환경 설정
- Python 3.7 이상 필요
- 필요한 패키지 설치: `pip install -r requirements.txt`
- GUI 데모는 디스플레이 환경 필요

### 2. 임시 파일
- 데모 실행 시 임시 파일이 생성됩니다
- 대부분 자동으로 정리되지만, 수동 정리가 필요할 수 있습니다
- 임시 파일 패턴: `demo_*.json`, `demo_*_folders/`

### 3. 데이터 안전성
- 데모는 실제 데이터에 영향을 주지 않습니다
- 별도의 임시 데이터 파일을 사용합니다
- 기존 할일 데이터는 보호됩니다

## 데모 커스터마이징

### 새로운 데모 추가
1. 적절한 카테고리 디렉토리 선택
2. `demo_[기능명].py` 형식으로 파일 생성
3. 다음 구조를 따라 작성:

```python
#!/usr/bin/env python3
"""
[기능명] 데모
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

def demo_function():
    """데모 함수"""
    print("데모 시작...")
    # 데모 코드
    print("데모 완료!")

def main():
    """메인 함수"""
    print("=" * 60)
    print("[기능명] 데모")
    print("=" * 60)
    
    try:
        demo_function()
    except Exception as e:
        print(f"데모 실행 중 오류: {e}")
    finally:
        # 정리 작업
        pass

if __name__ == "__main__":
    main()
```

### 기존 데모 수정
1. 해당 데모 파일 편집
2. 변경사항 테스트
3. 문서 업데이트

## 문제 해결

### GUI 데모가 실행되지 않는 경우
- 디스플레이 환경 확인 (X11, Wayland 등)
- tkinter 패키지 설치 확인
- 가상 환경에서 실행 시 GUI 패키지 설치

### 임시 파일이 남아있는 경우
```bash
# 임시 데모 파일 정리
rm -f demo_*.json
rm -rf demo_*_folders/
```

### 권한 오류 발생 시
- 쓰기 권한이 있는 디렉토리에서 실행
- 필요시 관리자 권한으로 실행

## 기여 방법

새로운 데모나 개선사항이 있으면:
1. 해당 카테고리에 데모 파일 추가
2. 이 문서 업데이트
3. 테스트 후 Pull Request 생성

데모 관련 질문이나 제안사항은 이슈로 등록해 주세요.