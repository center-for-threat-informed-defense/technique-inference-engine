<template>
  <div class="view-filter-control">
    <h6>{{ control.name }}</h6>
    <ul>
      <li :class="['show-all', { active: control.allShown() }]" @click="showAll()">
        <span></span>
        <p>Show All</p>
      </li>
      <template v-for="filter of control.filters" :key="filter">
        <li :class="{ active: isFilterChecked(filter) }" @click="toggleFilter(filter)">
          <span></span>
          <p>{{ filter }}</p>
        </li>
      </template>
    </ul>
  </div>
</template>

<script lang="ts">
import * as Command from "@/assets/scripts/PredictionsView/Commands";
import { defineComponent, type PropType } from "vue";
import type { ViewFilter } from "@/assets/scripts/PredictionsView";

export default defineComponent({
  name: "ViewFilterControl",
  props: {
    control: {
      type: Object as PropType<ViewFilter>,
      required: true
    }
  },
  emits: ["execute"],
  methods: {

    /**
     * Test if a filter is checked.
     * @param filter
     *  The filter to test.
     * @returns
     *  True if the filter is checked, false otherwise.
     */
    isFilterChecked(filter: string) {
      return !this.control.allShown() && this.control.isShown(filter);
    },

    /**
     * Toggle filter.
     * @param filter
     *  The name of the filter to toggle.
     */
    toggleFilter(filter: string) {
      const value = !this.control.appliedFilters.has(filter);
      this.$emit("execute", Command.setViewFilter(this.control, filter, value));
    },

    /**
     * Show all filters.
     */
    showAll() {
      this.$emit("execute", Command.showAllOfFilter(this.control));
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
  margin-right: scale.size("s");
}

span::after {
  content: "";
  display: block;
  width: 100%;
  height: 100%;
  background: currentColor;
  opacity: 0;
  transition: .15s opacity;
}

.active span::after {
  opacity: 1;
}

p {
  display: inline-block;
}

.show-all.active {
  opacity: 0.6;
  cursor: default;
}
</style>
