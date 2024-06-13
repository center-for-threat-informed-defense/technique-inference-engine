import type { NumpyShape } from "./NumpyShape";

/**
 * Result of dtype.str
 */
export type dtypeStr = string;


/**
 * Result of numpy.descr.
 */
export type dtypeDescr = ([string, dtypeDescr] | [string, string, NumpyShape?])[]


/**
 * Numpy dtype.
 * @remarks
 *  At the time of this implementation, when serializing a dtype, Numpy uses:
 *   - `dtype.str` when the dtype doesn't include names
 *   - `dtype.descr` when the dtype includes names
 *
 * Reference: https://github.com/numpy/numpy/blob/0516b05eacb5617d65c1c20748dc6c9cfd688c38/numpy/lib/format.py#L274-L298
 */
export type NumpyDtype = dtypeStr | dtypeDescr
