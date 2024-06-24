import type { ViewControl } from "../Controls";

export abstract class ControlCommand<T extends ViewControl = ViewControl> {

    /**
     * The command's control.
     */
    public readonly control: T;


    /**
     * Creates a new {@link ControlCommand}.
     * @param control
     *  The command's control.
     */
    constructor(control: T) {
        this.control = control;
    }


    /**
     * Executes the command.
     */
    public abstract execute(): void;

}
