export class PredictedTechniquesMetadata {

    /**
     * The amount of time taken to generate the predictions (in ms).
     */
    public readonly time: number;

    /**
     * The human-readable form of `time`.
     */
    public readonly humanReadableTime: string;

    /**
     * The backend used to generate the predictions.
     */
    public readonly backend: PredictionBackend;

    /**
     * The human-readable form of `backend`.
     */
    public readonly humanReadableBackend: string;

    /**
     * The ATT&CK Domain.
     */
    public readonly attackDomain: string;

    /**
     * The ATT&CK Version.
     */
    public readonly attackVersion: string;


    /**
     * Creates a new {@link PredictedTechniquesMetadata}.
     * @param time
     *  The amount of time taken to generate the predictions (in ms).
     * @param backend
     *  The backend used to generate the predictions.
     * @param domain
     *  The ATT&CK Domain.
     * @param version
     *  The ATT&CK Version.
     */
    constructor(time: number, backend: string, domain: string, version: string) {
        this.time = time;
        this.humanReadableTime = `${Math.round(time / 10) / 100} seconds`;
        this.attackDomain = domain;
        this.attackVersion = version;
        switch (backend) {
            case "webgl":
                this.backend = PredictionBackend.GPU;
                this.humanReadableBackend = "GPU";
                break;
            case "wasm":
                this.backend = PredictionBackend.CPU_COMPILED;
                this.humanReadableBackend = "CPU (Accelerated)";
                break;
            case "cpu":
                this.backend = PredictionBackend.CPU;
                this.humanReadableBackend = "CPU";
                break;
            default:
                this.backend = PredictionBackend.UNKNOWN;
                this.humanReadableBackend = backend;
                break;
        }
    }

}

/**
 * Supported Prediction Backends.
 */
export enum PredictionBackend {
    GPU,
    CPU_COMPILED,
    CPU,
    UNKNOWN
}
