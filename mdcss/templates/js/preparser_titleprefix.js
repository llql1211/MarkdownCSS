function roman(num, prefix) {
    if (typeof num !== 'number' || num < 1 || num > 3999) {
        return '';
    }
    const values = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1];
    const symbols = ['m', 'cm', 'd', 'cd', 'c', 'xc', 'l', 'xl', 'x', 'ix', 'v', 'iv', 'i'];
    let result = '';
    for (let i = 0; i < values.length; i++) {
        while (num >= values[i]) {
            result += symbols[i];
            num -= values[i];
        }
    }
    return result + ") ";
}
function romanUpper(num, prefix) {
    return roman(num, prefix).toUpperCase();
}
function latin(num, prefix) {
    if (typeof num !== 'number' || num <= 0 || !Number.isInteger(num)) {
        return '';
    }
    let result = '';
    let n = num;
    while (n > 0) {
        n--;
        const remainder = n % 26;
        result = String.fromCharCode(97 + remainder) + result;
        n = Math.floor(n / 26);
    }
    return result + ") ";
}
function latinUpper(num, prefix) {
    return latin(num, prefix).toUpperCase();
}
function chinese(num, prefix) {
    if (typeof num !== 'number' || num <= 0 || !Number.isInteger(num)) {
        return '';
    }
    const digits = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九'];
    const units = ['', '十', '百', '千'];
    const sectionUnits = ['', '万', '亿', '兆'];
    let numStr = num.toString();
    const sections = [];
    while (numStr.length > 4) {
        sections.push(numStr.slice(-4));
        numStr = numStr.slice(0, -4);
    }
    if (numStr.length > 0) sections.push(numStr);
    sections.reverse();
    function convertSection(sectionStr) {
        while (sectionStr.length < 4) sectionStr = '0' + sectionStr;
        let result = '';
        let hasOutput = false;
        let needZero = false;
        for (let i = 0; i < 4; i++) {
            const digit = parseInt(sectionStr[i], 10);
            if (digit !== 0) {
                if (needZero) {
                    result += '零';
                    needZero = false;
                }
                result += digits[digit] + units[3 - i];
                hasOutput = true;
            } else {
                if (hasOutput) {
                    needZero = true;
                }
            }
        }
        return result;
    }
    let chinese = '';
    let lastNonZeroExists = false;
    let needZeroFromPrevZero = false;
    for (let i = 0; i < sections.length; i++) {
        const sectionVal = parseInt(sections[i], 10);
        const sectionChinese = sectionVal === 0 ? '' : convertSection(sections[i]);
        const sectionUnit = sectionUnits[sections.length - 1 - i];
        if (sectionVal === 0) {
            needZeroFromPrevZero = true;
        } else {
            let needPrependZero = false;
            if (needZeroFromPrevZero) {
                needPrependZero = true;
                needZeroFromPrevZero = false;
            } else if (lastNonZeroExists && sectionVal < 1000) {
                needPrependZero = true;
            }
            if (needPrependZero) {
                chinese += '零';
            }
            chinese += sectionChinese + sectionUnit;
            lastNonZeroExists = true;
        }
    }
    if (chinese.startsWith('一十')) {
        chinese = chinese.slice(1);
    }
    return (chinese || '零') + "、";
}
function number(num, prefix) {
    if (typeof num !== 'number' || num <= 0 || !Number.isInteger(num)) {
        return '';
    }
    if (/^\d/.test(prefix)) {
        return `${prefix.replace(/\.?\s?$/i, "")}.\u200B${num} `;
    }
    return `${num}\u200B. `;
}
function none(num, prefix) {
    return '';
}
function preprocessMarkdown(markdown, mappers) {
    let prefix = [null, null, null, null, null, null];
    let counters = [0, 0, 0, 0, 0, 0];
    markdown = markdown.replace(
        /^(#{1,6})\s*?\.(.*?)$/gm,
        (match, hashes, title) => {
            const level = hashes.length - 1;
            counters[level]++;
            for (let i = level + 1; i < 6; i++) {
                counters[i] = 0;
                prefix[i] = null;
            }
            let lastPrefix = "";
            let i = level - 1;
            while (i >= 0) {
                if (prefix[i] === null) {
                    i--;
                    continue;
                }
                lastPrefix = prefix[i];
                break;
            }
            const newPrefix = mappers[level](
                counters[level],
                lastPrefix
            )
            prefix[level] = newPrefix;
            return `${hashes} ${newPrefix}${title}`;
        }
    )
    return markdown;
}
mappers = [@MAPPER_PLACEHOLDER@];
markdown = preprocessMarkdown(markdown, mappers);