<template>
  <div :class="['button-list-control', { 'menu-open': openMenu }]">
    <div class="button-list-container theme-light" @click="onFocusOut">
      <slot name="buttonList"></slot>
    </div>
    <button class="open-list-button" @click="onFocusIn">
      <slot name="button"></slot>
    </button>
  </div>
</template>

<script lang="ts">
// Dependencies
import { RawFocusBox } from "@/assets/scripts/Utilities";
import { defineComponent, markRaw } from "vue";

export default defineComponent({
  name: "ButtonList",
  data: () => ({
    openMenu: false,
    focusBox: markRaw(new RawFocusBox("click"))
  }),
  emits: ["menu-open", "menu-close"],
  methods: {

    /**
     * List focus in behavior.
     */
    onFocusIn() {
      this.openMenu = true;
      this.$emit("menu-open");
    },

    /**
     * List focus out behavior.
     */
    onFocusOut() {
      this.openMenu = false;
      this.$emit("menu-close");
    }

  },
  mounted() {
    this.focusBox.mount(
      this.$el,
      this.onFocusIn,
      this.onFocusOut
    );
  },
  unmounted() {
    this.focusBox.destroy()
  }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

/** === Main Control === */

.button-list-container {
  display: flex;
}

/** === Button List (Desktop) === */

@include scale.above-mobile-width() {

  .open-list-button {
    display: none;
  }

  .button-list-container :deep(button) {
    margin-right: scale.size("m");
  }

  .button-list-container :deep(button):last-child {
    margin-right: 0em;
  }

}

/** === Button List (Mobile) === */

@include scale.at-and-below-mobile-width() {

  .button-list-control {
    position: relative;
  }

  .open-list-button {
    position: relative;
  }

  .open-list-button::after {
    content: "";
    display: block;
    position: absolute;
    top: calc(100% - 1px);
    left: 0px;
    width: 100%;
    border-top: solid 2px #f0f1f2;
    border-bottom: solid 2px #ffffff;
    opacity: 0;
    z-index: 1;
    transition: opacity 0.1s ease-in-out;
  }

  .button-list-container {
    @include color.shadow;
    flex-direction: column;
    position: absolute;
    top: calc(100% - 1px);
    right: 0em;
    width: max-content;
    max-height: 300px;
    border-style: solid;
    border-width: 1px;
    padding: scale.size("m") scale.size("m");
    overflow-x: hidden;
    overflow-y: auto;
    opacity: 0;
    visibility: hidden;
    z-index: 1;
    transition:
      opacity 0.1s ease-in-out,
      visibility 0.1s ease-in-out;
  }

  .button-list-container :deep(button) {
    width: 100%;
    margin-bottom: scale.size("s");
  }

  .button-list-container :deep(button):last-child {
    margin-bottom: 0em;
  }

  .menu-open {

    .button-list-container {
      opacity: 1;
      visibility: visible;
    }

    .open-list-button {
      background: #f0f1f2;
      z-index: 1;
    }

    .open-list-button::after {
      opacity: 1;
    }

  }

}
</style>
