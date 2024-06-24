import { ControlCommand } from "./ControlCommand";
import type { ViewFilter } from "../Controls";

export class SetViewFilter extends ControlCommand<ViewFilter> {

    /**
     * The filter to modify.
     */
    public readonly filter: string | null;

    /**
     * The filter's new value.
     */
    public readonly value: boolean;


    /**
     * Sets the value of a {@link ViewFilter}'s filter.
     * @param control
     *  The command's control.
     * @param filter
     *  The filter to modify. (`null` for all filters)
     * @param value
     *  True to enable the filter, false to disable the filter.
     */
    constructor(control: ViewFilter, filter: string | null, value: boolean) {
        super(control);
        this.filter = filter;
        this.value = value;
    }


    /**
     * Executes the command.
     */
    public execute(): void {
        if (this.filter === null) {
            if (this.value) {
                this.control.showAll();
            }
        } else {
            if (this.value) {
                this.control.show(this.filter);
            } else {
                this.control.hide(this.filter);
            }
        }
    }

}
