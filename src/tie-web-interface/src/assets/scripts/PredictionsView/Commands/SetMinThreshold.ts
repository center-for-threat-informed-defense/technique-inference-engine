import { ControlCommand } from "./ControlCommand";
import type { ViewThreshold } from "../Controls";

export class SetMinThreshold extends ControlCommand<ViewThreshold> {

    /**
     * The min threshold's new value.
     */
    public readonly value: number;


    /**
     * Sets the min threshold of a {@link ViewThreshold}.
     * @param control
     *  The command's control.
     * @param value
     *  The min threshold's new value.
     */
    constructor(control: ViewThreshold, value: number) {
        super(control);
        this.value = value;
    }


    /**
     * Executes the command.
     */
    public execute(): void {
        this.control.minThreshold = this.value;
    }

}
