import type { RecordParameter } from "./RecordParameter";

export interface EventStorage {

    /**
     * Records an event to the event store.
     * @param name
     *  The event's name.
     * @param parameters
     *  The event's parameters.
     */
    record(name: string, parameters: { [key: string]: RecordParameter; }): void;

}
