#!/usr/bin/env bash
# 安装截图工具依赖。
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd -P)"
cd "$SCRIPT_DIR"

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

.venv/bin/pip install -r requirements.txt

echo "安装完成。将以下路径加入 PATH 或创建符号链接："
echo "  $SCRIPT_DIR/scripts/code-shot"
echo "  $SCRIPT_DIR/scripts/term-shot"
