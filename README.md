# MdMisc

这是一个用于存放与排版有关的杂项工具的仓库，几乎不会维护

## test/

存放测试用markdown

## mdcss.py

由于 vscode 的 markdown-preview-enhanced 插件无法为导出设置单独的主题，实现了该功能，同时实现了图片的语法增强、自定义字体、自定义页边距等功能

**必须使用 Chrome (Puppeteer) 才能生效**

使用示例

```bash
python mdcss.py \
    --font ~/.local/share/fonts/FZ-Hei/方正兰亭黑.TTF \
    --code-font /usr/share/fonts/truetype/ubuntu/UbuntuSansMono[wght].ttf \
    --preview-css preview_theme/github-light.css --codeblock-css prism_theme/github.css \
    --print-margin "5mm"
```
