const cr_regex = /(<td.*?)>(:?c\d+:?|:?r\d+:?|:?c\d+r\d+:?|:?r\d+c\d+:?)\s+(.*)<\/td>/g;
html = html.replace(cr_regex, (match, tdStart, spanInfo, content) => {
    let colspan = 1;
    let rowspan = 1;
    let align = '';
    const colMatch = spanInfo.match(/c(\d+)/);
    if (colMatch) {
        colspan = parseInt(colMatch[1], 10);
    }
    const rowMatch = spanInfo.match(/r(\d+)/);
    if (rowMatch) {
        rowspan = parseInt(rowMatch[1], 10);
    }
    if (spanInfo.startsWith(':') && spanInfo.endsWith(':')) {
        align = 'center';
    } else if (spanInfo.startsWith(':')) {
        align = 'left';
    } else if (spanInfo.endsWith(':')) {
        align = 'right';
    }
    if (align) {
        const styleMatch = tdStart.match(/style="(.*?)"/i);
        if (styleMatch) {
            tdStart = tdStart.replace(styleMatch[0], `style=\"${styleMatch[2]} text-align: ${align} !important;\"`);
        } else {
            tdStart += ` style=\"text-align: ${align} !important;\"`;
        }
    }
    return `${tdStart} colspan="${colspan}" rowspan="${rowspan}">${content}</td>`;
});
const rm_regex = /<td[^>]*>\\<\/td>/g;
html = html.replace(rm_regex, '');
const esc_regex = /<td([^>]*)>\\\\<\/td>/g;
html = html.replace(esc_regex, '<td$1>\\</td>');
const th_regex = /(<th.*?)>(:?c\d+:?)\s+(.*)<\/th>/g;
html = html.replace(th_regex, (match, thStart, spanInfo, content) => {
    let colspan = 1;
    let align = '';
    const colMatch = spanInfo.match(/c(\d+)/);
    if (colMatch) {
        colspan = parseInt(colMatch[1], 10);
    }
    if (spanInfo.startsWith(':') && spanInfo.endsWith(':')) {
        align = 'center';
    } else if (spanInfo.startsWith(':')) {
        align = 'left';
    } else if (spanInfo.endsWith(':')) {
        align = 'right';
    }
    if (align) {
        const styleMatch = thStart.match(/style="(.*?)"/i);
        if (styleMatch) {
            thStart = thStart.replace(styleMatch[0], `style=\"${styleMatch[2]} text-align: ${align} !important;\"`);
        } else {
            thStart += ` style=\"text-align: ${align} !important;\"`;
        }
    }
    return `${thStart} colspan="${colspan}">${content}</th>`;
});
const rm_th_regex = /<th[^>]*>\\<\/th>/g;
html = html.replace(rm_th_regex, '');
const esc_th_regex = /<th([^>]*)>\\\\<\/th>/g;
html = html.replace(esc_th_regex, '<th$1>\\</th>');