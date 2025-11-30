import json
import re
from pathlib import Path
from typing import Any, List
from utils.decorators import singletonclass


class JsoncParseError(Exception):
    def __init__(
        self,
        path: Path,
        lineno: int,
        colno: int,
        msg: str,
        snippet: str,
        hints: List[str] | None = None,
    ) -> None:
        super().__init__(
            f"Parse error in '{path}': line {lineno}, column {colno}: {msg}"
        )
        self.path = path
        self.lineno = lineno
        self.colno = colno
        self.msg = msg
        self.snippet = snippet
        self.hints = hints or []

    def pretty(self) -> str:
        lines = []
        lines.append(f"<red><bold>┌─ JSON parse error</bold></red>")
        lines.append(f"<red>│</red> File   : <cyan>{self.path}</cyan>")
        lines.append(f"<red>│</red> Line   : <yellow>{self.lineno}</yellow>")
        lines.append(f"<red>│</red> Column : <yellow>{self.colno}</yellow>")
        lines.append(f"<red>│</red> Reason : <magenta>{self.msg}</magenta>")
        lines.append(f"<red>├─ Snippet</red>")
        for l in self.snippet.splitlines():
            if l.strip().endswith("^"):
                lines.append(f"<red>│</red> <green>{l}</green>")
            else:
                lines.append(f"<red>│</red> {l}")
        if self.hints:
            lines.append(f"<red>├─ Hints</red>")
            for h in self.hints:
                lines.append(f"<red>│</red> • {h}")
        lines.append(f"<red>└──────────────────────────────────────────────────</red>")
        return "\n".join(lines)


@singletonclass
class Jsonc:
    _surrogate_pair_re = re.compile(
        r"\\u(d[89ab][0-9a-fA-F]{2})\\u(d[cdef][0-9a-fA-F]{2})", re.IGNORECASE
    )
    _single_esc_re = re.compile(r"\\u([0-9a-fA-F]{4})")

    def _decode_u_escapes_str(self, s: str) -> str:
        def repl_pair(m):
            hi = int(m.group(1), 16)
            lo = int(m.group(2), 16)
            cp = 0x10000 + ((hi - 0xD800) << 10) + (lo - 0xDC00)
            return chr(cp)

        def repl_single(m):
            return chr(int(m.group(1), 16))

        if "\\u" not in s:
            return s
        s = self._surrogate_pair_re.sub(repl_pair, s)
        s = self._single_esc_re.sub(repl_single, s)
        return s

    def _decode_u_escapes_any(self, obj: Any) -> Any:
        if isinstance(obj, str):
            return self._decode_u_escapes_str(obj)
        if isinstance(obj, list):
            return [self._decode_u_escapes_any(x) for x in obj]
        if isinstance(obj, dict):
            return {k: self._decode_u_escapes_any(v) for k, v in obj.items()}
        return obj

    def read(self, path: Path | str) -> dict:
        path = Path(path)
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            return {}
        clean = self._strip_comments(raw)
        clean = self._remove_trailing_commas(clean)
        try:
            data = self.loads(clean)
        except json.JSONDecodeError as e:
            snippet = self._format_error_snippet(clean, e.lineno, e.colno, 2)
            hints = self._diagnose_json_error(clean, e.lineno, e.colno, e.msg)
            raise JsoncParseError(path, e.lineno, e.colno, e.msg, snippet, hints)
        if isinstance(data, dict):
            return self._decode_u_escapes_any(data)
        return {}

    def get_path(
        self, path: Path | str, keypath: str, default: Any = None
    ) -> tuple[Any, bool]:
        data = Jsonc.get_data(Path(path))
        d: Any = data
        for k in keypath.split("."):
            if not isinstance(d, dict) or k not in d:
                return default, False
            d = d[k]
        return d, True

    def get_data(self, path: Path | str) -> dict:
        p = Path(path)
        if not p.exists():
            return {}
        return self.read(p)

    def update(self, path: Path | str, keypath: str, new_value: Any) -> bool:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        span = self._find_value_span_jsonc(text, keypath.split("."))
        if span:
            v_start, v_end = span
            serialized = self._serialize_json_literal(new_value)
            new_text = text[:v_start] + serialized + text[v_end:]
            if new_text != text:
                path.write_text(new_text, encoding="utf-8")
                return True
            return False
        data = self.get_data(path)
        d = data
        keys = keypath.split(".")
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        if d.get(keys[-1]) == new_value:
            return False
        d[keys[-1]] = new_value
        self.write(path, data)
        return True

    def append(self, path: Path, keypath: str, value: Any) -> bool:
        text = path.read_text(encoding="utf-8")
        segs = keypath.split(".")
        span = self._find_value_span_jsonc(text, segs)
        if span:
            start, end = span
            j = self._skip_ws_and_comments(text, start)
            if j < len(text) and text[j] == "[":
                serialized = self._serialize_json_literal(value)
                new_text = self._append_into_array_literal(text, j, end, serialized)
                if new_text != text:
                    path.write_text(new_text, encoding="utf-8")
                    return True
                return False
        data = self.get_data(path)
        d = data
        keys = segs
        for k in keys[:-1]:
            if k not in d or not isinstance(d[k], dict):
                d[k] = {}
            d = d[k]
        last = keys[-1]
        arr = d.get(last)
        if not isinstance(arr, list):
            d[last] = arr = []
        arr.append(value)
        self.write(path, data)
        return True

    def loads(self, content: str) -> dict:
        if not content.strip():
            return {}
        clean = self._strip_comments(content)
        clean = self._remove_trailing_commas(clean)
        return json.loads(clean)

    def length(self, data: dict) -> int:
        return len(data)

    def write(self, path: Path, data: dict, indent: int = 2) -> None:
        def default(o):
            if isinstance(o, Path):
                return str(o)
            return str(o)

        path.write_text(
            json.dumps(data, indent=indent, ensure_ascii=False, default=default),
            encoding="utf-8",
        )

    def dumps(self, content: Any, indent: int = 2) -> str:
        def default(o):
            if isinstance(o, Path):
                return str(o)
            return str(o)

        return json.dumps(content, indent=indent, ensure_ascii=False, default=default)

    def _strip_comments(self, raw: str) -> str:
        import io

        output = io.StringIO()
        inside_str = False
        prev_char = ""
        for line in raw.splitlines():
            new_line = ""
            i = 0
            while i < len(line):
                ch = line[i]
                if ch == '"' and prev_char != "\\":
                    inside_str = not inside_str
                if (
                    not inside_str
                    and ch == "/"
                    and i + 1 < len(line)
                    and line[i + 1] == "/"
                ):
                    break
                new_line += ch
                prev_char = ch
                i += 1
            output.write(new_line + "\n")
        return output.getvalue()

    def _remove_trailing_commas(self, s: str) -> str:
        return re.sub(r",(\s*[\]\}])", r"\1", s)

    def _serialize_json_literal(self, v: Any) -> str:
        if isinstance(v, str):
            return json.dumps(v, ensure_ascii=False)
        if v is True:
            return "true"
        if v is False:
            return "false"
        if v is None:
            return "null"
        return json.dumps(v, ensure_ascii=False, separators=(",", ":"))

    def _find_value_span_jsonc(self, s: str, segs: list[str]) -> tuple[int, int] | None:
        n = len(s)

        def skip_ws_and_comments(j: int) -> int:
            return self._skip_ws_and_comments(s, j)

        def scan_string(j: int) -> int:
            assert s[j] == '"'
            j += 1
            while j < n:
                ch = s[j]
                if ch == "\\":
                    j += 2
                    continue
                if ch == '"':
                    return j + 1
                j += 1
            return j

        def read_string_value(j: int) -> tuple[str, int]:
            j0 = j
            j = scan_string(j)
            raw = s[j0:j]
            try:
                val = json.loads(raw)
            except Exception:
                val = raw.strip('"')
            return val, j

        def find_value_end(j: int) -> int:
            j = skip_ws_and_comments(j)
            if j >= n:
                return j
            ch = s[j]
            if ch == '"':
                return scan_string(j)
            if ch == "{":
                depth = 0
                k = j
                in_str = False
                esc = False
                in_line_comment = False
                while k < n:
                    c = s[k]
                    if in_line_comment:
                        if c == "\n":
                            in_line_comment = False
                        k += 1
                        continue
                    if not in_str:
                        if c == "/" and k + 1 < n and s[k + 1] == "/":
                            in_line_comment = True
                            k += 2
                            continue
                        if c == "{":
                            depth += 1
                        elif c == "}":
                            depth -= 1
                            if depth == 0:
                                return k + 1
                        elif c == '"':
                            in_str = True
                    else:
                        if not esc and c == '"':
                            in_str = False
                            esc = False
                        elif c == "\\" and not esc:
                            esc = True
                            k += 1
                            continue
                        else:
                            esc = False
                    k += 1
                return k
            if ch == "[":
                depth = 0
                k = j
                in_str = False
                esc = False
                in_line_comment = False
                while k < n:
                    c = s[k]
                    if in_line_comment:
                        if c == "\n":
                            in_line_comment = False
                        k += 1
                        continue
                    if not in_str:
                        if c == "/" and k + 1 < n and s[k + 1] == "/":
                            in_line_comment = True
                            k += 2
                            continue
                        if c == "[":
                            depth += 1
                        elif c == "]":
                            depth -= 1
                            if depth == 0:
                                return k + 1
                        elif c == '"':
                            in_str = True
                    else:
                        if not esc and c == '"':
                            in_str = False
                            esc = False
                        elif c == "\\" and not esc:
                            esc = True
                            k += 1
                            continue
                        else:
                            esc = False
                    k += 1
                return k
            k = j
            while k < n and s[k] not in ",}\n]":
                k += 1
            return k

        def find_in_object(j: int, key: str) -> tuple[int, int] | None:
            j += 1
            while True:
                j = skip_ws_and_comments(j)
                if j >= n:
                    return None
                if s[j] == "}":
                    return None
                if s[j] != '"':
                    j += 1
                    continue
                kname, j2 = read_string_value(j)
                j = skip_ws_and_comments(j2)
                if j >= n or s[j] != ":":
                    j += 1
                    continue
                j += 1
                if kname == key:
                    v_start = skip_ws_and_comments(j)
                    v_end = find_value_end(v_start)
                    return (v_start, v_end)
                v_start = skip_ws_and_comments(j)
                v_end = find_value_end(v_start)
                j = v_end
                while j < n and s[j] not in ",}":
                    j += 1
                if j < n and s[j] == ",":
                    j += 1
                    continue
                if j < n and s[j] == "}":
                    return None

        i = self._skip_ws_and_comments(s, 0)
        if i >= n or s[i] != "{":
            return None
        cur = i
        for idx, seg in enumerate(segs):
            span = find_in_object(cur, seg)
            if span is None:
                return None
            v_start, v_end = span
            if idx == len(segs) - 1:
                return (v_start, v_end)
            j = self._skip_ws_and_comments(s, v_start)
            if j >= n or s[j] != "{":
                return None
            cur = j
        return None

    def _skip_ws_and_comments(self, s: str, j: int) -> int:
        n = len(s)
        in_line_comment = False
        while j < n:
            ch = s[j]
            if in_line_comment:
                if ch == "\n":
                    in_line_comment = False
                j += 1
                continue
            if ch in " \t\r\n":
                j += 1
                continue
            if ch == "/" and j + 1 < n and s[j + 1] == "/":
                in_line_comment = True
                j += 2
                continue
            break
        return j

    def _append_into_array_literal(
        self, s: str, arr_start: int, arr_end: int, item: str
    ) -> str:
        assert s[arr_start] == "["
        assert s[arr_end - 1] == "]"
        j = self._skip_ws_and_comments(s, arr_start + 1)
        if j < arr_end and s[j] == "]":
            insert = item
            return s[: arr_end - 1] + insert + s[arr_end - 1 :]
        insert = ", " + item
        return s[: arr_end - 1] + insert + s[arr_end - 1 :]

    def _format_error_snippet(
        self, text: str, lineno: int, colno: int, context: int = 2
    ) -> str:
        lines = text.splitlines()
        idx = max(0, min(lineno - 1, len(lines) - 1))
        start = max(0, idx - context)
        end = min(len(lines), idx + context + 1)
        width = len(str(end))
        out = []
        for i in range(start, end):
            num = str(i + 1).rjust(width)
            line = lines[i]
            out.append(f"{num} | {line}")
            if i == idx:
                caret = " " * max(0, colno - 1)
                out.append(f"{' ' * width} | {caret}^")
        return "\n".join(out)

    def _diagnose_json_error(
        self, text: str, lineno: int, colno: int, msg: str
    ) -> list[str]:
        hints: list[str] = []
        lines = text.splitlines()
        line = lines[lineno - 1] if 0 <= lineno - 1 < len(lines) else ""

        if "Expecting property name enclosed in double quotes" in msg:
            m = re.search(r"^\s*([A-Za-z_][\w\-]*)\s*:", line)
            if m:
                key = m.group(1)
                hints.append(f'Key {key} must be quoted: "{key}": ...')
            hints.append(
                "Check for a trailing comma before the closing '}' or ']' on the previous line."
            )

        if "Expecting ',' delimiter" in msg:
            hints.append(
                "A comma may be missing between fields. Add ',' after the previous item."
            )

        if "Unterminated string" in msg:
            hints.append(
                'Unterminated string. Ensure quotes are paired and inner quotes are escaped: \\".'
            )

        if "Invalid control character" in msg:
            hints.append(
                "Invalid control character. Escape backslashes and specials: '\\\\', '\\n', '\\t'."
            )

        if "Expecting value" in msg:
            hints.append(
                "Expecting value. Ensure a valid value appears after ':' and there is no stray comma."
            )

        return hints
