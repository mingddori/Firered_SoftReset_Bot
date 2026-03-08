import time
import threading

class MockController:
    """
    아두이노(Hardware)가 없을 때,
    시리얼 통신 대신 콘솔에 입력 명령을 출력만 해주는 가짜(Mock) 제어기입니다.
    """
    def __init__(self):
        print("[MOCK_HARDWARE] 가상 하드웨어 제어기가 초기화되었습니다.")

    def _press_and_sleep(self, button: str, delay_after: float):
        print(f"🎮 [MOCK_INPUT] 버튼 입력 전송 -> [{button}]")
        time.sleep(1/30) # 대략 1프레임 누르고 있음 가정
        print(f"🎮 [MOCK_INPUT] 버튼 뗌 -> [{button}]")
        if delay_after > 0:
            time.sleep(delay_after)

    def press_button(self, button: str, delay_after: float = 0.5):
        """특정 버튼을 짧게 누르고 뗍니다 (메인 스레드 렉 방지를 위해 백그라운드 처리)"""
        # cv2 메인 루프 프레임을 멈추지 않도록 데몬 스레드로 실행
        threading.Thread(target=self._press_and_sleep, args=(button, delay_after), daemon=True).start()

    def _reset_and_sleep(self):
        print(f"🚨 [MOCK_INPUT] 소프트 리셋 (A+B+X+Y) 전송!")
        time.sleep(2.0) # 리셋 후 화면 뜰 때까지 대기

    def soft_reset(self):
        """소프트 리셋 명령"""
        threading.Thread(target=self._reset_and_sleep, daemon=True).start()
