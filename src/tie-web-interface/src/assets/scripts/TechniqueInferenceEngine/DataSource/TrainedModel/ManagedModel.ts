import { Model } from "./Model";

export class ManagedModel extends Model {

    /**
     * Locks/Unlocks the {@link Model}'s disposal method.
     * @param lock
     *  If true, the model cannot be disposed.
     * @returns
     *  The {@link ManagedModel}.
     */
    public lockDisposal(lock: boolean): ManagedModel {
        this.disposalLocked = lock;
        return this;
    }

}
