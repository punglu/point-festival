from pydantic import BaseModel, Field

# Fixed key set, matching the canonical 2n Screen's real toggle items
# (its "시간대" row has no toggle at all -- static detail text, not a
# preference -- and is deliberately absent here).
KNOWN_KEYS = (
    "notify_all",
    "mission_decision",
    "point_change",
    "levelup_badge",
    "family_message",
    "schedule_reminder",
    "album_new_photo",
    "quiet_hours",
)

# Defaults match the canonical Screen's own fixture exactly, so a first-time
# reader (no rows yet) sees the same starting state the frozen design shows.
DEFAULTS: dict[str, bool] = {
    "notify_all": True,
    "mission_decision": True,
    "point_change": True,
    "levelup_badge": False,
    "family_message": True,
    "schedule_reminder": True,
    "album_new_photo": False,
    "quiet_hours": True,
}


class PreferenceEntry(BaseModel):
    pref_key: str = Field(pattern="^(" + "|".join(KNOWN_KEYS) + ")$")
    enabled: bool


class PreferencesReplace(BaseModel):
    preferences: list[PreferenceEntry] = Field(max_length=len(KNOWN_KEYS))


class PreferenceOut(BaseModel):
    pref_key: str
    enabled: bool
