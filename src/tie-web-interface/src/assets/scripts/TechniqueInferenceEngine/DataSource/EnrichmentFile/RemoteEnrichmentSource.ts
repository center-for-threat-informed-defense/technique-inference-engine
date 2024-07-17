import { DataSource } from "../DataSource";
import type { EnrichmentFile } from "./EnrichmentFile";

export class RemoteEnrichmentSource extends DataSource<EnrichmentFile> {


    /**
     * The url of the enrichment file.
     */
    private _url: string;


    /**
     * Creates a new {@link RemoteEnrichmentSource}.
     * @param url
     *  The url of the enrichment file.
     * @param enableCaching
     *  Whether the source should cache the model after it's retrieved.
     *  (Default: false)
     */
    constructor(url: string, enableCaching?: boolean) {
        super(enableCaching);
        this._url = `${import.meta.env.BASE_URL}${url}`;
    }


    /**
     * Returns the {@link EnrichmentFile} from its source.
     * @returns
     *  A Promise that resolves with the {@link EnrichmentFile}.
     */
    protected async getDataFromSource(): Promise<EnrichmentFile> {
        const file = await fetch(this._url);
        if (file.status === 200) {
            return JSON.parse(await file.text());
        } else {
            throw new Error(`Failed to fetch '${this._url}'. [Status: ${file.status}]`);
        }
    }

}
