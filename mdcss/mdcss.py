# Modification in mdcss.py
# 1. margin in Line 182:
# @media print {
#   @page {
#     margin: 2cm 2cm 2cm 2cm !important;
#   }
# 2. font-size in Line 214:
#   html body {
#     font-size: 18px !important;

import shutil
import re
import unicodedata
from pathlib import Path
from typing import List, Optional, Tuple, Any, Literal

import cssutils
from fontTools.ttLib import TTFont

# You may also install jsbeautifier and cssbeautifier for better output formatting,
# but they are optional dependencies.


# ======== 用户配置区域 ========

# 显式指定扩展目录，若为 None 则根据 EXTENSIONS_ROOT 和 EXTENSION_PATTERN 自动匹配
EXTENSION_DIR = None
# VS Code 扩展根目录，默认为用户目录下的 .vscode/extensions
EXTENSIONS_ROOT = Path.home() / ".vscode" / "extensions"
# 扩展目录匹配模式，自动查找 Markdown Preview Enhanced 扩展（当 EXTENSION_DIR 为 None 时使用）
EXTENSION_PATTERN = "shd101wyy.markdown-preview-enhanced-*"

# 正文字体路径，若为 None 则不覆盖默认字体（只需输入一个文件，程序会自动解析同族字体）
FONT = Path("D:/Coding/.resource/font/Segoe_UI/segoeui.ttf")
# 代码块字体路径，若为 None 则不覆盖默认代码字体
CODE_FONT = None

# 主主题 CSS 文件名（相对扩展目录 crossnote/styles/ 的相对路径或绝对路径），必须提供有效值
MAIN_CSS = Path("./preview_theme/github-light.css")
# 代码块主题 CSS 文件名（相对扩展目录 crossnote/styles/ 的相对路径或绝对路径），必须提供有效值
CODEBLOCK_CSS = Path("./prism_theme/github.css")

# 打印边距，支持 CSS 长度单位以及 1-4 个值，例如 "5mm"、"2cm 1cm" 等
# 1 个值 → 全部，2 个值 → 上下、左右，3 个值 → 上、左右、下，4 个值：上、右、下、左
PRINT_MARGIN = "2.54cm, 1.91cm, 2.54cm, 1.91cm"

# 图片尺寸预设范围（未启动 ENABLE_PARSER 时生效）
image_size_range = range(5, 101, 5)

# 是否在二级标题下添加横线
ENABLE_H2_UNDERLINE = True

# 模板文件位置
TEMPLATE_DIR = Path(__file__).parent / "templates"

# 输出目录，生成的 style.less 和 parser.js 将写入此目录
OUTPUT = Path.home() / ".crossnote"  # MPE 插件 style.less 的文件目录
# OUTPUT = Path("./output_style")

# ==== 自定义功能 ====

# 是否启用 parser.js 功能（如标题自动编号、图片尺寸控制、多列布局等）
ENABLE_PARSER = True

# 标题自动编号格式，按标题级别 1-6 顺序，用逗号分隔，支持：roman, romanUpper, latin, latinUpper, chinese, number, none
AUTO_COUNT = "none, number, number, number, latin, roman"
# 是否允许表格水平滚动，若为 False 则强制表格内换行（避免横向滚动条）
ENABLE_TABLE_HORIZONTAL_SCROLL = False

# ======== 配置区域结束 ========


FONT_FORMATS = {
    ".ttf": "truetype",
    ".otf": "opentype",
    ".woff": "woff",
    ".woff2": "woff2",
}


cssutils.log.setLevel("CRITICAL")


def load_template(dir_: Literal["css", "parser"], name: str, **kwargs: dict[str, Any]) -> str:
    file = TEMPLATE_DIR / dir_ / name
    if not file.exists():
        raise FileNotFoundError(f"Template not found: {file}")
    content = file.read_text(encoding="utf-8")
    # <variable>name</variable> in template will be replaced with kwargs["name"] value.
    for key, value in kwargs.items():
        placeholder = f"<variable>{key}</variable>"
        if not placeholder in content:
            raise ValueError(f"Placeholder '{placeholder}' not found in template '{file}'")
        content = content.replace(placeholder, str(value))
    if re.match(r"<variable>\w+</variable>", content):
        raise ValueError(f"Unreplaced placeholders remain in template '{file}' after substitution")
    return content if content.endswith("\n") else content + "\n"


def resolve_extension_dir(
    extensions_root: Path,
    extension_pattern: str,
    explicit_extension_dir: Optional[Path] = None,
) -> Path:
    if explicit_extension_dir is not None:
        if not explicit_extension_dir.exists():
            raise FileNotFoundError(f"Extension directory not found: {explicit_extension_dir}")
        return explicit_extension_dir

    matches = sorted(extensions_root.glob(extension_pattern))
    if not matches:
        raise FileNotFoundError(
            "No extension directory matched pattern "
            f"'{extension_pattern}' under '{extensions_root}'"
        )

    # Pick the latest-looking directory by lexical order to handle version suffixes.
    return matches[-1]


def generate_print_style(
    main_css_path,
    codeblock_css_path,
    reveal_css_path=None,
    print_margin: str = "2cm",
):
    """Generate @media print CSS safely with cssutils."""

    def load_css(path):
        if path is None:
            return None
        p = Path(path)
        if not p.exists():
            print(f"Warning: path not found, skipped: {p}")
            return None
        return p.read_text(encoding="utf-8")

    all_css = ""
    for path in [main_css_path, codeblock_css_path, reveal_css_path]:
        content = load_css(path)
        if content:
            all_css += content + "\n"

    if not all_css.strip():
        return "/* Error: no CSS content loaded */"

    sheet = cssutils.parseString(all_css)
    new_rules = []

    ui_keywords = {
        ".sidebar",
        ".app-nav",
        ".github-corner",
        ".progress",
        "#app",
        ".search",
        "section.cover",
        ".sidebar-toggle",
        ".emoji",
        "::-webkit-scrollbar",
        "main",
        ".anchor",
        ".md-sidebar-toc",
        ".cover-main",
        "body.close",
        "body.sticky",
    }

    disallowed_global_props = {
        "-webkit-overflow-scrolling",
        "-webkit-tap-highlight-color",
        "-webkit-text-size-adjust",
        "-webkit-touch-callout",
    }

    disallowed_print_props = {
        "font-family",
    }

    def is_ui_selector(selector_text: str) -> bool:
        return any(kw in selector_text for kw in ui_keywords)

    def convert_selector(selector_text: str) -> str:
        return (
            selector_text.replace(".markdown-preview.markdown-preview", "body").replace(
                ".markdown-preview", "body"
            )
        )

    def append_style_rule(rule_obj):
        selector = rule_obj.selectorText

        if not selector or is_ui_selector(selector):
            return

        new_rule = cssutils.css.CSSStyleRule()
        new_rule.selectorText = convert_selector(selector)

        for prop in rule_obj.style:
            if selector.strip() == "*" and prop.name in disallowed_global_props:
                continue
            if prop.name in disallowed_print_props:
                continue
            new_rule.style.setProperty(prop.name, prop.value, priority="important")

        if new_rule.style.length > 0:
            new_rules.append(new_rule.cssText)

    for rule in sheet:
        if rule.type == rule.STYLE_RULE:
            append_style_rule(rule)
        elif rule.type == rule.MEDIA_RULE:
            if "print" not in rule.media.mediaText.lower():
                continue

            nested_rules = []
            for nested in rule.cssRules:
                if nested.type != nested.STYLE_RULE:
                    continue

                selector = nested.selectorText
                if not selector or is_ui_selector(selector):
                    continue

                nested_rule = cssutils.css.CSSStyleRule()
                nested_rule.selectorText = convert_selector(selector)
                for prop in nested.style:
                    if prop.name in disallowed_print_props:
                        continue
                    nested_rule.style.setProperty(
                        prop.name,
                        prop.value,
                        priority="important",
                    )
                if nested_rule.style.length > 0:
                    nested_rules.append(nested_rule.cssText)

            if nested_rules:
                new_rules.extend(nested_rules)

    if not new_rules:
        # return "/* No valid content style extracted */"
        raise ValueError("No valid styles extracted for print media")
    
    return load_template(
        "css", "printstyle.css",
        new_rules="\n".join(new_rules),
        print_margin=print_margin,
    )


def _get_name_record(font: TTFont, name_ids: Tuple[int, ...]) -> Optional[str]:
    for name_id in name_ids:
        for record in font["name"].names:
            if record.nameID != name_id:
                continue
            try:
                value = record.toUnicode().strip()
            except Exception:
                continue
            if value:
                return value
    return None


def _normalize_font_family_name(name: str) -> str:
    return " ".join(name.split()).casefold()


def _safe_asset_stem(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    filtered = "".join(ch if ch.isalnum() else "-" for ch in ascii_text)
    cleaned = "-".join(part for part in filtered.split("-") if part)
    return cleaned.lower() or "font"


def _unique_keep_order(values: List[str]) -> List[str]:
    seen = set()
    ordered = []
    for item in values:
        key = item.strip()
        if not key:
            continue
        if key in seen:
            continue
        seen.add(key)
        ordered.append(key)
    return ordered


def _name_aliases(font: TTFont) -> List[str]:
    aliases: List[str] = []
    for record in font["name"].names:
        if record.nameID not in {1, 4, 6, 16, 17}:
            continue
        try:
            value = record.toUnicode().strip()
        except Exception:
            continue
        if value:
            aliases.append(value)
    return _unique_keep_order(aliases)


def _copy_font_to_assets(
    source_path: Path,
    assets_dir: Path,
    family_name: str,
    weight: int,
    style: str,
) -> str:
    assets_dir.mkdir(parents=True, exist_ok=True)
    stem = _safe_asset_stem(family_name)
    suffix = source_path.suffix.lower()
    dest_name = f"{stem}-{weight}-{style}{suffix}"
    dest_path = assets_dir / dest_name

    if not dest_path.exists() or source_path.stat().st_mtime > dest_path.stat().st_mtime:
        shutil.copy2(source_path, dest_path)

    return f"fonts/{dest_name}"


def read_font_metadata(font_path: Path) -> Tuple[str, int, str, str, List[str]]:
    if not font_path.exists():
        raise FileNotFoundError(f"Font file not found: {font_path}")
    if not font_path.is_file():
        raise ValueError(f"Font path is not a file: {font_path}")

    font_format = FONT_FORMATS.get(font_path.suffix.lower())
    if font_format is None:
        raise ValueError(
            f"Unsupported font file: {font_path} (.ttf/.otf/.woff/.woff2 only)"
        )

    with TTFont(font_path) as font:
        family_name = _get_name_record(font, (16, 1))
        if family_name is None:
            raise ValueError(f"Unable to determine font family name: {font_path}")
        aliases = _name_aliases(font)
        if family_name not in aliases:
            aliases.insert(0, family_name)

        weight = 400
        if "OS/2" in font:
            weight = int(getattr(font["OS/2"], "usWeightClass", 400) or 400)

        style = "normal"
        if "post" in font and float(getattr(font["post"], "italicAngle", 0) or 0) != 0:
            style = "italic"
        elif "head" in font and getattr(font["head"], "macStyle", 0) & 0b10:
            style = "italic"
        else:
            subfamily_name = _get_name_record(font, (17, 2)) or ""
            if "italic" in subfamily_name.casefold() or "oblique" in subfamily_name.casefold():
                style = "italic"

    return family_name, weight, style, font_format, aliases


def resolve_font_family(font_path: Path, font_assets_dir: Path) -> Tuple[str, str]:
    font_path = font_path.expanduser().resolve()
    base_family_name, _, _, _, _ = read_font_metadata(font_path)
    base_family_key = _normalize_font_family_name(base_family_name)

    variant_files: List[Tuple[Path, int, str, str, List[str]]] = []
    for candidate in sorted(font_path.parent.iterdir()):
        if candidate.suffix.lower() not in FONT_FORMATS or not candidate.is_file():
            continue

        try:
            family_name, weight, style, font_format, aliases = read_font_metadata(candidate)
        except Exception:
            continue

        if _normalize_font_family_name(family_name) != base_family_key:
            continue

        variant_files.append((candidate, weight, style, font_format, aliases))

    if not variant_files:
        raise ValueError(f"No usable font variants found for: {font_path}")

    variant_files.sort(key=lambda item: (item[1], item[2] == "italic", item[0].name.casefold()))

    css_lines = ["/* Auto-generated @font-face rules */"]
    for variant_path, weight, style, font_format, aliases in variant_files:
        asset_rel_path = _copy_font_to_assets(
            source_path=variant_path,
            assets_dir=font_assets_dir,
            family_name=base_family_name,
            weight=weight,
            style=style,
        )
        local_sources = ", ".join(f"local('{name}')" for name in _unique_keep_order(aliases))
        if local_sources:
            src_value = f"{local_sources}, url('{asset_rel_path}') format('{font_format}')"
        else:
            src_value = f"url('{asset_rel_path}') format('{font_format}')"
        css_lines.append("@font-face {")
        css_lines.append(f"  font-family: '{base_family_name}';")
        css_lines.append(f"  src: {src_value};")
        css_lines.append(f"  font-weight: {weight};")
        css_lines.append(f"  font-style: {style};")
        css_lines.append("  font-display: swap;")
        css_lines.append("}")
        css_lines.append("")

    return base_family_name, "\n".join(css_lines).strip()


def build_style_blocks(
    font_path: Optional[Path],
    main_css_path: Path,
    codeblock_css_path: Path,
    print_margin: str,
    font_assets_dir: Path,
    code_font_path: Optional[Path] = None,
    enable_parser: bool = False,
    enable_table_horizontal_scroll: bool = False,
) -> List[str]:
    blocks: List[str] = []

    font_family_name = None
    content_font_faces = None
    if font_path is not None:
        font_family_name, content_font_faces = resolve_font_family(font_path, font_assets_dir)
        blocks.append(content_font_faces)

    code_font_family = None
    blocks.append(
        """
.markdown-preview.markdown-preview {
"""
    )
    if code_font_path is not None:
        code_font_family, code_font_faces = resolve_font_family(code_font_path, font_assets_dir)
        if code_font_faces != content_font_faces:
            blocks.append(code_font_faces)
        if font_family_name:
            blocks.append(f"""
  *:not(:is(
    pre, pre *, code, code *, kbd, kbd *, samp, samp *,
    .katex, .katex *, .MathJax, .MathJax *, mjx-container, mjx-container *
  )) {{
    font-family: '{font_family_name}', 'Source Sans Pro', 'Noto Sans CJK SC', 'Noto Sans SC', sans-serif !important;
  }}
""")

    if not enable_parser:
        for i in image_size_range:
            blocks.append(f"""
  img[alt*="{i}"] {{
    width: {i}% !important;
    height: auto;
    display: block;
    margin: 0 auto;
  }}
""")

    blocks.append(
        load_template("css", "style.css")
    )

    if ENABLE_H2_UNDERLINE:
        blocks.append(
            """
  h1::after,
  h2::after {
    content: "";
    display: block;
    width: 100%;
    height: 0.5px;
    background-color: #bbbbbb;
    margin-top: 0.2em;
  }
""")

    if not enable_table_horizontal_scroll:
        blocks.append("""
  table {
    display: table !important;
    width: 100% !important;
    max-width: 100% !important;
    table-layout: fixed !important;
    overflow-x: visible !important;
  }
  th, td {
    white-space: normal !important;
    overflow-wrap: anywhere !important;
    word-break: break-word !important;
  }
""")

    if code_font_family:
        blocks.append(f"""
  pre, pre *, code, code *, kbd, kbd *, samp, samp *, pre[class*="language-"], pre[class*="language-"] *, code[class*="language-"], code[class*="language-"] * {{
    font-family: '{code_font_family}', monospace !important;
  }}
  .line-numbers-rows, .line-numbers-rows > span:before {{
    font-family: '{code_font_family}', monospace !important;
  }}
""")

    blocks.append("\n}\n")

    blocks.append(
        generate_print_style(
            main_css_path,
            codeblock_css_path,
            print_margin=print_margin,
        )
    )

    return blocks


def build_parser_blocks(mappers: str) -> Tuple[List[str], List[str]]:
    parser_blocks: List[str] = []
    html_blocks: List[str] = []
    # Paragraph indent
    parser_blocks.append(
        load_template("parser", "preparser_indent.js")
    )
    # Fence extract (must run first in markdown preprocess)
    parser_blocks.append(
        load_template("parser", "preparser_fence_extract.js")
    )
    # PDF center
    parser_blocks.append(
        load_template("parser", "preparser_pdf.js")
    )
    # Image alt size
    html_blocks.append(
        load_template("parser", "postparser_image.js")
    )
    # Table
    html_blocks.append(
        load_template("parser", "postparser_table.js")
    )
    # Image title
    html_blocks.append(
        load_template("parser", "postparser_imagetitle.js")
    )
    # title prefix
    levels = []
    for i in re.split(r"\s*,\s*", mappers.strip()):
        if i not in {"roman", "romanUpper", "latin", "latinUpper", "chinese", "number", "none"}:
            raise ValueError(f"Unsupported mapper: {i}, only <roman|romanUpper|latin|latinUpper|chinese|number|none> are supported.")
        levels.append(i)
    while len(levels) < 6:
        levels.append("none")
    if len(levels) > 6:
        raise ValueError(f"Too many mappers: {len(levels)}, at most 6 levels are supported.")
    parser_blocks.append(
        load_template("parser", "preparser_titleprefix.js")
        .replace("@MAPPER_PLACEHOLDER@", ", ".join(levels))
    )
    # Multicolunn
    parser_blocks.append(
        load_template("parser", "preparser_column.js")
    )
    # Fence restore (must run last in markdown preprocess)
    parser_blocks.append(
        load_template("parser", "preparser_fence_restore.js")
    )
    return parser_blocks, html_blocks


def write_output(
    output_path: Path,
    blocks: List[str],
    parse_blocks: List[str] = [],
    html_blocks: List[str] = [],
) -> None:
    try:
        import jsbeautifier
    except ImportError:
        jsbeautifier = None
    try:
        import cssbeautifier
    except ImportError:
        cssbeautifier = None
    output_path.mkdir(parents=True, exist_ok=True)
    style_less = output_path / "style.less"
    text = "\n".join(map(lambda x: x.strip("\n"), blocks))
    if cssbeautifier:
        text = cssbeautifier.beautify(text, {"indent_size": 2})
    style_less.write_text(text, encoding="utf-8")
    print(f"Generated style.less written to: {style_less.resolve()}")
    parser_blocks: List[str] = []
    if parse_blocks:
        parser_blocks.append(
            "  onWillParseMarkdown: async function(markdown) {"
        )
        parser_blocks.extend(parse_blocks)
        parser_blocks.append("    return markdown;")
        parser_blocks.append("  },")
    elif html_blocks:
        parser_blocks.append(
            "  onWillParseMarkdown: async function(markdown) { return markdown; },"
        )
    if html_blocks:
        parser_blocks.append(
            "  onDidParseMarkdown: async function(html) {"
        )
        parser_blocks.extend(html_blocks)
        parser_blocks.append("    return html;")
        parser_blocks.append("  },")
    elif parse_blocks:
        parser_blocks.append("  onDidParseMarkdown: async function(html) { return html; },")
    if parser_blocks:
        parser_js = output_path / "parser.js"
        output = "\n" + "\n".join(map(lambda x: x.strip("\n"), parser_blocks)) + "\n"
        output = f"({{{output}}})"
        if jsbeautifier:
            output = jsbeautifier.beautify(output, {"indent_size": 2}) # pyright: ignore[reportArgumentType]
        parser_js.write_text(output, encoding="utf-8")
        print(f"Generated parser.js written to: {parser_js.resolve()}")


def resolve_crossnote_style_path(extension_dir: Path, css_path: Path) -> Path:
    if css_path.is_absolute():
        return css_path
    return extension_dir / "crossnote" / "styles" / css_path


def main():
    extension_dir = resolve_extension_dir(
        extensions_root=EXTENSIONS_ROOT,
        extension_pattern=EXTENSION_PATTERN,
        explicit_extension_dir=EXTENSION_DIR,
    )
    main_css_path = resolve_crossnote_style_path(
        extension_dir=extension_dir,
        css_path=MAIN_CSS,
    )
    codeblock_css_path = resolve_crossnote_style_path(
        extension_dir=extension_dir,
        css_path=CODEBLOCK_CSS,
    )
    # 检查必需参数
    if MAIN_CSS is None or CODEBLOCK_CSS is None:
        raise ValueError("MAIN_CSS and CODEBLOCK_CSS must be provided in configuration.")
    
    print_margin = PRINT_MARGIN.strip()
    output_path = OUTPUT.expanduser().resolve()
    font_assets_dir = output_path / "fonts"

    blocks = build_style_blocks(
        font_path=FONT,
        main_css_path=main_css_path,
        codeblock_css_path=codeblock_css_path,
        print_margin=print_margin,
        font_assets_dir=font_assets_dir,
        code_font_path=CODE_FONT,
        enable_parser=ENABLE_PARSER,
        enable_table_horizontal_scroll=ENABLE_TABLE_HORIZONTAL_SCROLL,
    )

    if ENABLE_PARSER:
        parse_blocks, html_blocks = build_parser_blocks(AUTO_COUNT)
    else:
        parse_blocks, html_blocks = [], []

    write_output(output_path, blocks, parse_blocks, html_blocks)


if __name__ == "__main__":
    main()
