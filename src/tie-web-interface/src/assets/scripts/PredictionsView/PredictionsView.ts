import Papa from "papaparse";
import { PredictionGroup } from "./PredictionGroup";
import { ViewFilter, ViewOption, ViewLimit } from "./Controls";
import type { PredictionItem } from "./PredictionItem";
import type { PredictedTechniques } from "../TechniqueInferenceEngine";
import type { AttackNavigatorLayer } from "./AttackNavigatorTypes";

export class PredictionsView {

    /**
     * The view's list of techniques.
     */
    private _techniques: PredictedTechniques | null;

    /**
     * The view's filtered techniques.
     */
    private get _filteredTechniques(): [string, PredictionItem][] {
        if (!this._techniques) {
            return [];
        }
        const filteredTechniques: [string, PredictionItem][] = [];
        // Apply filters
        const techniques = [...this._techniques];
        const length = Math.min(this.filters.itemLimit.value, techniques.length);
        for (let i = 0; i < length; i++) {
            const [key, item] = techniques[i];
            if (item.score <= 0) {
                break;
            }
            if (!this.filters.platformFilter.isShown(item.platforms)) {
                break;
            }
            filteredTechniques.push([key, item]);
        }
        // Resolve order
        type Order<T> = (s: (a: T, b: T) => number) => (a: T, b: T) => number;
        let order: Order<PredictionItem>;
        const orderBy = this.organizations.orderBy.value;
        switch (orderBy) {
            case "Ascending":
                order = s => ((a, b) => s(a, b));
                break;
            case "Descending":
                order = s => ((a, b) => s(b, a));
                break;
            default:
                throw new Error(`Unknown order: '${orderBy}'`)
        }
        // Resolve sort
        type Sort = (a: PredictionItem, b: PredictionItem) => number;
        let sort: Sort;
        const sortBy = this.organizations.sortBy.value;
        switch (sortBy) {
            case "Rank":
                sort = order((a, b) => a.rank - b.rank);
                break;
            case "ID":
                sort = order((a, b) => a.id.localeCompare(b.id));
                break;
            case "Name":
                sort = order((a, b) => a.name.localeCompare(b.name));
                break;
            default:
                throw new Error(`Unknown sort: '${sortBy}'`)
        }
        // Apply sort
        return filteredTechniques.sort((a, b) => sort(a[1], b[1]));
    }


    /**
     * The view's filters.
     * @remarks
     *  All filters should take the form of a {@link ViewControl}.
     */
    public readonly filters: {

        /**
         * The view's item limit.
         */
        itemLimit: ViewLimit,

        /**
         * The view's permitted platforms.
         */
        platformFilter: ViewFilter<string>;

    };

    /**
     * The view's organizations.
     * @remarks
     *  All organizations should take the form of a {@link ViewControl}.
     */
    public readonly organizations: {

        /**
         * The view's sort property.
         */
        sortBy: ViewOption<string>;

        /**
         * The view's sort order.
         */
        orderBy: ViewOption<string>;

        /**
         * The view's grouping.
         */
        groupBy: ViewOption<string>;

    };

    /**
     * The view's visible items.
     */
    public get items(): Map<string, PredictionGroup | PredictionItem> {
        const filteredTechniques = this._filteredTechniques;
        // Bin Groups
        if (this.organizations.groupBy.value === "Tactic") {
            const filteredGroups = new Map<string, PredictionGroup>();
            for (const technique of filteredTechniques) {
                for (const tactic of technique[1].tactics) {
                    if (!filteredGroups.has(tactic)) {
                        filteredGroups.set(tactic, new PredictionGroup(tactic));
                    }
                    filteredGroups.get(tactic)!.push(technique[1]);
                }
            }
            return filteredGroups;
        } else {
            return new Map(filteredTechniques);
        }
    }


    /**
     * Creates a new {@link PredictionsView}.
     */
    constructor() {
        this._techniques = null;
        this.filters = {
            itemLimit: new ViewLimit("# of Results", 1, 50),
            platformFilter: new ViewFilter("Platform", new Set())
        }
        this.organizations = {
            sortBy: new ViewOption("Sort By", new Set(["Rank", "ID", "Name"])),
            orderBy: new ViewOption("Order By", new Set(["Ascending", "Descending"])),
            groupBy: new ViewOption("Group By", new Set(["None", "Tactic"]))
        }
        this.filters.itemLimit.value = 20;
    }


    /**
     * Sets the view's list of techniques.
     * @param data
     *  The list of techniques.
     */
    public setTechniques(techniques: PredictedTechniques | null) {
        this._techniques = techniques;
        // Collect techniques
        const platforms = new Set<string>();
        for (const technique of this._techniques?.values() ?? []) {
            for (const platform of technique.platforms) {
                platforms.add(platform);
            }
        }
        // Pivot filters
        const f = this.filters;
        f.platformFilter = f.platformFilter.pivot(platforms);
    }

    /**
     * Exports the current view to a CSV file.
     * @param all
     *  If true, all techniques will be exported.
     *  If false, only the visible techniques will be exported.
     *  (Default: true)
     * @returns
     *  The current view as a CSV file.
     */
    public exportViewToCsv(all: boolean = true): string {
        // Resolve techniques
        let techniques: PredictionItem[];
        if (all) {
            techniques = [...(this._techniques ?? new Map()).values()];
        } else {
            techniques = this._filteredTechniques.map(o => o[1]);
        }
        // Compile CSV
        if (techniques.length === 0) {
            return "";
        }
        const keys = ["rank", "id", "name", "score"] as (keyof PredictionItem)[];
        const rows = new Array(1 + techniques.length);
        // Configure header column
        rows[0] = keys;
        // Configure data columns
        for (let i = 0; i < techniques.length; i++) {
            rows[i + 1] = keys.map(k => techniques[i][k]);
        }
        return Papa.unparse(rows);
    }

    /**
     * Exports the current view to an ATT&CK Navigator Layer.
     * @param all
     *  If true, all techniques will be exported.
     *  If false, only the visible techniques will be exported.
     *  (Default: true)
     * @returns
     *  The current view as an ATT&CK Navigator Layer.
     */
    public exportViewToNavigatorLayer(all: boolean = true): string {
        // Resolve techniques
        if (this._techniques === null) {
            return "";
        }
        let techniques: PredictionItem[];
        if (all) {
            techniques = [...this._techniques.values()];
        } else {
            techniques = this._filteredTechniques.map(o => o[1]);
        }
        const metadata = this._techniques.metadata;
        // Create layer
        const description =
            `Heatmap of predicted techniques generated ` +
            `from Technique Inference Engine (TIE).`
        const layer: AttackNavigatorLayer = {
            name: `Technique Inference Engine (TIE) Prediction Heatmap`,
            versions: {
                navigator: "4.8.0",
                layer: "4.4",
                attack: metadata.attackVersion,
            },
            sorting: 3,
            description: description,
            domain: `${metadata.attackDomain}-attack`,
            techniques: [],
            gradient: {
                colors: ["#ffe766", "#ffaf66"],
                minValue: 0,
                maxValue: 100
            },
        }
        for (const technique of techniques) {
            layer.techniques.push({
                techniqueID: technique.id,
                score: technique.score,
                metadata: []
            });
        }
        // Calculate gradient
        const scores = layer.techniques.map(o => o.score);
        if (scores.length) {
            layer.gradient.minValue = Math.min(...scores);
            layer.gradient.maxValue = Math.max(...scores);
        }
        // Return Navigator Layer
        return JSON.stringify(layer, null, 4);
    }

}
