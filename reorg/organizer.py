"""
organizer.py  v2.1
-------------------
Organiza archivos de una carpeta origen agrupándolos por extensión
en una carpeta destino. Interfaz visual con Rich.

Uso interactivo:  python organizer.py
Uso por args:     python organizer.py --src ORIGEN --dest DESTINO [--dry-run]
"""

import argparse
import shutil
import sys
from pathlib import Path
from collections import defaultdict

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.tree import Tree
from rich import box
from rich.text import Text

console = Console()

HOME = Path.home()

COMMON_PATHS = {
    "1": ("Downloads",  HOME / "Downloads"),
    "2": ("Desktop",    HOME / "Desktop"),
    "3": ("Documents",  HOME / "Documents"),
    "4": ("Pictures",   HOME / "Pictures"),
    "5": ("Music",      HOME / "Music"),
    "6": ("Videos",     HOME / "Videos"),
}

# Íconos por tipo de extensión
EXT_ICONS = {
    # Documentos
    "pdf": "📄", "doc": "📝", "docx": "📝", "txt": "📃", "xlsx": "📊",
    "xls": "📊", "pptx": "📋", "ppt": "📋", "csv": "📊",
    # Imágenes
    "jpg": "🖼️", "jpeg": "🖼️", "png": "🖼️", "gif": "🖼️", "svg": "🖼️",
    "webp": "🖼️", "bmp": "🖼️", "heic": "🖼️",
    # Video
    "mp4": "🎬", "mov": "🎬", "avi": "🎬", "mkv": "🎬", "wmv": "🎬",
    # Audio
    "mp3": "🎵", "wav": "🎵", "flac": "🎵", "aac": "🎵",
    # Código
    "py": "🐍", "js": "💛", "ts": "💙", "html": "🌐", "css": "🎨",
    "json": "📦", "xml": "📦", "yaml": "📦", "yml": "📦",
    # Comprimidos
    "zip": "🗜️", "rar": "🗜️", "7z": "🗜️", "tar": "🗜️", "gz": "🗜️",
    # Ejecutables
    "exe": "⚙️", "msi": "⚙️", "dmg": "⚙️", "pkg": "⚙️",
    # Fuentes
    "ttf": "🔤", "otf": "🔤", "woff": "🔤",
}

def get_icon(ext: str) -> str:
    return EXT_ICONS.get(ext.lower(), "📁")


# ── HELPERS ────────────────────────────────────────────────────────────────────

def collect_files(src: Path) -> list[Path]:
    # Solo archivos en el nivel raíz — las subcarpetas no se tocan
    return [f for f in src.iterdir() if f.is_file()]


def unique_dest(dest_dir: Path, filename: str) -> Path:
    candidate = dest_dir / filename
    if not candidate.exists():
        return candidate
    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_dir / f"{stem}_{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def human_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def agrupar_por_ext(files: list[Path]) -> dict:
    grupos = defaultdict(list)
    for f in files:
        ext = f.suffix.lstrip(".").lower() or "sin_extension"
        grupos[ext].append(f)
    return dict(sorted(grupos.items(), key=lambda x: -len(x[1])))


# ── PREVIEW ────────────────────────────────────────────────────────────────────

def mostrar_preview(grupos: dict) -> None:
    console.print()
    total_archivos = sum(len(v) for v in grupos.values())
    total_size     = sum(f.stat().st_size for v in grupos.values() for f in v)

    tbl = Table(
        title=f"[bold]Resumen — {total_archivos:,} archivos · {human_size(total_size)}[/]",
        box=box.ROUNDED, header_style="bold cyan", show_lines=False,
    )
    tbl.add_column("",      width=3,  justify="center")
    tbl.add_column("Tipo",  style="bold white",  min_width=14)
    tbl.add_column("Archivos", justify="right", style="green")
    tbl.add_column("Tamaño",   justify="right", style="dim")
    tbl.add_column("Ejemplo",  style="dim",     max_width=35)

    for ext, files in grupos.items():
        size  = sum(f.stat().st_size for f in files)
        ej    = files[0].name if files else ""
        tbl.add_row(
            get_icon(ext),
            ext,
            f"{len(files):,}",
            human_size(size),
            ej,
        )

    console.print(tbl)


# ── ORGANIZAR ──────────────────────────────────────────────────────────────────

def organize(src: Path, dest: Path, dry_run: bool = False) -> dict:
    files = collect_files(src)

    # Filtrar archivos que ya están dentro de dest
    files = [f for f in files if not _inside(f, dest)]

    if not files:
        console.print("[yellow]No se encontraron archivos para organizar.[/]")
        return {}

    grupos  = agrupar_por_ext(files)
    mostrar_preview(grupos)

    if dry_run:
        return grupos

    # Confirmar
    console.print()
    if not Confirm.ask(
        f"  ¿Proceder a mover [bold green]{len(files):,}[/] archivos a [cyan]{dest}[/]?",
        default=False,
    ):
        console.print("\n[yellow]Cancelado. No se movió nada.[/]")
        return {}

    # Mover con barra de progreso
    console.print()
    movidos = 0
    errores = 0

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed:,}/{task.total:,}"),
        TimeElapsedColumn(),
        console=console,
    ) as prog:
        t = prog.add_task("Organizando archivos…", total=len(files))

        for file in files:
            ext     = file.suffix.lstrip(".").lower() or "sin_extension"
            ext_dir = dest / ext
            target  = unique_dest(ext_dir, file.name)

            prog.update(t, description=f"[dim]{file.name[:40]}[/]")
            try:
                ext_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), target)
                movidos += 1
            except Exception as e:
                console.print(f"  [red]✗ {file.name}[/]: {e}")
                errores += 1
            prog.advance(t)

        prog.update(t, description="[green]✓[/] Completado")

    # Resultado final
    console.print()
    tbl_r = Table(box=box.SIMPLE, show_header=False, padding=(0, 2))
    tbl_r.add_column(style="dim"); tbl_r.add_column(justify="right")
    tbl_r.add_row("Archivos movidos",  f"[bold green]{movidos:,}[/]")
    if errores:
        tbl_r.add_row("Errores",       f"[bold red]{errores:,}[/]")
    tbl_r.add_row("Destino",           f"[cyan]{dest}[/]")
    console.print(tbl_r)

    return grupos


def _inside(file: Path, dest: Path) -> bool:
    try:
        file.relative_to(dest)
        return True
    except ValueError:
        return False


# ── SELECCIÓN DE DIRECTORIO ────────────────────────────────────────────────────

def pick_directory(titulo: str) -> Path:
    console.print(f"\n[bold cyan]{titulo}[/]")

    tbl = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    tbl.add_column(style="bold cyan", width=4)
    tbl.add_column(style="white",     width=14)
    tbl.add_column(style="dim")

    for key, (label, path) in COMMON_PATHS.items():
        estado = "" if path.exists() else "[red](no encontrada)[/]"
        tbl.add_row(f"[{key}]", label, f"{path}  {estado}")
    tbl.add_row("[0]", "Ruta manual", "Escribe la ruta completa")

    console.print(tbl)

    while True:
        choice = Prompt.ask("  Elige una opción").strip()

        if choice in COMMON_PATHS:
            _, path = COMMON_PATHS[choice]
            if not path.exists():
                console.print("  [red]Esa carpeta no existe en este equipo.[/]")
                continue
            return path

        if choice == "0":
            while True:
                raw  = Prompt.ask("  Pega la ruta completa").strip().strip('"')
                path = Path(raw).expanduser().resolve()
                if path.is_dir():
                    return path
                console.print(f"  [red]'{raw}' no es un directorio válido.[/]")

        console.print("  [red]Opción inválida.[/]")


# ── MAIN ───────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--src",     default=None)
    parser.add_argument("--dest",    default=None)
    parser.add_argument("--dry-run", action="store_true")
    args, _ = parser.parse_known_args()

    console.print(Panel(
        "[bold white]Organizador de Archivos  v2.1[/]\n"
        "[dim]Agrupa tus archivos por tipo en una carpeta destino[/]",
        style="bold blue", expand=False,
    ))

    # Modo args (headless)
    if args.src and args.dest:
        src  = Path(args.src).resolve()
        dest = Path(args.dest).resolve()
        for path, label in ((src, "origen"), (dest, "destino")):
            if not path.is_dir():
                console.print(f"[red]Error:[/] '{path}' no es un directorio válido ({label}).")
                sys.exit(1)
        organize(src, dest, dry_run=args.dry_run)
        return

    # Modo interactivo
    src  = pick_directory("¿Desde qué carpeta quieres organizar?")
    dest = pick_directory("¿A qué carpeta quieres mover los archivos organizados?")

    console.print(f"\n  [dim]Origen :[/] [bold]{src}[/]")
    console.print(f"  [dim]Destino:[/] [bold]{dest}[/]")

    # Preview automático
    console.print("\n[bold cyan]Vista previa[/] [dim](nada se moverá todavía)[/]")
    files = [f for f in collect_files(src) if not _inside(f, dest)]
    if not files:
        console.print("[yellow]No se encontraron archivos.[/]")
        return

    grupos = agrupar_por_ext(files)
    mostrar_preview(grupos)

    console.print()
    if not Confirm.ask(
        f"  ¿Mover [bold green]{len(files):,}[/] archivos a [cyan]{dest}[/]?",
        default=False,
    ):
        console.print("\n[yellow]Cancelado.[/]")
        return

    # Mover
    movidos = errores = 0
    console.print()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("{task.completed:,}/{task.total:,}"),
        TimeElapsedColumn(),
        console=console,
    ) as prog:
        t = prog.add_task("Organizando…", total=len(files))
        for file in files:
            ext     = file.suffix.lstrip(".").lower() or "sin_extension"
            ext_dir = dest / ext
            target  = unique_dest(ext_dir, file.name)
            prog.update(t, description=f"[dim]{file.name[:45]}[/]")
            try:
                ext_dir.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), target)
                movidos += 1
            except Exception as e:
                console.print(f"  [red]✗[/] {file.name}: {e}")
                errores += 1
            prog.advance(t)
        prog.update(t, description="[green]✓[/] Listo")

    console.print()
    console.print(Panel(
        f"[bold green]✓ {movidos:,} archivos organizados[/]"
        + (f"\n[red]{errores} errores[/]" if errores else "")
        + f"\n[dim]Destino: {dest}[/]",
        style="green", expand=False,
    ))


if __name__ == "__main__":
    main()