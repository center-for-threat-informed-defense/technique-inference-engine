import type { Tensor } from "@tensorflow/tfjs";

export class Model {

    /**
     * A map that maps technique IDs to columns in `V`.
     */
    public readonly techniques: Map<string, number>;

    /**
     * The 'U' component of the trained model.
     */
    public U: Tensor;

    /**
     * The 'V' component of the trained model.
     */
    public V: Tensor;

    /**
     * If true, the model cannot be disposed.
     */
    protected disposalLocked: boolean;


    /**
     * Creates a new {@link Model}.
     * @param techniques
     *  A map that maps technique IDs to columns in `V`.
     * @param U
     *  An {@link NpyArray} containing the 'U' component of the trained model.
     * @param V
     *  An {@link NpyArray} containing the 'V' component of the trained model.
     */
    constructor(
        techniques: Map<string, number>,
        U: Tensor,
        V: Tensor
    ) {
        this.techniques = techniques;
        this.U = U;
        this.V = V;
        this.disposalLocked = false;
    }


    /**
     * Disposes the {@link Model} from memory.
     * @remarks
     *  When the model is cached by a `DataSource`, this method has no effect.
     *  To free a cached model, see `ModelSource.dumpCache()`.
     * @param override
     *  If true, the model is forcibly disposed.
     */
    public dispose() {
        if (!this.disposalLocked) {
            this.U.dispose();
            this.V.dispose();
        }
    }

}