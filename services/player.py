import gi
import json

gi.require_version("Playerctl", "2.0")
from gi.repository import Playerctl  # type: ignore


class PlayerManager:
    def __init__(self) -> None:
        self.players: dict[str, Playerctl.Player] = {}
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
                print(f"Поставлен на паузу: {name}")
            except Exception as e:
                print(f"Ошибка при попытке поставить на паузу '{name}': {e}")
        else:
            print(f"Плеер '{name}' не найден.")

    def play_player(self, name: str):
        player = self.players.get(name)
        if player:
            try:
                player.play()
                print(f"Воспроизведение: {name}")
            except Exception as e:
                print(f"Ошибка при попытке воспроизвести '{name}': {e}")
        else:
            print(f"Плеер '{name}' не найден.")

    def pause_all(self):
        for name, player in self.players.items():
            if player.props.playback_status == Playerctl.PlaybackStatus.PLAYING:
                try:
                    player.pause()
                    print(f"[Pause] {name}")
                except Exception as e:
                    print(f"[Pause Error] {name}: {e}")

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


# if __name__ == "__main__":
#     manager = PlayerManager()
#
#     print("🎵 Активные плееры:")
#     for pname in manager.players:
#         print(" •", pname)
#
#     print("\n▶️ Приостанавливаю воспроизведение...")
#     manager.pause_player("spotify")
#
#     print("\n📊 Статус:")
#     print(json.dumps(manager._get_playing_players(), indent=2))
