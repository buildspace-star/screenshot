# screenshot

终端风格的截图工具集。将代码文件或命令输出渲染为 PNG 图像。

## 安装

```bash
pip install -r requirements.txt
```

然后将 `scripts/` 目录加入 PATH，或者创建符号链接：

```bash
ln -s $(pwd)/scripts/code-shot /usr/local/bin/code-shot
ln -s $(pwd)/scripts/term-shot /usr/local/bin/term-shot
```

## 工具

### code-shot — 代码文件截图

将源文件渲染为带有语法高亮的 PNG 图像。

```bash
code-shot -f app.py                     # 基础截图
code-shot -f app.py --dark              # 深色主题
code-shot -f app.py -l 10-50            # 仅截取行范围
echo 'print(1)' | code-shot --stdin -L python   # 管道输入
code-shot --text 'SELECT 1;' -L sql -o q.png    # 直接传入文本
code-shot -c 'python experiment.py' -o r.png    # 执行命令并截图
```

| 选项 | 描述 |
|------|------|
| `-f`, `--file` | 代码文件路径 |
| `-l`, `--lines` | 行范围，如 `"10-25"` |
| `--stdin` | 从标准输入读取 |
| `--text` | 直接传入文本 |
| `-c`, `--command` | 执行命令并截图 |
| `-L`, `--language` | 指定 Pygments lexer |
| `--dark` | 深色背景（默认浅色） |
| `--no-line-numbers` | 隐藏行号 |
| `--json` | JSON 模式输出 |
| `--list-themes` | 列出所有可用主题 |

### term-shot — 终端命令截图

执行命令并将输出渲染为模拟终端的 PNG 图像。

```bash
term-shot -c 'python experiment.py'                        # 运行并截图
term-shot -c 'ls -la' -o listing.png                       # 指定输出
term-shot -c './run.sh' --cwd ~/project -o result.png      # 指定工作目录
term-shot -c './run.sh' --prompt-platform mac --prompt-user user --prompt-host MacBook
term-shot -c 'python experiment.py' --prompt-platform windows --prompt-user User --theme dark
echo "output" | term-shot --stdin -o result.png            # 管道输入
```

| 选项 | 描述 |
|------|------|
| `-c`, `--command` | 要执行的命令 |
| `--cwd` | 工作目录（默认：当前目录） |
| `--stdin` | 从标准输入读取 |
| `-o`, `--output` | 输出 PNG 路径 |
| `-L`, `--language` | Pygments lexer（默认：console） |
| `--theme` | 主题：`light` 白底黑字，`dark` 黑底白字 |
| `--dark` | 等同于 `--theme dark` |
| `--prompt-platform` | 提示符格式：`auto`、`mac`、`windows` |
| `--prompt-user` | 提示符用户名 |
| `--prompt-host` | mac 提示符主机名 |
| `--font-size` | 字体大小（默认：20） |
| `--json` | JSON 模式输出 |

截图自动包含终端提示符行。mac 风格：

```
用户名@主机名 当前目录 % 命令
命令输出...
```

Windows 风格：

```
C:\Users\用户名\目录> 命令
命令输出...
```

默认：纯白背景 `(255,255,255)`、纯黑文字 `(0,0,0)`、无行号。`--theme dark` 使用黑色背景和白色文字。

## 依赖

- Python 3.8+
- Pillow（图像渲染）
- Pygments（语法高亮）
