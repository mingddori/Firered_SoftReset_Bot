import time
import cv2
import numpy as np
from .base_game import BaseGamePreset
from shiny_check_bot.shiny_detector import is_shiny

# FRLG GameState 재사용을 위해 간소한 enum 역할
class FRLGState:
    UNKNOWN = "UNKNOWN"
    NICKNAME_PROMPT = "NICKNAME_PROMPT"
    OAK_DIALOGUE = "OAK_DIALOGUE"
    POKEMON_SUMMARY = "POKEMON_SUMMARY"


class FRLG_Preset(BaseGamePreset):
    @property
    def game_name(self) -> str:
        return "FireRed / LeafGreen"
        
    @property
    def template_dir(self) -> str:
        return "frlg"
        
    @property
    def roi_config(self) -> dict:
        return {
            "nickname_state": (726, 529, 219, 74),
            "pokemon_summary": (122, 5, 493, 68),
            "shiny_check": (521, 145, 109, 88),
            "dialog_box": (173, 519, 783, 144),
        }

    @property
    def template_map(self) -> dict:
        return {
            "00_nickname.png": FRLGState.NICKNAME_PROMPT,
            "01_pokemon_summary.png": FRLGState.POKEMON_SUMMARY,
            "02_green_dialog_box.png": FRLGState.OAK_DIALOGUE,
        }

    def __init__(self):
        # 파이어레드 전용 상태 메모리
        self.seen_oak_dialogue = False

    def get_current_state(self, frame: np.ndarray) -> str:
        """
        현재 프레임을 분석하여 게임의 주요 상태를 판단합니다.
        가장 먼저 매칭되는 상태를 반환합니다.
        """
        from pathlib import Path
        template_base = Path(__file__).resolve().parent.parent.parent / "templates" / self.template_dir / "scen"
        
        # 1. 포켓몬 스테이터스 창 확인
        try:
            summary_roi = self.get_roi_slice(frame, "pokemon_summary")
            if self.check_template_match(summary_roi, template_base / "01_pokemon_summary.png", threshold=0.85):
                return FRLGState.POKEMON_SUMMARY
        except Exception:
            pass 
            
        # 2. 닉네임 프롬프트 창 확인
        try:
            nickname_roi = self.get_roi_slice(frame, "nickname_state")
            if self.check_template_match(nickname_roi, template_base / "00_nickname.png", threshold=0.85):
                return FRLGState.NICKNAME_PROMPT
        except Exception:
            pass
            
        # 3. 오키드 박사 (또는 라이벌) 대화창 확인
        try:
            dialog_roi = self.get_roi_slice(frame, "dialog_box")
            if self.check_template_match(dialog_roi, template_base / "02_green_dialog_box.png", threshold=0.85):
                return FRLGState.OAK_DIALOGUE
        except Exception:
            pass
                
        return FRLGState.UNKNOWN

    def process_tick(self, frame: np.ndarray, current_state: str, controller) -> tuple[float, bool]:
        """
        현재 프레임과 인식된 상태를 기반으로 FRLG의 자동 리셋 매크로를 실행합니다.
        """
        action_cooldown = 0.5
        should_stop = False

        if current_state == FRLGState.UNKNOWN:
            if self.seen_oak_dialogue:
                print(f"[{self.game_name}] 🚨 대화창 사라짐 감지! 메뉴(X) -> 포켓몬 진입 매크로 실행...")
                controller.press_button("X", 1.0) # 메뉴 팝업 대기
                controller.press_button("A", 1.0) # '포켓몬' 선택 대기
                controller.press_button("A", 1.5) # 첫 번째 포켓몬(스타팅) 스테이터스 창 진입 대기
                self.seen_oak_dialogue = False
                action_cooldown = 0.5
            else:
                print(f"[{self.game_name}] 진행 중... (A 연타)")
                controller.press_button("A")
                action_cooldown = 0.5
                
        elif current_state == FRLGState.OAK_DIALOGUE:
            print(f"[{self.game_name}] 대화창 인식 중... (A 연타)")
            self.seen_oak_dialogue = True
            controller.press_button("A")
            action_cooldown = 0.5
            
        elif current_state == FRLGState.NICKNAME_PROMPT:
            print(f"[{self.game_name}] 닉네임 프롬프트 감지! B 버튼 (안 함)...")
            controller.press_button("B")
            action_cooldown = 1.5
            
        elif current_state == FRLGState.POKEMON_SUMMARY:
            print(f"[{self.game_name}] 스테이터스 창 진입! 이로치 탐색 시작...")
            time.sleep(1.0) # UI 이펙트 렌더링 대기 (is_shiny는 auto_run의 메인 루프에서 별도로 처리하거나, 여기로 넘겨올 수 있음)
            
            # 파이어레드는 스테이터스 창에서 shiny_star.png를 확인합니다.
            import numpy as np
            # 파이어레드는 is_shiny 함수 내부 로직을 재사용할 수 있으나, OOP 구조에 맞게 여기서 직접 검사하도록 변경하는 것이 좋습니다.
            # 지금은 임시로 기존 함수 재사용 (인스턴스의 경로 정보 전달)
            from shiny_check_bot.shiny_detector import check_template_match
            from pathlib import Path
            
            # base_game의 get_roi_slice 호출
            try:
                roi_frame = self.get_roi_slice(frame, "shiny_check")
            except ValueError:
                roi_frame = frame
                
            template_path = Path(__file__).resolve().parent.parent.parent / "templates" / self.template_dir / "shiny" / "shiny_mark.png"
            shiny_result = check_template_match(roi_frame, template_path, threshold=0.85)
            
            if shiny_result:
                print("====================================")
                print(f"✨✨✨ {self.game_name} 이로치 포켓몬 개체 발견!! ✨✨✨")
                print("🚨 리셋을 중단하고 봇을 종료합니다.")
                print("====================================")
                should_stop = True
            else:
                print(f"[{self.game_name}] ❌ 일반 개체입니다. 소프트 리셋을 진행합니다.")
                controller.soft_reset()
                action_cooldown = 5.0
                
        return action_cooldown, should_stop
