/**
 * Attack Navigator Layer type definition.
 */
export type AttackNavigatorLayer = {
    name: string,
    versions: {
        navigator: string,
        layer: string,
        attack: string,
    },
    sorting: number,
    description: string,
    domain: string,
    techniques: AttackTechnique[],
    gradient?: {
        colors: [string, string],
        minValue: number,
        maxValue: number
    },
}

/**
 * Attack Navigator Technique type definition.
 */
export type AttackTechnique = {
    techniqueID: string,
    score?: number,
    color?: string,
    metadata: AttackTechniqueMetadata[]
}

/**
 * Attack Navigator Technique metadata type definition.
 */
export type AttackTechniqueMetadata = {
    name?: string,
    value?: string,
    divider?: boolean,
}
