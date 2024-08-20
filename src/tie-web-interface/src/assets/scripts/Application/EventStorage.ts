export interface EventStorage {

    /**
     * Records an event to the event store.
     * @param name
     *  The event's name.
     * @param parameters
     *  The event's parameters.
     */
    record(name: string, parameters: { [key: string]: string | number | boolean; }): void;

}
