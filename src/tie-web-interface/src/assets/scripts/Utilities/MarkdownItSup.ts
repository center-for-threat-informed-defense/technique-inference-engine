/**
 * Developer Note:
 * This is a modified version of the official superscript plugin for markdown-it
 * (https://github.com/markdown-it/markdown-it-sup). This version of the plugin allows
 * formatting to take place within superscripts (links, emphasis, strikethrough, etc.)
 */

import type MarkdownIt from "markdown-it/index.js";
import type { StateInline } from "markdown-it/index.js"

function superscript(state: StateInline, silent: boolean) {
    const max = state.posMax
    const start = state.pos

    // Don't run any pairs in validation mode
    if (silent) {
        return false
    }

    // Validate beginning and end markers
    if (state.src.charCodeAt(start) !== 0x5E/* ^ */) {
        return false;
    }
    if (start + 2 >= max) {
        return false
    }

    // Attempt to resolve content
    state.pos = start + 1
    let found = false

    while (state.pos < max) {
        if (state.src.charCodeAt(state.pos) === 0x5E/* ^ */) {
            found = true
            break
        }

        state.md.inline.skipToken(state)
    }

    if (!found || start + 1 === state.pos) {
        state.pos = start
        return false
    }

    const content = state.src.slice(start + 1, state.pos)

    // Don't allow unescaped spaces/newlines inside
    if (content.match(/(^|[^\\])(\\\\)*\s/)) {
        state.pos = start
        return false
    }

    // Push tokens
    state.posMax = state.pos
    state.pos = start + 1

    const token_so = state.push('sup_open', 'sup', 1)
    token_so.markup = '^'

    state.md.inline.tokenize(state);

    const token_sc = state.push('sup_close', 'sup', -1)
    token_sc.markup = '^'

    state.pos = state.posMax + 1
    state.posMax = max
    return true
}

export default function sup_plugin(md: MarkdownIt) {
    md.inline.ruler.after('emphasis', 'sup', superscript)
}
