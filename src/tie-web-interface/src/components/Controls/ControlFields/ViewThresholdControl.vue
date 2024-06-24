<template>
  <div class="view-threshold-control">
    <div class="min-threshold">
      <h6>Min {{ control.name }}</h6>
      <input type="number" v-model="minThreshold" @change="updateMinThreshold" />
    </div>
    <div class="max-threshold">
      <h6>Max {{ control.name }}</h6>
      <input type="number" v-model="maxThreshold" @change="updateMaxThreshold" />
    </div>
  </div>
</template>

<script lang="ts">
import * as Command from "@/assets/scripts/PredictionsView/Commands";
import { defineComponent, type PropType } from "vue";
import type { ViewThreshold } from "@/assets/scripts/PredictionsView";

export default defineComponent({
  name: "ViewThresholdControl",
  props: {
    control: {
      type: Object as PropType<ViewThreshold>,
      required: true
    }
  },
  data: () => ({
    minThreshold: 0 as number | "",
    maxThreshold: 0 as number | "",
  }),
  emits: ["execute"],
  methods: {

    /**
     * Update min threshold behavior.
     */
    updateMinThreshold() {
      if (this.minThreshold !== "") {
        this.$emit("execute", Command.setMinThreshold(this.control, this.minThreshold));
      }
      this.updateProperties();
    },

    /**
     * Update max threshold behavior.
     */
    updateMaxThreshold() {
      if (this.maxThreshold !== "") {
        this.$emit("execute", Command.setMinThreshold(this.control, this.maxThreshold));
      }
      this.updateProperties();
    },

    /**
     * Updates the control's value.
     */
    updateProperties() {
      this.minThreshold = this.control.minThreshold;
      this.maxThreshold = this.control.maxThreshold;
    }

  },
  watch: {
    "control"() {
      this.updateProperties();
    },
    "control.minThreshold"() {
      this.updateProperties();
    },
    "control.maxThreshold"() {
      this.updateProperties();
    }
  },
  created() {
    this.updateProperties();
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

input {
  width: 100%;
  box-sizing: border-box;
}

.min-threshold {
  margin-bottom: scale.size("l");
}
</style>
