
const columnRegex = /(^-?\|\|\|-?:?\d*(?:%|px)?:?$)/m;
function parseCulumnSpec(spec) {
    let type = "separator";
    let width = "";
    let align = "";
    if (spec.startsWith("|||-")) {
        type = "start";
        spec = spec.slice(4);
    } else if (spec.startsWith("-|||")) {
        if (spec.length != 4) {
            return null;
        }
        type = "end";
        return { type, align, width };
    } else {
        spec = spec.slice(3);
    }
    // Standalone ":" should be treated as flex-end
    align = "flex-start";
    if (spec.endsWith(":")) {
        align = "flex-end";
        spec = spec.slice(0, -1);
        if (spec.startsWith(":")) {
            align = "center";
            spec = spec.slice(1);
        }
    } else if (spec.startsWith(":")) {
        spec = spec.slice(1);
    }
    width = "%";
    if (spec.endsWith("px")) {
        width = "px";
        spec = spec.slice(0, -2);
    } else if (spec.endsWith("%")) {
        spec = spec.slice(0, -1);
    }
    if (!/^-?\d+$/.test(spec)) {
        width = "1fr";
    } else {
        const num = parseInt(spec, 10);
        width = isNaN(num) ? width : `${num}${width}`;
    }
    return { type, align, width };
}
function mergeColumnSpec(markdown) {
    let parts = markdown.split(columnRegex);
    let specIndex = {};
    for (let i = 0; i < parts.length; i++) {
    if (!columnRegex.test(parts[i])) {
        continue;
    }
    const spec = parseCulumnSpec(parts[i]);
    if (!spec) {
        continue;
    }
    switch (spec.type) {
        case "start":
            if (Object.keys(specIndex).length > 0) {
                specIndex = {};
            }
            specIndex[i] = spec;
            break;
        case "separator":
            if (Object.keys(specIndex).length === 0) {
                break;
            }
            specIndex[i] = spec;
            break;
        case "end":
            if (Object.keys(specIndex).length === 0) {
                break;
            }
            {
                const cols = Object.values(specIndex).map((s) => s.width).join(' ');
                let outerDiv = `

<div style="display: grid; grid-template-columns: ${cols}; gap: 20px;">

`;
                for (const index in specIndex) {
                const s = specIndex[index];
                const innerDiv = `

<div style="display: flex; flex-direction: column; justify-content: ${s.align}; min-width: 0;">

`;
                parts[index] = outerDiv + innerDiv;
                outerDiv = `</div>`;
                }
                parts[i] = `</div></div>`;
                specIndex = {};
            }
            break;
        }
    }
    return parts.join("\n");
}
markdown = mergeColumnSpec(markdown);