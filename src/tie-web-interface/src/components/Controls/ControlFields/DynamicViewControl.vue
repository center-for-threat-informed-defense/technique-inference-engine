<template>
  <component :is="controlComponent" :control="control" @execute="execute" />
</template>

<script lang="ts">
// Dependencies
import { defineComponent, type PropType } from "vue";
import {
  ViewLimit,
  ViewFilter,
  ViewOption,
  ViewControl,
  ViewThreshold,
} from "@/assets/scripts/PredictionsView"
import type { ControlCommand } from "@/assets/scripts/PredictionsView/Commands";
// Components
import ViewLimitControl from "./ViewLimitControl.vue";
import ViewFilterControl from "./ViewFilterControl.vue";
import ViewOptionControl from "./ViewOptionControl.vue";
import ViewThresholdControl from "./ViewThresholdControl.vue";

export default defineComponent({
  name: "DynamicViewControl",
  props: {
    control: {
      type: Object as PropType<ViewControl>,
      required: true
    }
  },
  computed: {

    /**
     * Returns the control component to use.
     * @returns
     *  The control component to use.
     */
    controlComponent(): string {
      if (this.control instanceof ViewLimit) {
        return "ViewLimitControl";
      } else if (this.control instanceof ViewFilter) {
        return "ViewFilterControl"
      } else if (this.control instanceof ViewOption) {
        return "ViewOptionControl";
      } else if (this.control instanceof ViewThreshold) {
        return "ViewThresholdControl";
      } else {
        const name = this.control.constructor.name;
        throw new Error(`Unsupported control type: '${name}'`);
      }
    }

  },
  emits: ["execute"],
  methods: {

    /**
     * Execute behavior.
     * @param cmd
     *  The command to execute.
     */
    execute(cmd: ControlCommand) {
      this.$emit("execute", cmd);
    }

  },
  components: {
    ViewLimitControl,
    ViewFilterControl,
    ViewOptionControl,
    ViewThresholdControl
  }
});
</script>
