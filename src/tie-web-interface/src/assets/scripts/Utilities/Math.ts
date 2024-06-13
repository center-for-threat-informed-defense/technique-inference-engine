///////////////////////////////////////////////////////////////////////////////
//  1. General  ///////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////


/**
 * Bounds a number within a specified range.
 * 
 * **Example**
 * 
 * - `clamp(41, 0, 100)` returns `41`. 
 * - `clamp(-120, 0, 100)` returns `0`.
 * - `clamp(231, 0, 100)` returns `100`.
 * 
 * @param n
 *  The number to bound.
 * @param min
 *  The range's lower bound.
 * @param max
 *  The range's upper bound.
 * @returns
 *  The number's bounded value.
 */
export function clamp(n: number, min: number, max: number): number {
    return Math.min(Math.max(n, min), max);
}

/**
 * Rounds a number to the nearest multiple.
 * @param n
 *  The number to round.
 * @param multiple
 *  The multiple.
 * @returns
 *  The number rounded to the nearest multiple.
 */
export function round(n: number, multiple: number): number {
    return Math.sign(n) * Math.round(Math.abs(n) / multiple) * multiple;
}

/**
 * Checks if two floats are equal up to the specified decimal place.
 * @param a
 *  The first number to compare.
 * @param b
 *  The second number to compare.
 * @param decimals
 *  The number of decimal places.
 *  (Default: 5)
 */
export function floatEq(a: number, b: number, decimals: number = 5) {
    const m = 10 ** decimals;
    return Math.floor(a * m) === Math.floor(b * m); 
}

/**
 * Returns the unsigned modulus of a.
 * @param a
 *  The dividend.
 * @param n
 *  The divisor.
 * @returns
 *  The unsigned modulus of a.
 */
export function unsignedMod(a: number, n: number) {
    return ((a % n) + n) % n;
}


///////////////////////////////////////////////////////////////////////////////
//  2. Bit Functions  /////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////


/**
 * Generates an enum's bit mask.
 * @param obj
 *  The enum to evaluate.
 * @returns
 *  The enum's bit mask.
 */
export function generateBitMask(obj: { [key: string]: number }): number {
    let mask = 0;
    for (const bit in obj)
        mask |= obj[bit];   
    return mask;
}
