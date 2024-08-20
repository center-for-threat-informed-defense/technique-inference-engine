import Configuration from "@/assets/configuration/app.config";
import { markRaw } from 'vue';
import { defineStore } from 'pinia'
import { EventRecorder, GoogleEventStorage } from "@/assets/scripts/Application";
import {
  PredictedTechniques,
  RemoteEnrichmentSource,
  RemoteModelSource,
  TechniqueInferenceEngine,
  type EnrichmentFile,
} from '@/assets/scripts/TechniqueInferenceEngine';

export const useInferenceEngineStore = defineStore('inferenceEngineStore', {
  state: () => ({
    recorder: markRaw(new EventRecorder(new GoogleEventStorage())),
    inferenceEngine: markRaw(
      new TechniqueInferenceEngine(
        new RemoteModelSource(Configuration.trained_model, true),
        new RemoteEnrichmentSource(Configuration.enrichment_file, true)
      )
    ),
    isWarmingUp: false
  }),
  getters: {

    /**
     * Returns the engine's {@link EnrichmentFile}.
     * @returns
     *  A Promise that resolves with the engine's {@link EnrichmentFile}.
     */
    async getEnrichmentFile(): Promise<EnrichmentFile> {
      return (await this.inferenceEngine.enrichmentSource.getData());
    },

    /**
     * Returns the set of techniques the engine was trained on.
     * @returns
     *  A Promise that resolves with the set of techniques the engine was trained on.
     */
    async getTrainedTechniques(): Promise<Set<string>> {
      const techniques = (await this.inferenceEngine.modelSource.getData()).techniques;
      return new Set([...techniques.keys()])
    }

  },
  actions: {

    /**
     * Warms up the inference engine.
     */
    async warmup(): Promise<void> {
      this.isWarmingUp = true;
      await this.inferenceEngine.warmup();
      this.isWarmingUp = false;
    },

    /**
     * Predicts a set of techniques for a new, yet unseen, report.
     * @param ids
     *  A set of Technique IDs.
     * @returns
     *  The predicted set of techniques.
     */
    async predictNewReport(ids: Set<string>): Promise<PredictedTechniques> {
      return this.inferenceEngine.predictNewReport(ids);
    }

  }
});

// Define Application Store Type
export type InferenceEngineStore = ReturnType<typeof useInferenceEngineStore>;
