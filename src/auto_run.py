import cv2
import queue
import threading
import sys
import time
from capture_module.capture_save import save_frame
from capture_module.hardware_controller import MockController
from shiny_check_bot.state_check import get_current_state, GameState
from shiny_check_bot.shiny_detector import is_shiny

# msvcrt는 Windows에서만 동작합니다.
if sys.platform == 'win32':
    import msvcrt

def input_listener(q: queue.Queue, stop_event: threading.Event):
    """ 터미널 입력을 비동기적으로 받는 스레드 """
    if sys.platform == 'win32':
        while not stop_event.is_set():
            if msvcrt.kbhit():
                cmd = msvcrt.getwche().lower()
                if cmd == 'q':
                    q.put("quit")
                    break
            else:
                stop_event.wait(0.1)
    else:
        while not stop_event.is_set():
            try:
                cmd = input().strip().lower()
                if cmd == "q":
                    q.put("quit")
                    break
            except EOFError:
                break
            except Exception as e:
                print(f"[입력 스레드 오류] {e}")
                break

def start_auto_reset_session(camera_index: int):
    """
    캡처를 돌리면서 시나리오에 맞춰 하드웨어 컨트롤러에 명령을 내리는 메인 자동화 루프.
    """
    print(f"\n[INFO] 이로치 자동 리셋 봇을 시작합니다 (카메라 {camera_index}번).")
    
    cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cap.set(cv2.CAP_PROP_FPS, 30)

    if not cap.isOpened():
        print(f"[ERROR] 카메라 {camera_index}번을 열 수 없습니다.")
        return

    controller = MockController()
    
    print("\n==============================")
    print(" 봇이 화면을 감시하며 입력을 제어합니다.")
    print(" 튜토리얼:")
    print("   - 영상 창에서 'ESC' 키: 세션 강제 종료")
    print("   - 터미널 창 활성 상태에서 'q' 키: 세션 강제 종료")
    print("==============================\n")

    cmd_queue = queue.Queue()
    stop_event = threading.Event()
    
    t = threading.Thread(target=input_listener, args=(cmd_queue, stop_event), daemon=True)
    t.start()

    # 중복 입력을 막기 위한 쿨다운 관리
    last_action_time = time.time()
    ACTION_COOLDOWN = 1.0 # 상태 감지 후 다음 버튼을 누르기까지 최소 1초 대기
    overlay_state = GameState.UNKNOWN
    
    seen_oak_dialogue = False # 오키드(또는 라이벌) 대화창을 방금 전까지 봤는지 기억하는 변수

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            cv2.waitKey(100)
            continue

        # --- 자동화 매크로 & 렌더링 최적화 ---
        current_time = time.time()
        
        # ACTION_COOLDOWN 기간 동안은 렉 방지를 위해 불필요한 매칭(vision 검사)을 아예 스킵합니다.
        if current_time - last_action_time <= ACTION_COOLDOWN:
            current_state = GameState.UNKNOWN # 쿨다운 중엔 화면 판별 생략 (CPU 절약)
        else:
            # 쿨다운이 끝났을 때만 화면을 분석합니다 (30fps 매 프레임 검사 방지)
            current_state = get_current_state(frame)
            overlay_state = current_state
            
            if current_state == GameState.UNKNOWN:
                if seen_oak_dialogue:
                    # 방금 전까지 오키드 대화창이었는데(상태 기억됨) 이제 화면에서 사라짐(UNKNOWN) -> 매크로 발동 타이밍!
                    print("[BOT] 🚨 대화창 사라짐 감지! 메뉴(X) -> 포켓몬 진입 매크로 실행...")
                    controller.press_button("X", 1.0) # 메뉴 팝업 대기
                    controller.press_button("A", 1.0) # '포켓몬' 선택 대기
                    controller.press_button("A", 1.5) # 첫 번째 포켓몬(스타팅) 스테이터스 창 진입 대기
                    
                    seen_oak_dialogue = False # 매크로 1회만 실행되도록 리셋
                    last_action_time = time.time()
                    ACTION_COOLDOWN = 0.5
                else:
                    # 닉네임 창도 아니고 스테이터스 창도 아닐 땐 사실상 계속 A 버튼만 누르면 됨 (대화 넘기기 용도)
                    print("[BOT] 진행 중... (A 연타)")
                    controller.press_button("A")
                    last_action_time = time.time()
                    ACTION_COOLDOWN = 0.5
                    
            elif current_state == GameState.OAK_DIALOGUE:
                print("[BOT] 대화창 인식 중... (A 연타)")
                seen_oak_dialogue = True # 대화창을 봤다는 사실을 기억함
                controller.press_button("A")
                last_action_time = time.time()
                ACTION_COOLDOWN = 0.5
                
            elif current_state == GameState.NICKNAME_PROMPT:
                print(f"[BOT] 닉네임 프롬프트 감지! B 버튼 (안 함)...")
                controller.press_button("B")
                last_action_time = time.time()
                ACTION_COOLDOWN = 1.5
                
            elif current_state == GameState.POKEMON_SUMMARY:
                print(f"[BOT] 스테이터스 창 진입! 이로치 탐색 시작...")
                # UI 이펙트 렌더링을 위해 확실히 대기
                time.sleep(1.0) 
                
                # 최신 프레임을 다시 읽어 이로치 판정 (단 1회 수행)
                ret_s, frame_s = cap.read()
                if ret_s and frame_s is not None:
                    shiny_result = is_shiny(frame_s)
                    
                    if shiny_result:
                        print("====================================")
                        print("✨✨✨ 이로치 포켓몬 개체 발견!! ✨✨✨")
                        print("🚨 리셋을 중단하고 봇을 종료합니다.")
                        print("====================================")
                        # 이로치 발견 시 종료 플래그 설정 후 루프 탈출
                        break
                    else:
                        print("❌ 일반 개체입니다. 소프트 리셋을 진행합니다.")
                        controller.soft_reset()
                        # 리셋 직후 타이틀이 다시 뜰 때까지 넉넉히 대기
                        last_action_time = time.time()
                        ACTION_COOLDOWN = 5.0

        # --- 화면 드로잉 로직 ---
        display_frame = frame.copy()
        cv2.putText(
            display_frame, 
            f"STATE: {overlay_state}", 
            (20, 50), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.5, 
            (0, 255, 0) if overlay_state != "UNKNOWN" else (0, 0, 255), 
            3, 
            cv2.LINE_AA
        )
        # 이로치 판별 보조 텍스트
        cv2.putText(
            display_frame, 
            "TARGET(SHINY): ANY STARTER", 
            (20, 100), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            1.0, 
            (255, 255, 0), 
            2, 
            cv2.LINE_AA
        )

        cv2.imshow("Bot Auto Session", display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            print("[INFO] ESC 입력.")
            break
            
        if not cmd_queue.empty():
            cmd = cmd_queue.get()
            if cmd == "quit":
                print("[INFO] 터미널 종료 명령(q) 감지.")
                break

    stop_event.set()
    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] 봇 세션이 종료되었습니다.")
