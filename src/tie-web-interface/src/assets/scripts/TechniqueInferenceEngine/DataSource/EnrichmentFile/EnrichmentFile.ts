export type EnrichmentFile = {

    /**
     * The file's ATT&CK domain.
     */
    domain: string,

    /**
     * The file's ATT&CK version.
     */
    version: string,

    /**
     * The file's technique's.
     */
    techniques: {
        [key: string]: Technique
    }

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
    description: string,

    /**
     * The Technique's platforms.
     */
    platforms: string[];

    /**
     * The Technique's tactics.
     */
    tactics: string[];

    /**
     * The Technique's associated campaigns.
     */
    campaigns: string[];

    /**
     * The Technique's associated groups.
     */
    groups: string[];

}

/**
 * Creates an empty {@link EnrichmentFile}.
 * @returns
 *  An empty {@link EnrichmentFile}.
 */
export function createEmptyEnrichmentFile(): EnrichmentFile {
    return {
        domain: "",
        version: "",
        techniques: {}
    }
}
