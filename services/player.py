import gi
import json

gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl  # type: ignore


class PlayerManager:
    def __init__(self) -> None:
        self.players = {}
        self.callbacks = []
        self._init_players()

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
                return {}

        return result

    def _init_players(self):
        names = Playerctl.list_players()
        for name in names:
            player = Playerctl.Player.new_from_name(name)
            player.connect("playback-status", self._on_playback_status)
            self.players[name] = player

    def _on_playback_status(self, player, status):
        for cb in self.callbacks:
            cb()

    def add_status_callback(self, callback):
        self.callbacks.append(callback)

    def is_any_playing(self):
        for player in self.players.values():
            if player.props.playback_status == Playerctl.PlaybackStatus.PLAYING:
                return True
        return False


if __name__ == "__main__":
    PlayerManager()
