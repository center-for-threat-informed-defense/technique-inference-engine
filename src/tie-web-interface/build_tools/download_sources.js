/**
 * The base URL for the ATT&CK repository.
 */
const BASE_URL = "https://raw.githubusercontent.com/mitre-attack/attack-stix-data/master";


/**
 * Enterprise Sources
 */
const ENTERPRISE_SOURCES = new Map(
    [
        "14.1", "14.0", "13.1", "13.0",
        "12.1", "12.0", "11.2", "11.1",
        "11.0", "10.1", "10.0", "9.0",
        "8.2", "8.1", "8.0"
    ].map(
        v => [v, `${BASE_URL}/enterprise-attack/enterprise-attack-${v}.json`]
    )
);

/**
 * ICS Sources
 */
const ICS_SOURCES = new Map(
    [
        "14.1", "14.0", "13.1", "13.0",
        "12.1", "12.0", "11.3", "11.2",
        "11.1", "11.0", "10.1", "10.0",
        "9.0", "8.2", "8.1", "8.0"
    ].map(
        v => [v, `${BASE_URL}/ics-attack/ics-attack-${v}.json`]
    )
);

/**
 * Mobile Sources
 */
const MOBILE_SOURCES = new Map(
    [
        "14.1", "14.0", "13.1", "13.0",
        "12.1", "12.0", "11.3", "10.1",
        "10.0", "9.0", "8.2", "8.1",
        "8.0"
    ].map(
        v => [v, `${BASE_URL}/mobile-attack/mobile-attack-${v}.json`]
    )
);

/**
 * The STIX sources.
 */
const STIX_SOURCES = new Map([
    ["ics", ICS_SOURCES],
    ["mobile", MOBILE_SOURCES],
    ["enterprise", ENTERPRISE_SOURCES]
])

/**
 * Export
 */
module.exports = {
    STIX_SOURCES
};
