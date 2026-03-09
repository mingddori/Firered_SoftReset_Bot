import sys
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 필요한 폴더 보장
(Path(PROJECT_ROOT / "captures" / "raw")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "captures" / "roi")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "captures" / "shiny_candidates")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "refs" / "starters")).mkdir(parents=True, exist_ok=True)
(Path(PROJECT_ROOT / "templates")).mkdir(parents=True, exist_ok=True)


def print_header():
    print("=" * 50)
    print(" 포켓몬 이로치 체크 봇 - Capture CLI ")
    print("=" * 50)


def print_menu():
    print("\n메뉴를 선택하세요.")
    print("1. 캡처 실행")
    print("2. 사용 가능한 카메라 찾기")
    print("3. 종료")
    print("-" * 50)


def run_find_cameras():
    try:
        from capture_module.capture_find import find_available_cameras
    except Exception as e:
        print(f"[ERROR] capture_find 모듈 import 실패: {e}")
        return

    print("\n[INFO] 사용 가능한 카메라를 찾는 중입니다...\n")

    try:
        cameras = find_available_cameras(max_index=10)
    except Exception as e:
        print(f"[ERROR] 카메라 검색 중 예외 발생: {e}")
        return

    if not cameras:
        print("[WARN] 사용 가능한 카메라를 찾지 못했습니다.")
        return

    print("[INFO] 사용 가능한 카메라 목록")
    for cam in cameras:
        idx = cam.get("index")
        backend = cam.get("backend")
        width = cam.get("width")
        height = cam.get("height")
        print(f"  - index={idx}, backend={backend}, resolution={width}x{height}")


def select_game_preset():
    from games.frlg import FRLG_Preset
    from games.hgss import HGSS_Preset
    from games.oras import ORAS_Preset
    from games.bdsp import BDSP_Preset
    
    print("\n[INFO] 지원하는 게임 버전을 선택하세요.")
    print("1. FireRed / LeafGreen (1세대 리메이크 / 3세대 환경)")
    print("2. HeartGold / SoulSilver (2세대 리메이크 / 4세대 환경)")
    print("3. OmegaRuby / AlphaSapphire (3세대 리메이크 / 6세대 환경)")
    print("4. BrilliantDiamond / ShiningPearl (4세대 리메이크 / 8세대 환경)")
    
    choice = input("선택 > ").strip()
    if choice == "1":
        return FRLG_Preset()
    elif choice == "2":
        return HGSS_Preset()
    elif choice == "3":
        return ORAS_Preset()
    elif choice == "4":
        return BDSP_Preset()
    else:
        print("[WARN] 기본값인 FireRed / LeafGreen으로 시작합니다.")
        return FRLG_Preset()

def run_capture():
    try:
        from capture_module.capture_run import run_capture_session
    except Exception as e:
        print(f"[ERROR] capture_run 모듈 import 실패: {e}")
        return

    print("\n" + "=" * 50)
    game_preset = select_game_preset()
    
    print("\n" + "=" * 50)
    cam_input = input("카메라 번호를 입력하세요 (예: 0): ").strip()
    if not cam_input.isdigit():
        print("[ERROR] 숫자만 입력해주세요.")
        return

    print("\n[INFO] 캡처 세션을 시작합니다.")
    try:
        run_capture_session(
            camera_index=int(cam_input),
            save_dir=str(PROJECT_ROOT / "captures" / "raw"),
            game_preset=game_preset
        )
    except Exception as e:
        print(f"[ERROR] 캡처 실행 중 예외 발생: {e}")


def run_auto_bot():
    try:
        from auto_run import start_auto_reset_session
    except Exception as e:
        print(f"[ERROR] auto_run 모듈 import 실패: {e}")
        return
        
    print("\n" + "=" * 50)
    print("\n[INFO] 자동 리셋 봇 설정을 시작합니다.")
    
    game_preset = select_game_preset()
    
    # 카메라 설정
    print("\n" + "=" * 50)
    cam_input = input("사용할 카메라 번호를 입력하세요 (예: 0): ").strip()
    if not cam_input.isdigit():
        print("[ERROR] 숫자로 입력해주세요.")
        return
    
    try:
        start_auto_reset_session(
            camera_index=int(cam_input),
            game_preset=game_preset
        )
    except Exception as e:
        print(f"[ERROR] 봇 실행 중 예외 발생: {e}")


def main():
    print_header()

    while True:
        print("\n메뉴를 선택하세요.")
        print("1. [핵심] 자동 리셋 봇 실행 (Mock 컨트롤러)")
        print("2. 단순 캡처 실행 (프레임 확인 및 수집용)")
        print("3. 사용 가능한 카메라 찾기")
        print("4. 종료")
        print("-" * 50)
        
        choice = input("입력 > ").strip()

        if choice == "1":
            run_auto_bot()
        elif choice == "2":
            run_capture()
        elif choice == "3":
            run_find_cameras()
        elif choice == "4":
            print("프로그램을 종료합니다.")
            sys.exit(0)
        else:
            print("[WARN] 올바른 메뉴 번호를 입력해주세요.")

if __name__ == "__main__":
    main()