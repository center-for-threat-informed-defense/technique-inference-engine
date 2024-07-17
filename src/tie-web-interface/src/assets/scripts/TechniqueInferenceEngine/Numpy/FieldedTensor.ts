import { Tensor } from "@tensorflow/tfjs"
import type { NumpyShape } from "./NumpyShape";

export class FieldedTensor extends Array<TensorField> {

    /**
     * The shape of the {@link FieldedTensor}.
     */
    public shape: NumpyShape


    /**
     * Creates a new {@link FieldedTensor}.
     * @param value
     *  The tensor's values.
     * @param shape
     *  The tensor's shape.
     */
    constructor(value: TensorField[], shape: NumpyShape) {
        super(...value);
        this.shape = shape;
    }


    /**
     * Disposes the {@link FieldedTensor} from memory.
     */
    public dispose() {
        for (const tensor of this) {
            this.disposeRecursively(tensor);
        }
    }

    /**
     * Recursively disposes a {@link TensorField}.
     * @param field
     *  The {@link TensorField} to dispose.
     */
    private disposeRecursively(field: TensorField) {
        for (const key in field) {
            const value = field[key];
            if (value instanceof Tensor) {
                value.dispose();
            } else {
                this.disposeRecursively(value);
            }
        }
    }

}

/**
 * A Tensor field.
 */
export type TensorField = {
    [key: string]: TensorField | Tensor;
}
