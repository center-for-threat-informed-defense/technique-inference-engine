import type { PredictionItem } from "./PredictionItem";

export class PredictionGroup extends Array<PredictionItem> {

    /**
     * The name of the group.
     */
    public readonly name: string;


    /**
     * Creates a new {@link PredictionGroup}.
     * @param name
     *  The name of the group.
     */
    constructor(name: string) {
        super();
        this.name = name;
    }

}
