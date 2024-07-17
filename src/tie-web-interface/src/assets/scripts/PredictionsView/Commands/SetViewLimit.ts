import { ControlCommand } from "./ControlCommand";
import type { ViewLimit } from "../Controls";

export class SetViewLimit extends ControlCommand<ViewLimit> {

    /**
     * The limit's new value.
     */
    public readonly value: number;


    /**
     * Sets the value of a {@link ViewLimit}.
     * @param control
     *  The command's control.
     * @param value
     *  The limit's new value.
     */
    constructor(control: ViewLimit, value: number) {
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
