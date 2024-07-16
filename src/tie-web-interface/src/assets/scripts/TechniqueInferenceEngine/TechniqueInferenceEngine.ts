import { WalsRecommender } from "./Recommenders";
import { getBackend, tensor, tidy } from "@tensorflow/tfjs";
import { PredictedTechniques, PredictedTechniquesMetadata, type PredictedTechnique } from "./Results";
import type { DataSource, EnrichmentFile, Model } from "./DataSource";

export class TechniqueInferenceEngine {

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
        modelSource: DataSource<Model>,
        enrichmentSource: DataSource<EnrichmentFile>,
    ) {
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
            const index = model.techniques.get(id)!;
            if (index === undefined) {
                throw new Error(`Unknown Technique ID: '${id}'.`)
            }
            techniques[index] = 1;
        }
        const techniquesTensor = tidy(
            () => tensor(techniques, [techniques.length], "float32").expandDims(1)
        );

        // Perform predictions
        const recommender = new WalsRecommender(model.C, model.RC);
        const predictionsTensor = await recommender.predictNewEntity(
            techniquesTensor, model.U, model.V
        );

        // Enrich predictions
        let results: [string, PredictedTechnique][] = [];
        const enrichmentFile = await enrichmentFileRequest;
        for (const [id, index] of model.techniques) {
            // Exclude observed techniques from results
            if (ids.has(id)) {
                continue;
            }
            // Resolve enriched technique information
            let technique = enrichmentFile.techniques[id];
            if (!technique) {
                technique = {
                    id: id,
                    name: "Unknown Technique",
                    description: "Unknown Technique.",
                    tactics: [],
                    platforms: [],
                    campaigns: [],
                    groups: []
                }
            }
            // Apply enrichment to prediction
            const score = (await predictionsTensor.buffer()).get(index);
            results.push([id, { rank: 0, score, ...technique }]);
        }

        // Free tensors from memory
        techniquesTensor.dispose();
        predictionsTensor.dispose();
        model.dispose();

        // Calculate prediction time
        const end = performance.now();

        // Sort and Rank results
        results = results.sort((a, b) => b[1].score - a[1].score);
        let rank = 1;
        for (let i = 0; i < results.length; i++) {
            const nextResult = results[i][1];
            const lastResult = i > 0 ? results[i - 1][1] : null;
            if (lastResult?.score === nextResult.score) {
                nextResult.rank = lastResult.rank;
            } else {
                nextResult.rank = rank++;
            }
        }

        // Return results
        return new PredictedTechniques(
            new Map(results),
            new PredictedTechniquesMetadata(
                end - start,
                getBackend(),
                enrichmentFile.domain,
                enrichmentFile.version
            )
        );

    }

}
