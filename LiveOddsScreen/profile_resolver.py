import json
from pathlib import Path
from typing import Optional, Tuple


def resolve_chrome_profile() -> Tuple[Optional[str], Optional[str]]:
    """Return (chrome_user_data_dir, chrome_profile_dir) with robust fallbacks.

    Preference order:
    1) LiveOddsScreen/config.json values if present
    2) backend/config.json pto values if present
    3) Known local default PTO profile path used by the user
    """
    # 1) Try LiveOddsScreen/config.json
    local_cfg = Path("LiveOddsScreen/config.json")
    if local_cfg.exists():
        try:
            cfg = json.loads(local_cfg.read_text(encoding="utf-8"))
            cud = cfg.get("chrome_user_data_dir")
            cpd = cfg.get("chrome_profile_dir")
            if cud:
                return cud, (cpd or "Profile 1")
        except Exception:
            pass

    # 2) Fall back to backend/config.json -> pto
    backend_cfg = Path("backend/config.json")
    if backend_cfg.exists():
        try:
            cfg = json.loads(backend_cfg.read_text(encoding="utf-8"))
            pto = cfg.get("pto", {})
            cud = pto.get("chrome_user_data_dir")
            cpd = pto.get("chrome_profile_dir")
            if cud:
                return cud, (cpd or "Profile 1")
        except Exception:
            pass

    # 3) Fallback to user-known PTO profile path
    default_user_profile = r"C:\\Users\\steph\\AppData\\Local\\PTO_Chrome_Profile"
    if Path(default_user_profile).exists():
        return default_user_profile, "Profile 1"

    # As a last resort, return None values
    return None, None

