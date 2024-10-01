<template>
  <div :class="['help-tooltip-control', align]">
    <div class="help-icon">
      <QuestionIcon></QuestionIcon>
    </div>
    <div class="help-text theme-light">
      <slot></slot>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent, type PropType } from "vue";
// Components
import QuestionIcon from "../Icons/QuestionIcon.vue";

export default defineComponent({
  name: "HelpTooltip",
  props: {
    align: {
      type: String as PropType<"left" | "right">,
      default: "left"
    }
  },
  components: { QuestionIcon }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

/** === Main Control === */

.help-tooltip-control {
  position: relative;
}

.help-icon {
  @include color.help-icon;
  display: flex;
  align-items: center;
  width: 19px;
  cursor: pointer;
}

.help-text {
  @include color.shadow;
  position: absolute;
  top: 100%;
  width: max-content;
  max-width: 300px;
  padding: scale.size("l");
  border: solid 1px;
  margin-top: scale.size("t");
  z-index: 100;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0.15s ease-in-out,
    visibility 0.15s ease-in-out;
}

.help-tooltip-control:hover .help-text {
  opacity: 1;
  visibility: visible;
  transition:
    opacity 0.15s ease-in-out,
    visibility 0.15s ease-in-out;
}

.help-tooltip-control.left .help-text {
  left: 0px;
}

.help-tooltip-control.right .help-text {
  right: 0px;
}
</style>
