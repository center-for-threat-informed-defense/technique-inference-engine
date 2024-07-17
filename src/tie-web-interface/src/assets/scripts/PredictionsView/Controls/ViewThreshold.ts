import { ViewControl } from "./ViewControl";

export class ViewThreshold extends ViewControl {

    /**
     * The threshold's internal minimum value.
     */
    private _minValue: number;

    /**
     * The threshold's internal maximum value.
     */
    private _maxValue: number;

    /**
     * The minimum threshold.
     */
    private _minThreshold: number;

    /**
     * The maximum threshold.
     */
    private _maxThreshold: number;


    /**
     * The threshold's minimum value.
     */
    public get minValue(): number {
        return this._minValue;
    }

    /**
     * The threshold's minimum value.
     */
    public set minValue(value: number) {
        this._minValue = value;
        this._maxValue = Math.max(this._minValue, this.maxValue);
        this._minThreshold = Math.max(this._minValue, this._minThreshold);
        this._maxThreshold = Math.max(this._minValue, this._maxThreshold);
    }

    /**
     * The threshold's maximum value.
     */
    public get maxValue(): number {
        return this._minValue;
    }

    /**
     * The threshold's maximum value.
     */
    public set maxValue(value: number) {
        this._maxValue = value;
        this._minValue = Math.min(this._minValue, this.maxValue);
        this._minThreshold = Math.min(this._maxValue, this._minThreshold);
        this._maxThreshold = Math.min(this._maxValue, this._maxThreshold);
    }

    /**
     * The minimum threshold.
     */
    public get minThreshold(): number {
        return this._minThreshold;
    }

    /**
     * The minimum threshold.
     */
    public set minThreshold(value: number) {
        this._minThreshold = Math.min(Math.max(value, this._minValue), this._maxValue);
        this._maxThreshold = Math.max(this._minThreshold, this._maxThreshold);
    }

    /**
     * The maximum threshold.
     */
    public get maxThreshold(): number {
        return this._maxThreshold;
    }

    /**
     * The maximum threshold.
     */
    public set maxThreshold(value: number) {
        this._maxThreshold = Math.min(Math.max(value, this._minValue), this._maxValue);
        this._minThreshold = Math.min(this._minThreshold, this._maxThreshold);
    }


    /**
     * Creates a new {@link ViewThreshold}.
     * @param name
     *  The control's name.
     * @param min
     *  The threshold's minimum value.
     * @param max
     *  The threshold's maximum value.
     */
    constructor(name: string, min?: number, max?: number) {
        super(name);
        this._minValue = min ?? 0;
        this._maxValue = Math.max(this._minValue, max ?? 100);
        this._minThreshold = this._minValue;
        this._maxThreshold = this._maxValue;
    }


    /**
     * Creates a new {@link ViewThreshold} from the existing value.
     * @param min
     *  The threshold's new minimum value.
     * @param max
     *  The threshold's new maximum value.
     */
    public pivot(min: number, max: number): ViewThreshold {
        const _min = Math.min(min, max);
        const _max = Math.max(min, max);
        const pivot = new ViewThreshold(this.name, _min, _max);
        pivot.minThreshold = this.minThreshold;
        pivot.maxThreshold = this.maxThreshold;
        return pivot;
    }

}
