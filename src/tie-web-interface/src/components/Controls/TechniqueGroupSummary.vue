<template>
  <div class="technique-group-summary-control">
    <div class="technique-header">
      <div class="collapse-region" @click="collapsed = !collapsed">
        <div class="collapse-button">
          <CollapseArrow :class="{ collapsed }" />
        </div>
        <div class="technique-name">
          <h4>{{ item.name }}</h4>
        </div>
      </div>
    </div>
    <div class="technique-list" v-if="!collapsed">
      <template v-for="technique of item" :key="technique.id">
        <TechniqueItemSummary class="technique-summary" :item="technique">
          <slot :technique="technique"></slot>
        </TechniqueItemSummary>
      </template>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent, type PropType } from "vue";
import type { PredictionGroup } from "@/assets/scripts/PredictionsView";
// Components
import CollapseArrow from "@/components/Icons/CollapseArrow.vue";
import TechniqueItemSummary from "./TechniqueItemSummary.vue";

export default defineComponent({
  name: "TechniqueGroupSummary",
  props: {
    item: {
      type: Object as PropType<PredictionGroup>,
      required: true
    }
  },
  data: () => ({
    collapsed: false,
  }),
  components: { CollapseArrow, TechniqueItemSummary }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

/** === Main Control === */

.technique-group-summary-control {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/** === Technique Header === */

.collapse-region {
  flex: 1;
  display: flex;
  align-items: stretch;
  user-select: none;
  cursor: pointer;
}

.collapse-button {
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  width: scale.size("xh");
}

svg:not(.collapsed) {
  transform: rotate(90deg);
}

.technique-header {
  display: flex;
  align-items: stretch;
  color: #fff;
  background: var(--engenuity-navy);
}

.technique-name {
  flex: 1;
  padding: scale.size("l") 0em;
}

h4 {
  font-weight: 400;
  text-transform: none;
}

/** === Technique List === */

.technique-list {
  padding-top: scale.size("s");
}

.technique-summary {
  margin-bottom: scale.size("s");
}

.technique-summary:first-child {
  margin-top: scale.size("l");
}

.technique-summary:last-child {
  margin-bottom: scale.size("l");
}
</style>
