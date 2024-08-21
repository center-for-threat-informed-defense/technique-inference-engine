<template>
  <div class="predict-techniques-tool-element">
    <div class="observed-section">
      <div class="section-header">
        <h3>Observed Techniques</h3>
      </div>
      <div class="options-selector">
        <OptionSelector class="options-field" placeholder="Add Technique" :options="allTechniqueOptions"
          @select="addObservedTechniqueFromField" />
        <button @click="addObservedTechniqueFromCsv()">
          <UploadArrow class="icon" /><span>.CSV</span>
        </button>
      </div>
      <div class="techniques">
        <template v-for="observed of observedTechniquesList" :key="observed.id">
          <TechniqueItemSummary class="summary" :item="observed">
            <template v-if="!trainedTechniques.has(observed.id)" #notice>
              Due to current limitations in the dataset, {{ observed.id }} was not
              included in the training. Its inclusion here will not affect the predictions.
            </template>
            <template #default>
              <div class="action-icon" @click="deleteObservedTechnique(observed.id)">
                <DeleteIcon />
              </div>
            </template>
          </TechniqueItemSummary>
        </template>
      </div>
    </div>
    <div class="predicted-section">
      <div class="section-header">
        <h3>Predicted Techniques</h3>
        <small>{{ predictionMetadata }}</small>
      </div>
      <TechniquesViewController class="view-controller" :view="viewer" @execute="execute" @download="download" />
      <div class="instructions" v-if="!predicted">
        To generate a set of predictions, add one or more observed techniques.
      </div>
      <div class="techniques">
        <template v-for="[key, item] of view.items" :key="key">
          <component class="summary" :is="getSummaryType(item)" :item="item">
            <template v-slot="{ technique }">
              <div class="action-icon" @click="addObservedTechniqueFromPivot(technique.id)">
                <AddIcon />
              </div>
            </template>
          </component>
        </template>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
// Dependencies
import Papa from "papaparse";
import { Browser } from "@/assets/scripts/Utilities";
import { defineComponent } from "vue";
import { useInferenceEngineStore } from "@/stores/InferenceEngineStore";
import {
  PredictedTechniques,
  createEmptyEnrichmentFile,
  type Technique
} from "@/assets/scripts/TechniqueInferenceEngine";
import {
  PredictionGroup,
  PredictionsView,
  type PredictionItem,
  type ControlCommand
} from "@/assets/scripts/PredictionsView";
// Components
import AddIcon from "../Icons/AddIcon.vue";
import DeleteIcon from "@/components/Icons/DeleteIcon.vue";
import UploadArrow from "@/components/Icons/UploadArrow.vue";
import OptionSelector from "../Controls/Fields/OptionSelector.vue";
import TechniqueItemSummary from "../Controls/TechniqueItemSummary.vue";
import TechniqueGroupSummary from "../Controls/TechniqueGroupSummary.vue";
import TechniquesViewController from "../Controls/TechniquesViewController.vue";

export default defineComponent({
  name: "PredictTechniquesTool",
  data: () => ({
    engine: useInferenceEngineStore(),
    enrichmentFile: createEmptyEnrichmentFile(),
    trainedTechniques: new Set<string>(),
    observed: new Set<string>(),
    predicted: null as PredictedTechniques | null,
    view: new PredictionsView()
  }),
  computed: {

    /**
     * Returns all techniques options.
     * @returns
     *  All technique options.
     */
    allTechniqueOptions(): Map<string, string> {
      const techniques = this.enrichmentFile.techniques;
      let entries: [string, string][] = [];
      for (let id in techniques) {
        entries.push([id, `${id}: ${techniques[id].name}`]);
      }
      return new Map(entries.sort((a, b) => a[0].localeCompare(b[0])))
    },

    /**
     * Returns the observed techniques.
     * @returns
     *  The observed techniques.
     */
    observedTechniquesList(): Technique[] {
      const techniques = this.enrichmentFile.techniques;
      const observed = [];
      for (let id of this.observed) {
        if (techniques[id]) {
          observed.push(techniques[id]);
        }
      }
      return observed;
    },

    /**
     * Returns the human-readable prediction metadata.
     * @returns
     *  The human-readable prediction metadata.
     */
    predictionMetadata(): string {
      if (this.predicted) {
        const s = this.predicted.size;
        const t = this.predicted.metadata.humanReadableTime;
        const b = this.predicted.metadata.humanReadableBackend;
        return `Generated ${s} predictions in ${t} (on ${b}).`;
      }
      return "";
    },

    /**
     * Returns the {@link PredictionsView}.
     * @remarks
     *  Have to cast because Vue seems to struggle with type inference.
     */
    viewer(): PredictionsView {
      return this.view as PredictionsView;
    }

  },
  methods: {

    /**
     * Returns the summary type for a view item.
     * @param item
     *  The summary type for a view item.
     */
    getSummaryType(item: PredictionItem | PredictionGroup) {
      if (item instanceof PredictionGroup) {
        return "TechniqueGroupSummary";
      } else {
        return "TechniqueItemSummary";
      }
    },

    /**
     * Adds an observed technique to the set.
     * @param id
     *  The id of the technique to add.
     */
    async addObservedTechnique(id: string) {
      id = id.toLocaleUpperCase();
      if (this.allTechniqueOptions.has(id)) {
        this.observed.add(id);
      }
    },

    /**
     * Pivots a technique to the observed set.
     * @param id
     *  The id of the technique to add.
     */
    async addObservedTechniqueFromPivot(id: string) {
      // Add Technique
      this.addObservedTechnique(id);
      this.engine.recorder.addTechniques("technique_pivot", [id]);
      // Update predictions
      await this.updatePredictions();
    },

    /**
     * Adds an observed technique to the set from the technique field.
     * @param id
     *  The id of the technique to add.
     */
    async addObservedTechniqueFromField(id: string) {
      // Add Technique
      this.addObservedTechnique(id);
      this.engine.recorder.addTechniques("technique_field", [id]);
      // Update predictions
      await this.updatePredictions();
    },

    /**
     * Adds observed techniques to the set from a CSV file.
     */
    async addObservedTechniqueFromCsv() {
      // Open CSV File
      const { contents } = (await Browser.openTextFileDialog([], false));
      // Parse CSV File
      const objects = Papa.parse<PredictionItem>(`${contents}`, {
        header: true,
        transformHeader: header => header.toLocaleLowerCase()
      }).data;
      // Add Techniques
      for (let obj of objects) {
        this.addObservedTechnique(obj.id);
      }
      this.engine.recorder.addTechniques("import_csv", objects.map(o => o.id));
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
        this.engine.recorder.makePrediction(
          [...techniques],
          this.predicted.metadata.humanReadableBackend,
          this.predicted.metadata.time
        );
      } else {
        this.predicted = null;
      }
      this.view.setTechniques(this.predicted);
    },

    /**
     * Executes a control command.
     * @param cmd
     *  The command to execute.
     */
    execute(cmd: ControlCommand) {
      cmd.execute();
      this.engine.recorder.applyViewControl(cmd);
    },

    /**
     * Downloads a file to the device.
     * @param type
     *  The file's type.
     * @param contents
     *  The file's contents.
     */
    download(type: string, contents: string) {
      switch (type) {
        case "csv":
          Browser.downloadFile("predictions", contents, "csv");
          this.engine.recorder.downloadArtifact(type);
          break;
        case "navigator_layer":
          Browser.downloadFile("predictions_navigator_layer", contents, "json");
          this.engine.recorder.downloadArtifact(type);
          break;
        default:
          console.warn(`Cannot download unknown file type: '${type}'.`)
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
  components: {
    AddIcon, DeleteIcon, UploadArrow, OptionSelector,
    TechniqueItemSummary, TechniqueGroupSummary, TechniquesViewController
  }
});
</script>

<style lang="scss" scoped>
@use "@/assets/styles/engenuity_color_system.scss" as color;
@use "@/assets/styles/engenuity_scaling_system.scss" as scale;

/** === Main Element === */

.observed-section {
  margin-top: scale.size("xxh");
}

.observed-section,
.predicted-section {
  margin-bottom: scale.size("xxh");
}

.section-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}

.techniques {
  margin-top: scale.size("xl");
}

.summary {
  margin-bottom: scale.size("s");
}

.summary:last-child {
  margin-bottom: 0em;
}

.instructions {
  @include color.field-border;
  @include color.placeholder;
  padding: scale.size("l");
  border-style: dotted;
  border-width: 1px;
  margin-top: scale.size("xl");
}

@include scale.at-and-below-mobile-width {
  .section-header {
    flex-direction: column;
  }
}

/** === Observed Techniques Section === */

.options-selector {
  display: flex;
  margin-top: scale.size("xl");
}

.options-field {
  flex: 1;
  margin-right: scale.size("s");
}

.action-icon {
  @include color.icon;
  display: flex;
  align-items: center;
  justify-content: center;
  user-select: none;
  padding: 0em scale.size("xl");
  cursor: pointer;
}

/** === Predicted Techniques Section === */

.view-controller {
  margin-top: scale.size("l");
}
</style>
