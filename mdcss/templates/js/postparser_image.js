function extractWidthFromAlt(alt) {
    if (!alt) return null;

    // Support: 25, 25%, 300px, 25r, 30R, 40Lf, 40Rf
    const token = alt.trim().match(/^(\d{1,4})(?:\s*(px|%))?/i);
    if (!token) return null;

    const value = Number(token[1]);
    if (!Number.isFinite(value) || value <= 0) return null;

    const unit = (token[2] || '%').toLowerCase();
    if (unit === 'px') {
        return `${value}px`;
    }
    return `${Math.min(value, 100)}%`;
}

function resolveLayoutMode(alt) {
    const text = (alt || '').trim();
    if (text.includes('Lf') || text.includes('Rf')) {
        return 'float';
    }
    if (text.includes('L')) {
        return 'left';
    }
    if (text.includes('R')) {
        return 'right';
    }
    if (text.endsWith('r')) {
        return 'inline';
    }
    return 'center';
}

function mergeStyle(existingStyle, widthValue, alt) {
    const styleMap = new Map();
    const styleText = existingStyle || '';

    styleText
        .split(';')
        .map((s) => s.trim())
        .filter(Boolean)
        .forEach((entry) => {
            const idx = entry.indexOf(':');
            if (idx <= 0) return;
            const key = entry.slice(0, idx).trim().toLowerCase();
            const value = entry.slice(idx + 1).trim();
            if (!key || !value) return;
            styleMap.set(key, value);
        });

    styleMap.set('width', `${widthValue} !important`);
    styleMap.set('height', 'auto !important');

    const layoutMode = resolveLayoutMode(alt);

    // Clear conflicting keys before applying our layout intent.
    styleMap.delete('margin');
    styleMap.delete('margin-left');
    styleMap.delete('margin-right');
    styleMap.delete('vertical-align');

    if (layoutMode === 'inline') {
        styleMap.set('display', 'inline-block !important');
        styleMap.set('margin', '0 !important');
        styleMap.set('vertical-align', 'middle !important');
    } else if (layoutMode === 'left') {
        styleMap.set('display', 'block !important');
        styleMap.set('margin-left', '0 !important');
        styleMap.set('margin-right', 'auto !important');
    } else if (layoutMode === 'right') {
        styleMap.set('display', 'block !important');
        styleMap.set('margin-left', 'auto !important');
        styleMap.set('margin-right', '0 !important');
    } else if (layoutMode === 'center') {
        styleMap.set('display', 'block !important');
        styleMap.set('margin', '0 auto !important');
    } else {
        // float mode: keep width/height only; let CSS alt rules control float/layout.
        styleMap.delete('display');
    }

    return Array.from(styleMap.entries())
        .map(([k, v]) => `${k}: ${v}`)
        .join('; ');
}

html = html.replace(/<img\b[^>]*>/gi, (imgTag) => {
    const altMatch = imgTag.match(/\balt=(['"])(.*?)\1/i);
    const alt = altMatch ? altMatch[2] : '';
    const widthValue = extractWidthFromAlt(alt);
    if (!widthValue) return imgTag;

    const styleMatch = imgTag.match(/\bstyle=(['"])(.*?)\1/i);
    const mergedStyle = mergeStyle(styleMatch ? styleMatch[2] : '', widthValue, alt);

    if (styleMatch) {
        return imgTag.replace(styleMatch[0], `style="${mergedStyle}"`);
    }
    return imgTag.replace(/\/>$/, ` style="${mergedStyle}"/>`).replace(/>$/, ` style="${mergedStyle}">`);
});