# MdMisc

这是一个用于存放与排版有关的杂项工具的仓库

## 1. `mdcss.py`

这是一个增强 vscode/markdown-preview-enhanced 插件功能的脚本，旨在拓展 markdown 的排版能力，让相对轻量的排版需求不必使用 $\LaTeX$

脚本生成的配置文件允许为PDF导出设置单独的主题，同时实现了图片的排版增强、表格的合并单元格、自定义字体、自定义页边距等功能

注意，脚本提供的部分功能必须使用 **Chrome (Puppeteer)** 才能生效

### 1.1 使用示例

```bash
python mdcss.py \
    --font ~/.local/share/fonts/HanSans/CN/SourceHanSansCN-Regular.otf \
    --code-font ~/.local/share/fonts/maple-NF-CN/MapleMonoNL-NF-CN-Regular.ttf \
    --main-css preview_theme/github-light.css \
    --codeblock-css prism_theme/github.css \
    --print-margin "5mm" \
    --enable-parser
```

### 1.2 支持的功能

1. 打印样式
	1. 使用 `--main-css` 来设置打印时使用的正文主题，传入的相对路径在 `{EXTENSION_DIR}/crossnote` 中搜索
	2. 使用 `--codeblock-css` 来设置打印时使用的代码块主题，传入的相对路径在 `{EXTENSION_DIR}/crossnote` 中搜索
2. 图片
    1. 宽度设置：在alt中以1-2位整数开头，设置宽度百分比，`--enable-parser` 启用时还支持添加单位px来设置绝对宽度
    2. 单行多图布局：在alt中添加 `r`
    3. 左右对齐：在alt中添加 `L/R`
    4. 文字环绕图片：在alt中添加 `f`
    5. 图片标题：当 `--enable-parser` 启用时，可以在alt中使用 `([.]title)` 来插入标题，开头的`.`会被替换成递增的 `图N:`，对于 `r` 样式的图片，可以在第一个子图中添加 `([.]subfigure-title([.]figure-title))` 来添加整体标题
3. 字体
    1. 使用 `--font` 设置全局字体，只需要给出一个字体文件，程序会自动解析同族字体
    2. 使用 `--code-font` 设置代码块字体，只需要给出一个字体文件，程序会自动解析同族字体
    3. 对于公式，始终使用默认字体
4. 页边距
    - 使用 `--print-margin` 设置页边距
5. 小标题编号（当 `--enable-parser` 启用时生效）
	1. 在标题开头的 `.` 会被替换成编号
	2. 编号有多种样式
		- `latin[Upper]`: `a)`, `b)`, `c)`
		- `roman[Upper]`: `i)`, `ii)`, `iii)`，上限3999
		- `chinese`: `一、`, `二、`, `三、`
		- `number`: `1. `, `2. `, `3. `，且 `number` 在连续使用时可以生成 `1.1. `, `1.2. `, `1.3. `
		- `none`: 不编号
	 3. 设置 `--auto-count` 参数为 `,` 分割的六个编号样式，默认 `none, chinese, number, number, latin, roman`
6. PDF导入居中（当 `--enable-parser` 启用时生效）
    -  `@import` 导入的PDF会居中显示
7. 表格增强（当 `--enable-parser` 启用时生效）
    1. 使用 `\` 删除单元格（包括标题），如需要输入`\`，请使用`\\\\`
    2. 使用 `c\d` 和 `d\d` 的前缀来表示合并单元格，使用 `:` 为单元格单独设置对齐
    3. 例子
        ```markdown
        | c2: 标题1 |      \     |     标题2    | 标题3 |
        | --------- | ---------- | ------------ | ----- |
        |   文本1   | :c2: 文本2 |       \      |  \\\  |
        |  r2 文本3 |    文本4   | :r2c2: 文本5 |   \   |
        |     \     |    文本6   |       \      |   \   |
        ```
8. 代码块不会另起一页，而是直接跟随上一页


## 2. `test/`

存放测试用markdown