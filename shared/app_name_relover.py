from typing import Optional, Dict
from pathlib import Path
import re
from gi.repository import GLib  # type: ignore


def _normalize(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", (s or "").casefold())


def _token_set(s: str) -> set:
    return set(p for p in re.split(r"[^a-z0-9]+", (s or "").casefold()) if p)


class AppNameResolver:
    @staticmethod
    def _parse_desktop_file(path: str) -> Dict[str, str]:
        data: Dict[str, str] = {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                in_entry = False
                for raw in f:
                    line = raw.strip()
                    if not line or line.startswith("#"):
                        continue
                    if line.startswith("["):
                        in_entry = line.lower().startswith("[desktop entry")
                        continue
                    if not in_entry:
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        data[k.strip()] = v.strip()
        except Exception:
            pass
        return data

    @classmethod
    def resolve_name(cls, window_class: str) -> str:
        query = (window_class or "").strip()
        if not query:
            return "Unknown"

        search_dirs = [Path(GLib.get_user_data_dir()) / "applications"]
        search_dirs += [Path(d) / "applications" for d in GLib.get_system_data_dirs()]

        candidates = []
        for d in search_dirs:
            if d.exists():
                try:
                    candidates.extend(f for f in d.iterdir() if f.is_file())
                except Exception:
                    continue

        best_score = 0.0
        best_name: Optional[str] = None
        q_norm = _normalize(query)
        q_tokens = _token_set(query)

        for f in candidates:
            parsed = cls._parse_desktop_file(str(f))
            name = parsed.get("Name", "")
            icon = parsed.get("Icon", "")
            wm = parsed.get("StartupWMClass", "")
            exec_line = parsed.get("Exec", "")

            score = 0.0

            if wm and _normalize(wm) == q_norm:
                score = 1.0

            if score < 1.0:
                stem = f.stem
                if stem and stem.casefold() == query.casefold():
                    score = max(score, 0.98)

            if score < 0.98 and icon:
                if icon == query or _normalize(icon) == q_norm:
                    score = max(score, 0.97)

            if score < 0.97 and exec_line:
                exec_bin = Path(exec_line.split()[0]).name
                if _normalize(exec_bin) == q_norm:
                    score = max(score, 0.95)

            if score < 0.95 and name:
                name_tokens = _token_set(name)
                inter = q_tokens.intersection(name_tokens)
                if inter:
                    score = max(
                        score,
                        len(inter) / max(len(q_tokens.union(name_tokens)), 1) * 0.8,
                    )

            if score > best_score and name:
                best_score = score
                best_name = name

        return best_name or query
