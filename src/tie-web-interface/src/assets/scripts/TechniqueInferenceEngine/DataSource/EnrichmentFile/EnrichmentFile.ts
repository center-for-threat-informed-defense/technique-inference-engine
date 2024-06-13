export type EnrichmentFile = {
    [key: string]: Technique
}

export type Technique = {

    /**
     * The Technique's id.
     */
    id: string,

    /**
     * The Technique's name.
     */
    name: string,

    /**
     * The Technique's description.
     */
    description: string

}
