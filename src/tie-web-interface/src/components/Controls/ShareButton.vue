<template>
  <button :class="['share-button-control', { copied }]" @click="copyLinkToClipboard">
    <div class="copy">
      <CopyIcon /><span>Copied</span>
    </div>
    <div class="share">
      <ShareIcon /><span>Share</span>
    </div>
  </button>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
// Components
import CopyIcon from "../Icons/CopyIcon.vue";
import ShareIcon from "../Icons/ShareIcon.vue";

export default defineComponent({
  name: "ShareButton",
  data: () => ({
    copied: false,
    timeoutId: 0,
  }),
  emits: ["share"],
  methods: {

    /**
     * Copies the configured link to the device's clipboard.
     */
    copyLinkToClipboard() {
      // Emit share event
      this.$emit("share");
      // Flash message
      this.copied = true;
      clearTimeout(this.timeoutId);
      this.timeoutId = window.setTimeout(
        () => this.copied = false, 2000
      );
    }

  },
  components: { CopyIcon, ShareIcon }
});
</script>

<style lang="scss" scoped>
.share-button-control {
  display: grid;
  grid-template-rows: 1fr;
  grid-template-columns: 1fr;
}

.share-button-control {
  .copy {
    opacity: 0;
    visibility: hidden;
    transition:
      opacity 0.1s cubic-bezier(0.33, 1, 0.68, 1),
      visibility 0.1s cubic-bezier(0.33, 1, 0.68, 1);
  }

  .share {
    opacity: 1;
    visibility: visible;
    transition:
      opacity 0.1s cubic-bezier(0.32, 0, 0.67, 0) 0.1s,
      visibility 0.1s cubic-bezier(0.32, 0, 0.67, 0) 0.1s;
  }
}

.share-button-control.copied {
  .copy {
    opacity: 1;
    visibility: visible;
    transition:
      opacity 0.1s cubic-bezier(0.32, 0, 0.67, 0) 0.1s,
      visibility 0.1s cubic-bezier(0.32, 0, 0.67, 0) 0.1s;
  }

  .share {
    opacity: 0;
    visibility: hidden;
    transition:
      opacity 0.1s cubic-bezier(0.33, 1, 0.68, 1),
      visibility 0.1s cubic-bezier(0.33, 1, 0.68, 1);
  }
}

.copy,
.share {
  grid-row: 1;
  grid-column: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy svg {
  height: 13px;
}

.share svg {
  height: 16px;
}
</style>
