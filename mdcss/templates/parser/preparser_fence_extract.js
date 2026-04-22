const __MDCSS_FENCE_TOKEN_PREFIX__ = "@@MDCSS_FENCE_BLOCK_";
const __MDCSS_FENCE_TOKEN_SUFFIX__ = "@@";
const __MDCSS_FENCED_BLOCKS__ = [];
const __mdcssFenceBlockPattern = /(^```[^\n]*\n[\s\S]*?\n```[ \t]*$)/gm;
const __mdcssFenceBlockExactPattern = /^```[^\n]*\n[\s\S]*\n```[ \t]*$/;
markdown = markdown
    .split(__mdcssFenceBlockPattern)
    .map((part) => {
        if (!__mdcssFenceBlockExactPattern.test(part)) {
            return part;
        }
        const index = __MDCSS_FENCED_BLOCKS__.push(part) - 1;
        return `${__MDCSS_FENCE_TOKEN_PREFIX__}${index}${__MDCSS_FENCE_TOKEN_SUFFIX__}`;
    })
    .join("");
