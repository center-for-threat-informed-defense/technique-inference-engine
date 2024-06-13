/**
 * Valid decoding strategies.
 */
export enum DecodeStrategy {
    Byte,
    MultiByte,
    Unicode
}

/**
 * Array type descriptor base.
 */
export interface DescriptorBase<T extends DecodeStrategy> {

    /**
     * The array's decode strategy.
     */
    decodeStrategy: T;

}

/**
 * Array type descriptor for single-byte elements.
 */
export interface ByteArray extends DescriptorBase<DecodeStrategy.Byte> {

    /**
     * The constructor of the typed array that will define the tensor.
     */
    tensorType: typeof Int32Array;

    /**
     * The tensor's dtype.
     */
    tensorDtype
    : "int32";

    /**
     * The array's setter method.
     */
    setter: "setInt32";

    /**
     * The array's getter method.
     */
    getter: "getInt8" | "getUint8";

    /**
     * Each array element's size (in bytes).
     */
    size: 1;

    /**
     * Each array element's tensor size (in bytes).
     */
    tensorSize: 4;

}

/**
 * Array type descriptor for multi-byte elements.
 */
export interface MultiByteArray extends DescriptorBase<DecodeStrategy.MultiByte> {

    /**
     * The constructor of the typed array that will define the tensor.
     */
    tensorType
    : typeof Int32Array
    | typeof Float32Array;

    /**
     * The tensor's dtype.
     */
    tensorDtype
    : "int32"
    | "float32";

    /**
     * The array's setter method.
     */
    setter
    : "setInt32"
    | "setFloat32";

    /**
     * The array's getter method.
     */
    getter
    : "getUint16"
    | "getInt16"
    | "getInt32"
    | "getFloat32";

    /**
     * Each array element's size (in bytes).
     */
    size: 2 | 4;

    /**
     * Each array element's tensor size (in bytes).
     */
    tensorSize: 4,

    /**
     * The array's little endianness.
     */
    littleEndian: boolean;

}


/**
 * Array type descriptor for BigInt elements.
 */
export interface UnicodeArray extends DescriptorBase<DecodeStrategy.Unicode> {

    /**
     * Each array element's size (in bytes).
     */
    size: number;

    /**
     * The array's little endianness.
     */
    littleEndian?: boolean;

}

/**
 * Array type descriptor.
 */
export type ArrayTypeDescriptor
    = ByteArray | MultiByteArray | UnicodeArray;


/**
 * Decodes a dtype to an {@link ArrayTypeDescriptor}.
 * @param dtype
 *  The dtype to decode.
 * @returns
 *  An {@link ArrayTypeDescriptor} that represents the dtype.
 */
export function decodeArrayTypeDescriptor(dtype: string): ArrayTypeDescriptor {
    const dtypeTokens = /(<|>|\|)(.*?)(\d+)/g.exec(dtype)?.slice(1);
    if (dtypeTokens === undefined) {
        throw new Error(`Invalid dtype: '${dtype}'.`);
    }
    const [endianness, type, size] = dtypeTokens;
    // Decode endianness
    let littleEndian = false;
    switch (endianness) {
        case "<":
            littleEndian = true;
            break;
        case ">":
            littleEndian = false;
            break;
    }
    // Decode array type
    switch (type) {
        case "b":
            return {
                decodeStrategy: DecodeStrategy.Byte,
                tensorType: Int32Array,
                tensorDtype: "int32",
                setter: "setInt32",
                getter: "getInt8",
                size: 1,
                tensorSize: 4
            }
        case "B":
            return {
                decodeStrategy: DecodeStrategy.Byte,
                tensorType: Int32Array,
                tensorDtype: "int32",
                setter: "setInt32",
                getter: "getUint8",
                size: 1,
                tensorSize: 4
            }
        case "i":
            switch (size) {
                case "1":
                    return {
                        decodeStrategy: DecodeStrategy.Byte,
                        tensorType: Int32Array,
                        tensorDtype: "int32",
                        setter: "setInt32",
                        getter: "getInt8",
                        size: 1,
                        tensorSize: 4
                    }
                case "2":
                    return {
                        decodeStrategy: DecodeStrategy.MultiByte,
                        tensorType: Int32Array,
                        tensorDtype: "int32",
                        setter: "setInt32",
                        getter: "getInt16",
                        size: 2,
                        tensorSize: 4,
                        littleEndian
                    }
                case "4":
                    return {
                        decodeStrategy: DecodeStrategy.MultiByte,
                        tensorType: Int32Array,
                        tensorDtype: "int32",
                        setter: "setInt32",
                        getter: "getInt32",
                        size: 4,
                        tensorSize: 4,
                        littleEndian
                    }
                default:
                    throw new Error(`Unsupported dtype: '${dtype}'`)
            }
        case "u":
            switch (size) {
                case "1":
                    return {
                        decodeStrategy: DecodeStrategy.Byte,
                        tensorType: Int32Array,
                        tensorDtype: "int32",
                        setter: "setInt32",
                        getter: "getUint8",
                        size: 1,
                        tensorSize: 4
                    }
                case "2":
                    return {
                        decodeStrategy: DecodeStrategy.MultiByte,
                        tensorType: Int32Array,
                        tensorDtype: "int32",
                        setter: "setInt32",
                        getter: "getUint16",
                        size: 2,
                        tensorSize: 4,
                        littleEndian
                    }
                default:
                    throw new Error(`Unsupported dtype: '${dtype}'`)
            }
        case "f":
            switch (size) {
                case "4":
                    return {
                        decodeStrategy: DecodeStrategy.MultiByte,
                        tensorType: Float32Array,
                        tensorDtype: "float32",
                        setter: "setFloat32",
                        getter: "getFloat32",
                        size: 4,
                        tensorSize: 4,
                        littleEndian
                    }
                case "8":
                    console.warn("Warning! Casting dtype from 'f8' to 'f4'.")
                    return {
                        decodeStrategy: DecodeStrategy.MultiByte,
                        tensorType: Float32Array,
                        tensorDtype: "float32",
                        setter: "setFloat32",
                        getter: "getFloat64" as any,
                        size: 8 as any,
                        tensorSize: 4,
                        littleEndian
                    }
                default:
                    throw new Error(`Unsupported dtype: '${dtype}'`)
            }
        case "U":
            return {
                decodeStrategy: DecodeStrategy.Unicode,
                size: parseInt(size),
                littleEndian
            }
        default:
            throw new Error(`Unsupported dtype: '${dtype}'`)
    }
}
