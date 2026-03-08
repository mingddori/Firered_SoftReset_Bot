"""
카메라 장치를 열고 영상을 보여주는 코드입니다.
"""
import cv2
import threading
import queue
import sys


class CameraApp:
    def __init__(self):
        self.command_queue = queue.Queue()
        self.running = False

    def input_listener(self):
        """
        영상이 실행 중일 때 CLI 입력을 받는 스레드
        q 입력 시 종료 명령 전달
        """
        while self.running:
            try:
                cmd = input().strip().lower()
                if cmd == "q":
                    self.command_queue.put("quit")
                    break
            except EOFError:
                break
            except Exception as e:
                print(f"[입력 스레드 오류] {e}")
                break

    def run_camera(self, camera_index: int):
        print("\n[INFO] 카메라를 엽니다...")
        print("[INFO] 종료하려면 영상 창에서 ESC를 누르거나, CLI에 q 입력 후 Enter 하세요.")

        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cap.set(cv2.CAP_PROP_FPS, 30)

        if not cap.isOpened():
            print("[ERROR] 캡처 장치를 열 수 없습니다.")
            return

        self.running = True

        try:
            backend_name = cap.getBackendName()
        except Exception:
            backend_name = "알 수 없음"

        print(f"[INFO] camera opened")
        print(f"[INFO] backend: {backend_name}")

        listener_thread = threading.Thread(target=self.input_listener, daemon=True)
        listener_thread.start()

        while self.running:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[WARN] 프레임을 읽지 못했습니다.")
                continue

            cv2.imshow("capture", frame)

            # OpenCV 창 키 입력 처리
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("[INFO] ESC 입력으로 종료합니다.")
                self.running = False
                break

            # CLI 입력 처리
            while not self.command_queue.empty():
                command = self.command_queue.get()
                if command == "quit":
                    print("[INFO] CLI 명령으로 종료합니다.")
                    self.running = False
                    break

        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] 카메라 실행 종료\n")

    def main_menu(self):
        while True:
            print("===================================")
            print("   캡처 테스트 CLI")
            print("===================================")
            print("1. 실행하기")
            print("2. 종료하기")
            print("===================================")

            choice = input("메뉴를 선택하세요: ").strip()

            if choice == "1":
                camera_input = input("카메라 번호를 입력하세요 (예: 0): ").strip()

                if not camera_input.isdigit():
                    print("[ERROR] 숫자만 입력해주세요.\n")
                    continue

                camera_index = int(camera_input)
                self.run_camera(camera_index)

            elif choice == "2":
                print("프로그램을 종료합니다.")
                break

            else:
                print("[ERROR] 올바른 메뉴 번호를 입력해주세요.\n")


if __name__ == "__main__":
    app = CameraApp()
    app.main_menu()