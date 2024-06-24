import type { Technique } from "../DataSource";

/**
 * A predicted technique.
 */
export type PredictedTechnique = Technique & { rank: number, score: number };
