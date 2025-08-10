import gi
import json
import subprocess
from time import sleep

from loguru import logger

gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl  # type: ignore


class PlayerManager:
    def __init__(self) -> None:
        self.players: dict[str, Playerctl.Player] = {}
        self.callbacks = []
        self._init_players()
        # print(self._get_playing_players())
        # print(self.players)

    def _get_playing_players(self) -> dict:
        try:
            names = Playerctl.list_players()
        except Exception:
            return {}

        result = {"players": {}}

        for name in names:
            try:
                player = Playerctl.Player.new_from_name(name)
                if player.props.playback_status != Playerctl.PlaybackStatus.PLAYING:
                    continue

                metadata = dict(player.props.metadata)

                title = metadata.get("xesam:title", "Unknown")
                artist = metadata.get("xesam:artist", ["Unknown"])[0]
                album = metadata.get("xesam:album", "Unknown")
                url = metadata.get("xesam:url", None)
                art_url = metadata.get("mpris:artUrl", None)
                length_usec = metadata.get("mpris:length", 0)

                position_usec = player.get_position()
                position_sec = position_usec / 1_000_000
                length_sec = length_usec / 1_000_000 if length_usec else 0

                result["players"][player.props.player_name] = {
                    "title": title,
                    "artist": artist,
                    "album": album,
                    "url": url,
                    "art_url": art_url,
                    "positions": {
                        "second": round(position_sec, 2),
                        "minute": round(position_sec / 60, 2),
                        "percent": round((position_sec / length_sec) * 100, 2)
                        if length_sec
                        else 0,
                        "duration": round(length_sec, 2),
                    },
                }
            except Exception:
                continue

        return result

    def _init_players(self):
        names = Playerctl.list_players()
        for name in names:
            try:
                player = Playerctl.Player.new_from_name(name)
                player.connect("playback-status", self._on_playback_status)
                # ключ по player_name (короткому)
                self.players[player.props.player_name] = player
            except Exception as e:
                print(f"[Init Error] {name}: {e}")

    def _on_playback_status(self, player, status):
        for cb in self.callbacks:
            cb()

    def add_status_callback(self, callback):
        self.callbacks.append(callback)

    def is_any_playing(self) -> bool:
        return any(
            player.props.playback_status == Playerctl.PlaybackStatus.PLAYING
            for player in self.players.values()
        )

    def pause_player(self, name: str):
        player = self.players.get(name)
        if player:
            try:
                player.pause()
                logger.debug(f"[ Player ] Paused: {name}")
            except Exception as e:
                logger.warning(f"[ Player ] Error pausing '{name}': {e}")
        else:
            logger.warning(f"[ Player ] '{name}' not found.")

    def play_player(self, name: str):
        player = self.players.get(name)
        if player:
            try:
                player.play()
                logger.debug(f"[ Player ] Played: {name}")
            except Exception as e:
                logger.warning(f"[ Player ] Error playing '{name}': {e}")
        else:
            logger.warning(f"[ Player ] '{name}' not found.")

    def pause_all(self):
        for name, player in self.players.items():
            if player.props.playback_status == Playerctl.PlaybackStatus.PLAYING:
                try:
                    player.pause()
                    print(f"[Pause] {name}")
                except Exception as e:
                    print(f"[Pause Error] {name}: {e}")

    def pause_all_except(self, exclude_names):
        for name, player in self.players.items():
            if (
                player.props.playback_status == Playerctl.PlaybackStatus.PLAYING
                and name not in exclude_names
            ):
                try:
                    player.pause()
                    print(f"[Pause] {name}")
                except Exception as e:
                    print(f"[Pause Error] {name}: {e}")
            else:
                self.play_player(name)

    def _refresh_players(self):
        try:
            current_names = set(Playerctl.list_players())
        except Exception:
            current_names = set()

        existing_names = set(self.players.keys())
        removed = existing_names - current_names

        for name in removed:
            player = self.players.pop(name, None)
            if player is not None:
                try:
                    player.disconnect_by_func(self._on_playback_status)
                except Exception:
                    pass

        added = current_names - existing_names
        for name in added:
            try:
                player = Playerctl.Player.new_from_name(name)
                player.connect("playback-status", self._on_playback_status)
                self.players[player.props.player_name] = player
            except Exception:
                pass

    def is_playing(self) -> bool:
        return any(
            player.props.playback_status == Playerctl.PlaybackStatus.PLAYING
            for player in self.players.values()
        )

    def next_for(self, name: str):
        try:
            pname = Playerctl.PlayerName(name)
            player = Playerctl.Player.new_from_name(pname)
        except Exception as exc:
            logger.warning(f"[Player] No such player-name: «{name}», exc: {exc}")
            return

        try:
            player.next()
            logger.debug(f"[Player] Skipped to previous on «{name}»")
        except Exception as exc:
            logger.warning(f"[Player] Could not skip previous on «{name}»: {exc}")

    def prev_for(self, name: str):
        try:
            pname = Playerctl.PlayerName(name)
            player = Playerctl.Player.new_from_name(pname)
        except Exception as exc:
            logger.warning(f"[Player] No such player-name: «{name}», exc: {exc}")
            return

        try:
            player.previous()
            logger.debug(f"[Player] Skipped to previous on «{name}»")
        except Exception as exc:
            logger.warning(f"[Player] Could not skip previous on «{name}»: {exc}")

    def _seek_player(self, name: str, seconds: int):
        try:
            subprocess.run(
                [
                    "playerctl",
                    "-p",
                    name,
                    "position",
                    f"{abs(seconds)}{'+' if seconds > 0 else '-'}",
                ]
            )
            logger.debug(f"[Hack] Seek: {seconds} seconds → {name}")
        except Exception as e:
            logger.warning(f"[Hack] Failed to seek : {e}")

    def player_forward_seconds(self, name: str, seconds: int = 5):
        self._seek_player(name, +seconds)

    def player_backward_seconds(self, name: str, seconds: int = 5):
        self._seek_player(name, -seconds)

    def get_progress(self, name: str) -> tuple[float, float]:
        self._refresh_players()
        player = self.players.get(name)
        if (
            not player
            or player.props.playback_status != Playerctl.PlaybackStatus.PLAYING
        ):
            return 0.0, 1.0

        pos_us = player.props.position or 0
        meta = dict(player.props.metadata)
        length_us = meta.get("mpris:length") or 0

        pos = min(
            max(pos_us / 1e6, 0.0), (length_us / 1e6) if length_us else float("inf")
        )
        length = (length_us / 1e6) if length_us else max(pos, 1.0)
        return pos, length

    def seek_to(self, name: str, microseconds: int) -> None:
        player = self.players.get(name)
        if not player:
            logger.warning(f"[Player] Player '{name}' not found for seek_to.")
            return

        try:
            track_id = player.props.metadata.get("mpris:trackid")
            if not track_id:
                logger.warning(f"[Player] track_id not found for player '{name}'.")
                return

            player.set_position(track_id, microseconds)
            logger.debug(f"[Player] Seeked to {microseconds} µs in player '{name}'.")
        except Exception as e:
            logger.warning(f"[Player] Failed to seek player '{name}': {e}")

    def get_options(self, name: str, key: str, default=""):
        for player in self._get_playing_players().values():
            for k, v in player.items():
                if k == name:
                    return v.get(key, default)


# from typing import Literal
# import gi
# import json
# import subprocess
# from loguru import logger
#
# gi.require_version("Playerctl", "2.0")
# from gi.repository import Playerctl  # type: ignore
#
#
# class PlayerManager:
#     def __init__(self): ...
#
#     def _get_playing_players(self) -> dict:
#         try:
#             names = Playerctl.list_players()
#         except Exception:
#             return {}
#
#         result = {}
#
#         for name in names:
#             try:
#                 player = Playerctl.Player.new_from_name(name)
#                 if player.props.playback_status != Playerctl.PlaybackStatus.PLAYING:
#                     continue
#
#                 metadata = dict(player.props.metadata)
#
#                 title = metadata.get("xesam:title", "Unknown")
#                 artist = metadata.get("xesam:artist", ["Unknown"])[0]
#                 album = metadata.get("xesam:album", "Unknown")
#                 url = metadata.get("xesam:url", None)
#                 art_url = metadata.get("mpris:artUrl", None)
#                 length_usec = metadata.get("mpris:length", 0)
#
#                 position_usec = player.get_position()
#                 position_sec = position_usec / 1_000_000
#                 length_sec = length_usec / 1_000_000 if length_usec else 0
#
#                 result[player.props.player_name] = {
#                     "title": title,
#                     "artist": artist,
#                     "album": album,
#                     "url": url,
#                     "art_url": art_url,
#                     "positions": {
#                         "second": round(position_sec, 2),
#                         "minute": round(position_sec / 60, 2),
#                         "percent": round((position_sec / length_sec) * 100, 2)
#                         if length_sec
#                         else 0,
#                         "duration": round(length_sec, 2),
#                     },
#                 }
#             except Exception:
#                 continue
#
#         return result
#
#     def get_options(
#         self,
#         player: str,
#         key: Literal[
#             "title",
#             "artist",
#             "album",
#             "url",
#             "art_url",
#             "positions",
#             "positions.second",
#             "positions.minute",
#             "positions.percent",
#             "positions.duration",
#         ],
#         default="",
#     ) -> str:
#         try:
#             players = self._get_playing_players()
#             if player not in players:
#                 return default
#
#             data = players[player]
#             if key.startswith("positions."):
#                 subkey = key.split(".", 1)[1]
#                 return data.get("positions", {}).get(subkey, default)
#
#             if key == "positions":
#                 return data.get("positions", default)
#
#             return str(data.get(key, default))
#
#         except Exception as e:
#             logger.debug(e)
#             return ""
#
#
# player_manager = PlayerManager()
# list_players = player_manager._get_playing_players()
# # print(
# #     player_manager.get_options(
# #         "firefox",
# #         "art_url",
# #     )
# # )
# print(json.dumps(list_players, indent=4))
