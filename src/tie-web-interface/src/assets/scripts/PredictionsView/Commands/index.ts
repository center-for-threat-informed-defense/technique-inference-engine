import { SetViewLimit } from "./SetViewLimit";
import { SetViewFilter } from "./SetViewFilter";
import { SetViewOption } from "./SetViewOption";
import { SetMaxThreshold } from "./SetMaxThreshold";
import { SetMinThreshold } from "./SetMinThreshold";
import type { ControlCommand } from "./ControlCommand";
import type { ViewFilter, ViewLimit, ViewOption, ViewThreshold } from "../Controls";

export * from "./ControlCommand";

/**
 * Sets the value of a {@link ViewLimit}.
 * @param control
 *  The command's control.
 * @param value
 *  The limit's new value.
 */
export function setViewLimit(control: ViewLimit, value: number) {
    return new SetViewLimit(control, value);
}

/**
 * Sets the min threshold of a {@link ViewThreshold}.
 * @param control
 *  The command's control.
 * @param value
 *  The min threshold's new value.
 * @returns
 *  A command that represents the action.
 */
export function setMinThreshold(control: ViewThreshold, value: number): ControlCommand {
    return new SetMinThreshold(control, value);
}

/**
 * Sets the max threshold of a {@link ViewThreshold}.
 * @param control
 *  The command's control.
 * @param value
 *  The max threshold's new value.
 * @returns
 *  A command that represents the action.
 */
export function setMaxThreshold(control: ViewThreshold, value: number): ControlCommand {
    return new SetMaxThreshold(control, value);
}

/**
 * Sets the value of a {@link ViewOption}.
 * @param control
 *  The command's control.
 * @param value
 *  The option's new value.
 * @returns
 *  A command that represents the action.
 */
export function setViewOption(control: ViewOption, value: string): ControlCommand {
    return new SetViewOption(control, value);
}

/**
 * Sets the value of a {@link ViewFilter}'s filter.
 * @param control
 *  The command's control.
 * @param filter
 *  The filter to modify.
 * @param value
 *  True to enable the filter, false to disable the filter.
 * @returns
 *  A command that represents the action.
 */
export function setViewFilter(control: ViewFilter, filter: string, value: boolean): ControlCommand {
    return new SetViewFilter(control, filter, value);
}

/**
 * Shows all filter options.
 * @param control
 *  The command's control.
 * @returns
 *  A command that represents the action.
 */
export function showAllOfFilter(control: ViewFilter) {
    return new SetViewFilter(control, null, true);
}
