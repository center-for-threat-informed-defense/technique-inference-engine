import { DataSource } from "../DataSource";
import { ManagedModel } from "./ManagedModel";
import type { Tensor } from "@tensorflow/tfjs";

export abstract class ModelSource extends DataSource<ManagedModel> {

    /**
     * Configures a new {@link ManagedModel}.
     * @param T
     *  A map that maps technique IDs to columns in V.
     * @param U
     *  A {@link Tensor} containing the 'U' component of the trained model.
     * @param V
     *  A {@link Tensor} containing the 'V' component of the trained model.
     * @param C
     *  The trained model's `c` value.
     * @param RC
     *  The trained model's regularization coefficient.
     * @returns
     *  The configured {@link ManagedModel}.
     */
    protected newModel(
        T: Map<string, number>,
        U: Tensor,
        V: Tensor,
        C: number,
        RC: number
    ): ManagedModel {
        return new ManagedModel(T, U, V, C, RC).lockDisposal(this.cachingEnabled);
    }

    /**
     * Dumps the {@link Model} from the {@link DataSource}'s cache.
     * @param dispose
     *  Whether the {@link Model} should be disposed of after it's dumped.
     *  (Default: true)
     */
    public override dumpCache(dispose: boolean = true): void {
        this._cachedData?.lockDisposal(false);
        if (dispose) {
            this._cachedData?.dispose();
        }
        super.dumpCache();
    }

}
