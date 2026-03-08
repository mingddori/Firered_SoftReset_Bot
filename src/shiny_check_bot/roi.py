import numpy as np

# TODO: 실제 캡처 화면(1280x720)에 맞춰 좌표를 수정해야 합니다.
# (x, y, width, height) 형식
ROI_CONFIG = {
    "nickname_state" : (726, 529, 219, 74), # 닉네임 작성 여부 확인
    "pokemon_summary":   (122, 5, 493, 68),   # 포켓몬 정보창 확인 좌표
    "shiny_check" : (521, 145, 109, 88), # 포켓몬 색깔 확인 좌표
    "dialog_box": (173, 519, 783, 144), # 오키드 박사 (또는 라이벌) 대화창 확인용 좌표 (좌표 획득 필요)
}

def get_roi_slice(frame: np.ndarray, roi_name: str) -> np.ndarray:
    """
    원본 프레임에서 지정된 ROI 이름에 해당하는 영역을 잘라내어 반환합니다.
    """
    if roi_name not in ROI_CONFIG:
        raise ValueError(f"알 수 없는 ROI 이름입니다: {roi_name}")
        
    x, y, w, h = ROI_CONFIG[roi_name]
    
    # 이미지 배열의 범위를 벗어나지 않도록 방어 코드 추가
    max_h, max_w = frame.shape[:2]
    end_y = min(max_h, y + h)
    end_x = min(max_w, x + w)
    
    return frame[y:end_y, x:end_x]

def get_roi_coordinates(roi_name: str):
    """지정된 ROI의 (x, y, w, h) 좌표를 반환합니다."""
    return ROI_CONFIG.get(roi_name)
