import sys
from pathlib import Path
from rich import print

ROOT = Path(__file__).parent.parent

if ROOT.as_posix() not in sys.path:
    sys.path.append(ROOT.as_posix())


class Toster:
    def __init__(self, function):
        print(f"[bold blue]🧪 {function.__name__}[/bold blue] ...", end=" ")
        try:
            function()
            print("[green]✅ ok[/green]")
        except AssertionError as e:
            print(f"[red]❌ fail[/red]\n   {e}")
        except Exception as e:
            print(f"[yellow]💥 error[/yellow]\n   {type(e).__name__}: {e}")
