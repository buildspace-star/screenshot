#!/usr/bin/env python3
"""
term-shot - 终端命令运行结果截图工具。
执行命令并将输出渲染为终端风格的 PNG 截图。
默认：白色背景、黑色文字、无行号、纯色文本。
"""

import argparse
import datetime
import getpass
import ntpath
import os
import re
import socket
import subprocess
import sys

# 复用 code_shot 的渲染引擎
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from code_shot import find_font, build_lines
from PIL import Image, ImageDraw
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound

# ---- 默认设置 ----
DEFAULT_FONT_SIZE = 20
DEFAULT_PADDING = 30
THEMES = {
    "light": {"bg": (255, 255, 255), "fg": (0, 0, 0)},
    "dark": {"bg": (0, 0, 0), "fg": (255, 255, 255)},
}

# ANSI 转义码正则（覆盖 CSI、OSC、标题序列等）
ANSI_RE = re.compile(r'\x1b\[[0-9;?]*[A-Za-z]|\x1b\][^\x07]*\x07|\x1b\]0;[^\x1b]*\x1b\\|\x1b\[[0-9;]*[mKABCD]|\x1b\[[?][0-9;]*[hl]')


def strip_ansi(text):
    """移除 ANSI 转义码，保留可见文本。"""
    return ANSI_RE.sub('', text)


def format_macos_prompt_path(work_dir):
    """将路径格式化为更接近 macOS 终端默认提示符的样式。"""
    home = os.path.expanduser("~")
    work_dir = os.path.abspath(work_dir)
    if work_dir == home:
        return "~"
    return os.path.basename(work_dir.rstrip(os.sep)) or os.sep


def format_macos_hostname():
    """将主机名格式化为更接近 macOS 终端常见显示。"""
    host = socket.gethostname()
    return host.split(".", 1)[0]


def resolve_prompt_platform(platform):
    if platform != "auto":
        return platform
    return "windows" if os.name == "nt" else "mac"


def format_windows_prompt_path(work_dir, prompt_user):
    """将路径格式化为 Windows 命令提示符风格。"""
    work_dir = os.path.abspath(work_dir)
    if os.name == "nt":
        return ntpath.normpath(work_dir)

    home = os.path.expanduser("~")
    try:
        rel = os.path.relpath(work_dir, home)
    except ValueError:
        rel = None

    if rel and not rel.startswith(".."):
        win_rel = rel.replace(os.sep, "\\")
        if win_rel == ".":
            return f"C:\\Users\\{prompt_user}"
        return f"C:\\Users\\{prompt_user}\\{win_rel}"

    return "C:" + work_dir.replace("/", "\\")


def format_prompt(work_dir, command, prompt_user, prompt_host, platform):
    platform = resolve_prompt_platform(platform)
    if platform == "windows":
        disp_cwd = format_windows_prompt_path(work_dir, prompt_user)
        return f"{disp_cwd}> {command}"
    disp_cwd = format_macos_prompt_path(work_dir)
    return f"{prompt_user}@{prompt_host} {disp_cwd} % {command}"


def render_term_image(lines, theme, font_size, padding, output_path):
    """将终端输出行渲染为 PNG 图像。返回绝对输出路径。"""
    font = find_font(font_size)
    bg_color = THEMES[theme]["bg"]
    fg_color = THEMES[theme]["fg"]

    bbox = font.getbbox("X")
    char_width = bbox[2] - bbox[0]
    ascent, descent = font.getmetrics()
    line_height = ascent + descent + 2

    max_line_len = 0
    for line in lines:
        line_len = sum(len(seg[0]) for seg in line)
        max_line_len = max(max_line_len, line_len)

    content_w = max_line_len * char_width
    total_w = padding * 2 + max(content_w, 200)
    total_h = padding * 2 + max(len(lines), 1) * line_height

    img = Image.new("RGB", (total_w, total_h), bg_color)
    draw = ImageDraw.Draw(img)

    y = padding
    for line in lines:
        x = padding
        for text, _token_type in line:
            draw.text((x, y), text, fill=fg_color, font=font)
            x += len(text) * char_width
        y += line_height

    img.save(output_path, "PNG")
    return os.path.abspath(output_path)


def main():
    parser = argparse.ArgumentParser(
        description="终端命令运行结果截图工具。执行命令并渲染为终端风格 PNG。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例:\n"
               "  term-shot -c 'python experiment.py'\n"
               "  term-shot -c 'ls -la' -o listing.png\n"
               "  echo 'output' | term-shot --stdin",
    )
    parser.add_argument("-c", "--command", help="要执行的命令")
    parser.add_argument("--cwd", help="命令执行的工作目录（默认：当前目录）")
    parser.add_argument("--stdin", action="store_true", help="从标准输入读取文本")
    parser.add_argument("-o", "--output", help="输出 PNG 路径（默认：自动生成）")
    parser.add_argument("-L", "--language", default="console",
                        help="Pygments lexer 名称，仅用于分行处理（默认：console）")
    parser.add_argument("--theme", choices=sorted(THEMES), default="light",
                        help="截图主题：light=白底黑字，dark=黑底白字（默认：light）")
    parser.add_argument("--dark", action="store_true",
                        help="等同于 --theme dark")
    parser.add_argument("--prompt-platform", choices=["auto", "mac", "windows"], default="auto",
                        help="提示符目录格式（默认：auto）")
    parser.add_argument("--prompt-user", default=getpass.getuser(),
                        help="提示符用户名（默认：当前系统用户）")
    parser.add_argument("--prompt-host", default=format_macos_hostname(),
                        help="mac 提示符主机名（默认：当前短主机名）")
    parser.add_argument("--font-size", type=int, default=DEFAULT_FONT_SIZE,
                        help=f"字体大小，单位 px（默认：{DEFAULT_FONT_SIZE}）")
    parser.add_argument("--padding", type=int, default=DEFAULT_PADDING,
                        help=f"内边距，单位 px（默认：{DEFAULT_PADDING}）")
    parser.add_argument("--scale", type=float, default=2,
                        help="高 DPI 渲染缩放因子（默认：2）")
    parser.add_argument("--json", action="store_true",
                        help="成功后输出 JSON 格式")
    args = parser.parse_args()
    if args.dark:
        args.theme = "dark"

    # 确定工作目录
    work_dir = os.getcwd()
    if args.cwd:
        work_dir = os.path.abspath(os.path.expanduser(args.cwd))
        if not os.path.isdir(work_dir):
            msg = f"工作目录不存在: {args.cwd}"
            print(f'{{"error": "{msg}"}}' if args.json else f"错误: {msg}", file=sys.stderr)
            sys.exit(1)

    # 输入源：--command > --stdin
    if args.command:
        try:
            result = subprocess.run(
                args.command, shell=True, capture_output=True, text=True,
                timeout=300, cwd=work_dir,
            )
        except subprocess.TimeoutExpired:
            msg = "命令执行超时 (300s)"
            print(f'{{"error": "{msg}"}}' if args.json else f"错误: {msg}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            msg = f"命令执行失败: {e}"
            print(f'{{"error": "{msg}"}}' if args.json else f"错误: {msg}", file=sys.stderr)
            sys.exit(1)

        output_text = strip_ansi(result.stdout)
        if result.stderr:
            stderr_text = strip_ansi(result.stderr)
            if output_text and not output_text.endswith("\n"):
                output_text += "\n"
            output_text += stderr_text
        if output_text and not output_text.endswith("\n"):
            output_text += "\n"

        prompt = format_prompt(
            work_dir=work_dir,
            command=args.command,
            prompt_user=args.prompt_user,
            prompt_host=args.prompt_host,
            platform=args.prompt_platform,
        )
        text = f"{prompt}\n{output_text}"
    elif args.stdin:
        text = strip_ansi(sys.stdin.read())
    else:
        msg = "必须指定 -c/--command 或 --stdin"
        print(f'{{"error": "{msg}"}}' if args.json else f"错误: {msg}", file=sys.stderr)
        sys.exit(1)

    # 输出路径
    if args.output:
        output_path = args.output
    else:
        ts = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        output_path = f"term-shot-{ts}.png"

    # Lexer
    try:
        lexer = get_lexer_by_name(args.language, stripall=False)
    except ClassNotFound:
        msg = f"找不到 lexer '{args.language}'"
        print(f'{{"error": "{msg}"}}' if args.json else f"错误: {msg}", file=sys.stderr)
        sys.exit(1)

    # Tokenize → 构建显示行
    tokens = list(lexer.get_tokens(text))
    display_lines = build_lines(tokens)

    # 缩放
    font_size = int(args.font_size * args.scale)
    padding = int(args.padding * args.scale)

    result_path = render_term_image(display_lines, args.theme, font_size, padding, output_path)

    if args.json:
        print(f'{{"status": "ok", "path": "{result_path}"}}')
    else:
        print(f"已保存: {result_path}")


if __name__ == "__main__":
    main()
