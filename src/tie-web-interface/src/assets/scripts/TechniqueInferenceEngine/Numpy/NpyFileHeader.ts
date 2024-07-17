import type { NumpyDtype } from "./NumpyDtype";
import type { NumpyShape } from "./NumpyShape";

/**
 * NPY File Header.
 */
export type NpyFileHeader = {

    /**
     * An object that can be passed as an argument to the numpy.dtype() constructor to
     * create the array's dtype.
     */
    descr: NumpyDtype;

    /**
     * Whether the array data is Fortran-contiguous or not.
     */
    fortran_order: boolean;

    /**
     * The shape of the array.
     */
    shape: NumpyShape;

}
