import { ViewControl } from "./ViewControl";

export class ViewLimit extends ViewControl {

    /**
     * The limit's internal minimum value.
     */
    private _minLimit: number;

    /**
     * The limit's internal maximum value.
     */
    private _maxLimit: number;

    /**
     * The limit's internal value.
     */
    private _value: number;


    /**
     * The limit's minimum value.
     */
    public get minLimit(): number {
        return this._minLimit;
    }

    /**
     * The limit's minimum value.
     */
    public set minLimit(value: number) {
        this._minLimit = value;
        this._maxLimit = Math.max(this._minLimit, this._maxLimit);
        this.value = this._value;
    }

    /**
     * The limit's maximum value.
     */
    public get maxLimit(): number {
        return this._maxLimit;
    }

    /**
     * The limit's maximum value.
     */
    public set maxLimit(value: number) {
        this._maxLimit = value;
        this._minLimit = Math.min(this._minLimit, this._maxLimit);
        this.value = this._value;
    }

    /**
     * The limit's value.
     */
    public get value(): number {
        return this._value;
    }

    /**
     * The limit's value.
     */
    public set value(value: number) {
        this._value = Math.min(Math.max(value, this._minLimit), this._maxLimit);
    }


    /**
     * Creates a new {@link ViewLimit}.
     * @param name
     *  The control's name.
     * @param min
     *  The limit's minimum value.
     * @param max
     *  The limit's maximum value.
     */
    constructor(name: string, min?: number, max?: number) {
        super(name);
        this._minLimit = min ?? 0;
        this._maxLimit = Math.max(this._minLimit, max ?? 100);
        this._value = this._maxLimit;
    }


    /**
     * Creates a new {@link ViewLimit} from the existing value.
     * @param min
     *  The limit's new minimum value.
     * @param max
     *  The limit's new maximum value.
     */
    public pivot(min: number, max: number): ViewLimit {
        const _min = Math.min(min, max);
        const _max = Math.max(min, max);
        const pivot = new ViewLimit(this.name, _min, _max);
        pivot.value = this._value;
        return pivot;
    }

}
