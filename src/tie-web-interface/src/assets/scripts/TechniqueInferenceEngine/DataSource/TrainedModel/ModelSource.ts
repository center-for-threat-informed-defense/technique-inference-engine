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
     * @returns
     *  The configured {@link ManagedModel}.
     */
    protected newModel(T: Map<string, number>, TR: Set<string>, U: Tensor, V: Tensor): ManagedModel {
        return new ManagedModel(T, TR, U, V).lockDisposal(this.cachingEnabled);
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
