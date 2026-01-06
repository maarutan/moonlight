import re
from pathlib import Path

from utils.constants import Const

scss = Path(Const.STYLESHEET_SCSS_DIR / "_theme.scss").read_text()

pattern = r"\$([\w-]+):\s*([^;]+);"
matches = re.findall(pattern, scss)

col = {name: value.strip() for name, value in matches}


def resolve_var(name: str, colors_dict: dict, seen=None) -> str | None:
    if seen is None:
        seen = set()
    if name in seen:
        return None
    seen.add(name)

    val = colors_dict.get(name)
    if not val:
        return None

    val = val.strip()
    if val.startswith("$"):
        return resolve_var(val[1:], colors_dict, seen)
    return val


colors = {k: resolve_var(k, col) or col[k] for k in col}
