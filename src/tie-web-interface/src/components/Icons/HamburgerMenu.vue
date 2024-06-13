<template>
  <div :class="['hamburger-menu-icon', { close }]">
    <span></span>
    <span></span>
    <span></span>
  </div>
</template>

<script lang="ts">
import { defineComponent } from "vue";

export default defineComponent({
  name: "HamburgerMenu",
  props: {
    close: {
      type: Boolean,
      default: false
    }
  }
});
</script>

<style lang="scss" scoped>
@use 'sass:math';
@use "@/assets/styles/engenuity_scaling_system" as scale;

$bar-height: calc(2em / scale.$mobile-em-size);
$bar-margin: calc(4em / scale.$mobile-em-size);
$box-height: calc((3 * $bar-height) + (2 * $bar-margin));
$box-width: calc($box-height + (math.sqrt(2) * $bar-height));

.hamburger-menu-icon {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: $box-width;
  height: $box-height;
}

.hamburger-menu-icon span {
  width: 100%;
  height: $bar-height;
  background: currentColor;
  transform-origin: 0% 50%;
  transition: 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.close {
  span:nth-child(1) {
    transform: rotate(45deg) translate3d(0, 0, 0);
  }

  span:nth-child(2) {
    opacity: 0;
    width: 0px;
  }

  span:nth-child(3) {
    transform: rotate(-45deg) translate3d(0, 0, 0);
  }
}
</style>
