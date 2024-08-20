import type { EventStorage } from "./EventStorage";

declare const gtag: (
    command: "event",
    event_name: string,
    parameters: { [key: string]: string | number | boolean; }
) => void

export class GoogleEventStorage implements EventStorage {

    /**
     * Creates a new {@link GoogleEventStorage}.
     */
    constructor() { }

    /**
     * Records an event to the event store.
     * @remarks
     *  Please ensure the event `name` follows Google Analytic's naming convention of
     *  `[verb]_[noun]` where the verb is in the simple present tense. For example:
     *   - `join_group`
     *   - `view_item`
     *   - `select_item`
     *   - `spend_virtual_currency`
     * @param name
     *  The event's name.
     * @param parameters
     *  The event's parameters.
     */
    record(name: string, parameters: { [key: string]: string | number | boolean; }): void {
        // Validate record
        if (!name.match(/^[a-z][a-z_]*$/g)) {
            const error = `Event name '${name}' does not follow typical convention.`;
            throw new Error(error);
        }
        for (const key in parameters) {
            const type = typeof parameters[key];
            if (type !== "string" && type !== "number" && type !== "boolean") {
                const types = "string, number, or boolean";
                const error = `Value of event parameter '${key}' must be a ${types}.`
                throw new Error(error);
            }
        }
        // Record event
        gtag('event', name, parameters);
    }

}
