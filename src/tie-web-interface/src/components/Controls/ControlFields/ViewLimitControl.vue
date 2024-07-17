<template>
  <div class="view-limit-control">
    <h6>{{ control.name }}</h6>
    <input type="number" v-model="value" @change="updateValue" />
  </div>
</template>

<script lang="ts">
import * as Command from "@/assets/scripts/PredictionsView/Commands";
import { defineComponent, type PropType } from "vue";
import type { ViewLimit } from "@/assets/scripts/PredictionsView";

export default defineComponent({
  name: "ViewLimitControl",
  props: {
    control: {
      type: Object as PropType<ViewLimit>,
      required: true
    }
  },
  data: () => ({
    value: 0 as number | "",
  }),
  emits: ["execute"],
  methods: {


    /**
     * Update value behavior.
     */
    updateValue() {
      if (this.value !== "") {
        this.$emit("execute", Command.setViewLimit(this.control, this.value));
      }
      this.updateProperty();
    },

    /**
     * Updates the control's value.
     */
    updateProperty() {
      this.value = this.control.value;
    }

  },
  watch: {
    "control"() {
      this.updateProperty();
    },
    "control.value"() {
      this.updateProperty();
    }
  },
  created() {
    this.updateProperty();
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
</style>
