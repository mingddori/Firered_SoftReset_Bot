import cv2
import numpy as np
from pathlib import Path
from shiny_check_bot.state_check import check_template_match
from shiny_check_bot.roi import get_roi_slice

TEMPLATE_DIR = Path(__file__).resolve().parent.parent.parent / "templates" / "shiny"

def is_shiny(frame: np.ndarray) -> bool:
    """
    현재 주어진 프레임(포켓몬 스테이터스 창이어야 함)에서
    지정된 이로치 템플릿 마커(별표 등)가 감지되는지 확인합니다.
    주의: 연산량(렉)을 줄이기 위해 원본 1280x720 전체를 뒤지지 않고,
    'shiny_check' 로 지정된 구역 안에서만 탐색합니다.
    """
    marker_path = TEMPLATE_DIR / "shiny_mark.png"
    
    # 전체 프레임을 다 조사하면 너무 느리므로 ROI 지정된 영역만 잘라냄
    try:
        roi_frame = get_roi_slice(frame, "shiny_check")
    except ValueError:
        roi_frame = frame  # 만약 roi가 정의되지 않았다면 어쩔 수 없이 원본 사용
    
    # 캡처 퀄리티나 배경 투명도 등에 따라 임계값을 조절해야 할 수 있습니다 (기본 0.85)
    return check_template_match(roi_frame, marker_path, threshold=0.85)