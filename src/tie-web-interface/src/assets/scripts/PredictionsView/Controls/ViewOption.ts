import { ViewControl } from "./ViewControl";

export class ViewOption<T = string> extends ViewControl {

    /**
     * The internal available options.
     */
    private _options: Set<T>;

    /**
     * The internal selected option.
     */
    private _value: T | null;


    /**
     * The available options.
     */
    public get options(): ReadonlySet<T> {
        return this._options;
    }

    /**
     * The selected option.
     */
    public get value(): T | null {
        return this._value;
    }

    /**
     * The selected option.
     */
    public set value(value: T | null) {
        if (value === null) {
            this._value = value;
        } else if (this.options.has(value)) {
            this._value = value;
        } else {
            this._value = this.options.values().next().value ?? null;
        }
    }


    /**
     * Creates a new {@link ViewOption}.
     * @param name
     *  The control's name.
     * @param options
     *  The control's valid options.
     */
    constructor(name: string, options: Set<T>) {
        super(name);
        this._options = options;
        this._value = options.values().next().value ?? null;
    }


    /**
     * Creates a new {@link ViewOption} from the existing value.
     * @param options
     *  The new set of options.
     */
    public pivot(options: Set<T>): ViewOption<T> {
        const pivot = new ViewOption<T>(this.name, options);
        pivot.value = this.value;
        return pivot;
    }

}
