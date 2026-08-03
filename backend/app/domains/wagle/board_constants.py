"""Shared sentinel identifying the family board Room (W7.5 Phase D
REUSE-WAGLE-ROOMS-AS-BOARD / SLICE-WAGLE-BOARD-REACTIONS). A board is a
plain `WagleRoom` with this reserved title -- never shown to the user, the
Screen renders its own "가족 게시판" heading regardless.

Must match `FAMILY_BOARD_ROOM_TITLE` /
`BOARD_ROOM_TITLE` in `frontend/src/platform/wagle/board/WagleBoardPage.tsx`
exactly; there is no shared-schema mechanism between the two runtimes for a
plain string sentinel, so this value is intentionally duplicated in both
places rather than invented independently -- if one changes, the other
must change with it.
"""
FAMILY_BOARD_ROOM_TITLE = "__family_board__"
