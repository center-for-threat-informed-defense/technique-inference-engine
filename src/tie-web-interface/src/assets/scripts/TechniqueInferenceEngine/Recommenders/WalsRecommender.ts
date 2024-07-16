import { Recommender } from "./Recommender";
import { eye as vec_eye, NDArray, solve } from "vectorious";
import {
    eye as tf_eye, squeeze, stack, tensor,
    whereAsync, zeros, tidy, type Tensor
} from "@tensorflow/tfjs";

export class WalsRecommender extends Recommender {

    /**
     * ???
     */
    private c: number;

    /**
     * Coefficient on the embedding regularization term. Requires
     * `regularization_coefficient` > `0`.
     */
    private regularizationCoefficient: number;


    /**
     * Creates a new {@link WalsRecommender}.
     * @param c
     *  ???
     * @param regularizationCoefficient
     *  Coefficient on the embedding regularization term. Requires
     * `regularization_coefficient` > `0`.
     */
    constructor(c: number, regularizationCoefficient: number) {
        super();
        this.c = c;
        this.regularizationCoefficient = regularizationCoefficient;
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
    public async predictNewEntity(entity: Tensor, U: Tensor, V: Tensor): Promise<Tensor> {
        // Predict New Entity
        this.assert(entity.shape, [V.shape[0], 1]);
        const alpha = (1 / this.c) - 1;
        const newEntityFactor = await this.updateFactor(
            V, entity, alpha, this.regularizationCoefficient
        );
        const newEntityPredictions = tidy(
            () => squeeze(V.matMul(newEntityFactor, false, true))
        );
        // Free intermediate tensors from memory
        newEntityFactor.dispose();
        // Return predictions
        return newEntityPredictions;
    }

    /**
     * Updates factors according to least squares on the opposing factors. This function
     * determines factors which minimize loss on `data` based on `opposing_factors`.
     * For example, if `opposing_factors` are the item factors, this function determines
     * the entity factors which minimize loss on `data`.
     * @remarks
     *  It is the responsibility of the callee to free the returned tensor's memory.
     * @param opposingFactors
     *  A `p`x`k` {@link Tensor} of the fixed factors in the optimization step (i.e.
     *  entity or item factors). Requires `p`, `k` > `0`.
     * @param data
     *  A `p`x`q` {@link Tensor} of the observed values for each of the entities/items
     *  associated with the `p` `opposing_factors` and the `q` items/entities associated
     *  with factors. Requires `p`, `q` > `0`.
     * @param alpha
     *  Weight for positive training examples such that each positive example takes
     *  value `alpha + 1`.  Requires `alpha > 0`.
     * @param regularization_coefficient
     *  Coefficient on the embedding regularization term. Requires
     *  `regularization_coefficient` > `0`.
     * @returns
     *  A Promise that resolves with a `q`x`k` array of recomputed factors which
     *  minimize error.
     */
    private async updateFactor(
        opposing_factors: Tensor,
        data: Tensor,
        alpha: number,
        regularization_coefficient: number
    ): Promise<Tensor> {

        // Assert preconditions
        const [p, k] = opposing_factors.shape;
        const q = data.shape[1];
        this.assert(0 < p);
        // this.assert(k == self.k);
        this.assert(p === data.shape[0]);
        this.assert(q === undefined || 0 < q);
        this.assert(0 < alpha);
        this.assert(0 <= regularization_coefficient);

        const V_T_C_I_V = async (V: Tensor, c_array: Tensor) => {
            const k = V.shape[1]!;
            const c_minus_i = tidy(() => c_array.squeeze().sub(1).notEqual(0));
            const nonzero_c = await whereAsync(c_minus_i);
            const nonzero_c_indices = await nonzero_c.data();

            // Free intermediate tensors from memory
            c_minus_i.dispose();
            nonzero_c.dispose();

            // Compute product
            return tidy(() => {
                let product = zeros([k, k]);
                for (const i of nonzero_c_indices) {

                    const v_i = V.slice(i, 1);
                    const square_addition = v_i.matMul(v_i, true);

                    this.assert(square_addition.shape, [k, k]);

                    product = product.add(square_addition);

                }
                return product;
            });

        };

        // In line with the paper, we'll use variables names as if we are updating user
        // factors based on V, the item factors. Since the process is the same for both,
        // the variable names are interchangeable. This makes following along with the
        // paper easier.

        const V = opposing_factors;

        const new_U: Tensor[] = [];

        // For each item embedding:
        const V_T_V = V.matMul(V, true);

        // Update each of the q user factors
        for (let i = 0; i < q!; i++) {

            const P_u = data.slice([0, i], [data.shape[0], 1]);

            // C is c if unobserved, one otherwise
            const C_u = tidy(() => tensor(alpha + 1).where(P_u.greater(0), 1));

            this.assert(C_u.shape, [p, 1])

            const confidence_scaled_V_transpose_V = await V_T_C_I_V(V, C_u);

            // X = (V^T CV + \lambda I)^{-1} V^T CP
            const inv = await this.invert(
                tidy(
                    () => V_T_V
                        .add(confidence_scaled_V_transpose_V)
                        .add(tensor(regularization_coefficient).mul(tf_eye(k)))
                ),
                true
            );

            // Removed C_u here since unnecessary in binary case.
            // P_u is already binary.
            const U_i = tidy(() => inv.matMul(V, false, true).matMul(P_u).squeeze());

            new_U.push(U_i);

            // Free intermediate tensors from memory
            inv.dispose();
            P_u.dispose();
            C_u.dispose();
            V_T_V.dispose();
            confidence_scaled_V_transpose_V.dispose();

        }

        const new_entity_factor = stack(new_U);

        // Free intermediate tensors from memory
        new_U.forEach(o => o.dispose());

        return new_entity_factor;

    }

    /**
     * Computes the multiplicative inverse of a {@link Tensor}.
     * @remarks
     *  It is the responsibility of the callee to free the returned tensor's memory.
     * @param m
     *  The {@link Tensor} to invert.
     * @param dispose
     *  If true, `m` will be disposed once the inverse is calculated.
     *  (Default: false)
     * @returns
     *  The inverted {@link Tensor}.
     */
    private async invert(m: Tensor, dispose: Boolean = false) {
        this.assert(m.shape[0] === m.shape[1]);
        const x = new NDArray(await m.data(), { shape: m.shape });
        const y = vec_eye(m.shape[0]);
        const inv = tensor(solve(x, y).toArray(), m.shape, "float32");
        if (dispose) {
            m.dispose();
        }
        return inv;
    }

}
