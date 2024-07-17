/**
 * Navigation Link
 */
export interface Link {
    name: string,
    url: string,
}

/**
 * Section Link
 */
export interface SectionLink extends Link {
    description: string
}

/**
 * Main Link
 */
export interface MainLink extends Link {
    sections?: SectionLink[]
}
