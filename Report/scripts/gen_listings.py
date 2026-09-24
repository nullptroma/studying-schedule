#!/usr/bin/env python3
"""Generate Typst listing wrappers from the project source tree."""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore


def load_config(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        raise SystemExit("PyYAML required: pip install pyyaml")
    return yaml.safe_load(text)


def path_hash(rel: str) -> str:
    return hashlib.sha256(rel.encode()).hexdigest()[:8]


def lang_for(path: Path, ext_map: dict, name_map: dict) -> str:
    if path.name in name_map:
        return name_map[path.name]
    return ext_map.get(path.suffix.lower(), "text")


def should_skip(path: Path, parts: tuple[str, ...], cfg: dict) -> bool:
    exclude_dirs = set(cfg.get("exclude_dirs", []))
    if any(p in exclude_dirs for p in parts):
        return True
    s = path.as_posix()
    for g in cfg.get("exclude_globs", []):
        g = g.replace("**/", "")
        if g.startswith("**/"):
            g = g[3:]
        if g.endswith("/**"):
            if g[:-3] in parts:
                return True
        elif g.startswith("*."):
            if s.endswith(g[1:]):
                return True
        elif g in s:
            return True
    return False


def is_test_source(path: Path, cfg: dict) -> bool:
    if not cfg.get("only_test_filenames"):
        return True
    return path.name.endswith("Test.kt") or path.name == "YandexTestCredentials.kt"


def matches_path_filter(rel_posix: str, cfg: dict) -> bool:
    needles = cfg.get("only_path_substrings")
    if not needles:
        return True
    return any(n in rel_posix for n in needles)


def collect_files(scan_root: Path, cfg: dict) -> list[Path]:
    ext_map: dict = cfg.get("include_extensions", {})
    name_map: dict = cfg.get("include_filenames", {})
    allowed_suffixes = set(ext_map.keys())
    allowed_names = set(name_map.keys())

    files: list[Path] = []
    for p in scan_root.rglob("*"):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(scan_root).parts
        if should_skip(p, rel_parts, cfg):
            continue
        if p.name in allowed_names or p.suffix.lower() in allowed_suffixes:
            rel_posix = p.relative_to(scan_root).as_posix()
            if not matches_path_filter(rel_posix, cfg):
                continue
            if not is_test_source(p, cfg):
                continue
            files.append(p)
    return sorted(files, key=lambda x: x.as_posix())


def module_key(rel: Path, cfg: dict) -> str:
    order = cfg.get("modules_order", [])
    parts = rel.parts
    if rel.name in {Path(f).name for f in cfg.get("root_build_files", [])}:
        return "root"
    if parts and parts[0] in order:
        return parts[0]
    return "other"


def group_files(files: list[Path], scan_root: Path, cfg: dict) -> dict[str, list[Path]]:
    groups: dict[str, list[Path]] = {}
    root_files = {Path(f).name for f in cfg.get("root_build_files", [])}
    for f in files:
        rel = f.relative_to(scan_root)
        if rel.name in root_files or len(rel.parts) == 1 and rel.suffix in {".kts", ".properties"}:
            groups.setdefault("root", []).append(f)
            continue
        key = module_key(rel, cfg)
        groups.setdefault(key, []).append(f)
    order = cfg.get("modules_order", []) + ["other"]
    return {k: groups[k] for k in order if k in groups}


def typst_escape_path(rel: str) -> str:
    return rel.replace("\\", "/")


def typst_escape_caption(text: str) -> str:
    """Экранирование для текста в [...]; без обратных кавычек (inline raw ловит raw.line)."""
    for ch in "#$\\[]":
        text = text.replace(ch, "\\" + ch)
    return text


def write_listing(
    out_path: Path,
    rel_from_report: str,
    caption: str,
    label: str,
    lang: str,
    *,
    pagebreak_after: bool,
) -> None:
    rel_typ = typst_escape_path(rel_from_report)
    content = (
        f"#figure(\n"
        f"  [\n"
        f"    #figure.caption(position: top)[{caption}]\n"
        f"    #raw(read(\"{rel_typ}\"), lang: \"{lang}\", block: true, tab-size: 4, align: left)\n"
        f"  ],\n"
        f"  supplement: [Листинг],\n"
        f") <lst-{label}>\n"
    )
    if pagebreak_after:
        content += "#pagebreak(weak: true)\n"
    content += "\n"
    out_path.write_text(content, encoding="utf-8")


def module_heading(mod: str, cfg: dict) -> str:
    if mod == "root":
        return "Система сборки"
    for entry in cfg.get("module_titles", []):
        if entry.get("id") == mod:
            return entry["title"]
    return f"Модуль :{mod}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--config", default=None)
    args = parser.parse_args()

    script_dir = Path(__file__).resolve().parent
    report_dir = script_dir.parent
    config_path = Path(args.config) if args.config else report_dir / "listings" / "listings.config.yaml"
    cfg = load_config(config_path)

    scan_root = (report_dir / cfg.get("scan_root", "..")).resolve()
    generated = report_dir / "listings" / cfg.get("generated_subdir", "generated")
    appendix_name = cfg.get("appendix_filename", "appendix-a.typ")
    caption_prefix = cfg.get("caption_prefix", "Исходный файл ")
    pagebreak_after = cfg.get("pagebreak_after_listing", True)
    ext_map: dict = cfg.get("include_extensions", {})
    name_map: dict = cfg.get("include_filenames", {})

    files = collect_files(scan_root, cfg)
    if args.dry_run:
        for f in files:
            print(f.relative_to(scan_root).as_posix())
        print(f"Total: {len(files)}", file=sys.stderr)
        return 0

    generated.mkdir(parents=True, exist_ok=True)
    groups = group_files(files, scan_root, cfg)

    listing_paths: list[str] = []
    module_includes: list[str] = []

    for mod, mod_files in groups.items():
        mod_listings: list[str] = []
        for f in mod_files:
            rel_repo = f.relative_to(scan_root).as_posix()
            # Paths relative to listings/generated/*.typ (typst compile --root ..)
            rel_report = Path("../../..") / rel_repo
            rel_report_str = rel_report.as_posix()
            hid = path_hash(rel_repo)
            label = hid
            cap = f"{caption_prefix}{typst_escape_caption(rel_repo)}"
            lang = lang_for(f, ext_map, name_map)
            listing_name = f"listing-{hid}.typ"
            listing_path = generated / listing_name
            write_listing(
                listing_path,
                rel_report_str,
                cap,
                label,
                lang,
                pagebreak_after=pagebreak_after,
            )
            mod_listings.append(listing_name)
            listing_paths.append(listing_name)

        mod_file = generated / f"module-{mod}.typ"
        with mod_file.open("w", encoding="utf-8") as mf:
            title = module_heading(mod, cfg)
            mf.write(f"== {title}\n\n")
            if cfg.get("pagebreak_per_module") and mod != "root":
                mf.write("#pagebreak(weak: true)\n\n")
            for ln in mod_listings:
                mf.write(f'#include "{ln}"\n')
        module_includes.append(f"module-{mod}.typ")

    index = generated / "_index.typ"
    with index.open("w", encoding="utf-8") as ix:
        ix.write(f"// Generated listings: {len(files)} files\n\n")

    appendix = generated / appendix_name
    styles_path = report_dir / "includes" / "listings-appendix.typ"
    styles = styles_path.read_text(encoding="utf-8")
    with appendix.open("w", encoding="utf-8") as ap:
        ap.write("// AUTO-GENERATED by gen_listings.py — do not edit\n\n")
        ap.write("// Стили листингов (вставлены напрямую: #include не распространяет show-правила)\n")
        ap.write(styles)
        ap.write("\n")
        for mi in module_includes:
            ap.write(f'#include "{mi}"\n')

    print(f"Generated {len(files)} listings → {appendix}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
