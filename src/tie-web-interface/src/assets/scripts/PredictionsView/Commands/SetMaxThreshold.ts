import { ControlCommand } from "./ControlCommand";
import type { ViewThreshold } from "../Controls";

export class SetMaxThreshold extends ControlCommand<ViewThreshold> {

    /**
     * The max threshold's new value.
     */
    public readonly value: number;


    /**
     * Sets the max threshold of a {@link ViewThreshold}.
     * @param control
     *  The command's control.
     * @param value
     *  The max threshold's new value.
     */
    constructor(control: ViewThreshold, value: number) {
        super(control);
        this.value = value;
    }


    /**
     * Executes the command.
     */
    public execute(): void {
        this.control.maxThreshold = this.value;
    }

}
