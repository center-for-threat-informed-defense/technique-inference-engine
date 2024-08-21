import type { EventStorage } from "./EventStorage";
import type { RecordParameter } from "./RecordParameter";

declare const gtag: (
    command: "event",
    event_name: string,
    parameters: { [key: string]: RecordParameter; }
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
    record(name: string, parameters: { [key: string]: RecordParameter; }): void {
        // Validate record
        if (!name.match(/^[a-z][a-z_]*$/g)) {
            const error = `Event name '${name}' does not follow typical convention.`;
            throw new Error(error);
        }
        // Record event
        gtag('event', name, parameters);
    }

}
