import { getBackend, tensor, tidy } from "@tensorflow/tfjs";
import { PredictedTechniques } from "./PredictedTechniques";
import { PredictedTechniquesMetadata } from "./PredictedTechniquesMetadata";
import type { Recommender } from "./Recommenders";
import type { PredictedTechnique } from "./PredictedTechnique";
import type { DataSource, EnrichmentFile, Model } from "./DataSource";

export class TechniqueInferenceEngine {

    /**
     * The engine's underlying recommender model.
     */
    public readonly recommender: Recommender;

    /**
     * The engine's {@link Model}'s source.
     */
    public readonly modelSource: DataSource<Model>;

    /**
     * The engine's {@link EnrichmentFile}'s source.
     */
    public readonly enrichmentSource: DataSource<EnrichmentFile>;


    /**
     * Creates a new {@link TechniquePredictor}.
     * @param model
     *  The engine's underlying recommender model.
     * @param modelSource
     *  The engine's {@link Model}'s model.
     * @param enrichmentSource
     *  The engine's {@link EnrichmentFile}'s source.
     */
    constructor(
        recommender: Recommender,
        modelSource: DataSource<Model>,
        enrichmentSource: DataSource<EnrichmentFile>,
    ) {
        this.recommender = recommender;
        this.modelSource = modelSource;
        this.enrichmentSource = enrichmentSource;
    }


    /**
     * Warms up the recommender by preloading the {@link DataSource}s (if caching is
     * enabled on the sources) and performing an initial prediction.
     * @remarks
     *  TensorFlow does not immediately upload Tensor data to the GPU. Instead, Tensor
     *  data resides on the CPU until it is used in an operation. By performing an
     *  initial prediction, we can preemptively upload the required tensors to the GPU
     *  and decrease the runtime of the first prediction.
     */
    public async warmup(): Promise<void> {
        // Preload data sources
        const sources = [];
        if (this.enrichmentSource.cachingEnabled) {
            sources.push(this.enrichmentSource.preload());
        }
        if (this.modelSource.cachingEnabled) {
            sources.push(
                this.modelSource
                    .preload()
                    // Execute initial prediction
                    .then(() => this.predictNewReport(new Set()))
            );
        }
        await Promise.all(sources);
    }

    /**
     * Predicts a set of techniques for a new, yet unseen, report.
     * @param ids
     *  A set of Technique IDs.
     * @returns
     *  The predicted set of techniques.
     */
    public async predictNewReport(ids: Set<string>): Promise<PredictedTechniques> {

        // Start timer
        const start = performance.now();

        // Request enrichment file ahead of time
        const enrichmentFileRequest = this.enrichmentSource.getData();

        // Resolve model
        const model = await this.modelSource.getData();

        // Create technique tensor
        const techniques = new Array(model.V.shape[0]).fill(0);
        for (const id of ids) {
            const index = model.techniques.get(id);
            if (!index) {
                throw new Error(`Unknown Technique ID: '${id}'.`)
            }
            techniques[index] = 1;
        }
        const techniquesTensor = tidy(
            () => tensor(techniques, [techniques.length], "float32").expandDims(1)
        );

        // Perform predictions
        const predictionsTensor = await this.recommender.predictNewEntity(
            techniquesTensor, model.U, model.V
        );

        // Enrich predictions
        const enrichmentFile = await enrichmentFileRequest;
        const results = new Map<string, PredictedTechnique>();
        for (const [id, index] of model.techniques) {
            let technique = enrichmentFile[id];
            if (!technique) {
                technique = {
                    id: id,
                    name: "Unknown Technique",
                    description: "Unknown Technique.",
                }
            }
            const score = (await predictionsTensor.buffer()).get(index);
            results.set(id, { ...technique, score });
        }

        // Free tensors from memory
        techniquesTensor.dispose();
        predictionsTensor.dispose();
        model.dispose();

        // Calculate prediction time
        const end = performance.now();

        // Return results
        return new PredictedTechniques(
            results,
            new PredictedTechniquesMetadata(end - start, getBackend())
        );

    }

}
