import cv2
import numpy as np
from pathlib import Path

# 템플릿 이미지가 저장될 기본 경로
TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "scen"

class GameState:
    UNKNOWN = "UNKNOWN"
    NICKNAME_PROMPT = "NICKNAME_PROMPT"
    OAK_DIALOGUE = "OAK_DIALOGUE"
    POKEMON_SUMMARY = "POKEMON_SUMMARY"

# 템플릿 파일명과 GameState를 매핑
TEMPLATE_MAP = {
    "00_nickname.png": GameState.NICKNAME_PROMPT,
    "01_pokemon_summary.png": GameState.POKEMON_SUMMARY,
    "02_green_dialog_box.png": GameState.OAK_DIALOGUE,
}

def check_template_match(frame: np.ndarray, template_path: Path, threshold: float = 0.8) -> bool:
    """
    주어진 프레임 안에서 특정 템플릿과 매칭되는지 확인합니다.
    (간단한 cv2.matchTemplate 기반)
    """
    if not template_path.exists():
        return False
        
    # Windows 한글 경로 문제 해결을 위해 numpy와 imdecode 사용
    try:
        template_array = np.fromfile(str(template_path), np.uint8)
        template = cv2.imdecode(template_array, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[ERROR] 템플릿 로드 실패 ({template_path.name}): {e}")
        return False

    if template is None:
        return False

    th, tw = template.shape[:2]
    fh, fw = frame.shape[:2]
    if fh < th or fw < tw:
        return False

    result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(result)
    
    return max_val >= threshold

from shiny_check_bot.roi import get_roi_slice

def get_current_state(frame: np.ndarray) -> str:
    """
    현재 프레임을 분석하여 게임의 주요 상태를 판단합니다.
    TEMPLATE_MAP에 정의된 템플릿들을 순회하며 가장 먼저 매칭되는 상태를 반환합니다.
    """
    # [최적화] 전체 화면을 탐색하면 렉이 매우 심하므로, 각 상태별로 지정된 ROI(관심 구역)만 잘라서 검사합니다.
    
    # 1. 포켓몬 스테이터스 창 확인
    try:
        summary_roi = get_roi_slice(frame, "pokemon_summary")
        summary_template_path = TEMPLATE_DIR / "01_pokemon_summary.png"
        if check_template_match(summary_roi, summary_template_path, threshold=0.85):
            return GameState.POKEMON_SUMMARY
    except Exception:
        pass 
        
    # 2. 닉네임 프롬프트 창 확인
    try:
        nickname_roi = get_roi_slice(frame, "nickname_state")
        nickname_template_path = TEMPLATE_DIR / "00_nickname.png"
        if check_template_match(nickname_roi, nickname_template_path, threshold=0.85):
            return GameState.NICKNAME_PROMPT
    except Exception:
        pass
        
    # 3. 오키드 박사 (또는 라이벌) 대화창 확인
    try:
        dialog_roi = get_roi_slice(frame, "dialog_box")
        dialog_template_path = TEMPLATE_DIR / "02_green_dialog_box.png"
        if check_template_match(dialog_roi, dialog_template_path, threshold=0.85):
            return GameState.OAK_DIALOGUE
    except Exception:
        pass
            
    return GameState.UNKNOWN
