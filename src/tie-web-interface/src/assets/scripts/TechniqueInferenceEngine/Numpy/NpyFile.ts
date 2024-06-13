import { Tensor, tensor } from "@tensorflow/tfjs";
import { DecodeStrategy, decodeArrayTypeDescriptor } from "./ArrayTypeDescriptor";
import { FieldedTensor, type TensorField } from "./FieldedTensor";
import type { dtypeDescr } from "./NumpyDtype";
import type { NpyTensor } from "./NpyTensor";
import type { NpyFileHeader } from "./NpyFileHeader";
import type { NumpyShape } from "./NumpyShape";

export class NpyFile {

    /**
     * A NPY File's magic string. ('x93NUMPY').
     */
    public static NPY_MAGIC_STRING = new Uint8Array(
        [0x93, 0x4E, 0x55, 0x4D, 0x50, 0x59]
    )


    /**
     * The raw contents of the NPY file.
     */
    public readonly buffer: ArrayBuffer;

    /**
     * The raw content's data view.
     */
    private readonly _bufferView: DataView;


    /**
     * Whether the file is a NPY file or not.
     */
    public get fileIsNpy(): boolean {
        for (let i = 0; i < NpyFile.NPY_MAGIC_STRING.length; i++) {
            if (this._bufferView.getUint8(i) !== NpyFile.NPY_MAGIC_STRING[i]) {
                return false;
            }
        }
        return true;
    }

    /**
     * The file's major version.
     */
    public get fileMajorVersion(): number {
        const offset = NpyFile.NPY_MAGIC_STRING.length;
        return this._bufferView.getUint8(offset);
    }

    /**
     * The file's minor version.
     */
    public get fileMinorVersion(): number {
        const offset = NpyFile.NPY_MAGIC_STRING.length + 1;
        return this._bufferView.getUint8(offset);
    }

    /**
     * The file's header size.
     */
    public get fileHeaderSize(): number {
        const offset = NpyFile.NPY_MAGIC_STRING.length + 2;
        return this._bufferView.getUint16(offset, true);
    }

    /**
     * The file's header information.
     */
    public get fileHeader(): NpyFileHeader {
        const offsetBeg = 10;
        const offsetEnd = offsetBeg + this.fileHeaderSize;
        const bytes = this.buffer.slice(offsetBeg, offsetEnd);
        const serializedHeader = new TextDecoder("utf-8").decode(bytes)
            .trim()
            .replace(/'/g, '"')
            .replace(/\(/g, "[")
            .replace(/\)/g, "]")
            .replace(/(?<=\[\d+),\s*?(?=\])/g, "")
            // Assumes dtype names don't include ',}'
            .replace(/,\s*?(?=\})/g, " ")
            .replace(/(?<="fortran_order":)(.*?),/g, a => a.toLocaleLowerCase());
        return JSON.parse(serializedHeader) as NpyFileHeader;
    }

    /**
     * The file's contents.
     * @remarks
     *  It is the responsibility of the callee to free the returned tensor.
     */
    public get fileContents(): NpyTensor {
        const header = this.fileHeader;
        let offset = 10 + this.fileHeaderSize;
        if (typeof header.descr === "string") {
            return this.decodeTensor(offset, header.descr, header.shape);
        } else {
            type DecodeFromDescr = (d: dtypeDescr, o: number) => [TensorField, number];
            const decodeFromDescr: DecodeFromDescr = (d: dtypeDescr, o: number) => {
                const obj: TensorField = {};
                for (const col of d) {
                    if (Array.isArray(col[1])) {
                        [obj[col[0]], o] = decodeFromDescr(col[1], o);
                    } else {
                        obj[col[0]] = this.decodeTensor(o, col[1], col[2]);
                        o += NpyFile.getByteLength(col[1], col[2]);
                    }
                }
                return [obj, o];
            }
            const value = new Array<TensorField>(header.shape.reduce((a, b) => a * b));
            for (let i = 0; i < value.length; i++) {
                [value[i], offset] = decodeFromDescr(header.descr, offset);
            }
            return new FieldedTensor(value, header.shape);
        }
    }


    /**
     * Creates a new {@link NpyFile}.
     * @remarks
     *  Implementation follows NPY File Format Spec:
     *  https://github.com/numpy/numpy/blob/main/doc/neps/nep-0001-npy-format.rst
     * @param contents
     *  The contents of the NPY file.
     */
    private constructor(contents: ArrayBuffer) {
        // Build content view
        this.buffer = contents;
        this._bufferView = new DataView(this.buffer);
        // Validate file
        if (!this.fileIsNpy) {
            throw new Error("Provided file is not a NPY file.");
        }
    }


    /**
     * Creates a new {@link NpyFile} from a {@link Blob}.
     * @param blob
     *  A blob containing an NPY file.
     * @returns
     *  A Promise that resolves with the {@link NpyFile}.
     */
    public static async fromBlob(blob: Blob): Promise<NpyFile> {
        return NpyFile.fromArrayBuffer(await blob.arrayBuffer());
    }

    /**
     * Creates a new {@link NpyFile} from an {@link ArrayBuffer}.
     * @param buffer
     *  An array buffer containing an NPY file.
     * @returns
     *  A {@link NpyFile}.
     */
    public static fromArrayBuffer(buffer: ArrayBuffer): NpyFile {
        return new NpyFile(buffer);
    }

    /**
     * Decodes a numpy array from the file to a {@link Tensor}.
     * @param dtype
     *  The array's dtype.
     * @param shape
     *  The array's shape.
     * @param offset
     *  The array's offset in the file.
     * @returns
     *  The numpy array as a {@link Tensor}.
     */
    private decodeTensor(offset: number, dtype: string, shape?: NumpyShape): Tensor {
        const length = (shape ? shape.reduce((a, b) => a * b) : 1);
        const desc = decodeArrayTypeDescriptor(dtype);
        let buffer, getter, setter, decodedArray;
        switch (desc.decodeStrategy) {
            case DecodeStrategy.Byte:
                buffer = this.buffer.slice(offset, offset + length);
                return tensor(new desc.tensorType(buffer), shape, desc.tensorDtype);
            case DecodeStrategy.MultiByte:
                buffer = new ArrayBuffer(length * desc.tensorSize);
                setter = DataView.prototype[desc.setter].bind(new DataView(buffer));
                getter = DataView.prototype[desc.getter].bind(this._bufferView);
                for (let i = 0, value; i < length; i++) {
                    value = getter(offset + (i * desc.size), desc.littleEndian);
                    setter(i * desc.tensorSize, value, true);
                }
                return tensor(new desc.tensorType(buffer), shape, desc.tensorDtype);
            case DecodeStrategy.Unicode:
                decodedArray = [];
                for (let i = 0, o1, o2, str, size = 4 * desc.size; i < length; i++) {
                    o1 = offset + (i * size);
                    o2 = o1 + size;
                    str = "";
                    for (let c; o1 < o2; o1 += 4) {
                        c = this._bufferView.getUint32(o1, desc.littleEndian);
                        if (c === 0) {
                            break;
                        }
                        str += String.fromCodePoint(c)
                    }
                    decodedArray.push(str);
                }
                return tensor(decodedArray, shape, "string");
        }
    }

    /**
     * Gets the length of a numpy array (in bytes) given its dtype and shape.
     * @param dtype
     *  The numpy array's dtype.
     * @param shape
     *  The numpy array's shape.
     * @returns
     *  The length of the numpy array in bytes.
     */
    private static getByteLength(dtype: string, shape?: NumpyShape): number {
        const desc = decodeArrayTypeDescriptor(dtype);
        const length = (shape ? shape.reduce((a, b) => a * b) : 1) * desc.size;
        if (desc.decodeStrategy === DecodeStrategy.Unicode) {
            return length * 4;
        } else {
            return length;
        }
    }

}
