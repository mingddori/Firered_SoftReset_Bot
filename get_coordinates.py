import cv2
import sys
from pathlib import Path

# 전역 변수로 선택 영역 상태 저장
drawing = False
start_x, start_y = -1, -1
end_x, end_y = -1, -1
img_copy = None
original_img = None

def mouse_callback(event, x, y, flags, param):
    global drawing, start_x, start_y, end_x, end_y, img_copy
    
    # 1. 마우스 왼쪽 버튼을 누를 때 (시작점)
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_x, start_y = x, y
        end_x, end_y = x, y
        
    # 2. 마우스를 드래그할 때 (임시 박스 그리기)
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_x, end_y = x, y
            # 원본 이미지를 계속 복사해와야 이전 잔상이 안 남습니다.
            img_copy = original_img.copy()
            cv2.rectangle(img_copy, (start_x, start_y), (end_x, end_y), (0, 255, 0), 2)
            cv2.imshow("Coordinate Finder", img_copy)
            
    # 3. 마우스 왼쪽 버튼을 뗄 때 (영역 확정 및 로그 출력)
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_x, end_y = x, y
        
        # 시작점과 끝점 중 작은쪽이 시작점이 되도록 보정 (역방향 드래그 대비)
        x1, x2 = min(start_x, end_x), max(start_x, end_x)
        y1, y2 = min(start_y, end_y), max(start_y, end_y)
        w = x2 - x1
        h = y2 - y1
        
        cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 0, 255), 3)
        cv2.imshow("Coordinate Finder", img_copy)
        
        print("\n" + "="*40)
        print(f"✅ 드래그한 영역 좌표 확인!")
        print(f"X (가로 시작점)  : {x1}")
        print(f"Y (세로 시작점)  : {y1}")
        print(f"W (가로 너비)    : {w}")
        print(f"H (세로 높이)    : {h}")
        print("-"*40)
        print(f"👉 roi.py 입력용: ({x1}, {y1}, {w}, {h})")
        print("="*40 + "\n")


def main():
    global original_img, img_copy
    
    print("\n[INFO] ROI(관심 영역) 좌표 확인 도구를 시작합니다.")
    print("원하시는 장면을 캡처한 이미지(raw 폴더 안의 png)의 전체 경로를 입력해주세요.")
    print("예시: C:\\Users\\...\\captures\\raw\\capture_2026...png")
    
    img_path_str = input("이미지 경로 입력 > ").strip()
    
    # 앞뒤 따옴표 제거
    if img_path_str.startswith('"') and img_path_str.endswith('"'):
        img_path_str = img_path_str[1:-1]
        
    img_path = Path(img_path_str)
    
    if not img_path.exists():
        print(f"[ERROR] 해당 위치에 파일이 없습니다: {img_path}")
        return
        
    # OpenCV imread 한글 경로 문제 회피
    import numpy as np
    try:
        img_array = np.fromfile(str(img_path), np.uint8)
        original_img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    except Exception as e:
        print(f"[ERROR] 파일 열기 실패: {e}")
        return

    img_copy = original_img.copy()

    cv2.namedWindow("Coordinate Finder", cv2.WINDOW_AUTOSIZE)
    # 마우스 이벤트 콜백 연결
    cv2.setMouseCallback("Coordinate Finder", mouse_callback)

    print("\n[안내] 창이 열렸습니다.")
    print(" 1. 이미지 위에서 마우스 왼쪽 버튼을 클릭한 채로 드래그하여 원하시는 영역을 설정해주세요.")
    print(" 2. 버튼을 떼면 콘솔 창에 (x, y, w, h) 좌표가 출력됩니다.")
    print(" 3. 좌표 확인이 끝나면 창을 선택하고 아무 키나 누르거나, ESC 를 눌러 종료하세요.\n")

    while True:
        cv2.imshow("Coordinate Finder", img_copy)
        key = cv2.waitKey(1) & 0xFF
        # ESC(27)를 누르거나 창 닫기 버튼을 누르면 종료
        if key == 27:
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
