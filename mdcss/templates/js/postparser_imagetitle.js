html = html.replace(
    /<img[^\>]*>/g,
    (imgTag) => {
        let match = imgTag.match(/alt=(['"])(.*?)\1/i);
        const alt = match ? match[2] : '';
        match = alt.match(/\((.+)\)/i);
        let caption = match ? match[1] : '';
        let format = alt.replace(`(${caption})`, '').trim();
        if (!caption) return imgTag;
        const isFloat = format.includes('Lf') || format.includes('Rf');
        const isSideAligned = !isFloat && (format.includes('L') || format.includes('R'));
        if (!format.includes("r")) {
            const finalCaption = caption.startsWith('.') ? `图@COUNT_PLACEHOLDER@:\t` + caption.slice(1) : caption;
            if (isFloat) {
                match = imgTag.match(/style=(['"])(.*?)\1/i);
                let style = match ? match[2] : '';
                style = style.replace(/float:\s*(left|right)\s*!?important?/gi, '');
                style = style.replace(/display:\s*inline-block/g, 'display: block');
                match = style.match(/width:\s*(\d{1,4}(?:px|%))/i);
                const width = match ? match[1] : '100%';
                style = style.replace(/width:\s*\d{1,4}(?:px|%)/g, `width: 100%`);
                if (!/display\s*:/i.test(style)) {
                    style = `${style}; display: block`;
                }
                style = style
                    .split(';')
                    .map((s) => s.trim())
                    .filter(Boolean)
                    .join('; ');
                if (imgTag.match(/style=(['"])(.*?)\1/i)) {
                    imgTag = imgTag.replace(/style=(['"])(.*?)\1/i, `style="${style}"`);
                } else {
                    imgTag = imgTag.replace(/\/>$/, ` style="${style}"/>`).replace(/>$/, ` style="${style}">`);
                }
                const floatDir = format.includes('Rf') ? 'right' : 'left';
                const margin = floatDir === 'left' ? '0 1em 1em 0' : '0 0 1em 1em';
                return `<figure style="float: ${floatDir}; width: ${width}; margin: ${margin};" alt="${format}">
${imgTag}
<figcaption style="text-align: center;">${finalCaption}</figcaption>
</figure>`;
            }

            if (isSideAligned) {
                match = imgTag.match(/style=(['"])(.*?)\1/i);
                let style = match ? match[2] : '';
                style = style.replace(/display:\s*inline-block/g, 'display: block');
                match = style.match(/width:\s*(\d{1,4}(?:px|%))/i);
                const width = match ? match[1] : '100%';
                style = style.replace(/width:\s*\d{1,4}(?:px|%)/g, `width: 100%`);
                style = style
                    .split(';')
                    .map((s) => s.trim())
                    .filter(Boolean)
                    .join('; ');
                if (imgTag.match(/style=(['"])(.*?)\1/i)) {
                    imgTag = imgTag.replace(/style=(['"])(.*?)\1/i, `style="${style}"`);
                } else {
                    imgTag = imgTag.replace(/\/>$/, ` style="${style}"/>`).replace(/>$/, ` style="${style}">`);
                }

                const margin = format.includes('R') ? '0 0 1em auto' : '0 auto 1em 0';
                return `<figure style="width: ${width}; margin: ${margin};" alt="${format}">
${imgTag}
<figcaption style="text-align: center;">${finalCaption}</figcaption>
</figure>`;
            }

            return `<figure>
${imgTag}
<figcaption style="text-align: center;">${finalCaption}</figcaption>
</figure>`;
        }
        match = imgTag.match(/style=(['"])(.*?)\1/i);
        let style = match ? match[2] : '';
        style = style.replace(/display:\s*inline-block/g, 'display: block');
        match = style.match(/width:\s*(\d{1,4}(?:px|%))/i);
        const width = match ? match[1] : '100%';
        style = style.replace(/width:\s*\d{1,4}(?:px|%)/g, `width: 100%`);
        imgTag = imgTag.replace(/style=(['"])(.*?)\1/i, `style="${style}"`);
        const finalCaption = caption.startsWith('.') ? `图@COUNT_PLACEHOLDER@:\t` + caption.slice(1) : caption;
        return `<figure style="width: ${width}; margin: 0 auto; display: inline-block;" alt="${format}">
${imgTag}
<figcaption style="text-align: center;">${finalCaption}</figcaption>
</figure>`;
    }
)

html = html.replace(
    /((<figure.*?alt=["'].*?r.*?["'].*?>.*?<\/figure>\s*)+)/gs,
    (match) => {
        let firstFigure = match.split('</figure>')[0];
        let captionMatch = firstFigure.match(/<figcaption.*?>(.*?)<\/figcaption>/i);
        let caption = captionMatch ? captionMatch[1] : '';
        let generalCaptionMatch = caption.match(/\((.+)\)/i);
        let generalCaption = generalCaptionMatch ? generalCaptionMatch[1] : '';
        if (generalCaption) {
            let modifiedCaption = caption.replace( /\((.+)\)/i, "");
            let modifiedCaptionTag = captionMatch[0].replace(caption, modifiedCaption);
            let modifiedFirstFigure = firstFigure.replace(captionMatch[0], modifiedCaptionTag);
            match = match.replace(firstFigure, modifiedFirstFigure);
            generalCaption = generalCaption.startsWith('.') ? `图@COUNT_PLACEHOLDER@:\t` + generalCaption.slice(1) : generalCaption;
            generalCaption = `<figcaption style="text-align: center;">${generalCaption}</figcaption>`;
        }
        return `<figure style="text-align: center;">
${match}
${generalCaption || ''}
</figure>`;
    }
)

let cnt = 0;
html = html.replace(/@COUNT_PLACEHOLDER@/g, (match) => {
    cnt += 1;
    return cnt;
});