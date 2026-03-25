#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
xmind2md: Convert an .xmind mind map into a Markdown outline.

Features
- Supports XMind 2020/Zen packages (content.json).
- Preserves sheet titles, topics (hierarchy), notes, labels, markers, and hyperlinks (when present).
- Extracts images/attachments to an 'images' folder alongside the output Markdown file.
- Outputs a clean Markdown outline using headings for sheet/root, and nested bullet lists for child topics.
- CLI usage:
    python xmind2md.py input.xmind -o output.md [--max-depth N] [--no-notes] [--no-labels] [--no-markers]

Limitations
- Relationships, boundaries, and summaries from XMind are not rendered (basic listing only when found).

Author: ChatGPT
License: MIT
"""

import zipfile
import json
from typing import List, Optional, Dict, Any, Tuple
import re
import os
import argparse
import shutil
import hashlib
from pathlib import Path
from collections import OrderedDict

IMAGE_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.svgz', '.webp',
    '.tif', '.tiff', '.ico', '.avif', '.heic', '.heif', '.jfif', '.emf', '.wmf'
}

RESOURCE_DIR_PREFIXES = ('resources/', 'attachments/')

_IMAGE_REL_PREFIX = "images"
_IMAGE_OUTPUT_DIR: Optional[Path] = None
_BOX_DRAWING_CHARS = set("┌┐└┘├┤┬┴┼─│╭╮╯╰╱╲╳╴╶◌«»")


def _normalize_image_prefix(prefix: Optional[str]) -> str:
    if prefix is None:
        return "images"
    cleaned = str(prefix).strip()
    cleaned = cleaned.strip('/\\')
    return cleaned or "images"


def _set_image_rel_prefix(prefix: str) -> str:
    global _IMAGE_REL_PREFIX
    previous = _IMAGE_REL_PREFIX
    _IMAGE_REL_PREFIX = prefix
    return previous


def _set_image_output_dir(path: Optional[Path]) -> Optional[Path]:
    global _IMAGE_OUTPUT_DIR
    previous = _IMAGE_OUTPUT_DIR
    _IMAGE_OUTPUT_DIR = path
    return previous


def _image_relpath(filename: str) -> str:
    fname = os.path.basename(filename or "")
    if not fname:
        return ""
    prefix = _IMAGE_REL_PREFIX.strip('/\\')
    if prefix:
        return f"{prefix}/{fname}"
    return fname

def _slugify_name(value: str) -> str:
    """
    Return a filesystem-friendly slug derived from the given value (preserve CJK chars).
    """
    if not value:
        return "mindmap"
    stem = Path(value).stem
    stem = stem.strip()
    if not stem:
        stem = value.strip()
    norm = stem.replace('（', '(').replace('）', ')')
    norm = re.sub(r'[\\/:]+', '-', norm)
    norm = re.sub(r'\s+', '-', norm)
    norm = re.sub('[^0-9A-Za-z_.()\u4e00-\u9fff-]+', '-', norm)
    norm = re.sub(r'-{2,}', '-', norm)
    norm = norm.strip('-_.')
    return norm or "mindmap"


def _ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def _serialize_front_matter_value(key: str, value: Any) -> List[str]:
    if isinstance(value, bool):
        return [f"{key}: {'true' if value else 'false'}"]
    if isinstance(value, (int, float)):
        return [f"{key}: {value}"]
    if isinstance(value, (list, tuple)):
        lines = [f"{key}:"]
        for item in value:
            if isinstance(item, (int, float)):
                lines.append(f"  - {item}")
            elif isinstance(item, bool):
                lines.append(f"  - {'true' if item else 'false'}")
            else:
                escaped = str(item).replace('\"', '\\\"')
                lines.append(f'  - "{escaped}"')
        if len(lines) == 1:
            return [f"{key}: []"]
        return lines
    if isinstance(value, dict):
        lines = [f"{key}:"]
        for sub_key, sub_val in value.items():
            nested = _serialize_front_matter_value(sub_key, sub_val)
            nested = [f"  {nested[0]}"] + [f"  {ln}" for ln in nested[1:]]
            lines.extend(nested)
        return lines
    escaped = str(value).replace('\"', '\\\"')
    return [f'{key}: "{escaped}"']


def _render_front_matter(meta: OrderedDict) -> str:
    lines: List[str] = ["---"]
    for key, value in meta.items():
        if value is None:
            continue
        lines.extend(_serialize_front_matter_value(key, value))
    lines.append("---")
    return "\n".join(lines)


def _relative_to(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def _compose_page_body(outline_md: str,
                       *,
                       markmap: bool,
                       markmap_meta: Optional[Dict[str, Any]],
                       include_outline: bool,
                       collapse_outline: bool) -> str:
    outline = outline_md.strip()
    parts: List[str] = []
    if markmap and outline:
        parts.append(_render_markmap_block(outline, markmap_meta))
    if include_outline and outline:
        if collapse_outline:
            parts.append(f"<details open>\n<summary>大纲</summary>\n\n{outline}\n</details>")
        else:
            parts.append(outline)
    body = "\n\n".join(part.strip() for part in parts if part.strip())
    if body and not body.endswith("\n"):
        body += "\n"
    elif not body:
        body = outline_md if include_outline else ""
    return body


def _write_text(path: Path, content: str) -> None:
    _ensure_directory(path.parent)
    with open(path, "w", encoding="utf-8") as fp:
        fp.write(content)


def _render_markmap_block(markdown_text: str,
                          markmap_meta: Optional[Dict[str, Any]]) -> str:
    trimmed = markdown_text.strip("\n")
    payload_parts: List[str] = []
    if markmap_meta:
        fm = OrderedDict()
        fm["markmap"] = markmap_meta
        payload_parts.append(_render_front_matter(fm))
    payload_parts.append(trimmed)
    payload = "\n\n".join(payload_parts)
    return f"```markmap\n{payload}\n```"

def _is_image_filename(name: str) -> bool:
    _, ext = os.path.splitext(name or '')
    return ext.lower() in IMAGE_EXTENSIONS

def _resource_filename_from_src(src: Optional[str]) -> Optional[str]:
    """Return the resource file name if src points to a packaged resource image."""
    if not src:
        return None
    cleaned = src.strip()
    if not cleaned:
        return None
    lower = cleaned.lower()
    for prefix in ('xap:', 'xap#'):
        if lower.startswith(prefix):
            cleaned = cleaned[len(prefix):]
            lower = cleaned.lower()
            break
    cleaned = cleaned.replace('\\', '/').lstrip('/')
    lower = cleaned.lower()
    for root in RESOURCE_DIR_PREFIXES:
        if lower.startswith(root):
            trimmed = cleaned[len(root):]
            filename = os.path.basename(trimmed)
            return filename or None
    return None

def _resource_image_relpath(src: Optional[str]) -> Optional[str]:
    filename = _resource_filename_from_src(src)
    if filename and _is_image_filename(filename):
        return _image_relpath(filename)
    return None

def _split_link_and_image(hyperlink: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Return (link, image_path). If hyperlink points to a packaged resource image,
    treat it as an image instead of a navigable link.
    """
    image_path = _resource_image_relpath(hyperlink)
    if image_path:
        return None, image_path
    return hyperlink, None

def _zip_entry_is_image(name: str) -> bool:
    if not name or name.endswith('/'):
        return False
    lower = name.lower()
    if not any(lower.startswith(prefix) for prefix in RESOURCE_DIR_PREFIXES):
        return False
    return _is_image_filename(os.path.basename(name))

def _md_escape(text: str) -> str:
    """Escape only HTML-sensitive chars for plain Markdown text content."""
    if text is None:
        return ""
    # Keep output close to the source text; avoid noisy punctuation escaping.
    return (text
            .replace('\\', r'\\')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            )


def _md_escape_bracket_text(text: str) -> str:
    """Escape text for [] contexts such as link labels and image alt."""
    return _md_escape(text).replace('[', r'\[').replace(']', r'\]')

def _norm_ws(s: Optional[str]) -> str:
    return re.sub(r'[ \t]+\n', '\n', s or '').strip()


def _single_line_text(s: Optional[str]) -> str:
    """Collapse multi-line text into one line for stable list-item rendering."""
    return re.sub(r'\s+', ' ', (s or '').strip()).strip()


def _contains_box_drawing(text: str) -> bool:
    return any(ch in _BOX_DRAWING_CHARS for ch in text)


def _extract_ascii_diagram(text: str) -> Tuple[str, List[str]]:
    """
    Split topic text into (leading_caption, ascii_diagram_lines).
    Returns empty diagram lines if this is not likely a box-drawing diagram.
    """
    if not text or '\n' not in text:
        return _single_line_text(text), []

    lines = [ln.rstrip() for ln in text.splitlines()]
    first_art_idx = None
    for idx, line in enumerate(lines):
        if _contains_box_drawing(line):
            first_art_idx = idx
            break
    if first_art_idx is None:
        return _single_line_text(text), []

    art_lines = lines[first_art_idx:]
    box_char_count = sum(sum(1 for ch in ln if ch in _BOX_DRAWING_CHARS) for ln in art_lines)
    non_blank_lines = [ln for ln in art_lines if ln.strip()]
    if box_char_count < 8 or len(non_blank_lines) < 2:
        return _single_line_text(text), []

    while art_lines and not art_lines[0].strip():
        art_lines.pop(0)
    while art_lines and not art_lines[-1].strip():
        art_lines.pop()

    lead = _single_line_text("\n".join(lines[:first_art_idx]))
    return lead, art_lines


def _render_ascii_diagram_image(lines: List[str]) -> Optional[str]:
    """
    Render box-drawing text to a PNG image and return markdown-relative path.
    Returns None if Pillow is unavailable or rendering fails.
    """
    if not lines or _IMAGE_OUTPUT_DIR is None:
        return None
    try:
        from PIL import Image, ImageDraw, ImageFont  # type: ignore
    except Exception:
        return None

    payload = "\n".join(lines).strip("\n")
    if not payload:
        return None
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]
    filename = f"ascii-{digest}.png"
    abs_path = _IMAGE_OUTPUT_DIR / filename
    if abs_path.exists():
        return _image_relpath(filename)

    try:
        font = ImageFont.truetype("DejaVuSansMono.ttf", 18)
    except Exception:
        try:
            font = ImageFont.truetype("NotoSansMono-Regular.ttf", 18)
        except Exception:
            font = ImageFont.load_default()

    # Measure text extents line by line for consistent padding and clipping.
    tmp_img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(tmp_img)
    max_w = 1
    line_h = 18
    for ln in lines:
        bbox = draw.textbbox((0, 0), ln or " ", font=font)
        max_w = max(max_w, bbox[2] - bbox[0])
        line_h = max(line_h, bbox[3] - bbox[1])

    pad_x = 18
    pad_y = 14
    spacing = 6
    img_w = max_w + pad_x * 2
    img_h = len(lines) * line_h + max(0, len(lines) - 1) * spacing + pad_y * 2

    image = Image.new("RGB", (img_w, img_h), color=(250, 250, 250))
    draw = ImageDraw.Draw(image)
    y = pad_y
    for ln in lines:
        draw.text((pad_x, y), ln, font=font, fill=(24, 24, 24))
        y += line_h + spacing

    abs_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(abs_path, format="PNG", optimize=True)
    return _image_relpath(filename)


def _escape_leading_markdown_syntax(text: str) -> str:
    """
    Escape leading markdown constructs that can make a list item's visible label
    disappear (e.g. task-list marker like "[ ]").
    """
    if not text:
        return text
    stripped = text.lstrip()
    if not stripped:
        return text
    prefix_len = len(text) - len(stripped)
    prefix = text[:prefix_len]

    # Task list marker at start: "[ ] xxx" / "[x] xxx"
    if re.match(r'^\[[ xX]\](?:\s|$)', stripped):
        stripped = '\\' + stripped
    # Heading marker: "# xxx"
    elif re.match(r'^#{1,6}(?:\s|$)', stripped):
        stripped = '\\' + stripped
    # Unordered list marker: "- xxx" / "+ xxx" / "* xxx"
    elif re.match(r'^[-+*](?:\s|$)', stripped):
        stripped = '\\' + stripped
    # Ordered list marker: "1. xxx" / "1) xxx"
    else:
        ordered = re.match(r'^(\d+)([.)])(\s+.*)$', stripped)
        if ordered:
            stripped = f"{ordered.group(1)}\\{ordered.group(2)}{ordered.group(3)}"

    # Blockquote marker
    if stripped.startswith('>'):
        stripped = '\\' + stripped
    # Horizontal rule style text
    if re.match(r'^[-*_]{3,}\s*$', stripped):
        stripped = '\\' + stripped

    return prefix + stripped


def _is_effectively_empty_markdown(text: str) -> bool:
    """Best-effort check for markdown that renders as an empty label."""
    if not text:
        return True
    cleaned = text.strip()
    if not cleaned:
        return True
    # Reduce common inline syntaxes to their visible text.
    cleaned = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', cleaned)
    cleaned = re.sub(r'\[([^\]]*)\]\([^)]+\)', r'\1', cleaned)
    cleaned = re.sub(r'`([^`]*)`', r'\1', cleaned)
    cleaned = re.sub(r'\\([\\`*_{}\[\]()#+\-.!])', r'\1', cleaned)
    cleaned = re.sub(r'&(?:nbsp|#160);', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', '', cleaned)
    return cleaned == ""


def _indent(level: int) -> str:
    return '  ' * level


def _looks_like_hash_title(title: str) -> bool:
    if not title:
        return False
    t = title.strip()
    return bool(re.fullmatch(r'[0-9a-fA-F]{32,}', t))

def _add_note_lines(lines: List[str], note: str, level: int) -> None:
    note = _norm_ws(note)
    if not note:
        return
    # Render notes as a nested blockquote under the item
    for ln in note.splitlines():
        if ln.strip() == '':
            continue
        lines.append(f"{_indent(level+1)}> {ln}")


def _render_image_markup(path: str, title: str) -> str:
    alt = _md_escape_bracket_text(title) if title else os.path.basename(path) or "image"
    return f"![{alt}]({path})"


def _format_line(title: str,
                 hyperlink: Optional[str] = None,
                 labels: Optional[List[str]] = None,
                 markers: Optional[List[str]] = None,
                 image_paths: Optional[List[str]] = None) -> str:
    text = _md_escape(title) if title else ""
    text = _escape_leading_markdown_syntax(text)
    if hyperlink:
        # ensure parentheses don't break the link
        safe_url = hyperlink.replace(')', r'\)')
        link_label = _md_escape_bracket_text(title) if title else _md_escape_bracket_text(safe_url)
        text = f"[{link_label}]({safe_url})"
    # append labels as inline tags
    suffix = []
    if labels:
        for lb in labels:
            lb = str(lb).strip()
            if lb:
                suffix.append(f"`{_md_escape(lb)}`")
    if markers:
        for mk in markers:
            mk = str(mk).strip()
            if mk:
                suffix.append(f"`{_md_escape(mk)}`")
    if suffix:
        suffix_text = " ".join(suffix)
        if text:
            text = f"{text} {suffix_text}"
        else:
            text = suffix_text
    if not text and not image_paths:
        text = "(untitled)"
    if image_paths:
        image_md_parts = []
        for path in image_paths:
            if not path:
                continue
            image_md_parts.append(_render_image_markup(path, title))
        if image_md_parts:
            images_md = " ".join(image_md_parts)
            if text:
                text = f"{text} {images_md}"
            else:
                text = images_md
    return text

# ----------------------- JSON (XMind 2020/Zen) -----------------------

def _json_get_note(topic: Dict[str, Any]) -> str:
    notes = topic.get('notes') or {}
    # Common: {"notes":{"plain":{"content":"..."}}}
    plain = notes.get('plain') or {}
    if isinstance(plain, dict):
        return _norm_ws(plain.get('content'))
    # Sometimes notes may be directly a string (rare)
    if isinstance(notes, str):
        return _norm_ws(notes)
    return ""

def _json_get_labels(topic: Dict[str, Any]) -> List[str]:
    lbs = topic.get('labels') or {}
    # Either {"labels":{"labels":[...]}} or {"labels":[...]}
    if isinstance(lbs, dict):
        res = lbs.get('labels') or []
        if isinstance(res, list):
            return [str(x) for x in res]
        return []
    if isinstance(lbs, list):
        return [str(x) for x in lbs]
    return []

def _json_get_markers(topic: Dict[str, Any]) -> List[str]:
    # Markers may be under "markers": [{"markerId": "..."}] or ["..."]
    mks = topic.get('markers') or []
    out = []
    if isinstance(mks, list):
        for m in mks:
            if isinstance(m, dict):
                mid = m.get('markerId') or m.get('id') or m.get('marker-id')
                if mid: out.append(str(mid))
            elif isinstance(m, str):
                out.append(m)
    # Some versions use "marker-refs": [{"markerId": "..."}]
    mrefs = topic.get('marker-refs') or topic.get('markerRefs') or []
    if isinstance(mrefs, list):
        for m in mrefs:
            if isinstance(m, dict):
                mid = m.get('markerId') or m.get('id')
                if mid: out.append(str(mid))
    return out

def _json_children(topic: Dict[str, Any]) -> List[Dict[str, Any]]:
    ch = topic.get('children') or {}
    # Common: {"children":{"attached":[...]}} ; also "detached"
    res = []
    for k in ('attached', 'detached'):
        arr = ch.get(k) or []
        if isinstance(arr, list):
            res.extend(arr)
    return res

def _extract_image_paths(value: Any) -> List[str]:
    """Recursively find resource-backed image references in arbitrary JSON blobs."""
    results: List[str] = []

    def _append(path: Optional[str]) -> None:
        if not path:
            return
        if path not in results:
            results.append(path)

    if isinstance(value, str):
        _append(_resource_image_relpath(value))
    elif isinstance(value, dict):
        for key in ('src', 'url', 'href', 'path', 'xlink:href'):
            _append(_resource_image_relpath(value.get(key)))
        for nested in value.values():
            if isinstance(nested, (dict, list)):
                for item in _extract_image_paths(nested):
                    _append(item)
            elif isinstance(nested, str):
                _append(_resource_image_relpath(nested))
    elif isinstance(value, list):
        for item in value:
            for nested in _extract_image_paths(item):
                _append(nested)
    return results

def _json_topic_images(topic: Dict[str, Any]) -> List[str]:
    """Return relative paths for any images embedded in the topic."""
    images: List[str] = []
    for key in ('image', 'images', 'img', 'imageUrl'):
        for path in _extract_image_paths(topic.get(key)):
            if path not in images:
                images.append(path)
    return images

def _derive_fallback_title(note: str,
                           image_paths: Optional[List[str]]) -> str:
    note = (note or "").strip()
    if note:
        first_line = note.splitlines()[0].strip()
        if first_line:
            if len(first_line) > 80:
                first_line = first_line[:77].rstrip() + "..."
            return first_line
    return ""

def _walk_json_topic(lines: List[str],
                     topic: Dict[str, Any],
                     level: int,
                     opts) -> None:
    if opts.max_depth is not None and level > opts.max_depth:
        return
    raw_title = topic.get('title') or ""
    title, ascii_diagram_lines = _extract_ascii_diagram(raw_title if isinstance(raw_title, str) else str(raw_title))
    raw_link = topic.get('hyperlink') or topic.get('href') or None
    hyperlink, link_image = _split_link_and_image(raw_link)
    labels = _json_get_labels(topic) if opts.labels else None
    markers = _json_get_markers(topic) if opts.markers else None
    image_paths = _json_topic_images(topic)
    note = _json_get_note(topic) if opts.notes else ""

    ascii_image_path = _render_ascii_diagram_image(ascii_diagram_lines)
    if ascii_image_path and ascii_image_path not in image_paths:
        image_paths.append(ascii_image_path)

    # XMind sometimes stores pasted-image-only nodes with a hash-like placeholder
    # title that matches the image filename. Hide that synthetic title.
    if title and image_paths:
        normalized_title = title.strip().lower()
        stems = {
            os.path.splitext(os.path.basename(p))[0].strip().lower()
            for p in image_paths if p
        }
        if _looks_like_hash_title(title) or normalized_title in stems:
            title = ""

    if not title:
        title = _single_line_text(_derive_fallback_title(note, image_paths))

    if link_image and link_image not in image_paths:
        image_paths.append(link_image)

    has_visible_content = bool(
        title or hyperlink or (labels and len(labels)) or
        (markers and len(markers)) or image_paths or (note and note.strip())
    )
    if not has_visible_content:
        # Skip empty placeholder topics but keep their children at the same level.
        for child in _json_children(topic):
            _walk_json_topic(lines, child, level, opts)
        return

    item = _format_line(
        title,
        hyperlink,
        labels,
        markers,
        image_paths=image_paths or None
    )
    if _is_effectively_empty_markdown(item):
        item = "(untitled)"
    lines.append(f"{_indent(level)}- {item}")
    if opts.notes:
        _add_note_lines(lines, note, level)
    for child in _json_children(topic):
        _walk_json_topic(lines, child, level + 1, opts)

def _parse_content_json(zf: zipfile.ZipFile) -> List[Dict[str, Any]]:
    """Return list of sheets from content.json (XMind Zen/2020)."""
    with zf.open('content.json') as fp:
        data = json.load(fp)
    # data can be {"rootTopic":..., "title":...} for single sheet,
    # or {"sheets":[...]} or a list of sheets
    if isinstance(data, dict) and 'sheets' in data:
        sheets = data['sheets']
    elif isinstance(data, dict) and 'rootTopic' in data:
        sheets = [data]
    elif isinstance(data, list):
        sheets = data
    else:
        raise ValueError("Unrecognized JSON structure in content.json")
    return sheets

# ----------------------- Converter -----------------------

class Opts:
    def __init__(self, notes=True, labels=True, markers=True, max_depth=None):
        self.notes = notes
        self.labels = labels
        self.markers = markers
        self.max_depth = max_depth  # None or int

def convert_xmind_to_markdown(input_path: str,
                              output_path: Optional[str] = None,
                              *,
                              notes: bool = True,
                              labels: bool = True,
                              markers: bool = True,
                              max_depth: Optional[int] = None,
                              images_subdir: str = "images",
                              assets_dir: Optional[str] = None) -> str:
    """
    Convert a .xmind file to Markdown; returns the Markdown string.
    If output_path is provided, also saves to that file (UTF-8).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input file not found: {input_path}")

    opts = Opts(notes=notes, labels=labels, markers=markers, max_depth=max_depth)
    lines: List[str] = []
    images_subdir = _normalize_image_prefix(images_subdir)

    if output_path:
        base_dir = os.path.dirname(os.path.abspath(output_path))
    elif assets_dir:
        base_dir = os.path.abspath(assets_dir)
    else:
        base_dir = os.path.dirname(os.path.abspath(input_path))
    _ensure_directory(Path(base_dir))
    images_dir = os.path.join(base_dir, images_subdir) if images_subdir else base_dir
    os.makedirs(images_dir, exist_ok=True)

    previous_prefix = _set_image_rel_prefix(images_subdir)
    previous_image_dir = _set_image_output_dir(Path(images_dir))
    try:
        with zipfile.ZipFile(input_path, 'r') as zf:
            names = set(zf.namelist())
            if 'content.json' not in names:
                raise ValueError("content.json not found inside the .xmind package (XMind 2020/Zen format required).")

            # Extract images/resources
            for name in names:
                if _zip_entry_is_image(name):
                    filename = os.path.basename(name)
                    with zf.open(name) as src, open(os.path.join(images_dir, filename), 'wb') as dst:
                        dst.write(src.read())

            sheets = _parse_content_json(zf)  # list of dicts with rootTopic
            multi_sheet = len(sheets) > 1
            for i, sheet in enumerate(sheets, 1):
                stitle = _single_line_text(sheet.get('title') or f'Sheet {i}')
                if multi_sheet:
                    lines.append(f"# {stitle}")
                root = sheet.get('rootTopic') or {}
                # Some files store root as {'title':...} or include 'children'
                rtitle = _single_line_text(root.get('title') or 'Root')
                heading_level = "##" if multi_sheet else "#"
                lines.append(f"{heading_level} {rtitle}")
                if opts.notes:
                    _add_note_lines(lines, _json_get_note(root), 0)
                for child in _json_children(root):
                    _walk_json_topic(lines, child, 0, opts)
                # blank line between sheets
                lines.append("")
    finally:
        _set_image_output_dir(previous_image_dir)
        _set_image_rel_prefix(previous_prefix)

    md = "\n".join(lines).rstrip() + "\n"
    if output_path:
        _write_text(Path(output_path), md)
    return md

def _conversion_kwargs_from_args(args) -> Dict[str, Any]:
    return {
        "notes": not args.no_notes,
        "labels": not args.no_labels,
        "markers": not args.no_markers,
        "max_depth": args.max_depth,
        "images_subdir": args.images_subdir,
    }


def _needs_template_mode(args) -> bool:
    return bool(args.markmap or args.no_outline or args.collapse_outline or args.hugo)


def _should_include_outline(args) -> bool:
    if getattr(args, "include_outline", False):
        return True
    if args.no_outline:
        return False
    return not args.markmap


def _markmap_meta_from_args(args) -> Optional[Dict[str, Any]]:
    options: Dict[str, Any] = {}
    level = getattr(args, "markmap_initial_level", None)
    if level is not None and level >= 0:
        options["initialExpandLevel"] = level
    max_width = getattr(args, "markmap_max_width", None)
    if max_width is not None and max_width > 0:
        options["maxWidth"] = max_width
    spacing_vertical = getattr(args, "markmap_spacing_vertical", None)
    if spacing_vertical is not None and spacing_vertical > 0:
        options["spacingVertical"] = spacing_vertical
    spacing_horizontal = getattr(args, "markmap_spacing_horizontal", None)
    if spacing_horizontal is not None and spacing_horizontal > 0:
        options["spacingHorizontal"] = spacing_horizontal
    return options or None


def _run_single_conversion(args) -> None:
    if not args.input:
        raise ValueError("Input .xmind path is required for single conversion.")
    in_path = Path(args.input).expanduser()
    if not in_path.exists():
        raise FileNotFoundError(f"Input file not found: {in_path}")
    out_path = Path(args.output or in_path.with_suffix(".md")).expanduser()
    title = args.title or in_path.stem
    conversion_kwargs = _conversion_kwargs_from_args(args)
    include_outline = _should_include_outline(args)
    collapse_outline = args.collapse_outline
    markmap_flag = args.markmap
    markmap_meta = _markmap_meta_from_args(args)
    template_mode = _needs_template_mode(args)

    if template_mode:
        outline_md = convert_xmind_to_markdown(
            str(in_path),
            output_path=None,
            assets_dir=str(out_path.parent),
            **conversion_kwargs,
        )
        body = _compose_page_body(
            outline_md,
            markmap=markmap_flag,
            markmap_meta=markmap_meta,
            include_outline=include_outline,
            collapse_outline=collapse_outline
        )
        sections: List[str] = []
        if args.hugo:
            fm = OrderedDict()
            fm["title"] = title
            if args.hugo_type:
                fm["type"] = args.hugo_type
            fm["markmap"] = markmap_flag
            fm["xmindSource"] = _relative_to(in_path, Path.cwd())
            sections.append(_render_front_matter(fm))
        if body.strip():
            sections.append(body.strip())
        content = "\n\n".join(sections).strip() + "\n"
        _write_text(out_path, content)
    else:
        convert_xmind_to_markdown(
            str(in_path),
            output_path=str(out_path),
            **conversion_kwargs,
        )
    print(f"Converted to: {out_path}")


def _gather_xmind_files(input_dir: Path, recursive: bool) -> List[Path]:
    pattern = "**/*.xmind" if recursive else "*.xmind"
    files = sorted(input_dir.glob(pattern))
    return [p for p in files if p.is_file()]


def _run_bulk_conversion(args) -> None:
    input_dir = Path(args.input_dir).expanduser()
    output_dir = Path(args.output_dir).expanduser()
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    _ensure_directory(output_dir)
    files = _gather_xmind_files(input_dir, args.recursive)
    if not files:
        print(f"No .xmind files found under {input_dir}")
        return

    conversion_kwargs = _conversion_kwargs_from_args(args)
    include_outline = _should_include_outline(args)
    collapse_outline = args.collapse_outline
    markmap_flag = args.markmap
    markmap_meta = _markmap_meta_from_args(args)

    slug_usage: Dict[str, int] = {}
    converted = 0
    for index, src in enumerate(files, start=1):
        base_slug = _slugify_name(src.name)
        count = slug_usage.get(base_slug, 0)
        slug_usage[base_slug] = count + 1
        slug = base_slug if count == 0 else f"{base_slug}-{count+1}"
        target_dir = output_dir / slug
        md_target = target_dir / "_index.md"

        if md_target.exists() and not args.overwrite:
            print(f"[skip] {md_target} exists (use --overwrite to replace).")
            continue

        if args.overwrite:
            if md_target.exists():
                md_target.unlink()
            images_dir = target_dir / args.images_subdir
            if images_dir.exists():
                shutil.rmtree(images_dir)

        outline_md = convert_xmind_to_markdown(
            str(src),
            output_path=None,
            assets_dir=str(target_dir),
            **conversion_kwargs,
        )
        body = _compose_page_body(
            outline_md,
            markmap=markmap_flag,
            markmap_meta=markmap_meta,
            include_outline=include_outline,
            collapse_outline=collapse_outline
        )
        sections: List[str] = []
        if args.hugo:
            fm = OrderedDict()
            fm["title"] = src.stem if args.title is None else args.title
            if args.hugo_type:
                fm["type"] = args.hugo_type
            if args.weight_step:
                fm["weight"] = args.weight_start + (index - 1) * args.weight_step
            fm["markmap"] = markmap_flag
            fm["xmindSource"] = _relative_to(src, input_dir)
            sections.append(_render_front_matter(fm))
        if body.strip():
            sections.append(body.strip())
        content = "\n\n".join(sections).strip() + "\n"
        _write_text(md_target, content)
        converted += 1
        print(f"[ok] {src} -> {md_target}")

    print(f"Converted {converted} file(s) into {output_dir}")

def main():
    parser = argparse.ArgumentParser(
        description="Convert XMind (.xmind) files into Markdown/Markmap (single file or batch)."
    )
    parser.add_argument("input", nargs="?", help="Path to a single input .xmind file")
    parser.add_argument("-o", "--output", help="Path to the output .md file (single mode)")
    parser.add_argument("--input-dir", help="Directory containing .xmind files for batch conversion")
    parser.add_argument("--output-dir", help="Destination directory for batch conversion outputs")
    parser.add_argument("--recursive", action="store_true", help="Recursively scan --input-dir for .xmind files")
    parser.add_argument("--markmap", action="store_true", help="Render a Markmap visualization block")
    parser.add_argument("--markmap-initial-level", type=int, default=2,
                        help="Initial expand level for Markmap (set to -1 for fully expanded)")
    parser.add_argument("--markmap-max-width", type=int, default=0,
                        help="Maximum text width (px) for Markmap nodes (set <=0 to disable Markmap's default handling)")
    parser.add_argument("--markmap-spacing-vertical", type=int, default=30,
                        help="Vertical spacing between sibling Markmap nodes (pixels)")
    parser.add_argument("--markmap-spacing-horizontal", type=int, default=180,
                        help="Horizontal spacing between parent and child nodes (pixels)")
    parser.add_argument("--no-outline", action="store_true", help="Skip the plain Markdown outline (useful with --markmap)")
    parser.add_argument("--include-outline", action="store_true",
                        help="Force-include the plain Markdown outline even when --markmap is enabled")
    parser.add_argument("--collapse-outline", action="store_true", help="Wrap the outline in a collapsible <details> element")
    parser.add_argument("--hugo", action="store_true", help="Wrap Markdown with Hugo front matter (title/type/weight)")
    parser.add_argument("--hugo-type", default="docs", help="Value for the `type` front matter field when --hugo is set")
    parser.add_argument("--title", help="Override the generated title (single or batch)")
    parser.add_argument("--weight-step", type=int, default=10, help="Weight increment between batch pages (Hugo)")
    parser.add_argument("--weight-start", type=int, default=10, help="Starting weight for batch pages (Hugo)")
    parser.add_argument("--images-subdir", default="images", help="Relative folder name used for extracted images")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing outputs when running in batch mode")
    parser.add_argument("--max-depth", type=int, default=None, help="Limit output depth (0 = only first level topics)")
    parser.add_argument("--no-notes", action="store_true", help="Do not include topic notes")
    parser.add_argument("--no-labels", action="store_true", help="Do not include topic labels")
    parser.add_argument("--no-markers", action="store_true", help="Do not include topic markers")

    args = parser.parse_args()

    if args.input_dir:
        if not args.output_dir:
            parser.error("--output-dir is required when using --input-dir.")
        _run_bulk_conversion(args)
    else:
        if not args.input:
            parser.error("input path is required unless --input-dir is provided.")
        _run_single_conversion(args)

if __name__ == "__main__":
    main()
