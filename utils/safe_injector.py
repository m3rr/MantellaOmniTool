# utils/safe_injector.py
import os
import shutil
import stat
import time
from pathlib import Path
from utils.logger import get_logger

log = get_logger()

# --- THE GOLD MASTER TEMPLATE (v7.1 - Escaped for Python Formatting) ---
# FIX: All non-injection placeholders must be double-braced {{variable}}
MANTELLA_TEMPLATE = """; ==============================================================================
;  MANTELLA CONFIGURATION (h4 OMNI-TOOL v7.1)
; ==============================================================================
[Game]
game = {game_mode}
port = {port}
skyrim_mod_folder = {mod_root}
skyrimvr_mod_folder = {mod_root}
fallout4_mod_folder = {mod_root}
fallout4vr_mod_folder = {mod_root}
fallout4_folder = C:\Games\Steam\steamapps\common\Fallout 4
fallout4vr_folder = C:\Games\Steam\steamapps\common\Fallout4VR

[LLM]
; KEY SETTING: We inject the Proxy URL here to force traffic through Port 5001
llm_api = {llm_api}
model = {model}
max_response_sentences_single = 4
max_response_sentences_multi = 12
custom_token_count = {tokens}
wait_time_buffer = 0
llm_params = {{
    "max_tokens": 250,
    "stop": ["#"]
    }}
narration_handling = Cut narrations
narrator_voice =
narration_start_indicators = *, (, [
narration_end_indicators = *, ), ]
speech_start_indicators = "
speech_end_indicators = "
narration_indicators = ()

[TTS]
tts_service = {tts_service}
xvasynth_folder = {xvasynth_path}
xtts_server_folder = C:\Games\Steam\steamapps\common\XTTS
piper_folder =
lipgen_folder =
facefx_folder =
number_words_tts = 3
lip_generation = Enabled
fast_response_mode = False
fast_response_mode_volume = 40
xtts_url = http://127.0.0.1:8020
xtts_default_model = main
xtts_device = cpu
xtts_deepspeed = False
xtts_lowvram = True
xtts_data = {{"temperature": 0.75, "length_penalty": 1.0, "repetition_penalty": 5.0, "top_k": 50, "top_p": 0.85, "speed": 1, "enable_text_splitting": true, "stream_chunk_size": 100}}
xtts_accent = False
tts_print = False
tts_process_device = cpu
pace = 1.0
use_cleanup = False
use_sr = False

[STT]
audio_threshold = 0.4
allow_interruption = True
save_mic_input = False
stt_service = Moonshine
pause_threshold = 0.25
play_cough_sound = True
listen_timeout = 30
moonshine_model_size = moonshine/tiny/quantized
whisper_model_size = base
proactive_mic_mode = False
min_refresh_secs = 0.3
external_whisper_service = False
whisper_url = OpenAI
stt_language = en
stt_translate = False
process_device = cpu
moonshine_folder =

[Vision]
vision_enabled = {vision_enabled}
low_resolution_mode = True
save_screenshot = True
image_quality = 50
resize_method = Nearest
capture_offset = {{"left": 0, "right": 0, "top": 0, "bottom": 0}}
custom_vision_model = False
vision_llm_api = OpenRouter
vision_model = {vision_model}
vision_custom_token_count = 4096
vision_llm_params = {{"max_tokens": 100, "stop": ["#"]}}
use_game_screenshots = False

[Language]
language = en
end_conversation_keyword = goodbye, bye, good-bye, good bye, good-by, good by, good to buy
goodbye_npc_response = Safe travels
collecting_thoughts_npc_response = I need to gather my thoughts for a moment
follow_npc_response = Follow
inventory_npc_response = Inventory
offended_npc_response = Offended
forgiven_npc_response = Forgiven

[Prompts]
skyrim_prompt = You are {{name}}, and you live in Skyrim. This is your background: {{bio}}
    Sometimes in-game events will be passed before the player response within brackets. You cannot respond with brackets yourself, they only exist to give context. Here is an example:
    (The player picked up a pair of gloves)
    Who do you think these belong to?
    You are having a conversation with {{player_name}} (the player) who is {{trust}} in {{location}}. {{player_name}} {{player_description}} {{player_equipment}} {{equipment}}
    This conversation is a script that will be spoken aloud, so please keep your responses appropriately concise and avoid text-only formatting such as numbered lists.
    The time is {{time}} {{time_group}}.
    {{weather}}
    Remember to stay in character.
    {{actions}}
    The conversation takes place in {{language}}.
    {{conversation_summary}}

skyrim_multi_npc_prompt = The following is a conversation in {{location}} in Skyrim between {{names_w_player}}. {{player_name}} {{player_description}} {{player_equipment}}
    Here are their backgrounds:
    {{bios}}
    {{equipment}}
    And here are their conversation histories:
    {{conversation_summaries}}
    The time is {{time}} {{time_group}}.
    {{weather}}
    You are tasked with providing the responses for the NPCs. Please begin your response with an indication of who you are speaking as, for example: '{{name}}: Good evening.'.
    Please use your own discretion to decide who should speak in a given situation (sometimes responding with all NPCs is suitable).
    {{actions}}
    Remember, you can only respond as {{names}}. Ensure to use their full name when responding.
    The conversation takes place in {{language}}.

skyrim_radiant_prompt = The following is a conversation in {{location}} in Skyrim between {{names}}.
    Here are their backgrounds:
    {{bios}}
    {{conversation_summaries}}
    The time is {{time}} {{time_group}}.
    {{weather}}
    You are tasked with providing the responses for the NPCs. Please begin your response with an indication of who you are speaking as, for example: '{{name}}: Good evening.'.
    Please use your own discretion to decide who should speak in a given situation (sometimes responding with all NPCs is suitable).
    {{actions}}
    Remember, you can only respond as {{names}}. Ensure to use their full name when responding.
    The conversation takes place in {{language}}.

fallout4_prompt = You are {{name}}, and you live in the post-apocalyptic Commonwealth of Fallout. This is your background: {{bio}}
    Sometimes in-game events will be passed before the player response within. You cannot respond with brackets yourself, they only exist to give context. Here is an example:
    (The player picked up a pair of gloves)
    Who do you think these belong to?
    You are having a conversation with {{trust}} (the player) in {{location}}.
    This conversation is a script that will be spoken aloud, so please keep your responses appropriately concise and avoid text-only formatting such as numbered lists.
    {{actions}}
    The time is {{time}} {{time_group}}.
    The conversation takes place in {{language}}.
    {{conversation_summary}}

fallout4_multi_npc_prompt = The following is a conversation in {{location}} in the post-apocalyptic Commonwealth of Fallout between {{names_w_player}}. Here are their backgrounds:
    {{bios}}
    And here are their conversation histories: {{conversation_summaries}}
    The time is {{time}} {{time_group}}.
    You are tasked with providing the responses for the NPCs. Please begin your response with an indication of who you are speaking as, for example: '{{name}}: Good evening.'.
    Please use your own discretion to decide who should speak in a given situation (sometimes responding with all NPCs is suitable).
    {{actions}}
    Remember, you can only respond as {{names}}. Ensure to use their full name when responding.
    The conversation takes place in {{language}}.

fallout4_radiant_prompt = The following is a conversation in {{location}} in the post-apocalyptic Commonwealth of Fallout between {{names}}. Here are their backgrounds: {{bios}}
    And here are their conversation histories: {{conversation_summaries}}
    The time is {{time}} {{time_group}}.
    You are tasked with providing the responses for the NPCs. Please begin your response with an indication of who you are speaking as, for example: '{{name}}: Good evening.'.
    Please use your own discretion to decide who should speak in a given situation (sometimes responding with all NPCs is suitable).
    {{actions}}
    Remember, you can only respond as {{names}}. Ensure to use their full name when responding.
    The conversation takes place in {{language}}.

memory_prompt = You are tasked with summarizing the conversation between {{name}} (the assistant) and the player (the user) / other characters. These conversations take place in {{game}}.
    It is not necessary to comment on any mixups in communication such as mishearings. Text contained within brackets state in-game events.
    Please summarize the conversation into a single paragraph in {{language}}.

resummarize_prompt = You are tasked with summarizing the conversation history between {{name}} (the assistant) and the player (the user) / other characters. These conversations take place in {{game}}.
    Each paragraph represents a conversation at a new point in time. Please summarize these conversations into a single paragraph in {{language}}.

vision_prompt = This image is to give context and is from the player's point of view in the game of {{game}}.
    Describe the details visible inside it without mentioning the game. Refer to it as a scene instead of an image.

radiant_start_prompt = Please begin / continue a conversation topic (greetings are not needed). Ensure to change the topic if the current one is losing steam.
    The conversation should steer towards topics which reveal information about the characters and who they are, or instead drive forward previous conversations in their memory.

radiant_end_prompt = Please wrap up the current topic between the NPCs in a natural way. Nobody is leaving, so there is no need for formal goodbyes.

[Startup]
auto_launch_ui = True
play_startup_sound = True
remove_mei_folders = True

[Other]
automatic_greeting = True
active_actions = Follow, Inventory, Offended, Forgiven
max_count_events = 5
events_refresh_time = 10
hourly_time = False
player_character_description = {player_description}
voice_player_input = False
player_voice_model =
save_audio_data_to_character_folder = False
port = {port}
show_http_debug_messages = False
advanced_logs = True
"""

def inject_safely(file_path, settings_dict, log_callback=None):
    """
    The 'Nuclear Option' Configuration Injector (v7.1).
    Writes a fully schema-compliant INI for Mantella 0.13.1.
    """
    
    path = Path(file_path)
    
    def _log(msg):
        log.info(f"[INJECTOR] {msg}")
        if log_callback: log_callback(f"[INJECTOR] {msg}")

    _log(f"Targeting: {path}")

    # --- PHASE 1: PREPARATION ---
    if not path.parent.exists():
        try:
            os.makedirs(path.parent)
            _log("Target directory created.")
        except Exception as e:
            _log(f"CRITICAL: Cannot create directory {path.parent}: {e}")
            return False

    # --- PHASE 2: PARAMETER MAPPING ---
    
    # DETERMINE OLLAMA URI
    # If using Proxy, we point llm_api to the local Proxy URL.
    ollama_host = settings_dict.get("ollama_host", "127.0.0.1")
    ollama_port = settings_dict.get("ollama_port", "11434") # Usually ignored if we force Proxy
    
    # We default to pointing to our Proxy (5001) unless specified otherwise.
    # The 'port' key in settings_dict usually comes from 'target_game_port' (4999), 
    # but 'ollama_port' comes from 'target_proxy_port' (5001).
    proxy_port_val = settings_dict.get("ollama_port", "5001")
    
    # Construct the API URL. 
    # Since we are emulating OpenAI, we point to the root. 
    # Bridge Server handles /chat/completions appending.
    llm_api_val = f"http://{ollama_host}:{proxy_port_val}"
    
    safe_data = {
        "model": settings_dict.get("model", "dolphin-llama3:8b"),
        "tokens": settings_dict.get("tokens", "4096"),
        "game_mode": settings_dict.get("game_mode", "SkyrimSE"),
        "vision_enabled": str(settings_dict.get("vision_enabled", "False")).capitalize(),
        "vision_model": settings_dict.get("vision_model", "llava:latest"),
        "tts_service": settings_dict.get("tts_service", "Piper"),
        "xvasynth_path": settings_dict.get("xvasynth_path", ""),
        
        
        # KEY NETWORK MAPPINGS
        "llm_api": llm_api_val,
        "port": settings_dict.get("port", "4999"),
        
        # PATH MAPPINGS
        "mod_root": settings_dict.get("mod_root", r"C:\Modding\MO2\Skyrim\mods\Mantella"),
        
        # PLAYER LORE
        "player_description": settings_dict.get("player_description", "")
    }

    # GENERATE THE CONTENT
    try:
        file_content = MANTELLA_TEMPLATE.format(**safe_data)
        _log("Schema-Compliant Configuration generated.")
    except Exception as e:
        _log(f"FATAL: Template formatting failed. {e}")
        return False

    # --- PHASE 3: THE WRITE ---

    # Unlock
    if path.exists():
        try: os.chmod(path, stat.S_IWRITE)
        except: pass 

    # Write
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(file_content)
        _log("SUCCESS: Injection complete.")
        return True
    except Exception as e:
        _log(f"Write failed: {e}")
        return False