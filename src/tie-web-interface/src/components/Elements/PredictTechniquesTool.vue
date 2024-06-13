<template>
  <div class="predict-techniques-tool-element">
    <div class="observed-section">
      <h3>Observed Techniques</h3>
      <OptionSelector class="options-selector" placeholder="Add Technique" :options="allTechniqueOptions"
        @select="addObservedTechnique" />
      <div class="techniques">
        <template v-for="observed of observedTechniquesList" :key="observed.id">
          <TechniqueSummary class="technique-summary" :technique="observed">
            <div class="unknown" v-if="!trainedTechniques.has(observed.id)">(?)</div>
            <div class="delete-icon" @click="deleteObservedTechnique(observed.id)">
              <DeleteIcon />
            </div>
          </TechniqueSummary>
        </template>
      </div>
    </div>
    <div class="predicted-section">
      <div class="section-header">
        <h3>Predicted Techniques</h3>
        <small v-if="predicted">
          Generated {{ predicted.size }} predictions in {{ predicted.metadata.humanReadableTime }}
          (on {{ predicted.metadata.humanReadableBackend }}).
        </small>
      </div>
      <div v-if="engine.isWarmingUp">Warming Up...</div>
      <div class="instructions" v-if="!predicted">
        No Observed Techniques
      </div>
      <div class="techniques">
        <template v-for="prediction of predictedTechniquesList" :key="prediction.id">
          <TechniqueSummary class="technique-summary" :technique="prediction">
            <div class="unknown" v-if="!trainedTechniques.has(prediction.id)">(?)</div>
            <div class="score-bar-container">
              <div class="score-bar">
                <span :style="{ width: relativeScores.get(prediction.id) }"></span>
              </div>
            </div>
            <div class="delete-icon" @click="addObservedTechnique(prediction.id)">
              <AddIcon />
            </div>
          </TechniqueSummary>
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import { defineComponent } from "vue";
import { useInferenceEngineStore } from "@/stores/InferenceEngineStore";
import type {
  EnrichmentFile, PredictedTechnique,
  PredictedTechniques, Technique
} from "@/assets/scripts/TechniqueInferenceEngine";
// Components
import AddIcon from "../Icons/AddIcon.vue";
import DeleteIcon from "@/components/Icons/DeleteIcon.vue"
import OptionSelector from "../Controls/Fields/OptionSelector.vue";
import TechniqueSummary from "../Controls/TechniqueSummary.vue"

export default defineComponent({
  name: "PredictTechniquesTool",
  data: () => ({
    engine: useInferenceEngineStore(),
    enrichmentFile: {} as EnrichmentFile,
    observed: new Set<string>(),
    predicted: null as null | PredictedTechniques,
    trainedTechniques: new Set<string>()
  }),
  computed: {

    /**
     * Returns all techniques options.
     * @returns
     *  All technique options.
     */
    allTechniqueOptions(): Map<string, string> {
      let entries: [string, string][] = [];
      for (let id in this.enrichmentFile) {
        entries.push([id, `${id}: ${this.enrichmentFile[id].name}`]);
      }
      return new Map(entries.sort((a, b) => a[0].localeCompare(b[0])))
    },

    /**
     * Returns the observed techniques.
     * @returns
     *  The observed techniques.
     */
    observedTechniquesList(): Technique[] {
      const observed = [];
      for (let id of this.observed) {
        if (this.enrichmentFile[id]) {
          observed.push(this.enrichmentFile[id]);
        }
      }
      return observed;
    },

    /**
     * Returns a subset of the predicted techniques.
     * @returns
     *  A subset of the predicted techniques.
     */
    predictedTechniquesList(): PredictedTechnique[] {
      if (this.predicted) {
        return [...this.predicted.values()].slice(0, 10);
      } else {
        return [];
      }
    },

    /**
     * Returns the relative scores for the predictions.
     * @returns
     *  The relative scores for the predictions.
     */
    relativeScores(): Map<string, number> {
      const relativeScores = new Map();
      if (this.predicted) {
        const scores = [...this.predicted.values()].map(t => t.score);
        const maxScore = Math.max(...scores);
        for (const t of this.predicted.values()) {
          const relativeScore = maxScore ? t.score / maxScore : 0;
          relativeScores.set(t.id, `${Math.round(relativeScore * 10000) / 100}%`);
        }
      }
      return relativeScores;
    }

  },
  methods: {

    /**
     * Adds an observed technique to the set.
     * @param id
     *  The id of the technique to add.
     */
    async addObservedTechnique(id: string) {
      // Add techniques
      this.observed.add(id);
      // Update predictions
      await this.updatePredictions();
    },

    /**
     * Deletes an observed techniques from the set.
     * @param id
     *  The id of the technique to remove.
     */
    async deleteObservedTechnique(id: string) {
      // Remove techniques
      this.observed.delete(id);
      // Update predictions
      await this.updatePredictions();
    },

    /**
     * Updates the current set of predictions.
     */
    async updatePredictions() {
      if (this.observed.size) {
        const a = [...this.observed.keys()];
        const b = this.trainedTechniques;
        const techniques = new Set(a.filter(t => b.has(t)));
        this.predicted = await this.engine.predictNewReport(techniques);
      } else {
        this.predicted = null;
      }
    }

  },
  async created() {
    // Make simultaneous requests
    const [enrichmentFile, trainedTechniques] = [
      this.engine.getEnrichmentFile,
      this.engine.getTrainedTechniques
    ]
    // Await results
    this.enrichmentFile = await enrichmentFile;
    this.trainedTechniques = await trainedTechniques;
  },
  components: { AddIcon, DeleteIcon, OptionSelector, TechniqueSummary }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system.scss" as color;
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

.observed-section {
  margin-top: scale.size("xxh");
}

.observed-section,
.predicted-section {
  margin-bottom: scale.size("xxh");
}

.options-selector {
  margin-top: scale.size("xl");
}

.technique-summary {
  margin-bottom: scale.size("s");
}

.technique-summary:first-child {
  margin-top: scale.size("xl");
}

.technique-summary:last-child {
  margin-bottom: 0em;
}

.delete-icon {
  @include color.icon;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  padding: 0em scale.size("xl");
  cursor: pointer;
}

.score-bar-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.score-bar {
  width: 2 * scale.size("h");
  height: scale.size("l");
  border-style: solid;
  border-width: 1px;
  border-color: #f56600;
  box-sizing: border-box;
}

.score-bar span {
  display: block;
  height: 100%;
  background: #f56600;
}

.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.instructions {
  @include color.field-border;
  @include color.placeholder;
  padding: scale.size("m");
  border-style: dotted;
  border-width: 1px;
  margin-top: scale.size("xl");
}

.unknown {
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  padding: 0em scale.size("xl");
  @include scale.h6
}

@include scale.at-and-below-mobile-width {
  .section-header {
    flex-direction: column;
  }

  .score-bar {
    display: none;
  }
}
</style>
