import { ControlCommand } from "./ControlCommand";
import type { ViewOption } from "../Controls";

export class SetViewOption extends ControlCommand<ViewOption> {

    /**
     * The option's new value.
     */
    public readonly value: string;


    /**
     * Sets the value of a {@link ViewOption}.
     * @param control
     *  The command's control.
     * @param value
     *  The option's new value.
     */
    constructor(control: ViewOption, value: string) {
        super(control);
        this.value = value;
    }


    /**
     * Executes the command.
     */
    public execute(): void {
        this.control.value = this.value;
    }

}
