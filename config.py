"""
할일 관리 프로그램 설정 및 상수
"""
import os

# 파일 경로 설정
DATA_DIR = "data"
TODO_FOLDERS_DIR = "todo_folders"
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")

# 폴더명 설정
MAX_FOLDER_NAME_LENGTH = 50
FOLDER_NAME_PATTERN = "todo_{id}_{title}"

# 메뉴 옵션
MENU_OPTIONS = {
    '1': '할일 추가',
    '2': '할일 목록 보기',
    '3': '할일 수정',
    '4': '할일 삭제',
    '5': '할일 폴더 열기',
    '6': '프로그램 종료'
}

# 메시지
MESSAGES = {
    'welcome': '=== 할일 관리 프로그램 ===',
    'menu_prompt': '원하는 기능을 선택하세요: ',
    'invalid_choice': '잘못된 선택입니다. 다시 선택해주세요.',
    'empty_title': '할일 제목을 입력해주세요.',
    'no_todos': '할일이 없습니다.',
    'todo_added': '할일이 추가되었습니다.',
    'todo_updated': '할일이 수정되었습니다.',
    'todo_deleted': '할일이 삭제되었습니다.',
    'todo_not_found': '해당 할일을 찾을 수 없습니다.',
    'folder_created': '할일 폴더가 생성되었습니다.',
    'folder_opened': '할일 폴더를 열었습니다.',
    'folder_delete_confirm': '관련 폴더도 삭제하시겠습니까? (y/n): ',
    'delete_confirm': '정말 삭제하시겠습니까? (y/n): ',
    'goodbye': '프로그램을 종료합니다.',
    'file_error': '파일 처리 중 오류가 발생했습니다.',
    'data_corrupted': '데이터 파일이 손상되었습니다. 새로 시작합니다.'
}

# 기본 설정
DEFAULT_ENCODING = 'utf-8'
BACKUP_COUNT = 5