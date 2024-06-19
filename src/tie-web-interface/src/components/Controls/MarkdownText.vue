<template>
  <div class="markdown-text-control" v-html="compiledSource"></div>
</template>

<script lang="ts">
import { defineComponent, markRaw } from "vue";
import MarkdownIt from "markdown-it";
import MarkdownItSup from "@/assets/scripts/Utilities/MarkdownItSup";

// Configure base renderer
const markdown = markRaw(new MarkdownIt({

  /**
   * Warning:
   * Do NOT enable HTML tags in source without an external sanitizer package. Enabling
   * tags without a sanitizer can open the door to XSS attacks. Consult all security
   * {@link https://github.com/markdown-it/markdown-it/blob/master/docs/security.md guidelines }
   * before altering this configuration.
   */
  html: false

})).use(MarkdownItSup);

// Remember old renderer if overridden, or proxy to the default renderer.
const defaultRender = markdown.renderer.rules.link_open ?? function (tokens, idx, options, _, self) {
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
