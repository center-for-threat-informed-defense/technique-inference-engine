<template>
  <div :class="['button-menu-control', { 'menu-open': openMenu }]">
    <div class="button-menu-container" @click="onFocusOut">
      <div class="button-menu theme-light" ref="menu" @click.stop>
        <div class="menu-header">
          <div class="menu-header-text">
            <slot name="menuHeader"></slot>
          </div>
          <DeleteIcon @click="onFocusOut" />
        </div>
        <div class="menu-body">
          <slot name="menuBody"></slot>
        </div>
      </div>
    </div>
    <button @click="onFocusIn">
      <slot name="button"></slot>
    </button>
  </div>
</template>

<script lang="ts">
// Dependencies
import { RawFocusBox } from "@/assets/scripts/Utilities";
import { defineComponent, inject, markRaw } from "vue";
// Components
import DeleteIcon from "../Icons/DeleteIcon.vue";

export default defineComponent({
  name: "ButtonMenu",
  setup() {
    const lockPageScroll = inject<(l: boolean) => void>("lockPageScroll");
    return {
      lockPageScroll: lockPageScroll ?? (() => { })
    }
  },
  data: () => ({
    openMenu: false,
    focusBox: markRaw(new RawFocusBox("click"))
  }),
  emits: ["menu-open", "menu-close"],
  methods: {

    /**
     * Menu focus in behavior.
     */
    onFocusIn() {
      this.openMenu = true;
      this.$emit("menu-open");
    },

    /**
     * Menu focus out behavior.
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
  },
  components: { DeleteIcon }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

$_fs : scale.font-size("h6");
$_lh : scale.line-height("h6");

/**
 * The header's padding.
 */
$header-padding: scale.size("h");

/*
 * The header's calculated height.
 */
$header-height: calc(($header-padding * 2) + ($_fs * $_lh / scale.$units));

/** === Main Control === */

.button-menu-control {
  position: relative;
}

.button-menu-container {
  opacity: 0;
  visibility: hidden;
}

.menu-header-text {
  display: flex;
  align-items: center;
}

.menu-open {

  .button-menu-container {
    opacity: 1;
    visibility: visible;
  }

}

/** === Button Menu (Desktop) === */

@include scale.above-mobile-width() {

  .button-menu-container {
    transition:
      opacity 0.1s ease-in-out,
      visibility 0.1s ease-in-out;
  }

  button {
    position: relative;
    width: 100%;
    height: 100%;
  }

  button::after {
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

  .button-menu {
    @include color.shadow;
    position: absolute;
    top: calc(100% - 1px);
    width: max-content;
    max-height: 300px;
    border-style: solid;
    border-width: 1px;
    padding: scale.size("xl") scale.size("xxl");
    overflow-x: hidden;
    overflow-y: auto;
    z-index: 1;
  }

  .menu-header {
    display: none;
  }

  .menu-open {

    button {
      background: #f0f1f2;
      z-index: 1;
    }

    button::after {
      opacity: 1;
    }

  }

}

/** === Button Menu (Mobile) === */

@include scale.at-and-below-mobile-width() {

  .button-menu-container {
    display: flex;
    flex-direction: column;
    justify-content: end;
    position: fixed;
    top: 0em;
    left: 0em;
    right: 0em;
    bottom: 0em;
    background: rgb(0 0 0 / 50%);
    transition:
      opacity 0.25s ease-in-out 0s,
      visibility 0.25s ease-in-out 0s;
    z-index: 2;
  }

  .button-menu {
    display: flex;
    flex-direction: column;
    max-height: calc(100vh - (2 * $header-height));
    box-sizing: border-box;
  }

  .menu-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom-style: solid;
    border-bottom-width: 2px;
    padding: scale.size("l") scale.size("h");
    @include color.accent-border;
  }

  .menu-body {
    flex: 1;
    font-size: 16px;
    overflow-y: scroll;
    padding: scale.size("l") scale.size("h");
  }

  .button-menu :slotted(div) {
    transform: translateX(- scale.size("h"));
    transition:
      transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  @for $index from 1 through 9 {
    .button-menu :slotted(div):nth-child(#{ $index }) {
      transition-delay: $index * 0.025s;
    }
  }

  .menu-open {

    .button-menu :slotted(div) {
      transform: translateX(0em);
    }

  }

}
</style>
