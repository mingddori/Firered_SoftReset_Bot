"""
장치 번호를 0부터 9까지 테스트하여 연결된 카메라 장치를 찾는 코드입니다.
"""

import cv2

for i in range(10):
    print(f"{i}번 장치 테스트 중...")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)

    if not cap.isOpened():
        print(f"{i}번 장치 열기 실패")
        continue

    ret, frame = cap.read()
    if ret:
        cv2.imshow(f"device_{i}", frame)
        print(f"{i}번 장치 화면 표시 중. 아무 키나 누르면 다음 장치로 넘어감.")
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    else:
        print(f"{i}번 장치 프레임 읽기 실패")

    cap.release()