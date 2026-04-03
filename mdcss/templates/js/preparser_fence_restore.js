const __mdcssFenceTokenRestorePattern = /@@MDCSS_FENCE_BLOCK_(\d+)@@/g;

markdown = markdown.replace(__mdcssFenceTokenRestorePattern, (match, indexText) => {
    const index = Number(indexText);
    if (!Number.isInteger(index) || index < 0 || index >= __MDCSS_FENCED_BLOCKS__.length) {
        return match;
    }
    return __MDCSS_FENCED_BLOCKS__[index];
});
