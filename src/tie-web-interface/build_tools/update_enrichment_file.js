const { resolve } = require("path");
const { writeFileSync } = require("fs");
const { fetchAttackData } = require("./download_attack");
const { STIX_SOURCES } = require("./download_sources");


/**
 * The enrichment file.
 */
const ENRICHMENT_FILE = "./public/app.enrichment.json"


/**
 * Filters a set of ATT&CK Objects to only those that haven't been deprecated.
 * @param {AttackObject} objects
 *  The set of ATT&CK Objects to filter.
 */
function filterAttackObjects(objects) {
    let filtered = [];
    for (let object of objects) {
        if (object.deprecated) {
            continue;
        }
        filtered.push({
            id: object.id,
            name: object.name,
            description: object.description
        });
    }
    return filtered;
}

/**
 * Updates the Technique Enrichment File.
 * @param {string} path
 *  The Enrichment file's path.
 * @param {string} version
 *  The version of ATT&CK
 */
async function updateEnrichmentFile(path, domain, version) {

    // Resolve URL
    let url = STIX_SOURCES;
    if ((url = url.get(domain)) === undefined) {
        throw new Error(`Unknown ATT&CK domain: '${domain}'.`)
    }
    if ((url = url.get(version)) === undefined) {
        throw new Error(`Unknown ATT&CK ${domain} version: '${version}'.`)
    }

    // Download Techniques
    const listing = await fetchAttackData(url);

    // Generate Enrichment File
    console.log("→ Generating Enrichment File...");

    const techniques = filterAttackObjects(listing.get("technique"));
    const enrichmentFile = Object.fromEntries(techniques.map(o => [o.id, o]));
    writeFileSync(path, JSON.stringify(enrichmentFile, null, 4));

    // Done
    console.log("\nEnrichment file updated successfully.\n");

}

/**
 * Main
 */
updateEnrichmentFile(ENRICHMENT_FILE, "enterprise", "14.1");