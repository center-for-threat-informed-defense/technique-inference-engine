<template>
  <div class="markdown-text-control" v-html="compiledSource"></div>
</template>

<script lang="ts">
import { defineComponent, markRaw } from "vue";
import MarkdownIt from "markdown-it";
import MarkdownItSup from "@/assets/scripts/Utilities/MarkdownItSup";
import type { RenderRule } from "markdown-it/lib/renderer.mjs";

// Configure markdown renderer
const markdown = markRaw(new MarkdownIt({

  /**
   * Warning:
   * Do NOT enable HTML tags in source without an external sanitizer package. Enabling
   * tags without a sanitizer can lead to XSS attacks. Consult all security guidelines
   * (https://github.com/markdown-it/markdown-it/blob/master/docs/security.md) before
   * altering this configuration.
   */
  html: false

})).use(MarkdownItSup);

// Remember old renderer if overridden, or proxy to the default renderer.
let defaultRender: RenderRule | undefined;
defaultRender ??= markdown.renderer.rules.link_open;
defaultRender ??= function (tokens, idx, options, _, self) {
  return self.renderToken(tokens, idx, options);
};
// Configure renderer to open links in new tab
markdown.renderer.rules.link_open = function (tokens, idx, options, env, self) {
  // Add a new `target` attribute, or replace the value of the existing one.
  tokens[idx].attrSet('target', '_blank');
  // Pass the token to the default renderer.
  return defaultRender(tokens, idx, options, env, self);
};

export default defineComponent({
  name: "MarkdownText",
  props: {
    source: {
      type: String,
      default: ""
    }
  },
  computed: {

    /**
     * Returns the compiled markdown.
     * @returns
     *  The compiled markdown.
     */
    compiledSource() {
      return markdown.render(this.source);
    }

  }
});
</script>
