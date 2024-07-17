import type { Shape, Tensor } from "@tensorflow/tfjs";

export abstract class Recommender {

    /**
     * Creates a new {@link Recommender}.
     */
    constructor() { }


    /**
     * Tests whether a condition is true or false. If false, an error is raised.
     * @param condition
     *  The condition to test.
     */
    protected assert(condition: Boolean): void;

    /**
     * Tests whether two shapes are equal. If they aren't an error is raised.
     * @param shape1
     *  The first shape.
     * @param shape2
     *  The second shape.
     */
    protected assert(shape1: Shape, shape2: Shape): void;
    protected assert(a: Shape | Boolean, b?: Shape) {
        // If shape comparison:
        if (Array.isArray(a) && Array.isArray(b)) {
            const shape1 = a;
            const shape2 = b;
            a = true;
            if (shape1.length !== shape2.length) {
                a = false;
            } else {
                for (let i = 0; i < shape1.length; i++) {
                    if (shape1[i] !== shape2[i]) {
                        a = false;
                        break;
                    }
                }
            }
        }
        // If condition comparison:
        if (!a) {
            throw new Error("Assertion failed.");
        }
    }

    /**
     * Recommends items to an unseen entity.
     * @remarks
     *  It is the responsibility of the callee to free the returned tensor's memory.
     * @param entity
     *  A length-V tensor which rates each item in the (new) entity. Items must be
     *  indexed exactly as they are in the training data.
     * @param U
     *  The 'U' component of the trained model.
     * @param V
     *  The 'V' component of the trained model.
     * @returns
     *  A Promise that resolves with a tensor containing the predicted values for the
     *  new entity.
     */
    public abstract predictNewEntity(entity: Tensor, U: Tensor, V: Tensor): Promise<Tensor>;

}
