import type { PredictedTechnique } from "./PredictedTechnique";
import type { PredictedTechniquesMetadata } from "./PredictedTechniquesMetadata";

export class PredictedTechniques extends Map<string, PredictedTechnique> {

    /**
     * Metadata about the prediction.
     */
    public metadata: PredictedTechniquesMetadata;


    /**
     * Creates a new {@link PredictedTechniques}.
     * @param techniques
     *  A {@link Map} of {@link PredictedTechnique}.
     * @param metadata
     *  Metadata about the prediction.
     */
    constructor(
        techniques: Map<string, PredictedTechnique>,
        metadata: PredictedTechniquesMetadata
    ) {
        super([...techniques].sort((a, b) => a[1].rank - b[1].rank));
        this.metadata = metadata;
    }


    /**
     * Returns a string representation of the object.
     * @param results
     *  The number of results to include in the string.
     *  (Default: 10)
     */
    public toString(results: number = 10): string {
        const FORMAT_NUM_SIG_DIGITS = 10;
        const PAD = 3;
        const e = [...this].slice(0, results);
        // Calculate padding
        const scoreLength = 2 + FORMAT_NUM_SIG_DIGITS;  // +2 for "0.";
        const idPad = Math.max(...e.map(e => e[1].id.length)) + PAD;
        const namePad = Math.max(...e.map(e => e[1].name.length), scoreLength) + PAD;
        // Table footer
        let tableFooter;
        if (results < this.size) {
            tableFooter = `\n${"...".padEnd(idPad) + "...".padStart(namePad)}\n`;
        } else {
            tableFooter = "\n";
        }
        // Generate string
        let str = ""
        // Metadata
        str += `Generated ${this.size} predictions in `;
        str += `${this.metadata.humanReadableTime} (using `
        str += `${this.metadata.humanReadableBackend}):\n\n`
        // Score Table
        str += "ID".padEnd(idPad);
        str += "Score".padStart(namePad);
        str += "\n";
        for (let i = 0; i < 10; i++) {
            str += "\n";
            str += e[i][1].id.padEnd(idPad);
            str += e[i][1].score.toFixed(FORMAT_NUM_SIG_DIGITS).padStart(namePad);
        }
        str += tableFooter;
        // Name Table
        str += "\n"
        str += "ID".padEnd(idPad);
        str += "Name".padStart(namePad);
        str += "\n";
        for (let i = 0; i < 10; i++) {
            str += "\n";
            str += e[i][1].id.padEnd(idPad);
            str += e[i][1].name.padStart(namePad);
        }
        str += tableFooter;
        return str;
    }

}
