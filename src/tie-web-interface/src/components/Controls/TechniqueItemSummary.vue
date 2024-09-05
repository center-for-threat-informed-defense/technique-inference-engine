<template>
  <div class="technique-item-summary-control">
    <div class="technique-header">
      <div class="collapse-region" @click="collapsed = !collapsed">
        <div class="collapse-button">
          <CollapseArrow :class="{ collapsed }" />
        </div>
        <div class="technique-name">
          <mark>{{ item.id }}:</mark>
          <h4>{{ item.name }}</h4>
        </div>
        <div class="technique-notice" v-if="$slots.notice !== undefined">
          <div class="notice-icon theme-dark">!</div>
        </div>
        <div class="technique-score" v-if="'rank' in item">
          <var>#{{ item.rank }}</var>
        </div>
      </div>
      <div class="technique-controls">
        <slot :technique="item"></slot>
      </div>
    </div>
    <div class="technique-body" v-if="!collapsed">
      <hr />
      <div v-if="$slots.notice !== undefined" class="notice">
        <h6>Notice:</h6>
        <p>
          <slot :technique="item" name="notice"></slot>
        </p>
      </div>
      <MarkdownText class="technique-description" :source="item.description" />
      <div class="technique-footer">
        <a class="learn-more" :href="learnMoreLink" target="_blank">Learn More</a>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent, type PropType } from "vue";
import type { PredictedTechnique, Technique } from "@/assets/scripts/TechniqueInferenceEngine";
// Components
import MarkdownText from "@/components/Controls/MarkdownText.vue";
import CollapseArrow from "@/components/Icons/CollapseArrow.vue";

export default defineComponent({
  name: "TechniqueItemSummary",
  props: {
    item: {
      type: Object as PropType<Technique | PredictedTechnique>,
      required: true
    }
  },
  data: () => ({
    collapsed: true,
  }),
  computed: {

    /**
     * Returns the technique's "Learn More" link
     * @returns
     *  The technique's "Learn More" link.
     */
    learnMoreLink(): string {
      const id = this.item.id.replace(/\./g, "/");
      return `https://attack.mitre.org/techniques/${id}/`
    }

  },
  components: { MarkdownText, CollapseArrow }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system" as color;
@use "@/assets/styles/engenuity_scaling_system" as scale;

/** === Main Control === */

.technique-item-summary-control {
  @include color.field-border;
  display: flex;
  flex-direction: column;
  border-style: solid;
  border-width: 1px;
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
  @include scale.selection-area;
  display: flex;
  align-items: stretch;
}

.technique-name {
  flex: 1;
  padding: scale.size("l") 0em;
}

mark {
  @include scale.h6;
  font-weight: 400;
}

.technique-score {
  display: flex;
  align-items: center;
  user-select: none;
  margin-left: scale.size("xl");
}

.technique-notice {
  display: flex;
  align-items: center;
}

.notice-icon {
  @include scale.small;
  @include scale.box("xxl");
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  background: var(--engenuity-navy);
}

.technique-controls {
  display: flex;
  align-items: center;
}

/** === Technique Body === */

.technique-body {
  padding: 0em scale.size("xl") scale.size("h") scale.size("xh");
}

hr {
  @include color.field-border;
  border-style: solid none none none;
  border-width: 1px;
}

.notice {
  display: block;
  padding: scale.size("l") scale.size("xl");
  margin-top: scale.size("xl");
  background: #f0f1f2;
}

.notice h6 {
  margin: scale.size("xxt") 0em;
}

.technique-description {
  white-space: pre-wrap;
  padding: scale.size("l") 0em scale.size("xl");
}

.notice~.technique-description {
  padding-top: scale.size("xl");
}

.technique-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
