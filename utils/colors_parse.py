import re
from pathlib import Path
from utils.constants import Const

scss = Path(Const.THEME_SCSS).read_text()


pattern = r"\$([\w-]+):\s*(#[0-9a-fA-F]{6})"
colors = dict(re.findall(pattern, scss))
