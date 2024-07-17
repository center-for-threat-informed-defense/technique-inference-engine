<template>
  <div class="view-option-control">
    <h6>{{ control.name }}</h6>
    <ul>
      <template v-for="option of control.options" :key="option">
        <li @click="setOption(option)" :class="{ active: control.value === option }">
          <span></span>
          <p>{{ option }}</p>
        </li>
      </template>
    </ul>
  </div>
</template>

<script lang="ts">
import * as Command from "@/assets/scripts/PredictionsView/Commands";
import { defineComponent, type PropType } from "vue";
import type { ViewOption } from "@/assets/scripts/PredictionsView";

export default defineComponent({
  name: "ViewOptionControl",
  props: {
    control: {
      type: Object as PropType<ViewOption>,
      required: true
    }
  },
  emits: ["execute"],
  methods: {

    /**
     * Set's the control's option
     * @param option
     *  The option to set.
     */
    setOption(option: string) {
      this.$emit("execute", Command.setViewOption(this.control, option));
    }

  }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_scaling_system" as scale;

/** === Main Control === */

h6 {
  @include scale.h7;
  margin-bottom: scale.size("t");
}

ul {
  list-style: none;
  padding: 0em;
}

li {
  display: flex;
  align-items: center;
  user-select: none;
  cursor: pointer;
}

li:not(.active):hover span {
  opacity: 0.6;
}

span {
  display: inline-block;
  /**
   * PX must be used here. Depending on the screen, rounding
   * differences in EM can result in a box that isn't square.
   */
  width: 6px;
  height: 6px;
  padding: 2px;
  border: solid 1.5px;
  border-radius: 6px;
  margin-right: scale.size("s");
}

span::after {
  content: "";
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 6px;
  background: currentColor;
  opacity: 0;
  transition: .15s opacity;
}

.active span::after {
  opacity: 1;
}

p {
  display: inline;
}
</style>
