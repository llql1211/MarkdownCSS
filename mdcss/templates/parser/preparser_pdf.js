const regex = /^@import\s+"(.*\.pdf)"\s*(\{.*?\})?/mg;
markdown = markdown.replace(regex, (match, pdf, argument) => {
    return `
<div style="display: flex; justify-content: center; flex-wrap: wrap;">

@import "${pdf}"{${argument}}

</div>

`
});