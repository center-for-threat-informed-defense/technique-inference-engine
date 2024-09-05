const { resolve } = require("path");
const { writeFileSync } = require("fs");
const { fetchAttackData } = require("./download_attack.cjs");
const { STIX_SOURCES } = require("./download_sources.cjs");


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
            description: processMarkdownText(
                object.description,
                object.external_references
            ),
            platforms: object.platforms,
            tactics: object.tactics,
            campaigns: (object.campaigns ?? []).map(o => o.name),
            groups: (object.groups ?? []).map(o => o.name),
        });
    }
    return filtered;
}

/**
 * Replaces:
 *  * Common HTML tags found in `source` with their markdown equivalent.
 *  * Citations with Markdown superscripts.
 * @param {*} source
 *  The markdown source.
 * @param {*} references
 *  The citation references.
 */
function processMarkdownText(source, references = []) {
    // Replace common HTML tags
    source = source
        .replace(/<\/?code>/g, "`");
    // Replace citations
    const citationIndex = new Map();
    source = source.replace(/\(Citation: (.*?)\)/g, (match, name) => {
        if (!citationIndex.has(name)) {
            const ref = references;
            const url = ref[ref.findIndex(o => o.source_name === name)]?.url;
            if (!url) {
                // If no url, bail on replacement
                return match;
            }
            citationIndex.set(name, [citationIndex.size + 1, url]);
        }
        const [index, url] = citationIndex.get(name);
        return `^[[${index}]](${url})^`
    })
    return source;
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
    const enrichmentFile = {
        domain,
        version,
        techniques: Object.fromEntries(techniques.map(o => [o.id, o]))
    };
    writeFileSync(path, JSON.stringify(enrichmentFile));

    // Done
    console.log("\nEnrichment file updated successfully.\n");

}

/**
 * Main
 */
updateEnrichmentFile(ENRICHMENT_FILE, "enterprise", "14.1");
