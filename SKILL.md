---
name: screenshot
description: 截图工具集。code-shot 将代码文件渲染为语法高亮 PNG，term-shot 执行终端命令并捕获输出为终端风格截图。适用于代码截图、实验输出快照、命令运行结果截图等场景。
---

# code-shot

终端风格的代码截图工具。将源文件渲染为带有语法高亮的 PNG 图像。

## 使用方法

```
code-shot -f <文件路径> [选项]
```

### 常用选项

| 标志 | 描述 |
|------|-------------|
| `-f`, `--file` | 代码文件路径 |
| `-l`, `--lines` | 行范围，例如 `"10-25"` 或 `"10-25,30-40"` |
| `-o`, `--output` | 输出 PNG 路径（默认：根据文件名自动生成） |
| `-t`, `--theme` | Pygments 样式名称（默认：浅色为 `default`，深色为 `monokai`） |
| `--font-size` | 字体大小，单位 px（默认：20） |
| `--padding` | 内边距，单位 px（默认：30） |
| `--scale` | 高 DPI 缩放因子（默认：2 = Retina） |
| `--dark` | 深色终端风格背景（默认为浅色） |
| `--no-line-numbers` | 不显示行号 |
| `--json` | 输出 JSON 格式，方便脚本调用 |
| `--list-themes` | 列出所有可用的 Pygments 主题 |
| `--stdin` | 从标准输入读取代码/文本 |
| `--text` | 直接传入文本内容（适用于短文本） |
| `-c`, `--command` | 执行命令并截图其输出（自动包含终端提示符） |
| `-L`, `--language` | 手动指定 Pygments lexer 名称（如 bash, python, console, json） |

## 示例

```bash
# 基础截图（白色背景，2x Retina 缩放）
code-shot -f src/app.py

# 深色主题
code-shot -f src/app.py --dark

# 仅截取特定行
code-shot -f src/app.py -l 10-50

# 多个行范围
code-shot -f src/app.py -l 10-25,40-60

# 输出到指定文件，1x 缩放（文件更小）
code-shot -f src/app.py -o output.png --scale 1

# 输出 JSON 格式
code-shot -f src/app.py --json

# 从 stdin 管道输入（Agent 常用）
echo 'print(42)' | code-shot --stdin -L python -o result.png

# 直接传入文本
code-shot --text 'SELECT * FROM users;' -L sql -o query.png

# 执行命令并截图（包含终端提示符）
code-shot -c 'python experiment.py' -o result.png
```

## 规则

- 输入源优先级：`-c` > `--text` > `--stdin` > `-f`，至少指定一个。
- 默认值：浅灰背景 `(248,248,248)`，使用 `default` Pygments 主题，2x 缩放，显示行号。
- 使用 `--dark` 可获得终端风格的深色背景，配合 `monokai` 主题。
- 除非文件在当前工作目录中，否则请始终对路径使用绝对路径。
- 对于较大的文件，请使用 `-l` 仅捕获相关的部分。
- `--json` 标志输出 `{"status": "ok", "path": "..."}` 或 `{"error": "..."}`。

# term-shot

终端命令运行结果截图工具。执行命令并将输出渲染为模拟 macOS 终端窗口的 PNG 图像。专为实验报告、命令输出快照设计。

## 使用方法

```
term-shot -c <命令> [选项]
```

### 常用选项

| 标志 | 描述 |
|------|-------------|
| `-c`, `--command` | 要执行的命令 |
| `--cwd` | 命令执行的工作目录（默认：当前目录） |
| `--stdin` | 从标准输入读取文本（而非执行命令） |
| `-o`, `--output` | 输出 PNG 路径（默认：`term-shot-{时间戳}.png`） |
| `-L`, `--language` | Pygments lexer 名称（默认：`console`） |
| `--theme` | 主题：`light` 白底黑字，`dark` 黑底白字（默认：`light`） |
| `--dark` | 等同于 `--theme dark` |
| `--prompt-platform` | 提示符格式：`auto`、`mac`、`windows`（默认：`auto`） |
| `--prompt-user` | 提示符用户名，适合公开截图或跨机器复用 |
| `--prompt-host` | mac 提示符主机名 |
| `--font-size` | 字体大小，单位 px（默认：20） |
| `--padding` | 内边距，单位 px（默认：30） |
| `--scale` | 高 DPI 缩放因子（默认：2 = Retina） |
| `--json` | 输出 JSON 格式，方便脚本/Agent 调用 |

## 示例

```bash
# 运行命令并截图
term-shot -c 'python experiment.py'

# 指定输出路径
term-shot -c 'ls -la' -o listing.png

# 在指定目录下运行（提示符会显示该路径）
term-shot -c './run.sh' --cwd ~/project -o result.png

# mac 风格提示符，白底黑字
term-shot -c './run.sh' --prompt-platform mac --prompt-user user --prompt-host MacBook --theme light

# Windows 风格提示符，黑底白字
term-shot -c 'python experiment.py' --prompt-platform windows --prompt-user User --theme dark

# 管道输入
echo "program output" | term-shot --stdin -o result.png

# Agent 调用（JSON 模式）
term-shot -c 'python experiment.py' --json
```

## 截图内容

使用 `-c/--command` 时，截图会包含终端提示符行。macOS 风格：

```
用户名@主机名 当前目录 % 命令
命令输出...
```

Windows 风格：

```
C:\Users\用户名\目录> 命令
命令输出...
```

## 规则

- **默认**：纯白背景 `(255,255,255)`、纯黑文字 `(0,0,0)`、无行号、纯色文字。
- `--theme light` 使用白底黑字，`--theme dark` 使用黑底白字。
- `-c` 和 `--stdin` 必须指定其一。
- `--stdin` 模式不会自动添加提示符，仅渲染标准输入内容。
- 自动剥离命令输出中的 ANSI 转义码（如颜色码），确保截图干净可读。
- 超时时间 300 秒，stderr 会合并到输出中显示。
- mac 提示符默认显示为 `用户@主机 当前目录 % 命令`，当前目录只显示最后一级目录名。
- Windows 提示符显示为 `C:\Users\用户\...\目录> 命令`。
- 用 `--prompt-user` 指定截图里的用户名，避免在公开仓库中写死本机用户名。
- Agent 调用推荐使用 `--json` 获取输出路径。
