export abstract class DataSource<T> {

    /**
     * Whether the source caches the data after it's retrieved.
     */
    public readonly cachingEnabled: boolean;

    /**
     * The source's cached data.
     */
    protected _cachedData: T | null;


    /**
     * Creates a new {@link DataSource}.
     * @param enableCaching
     *  Whether the source should cache the data after it's retrieved.
     *  (Default: false)
     */
    constructor(enableCaching: boolean = false) {
        this.cachingEnabled = enableCaching;
        this._cachedData = null;
    }


    /**
     * Returns the data.
     * @returns
     *  A Promise that resolves with the data.
     */
    public async getData(): Promise<T> {
        if (this._cachedData) {
            return Promise.resolve(this._cachedData);
        } else if (this.cachingEnabled) {
            this._cachedData = await this.getDataFromSource();
            return this._cachedData;
        } else {
            return await this.getDataFromSource();
        }
    }

    /**
     * Returns the data from its source.
     * @returns
     *  A Promise that resolves with the data.
     */
    protected abstract getDataFromSource(): Promise<T>;

    /**
     * Preloads the data.
     * @remarks
     *  This method has no effect if caching is disabled.
     * @returns
     *  A Promise that resolves once the data is preloaded.
     */
    public async preload(): Promise<void> {
        if (this.cachingEnabled) {
            await this.getData();
        } else {
            console.warn("Source does not cache its data, preloading has no effect.");
        }
    }

    /**
     * Dumps the data from the cache.
     */
    public dumpCache() {
        this._cachedData = null;
    }

}
