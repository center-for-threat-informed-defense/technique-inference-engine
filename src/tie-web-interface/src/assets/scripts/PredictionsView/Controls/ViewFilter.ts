import { ViewControl } from "./ViewControl";

export class ViewFilter<T = string> extends ViewControl {

    /**
     * The internal applied filters.
     */
    private _appliedFilters: Set<T>;

    /**
     * The internal available filters.
     */
    private _filters: Set<T>;

    /**
     * The applied filters.
     */
    public get appliedFilters(): ReadonlySet<T> {
        return this._appliedFilters;
    }

    /**
     * The available filters.
     */
    public get filters(): ReadonlySet<T> {
        return this._filters;
    }


    /**
     * Creates a new {@link ViewFilter}.
     * @param name
     *  The control's name.
     * @param filters
     *  The available filters.
     */
    constructor(name: string, filters: Set<T>) {
        super(name);
        this._appliedFilters = new Set();
        this._filters = filters;
    }


    /**
     * Show all items.
     */
    public showAll() {
        this._appliedFilters.clear();
    }

    /**
     * Show all items with the specified value.
     * @param value
     *  The filter value.
     */
    public show(value: T) {
        if (!this._filters.has(value)) {
            return;
        }
        this._appliedFilters.add(value);
        if (this._appliedFilters.size === this._filters.size) {
            this._appliedFilters.clear();
        }
    }

    /**
     * Hides all items with the specified value.
     * @param value
     *  The filter value.
     */
    public hide(value: T) {
        this._appliedFilters.delete(value);
    }

    /**
     * Tests if items with the specified value are shown.
     * @param value
     *  The filter value.
     * @returns
     *  True if items with the specified value are shown, false otherwise.
     */
    public isShown(value: T | T[]) {
        if (this.allShown()) {
            return true;
        }
        if (Array.isArray(value)) {
            for (const item of value) {
                if (this._appliedFilters.has(item)) {
                    return true;
                }
            }
            return false;
        } else {
            return this._appliedFilters.has(value);
        }
    }

    /**
     * Tests if all items are shown.
     * @returns
     *  True if all items are shown, false otherwise.
     */
    public allShown(): boolean {
        return this._appliedFilters.size === 0;
    }

    /**
     * Creates a new {@link ViewFilter} from the existing value.
     * @param filters
     *  The new set of filters.
     */
    public pivot(filters: Set<T>): ViewFilter<T> {
        const pivot = new ViewFilter(this.name, filters);
        for (const filter of this.appliedFilters) {
            pivot.show(filter);
        }
        return pivot;
    }

}
