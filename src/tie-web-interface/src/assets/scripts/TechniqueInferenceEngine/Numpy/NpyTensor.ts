import type { Tensor } from "@tensorflow/tfjs";
import type { FieldedTensor } from "./FieldedTensor";

/**
 * NPY File Tensor.
 */
export type NpyTensor = Tensor | FieldedTensor;
