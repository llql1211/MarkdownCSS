__mdcssHasIndent = false;
if (markdown.trimStart().startsWith('@indent')) {
    markdown = markdown.trimStart().slice('@indent'.length);
    __mdcssHasIndent = true;
} else if (markdown.trimStart().startsWith('<indent>')) {
    markdown = markdown.trimStart().slice('<indent>'.length);
    __mdcssHasIndent = true;
}
if (__mdcssHasIndent) {
    markdown = `<div class="has-indent">

${markdown}

</div>

`;
}
