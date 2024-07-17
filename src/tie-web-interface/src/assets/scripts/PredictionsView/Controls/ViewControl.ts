export abstract class ViewControl {

    /**
     * The control's name.
     */
    public readonly name: string;


    /**
     * Creates a new {@link ViewControl}.
     * @param name
     *  The control's name.
     */
    constructor(name: string) {
        this.name = name;
    }

}
