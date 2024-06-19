<template>
  <div class="technique-summary-control">
    <div class="technique-header">
      <div class="collapse-region" @click="collapsed = !collapsed">
        <div class="collapse-button">
          <CollapseArrow :class="{ collapsed }" />
        </div>
        <div class="technique-name">
          <mark>{{ technique.id }}:</mark>
          <h4>{{ technique.name }}</h4>
        </div>
      </div>
      <slot></slot>
    </div>
    <div class="technique-body" v-if="!collapsed">
      <MarkdownText class="technique-description" :source="technique.description" />
      <div class="technique-footer">
        <a class="learn-more" :href="learnMoreLink" target="_blank">Learn More</a>
        <var class="score" v-if="'score' in technique">
          Score: {{ Math.round(technique.score * 10000) / 100 }}
        </var>
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
  name: "TechniqueSummary",
  props: {
    technique: {
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
      const id = this.technique.id.replace(/\./g, "/");
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

.technique-summary-control {
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
}

.technique-name {
  flex: 1;
  padding: scale.size("l") 0em;
}

mark {
  @include scale.h6;
  font-weight: 400;
}

/** === Technique Body === */

.technique-body {
  padding: 0em scale.size("xl") scale.size("h") scale.size("xh");
}

.technique-description {
  @include color.field-border;
  white-space: pre-wrap;
  padding: scale.size("l") 0em scale.size("xl");
  border-top-style: solid;
  border-top-width: 1px;
}

.technique-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.score {
  margin-right: scale.size("xl")
}

@include scale.at-and-below-mobile-width {
  .score {
    display: none;
  }
}
</style>
