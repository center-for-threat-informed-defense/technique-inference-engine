import { BlobReader, BlobWriter, ZipReader } from "@zip.js/zip.js";
import { NpyFile } from "./NpyFile";
import type { NpyTensor } from "./NpyTensor";

export class NpzFile {

    /**
     * The {@link NpzFile}'s tensors.
     */
    public readonly tensors: ReadonlyMap<string, NpyTensor>;


    /**
     * Creates a new {@link NpzFile}.
     * @param tensors
     *  The {@link NpzFile}'s tensors.
     */
    private constructor(tensors: ReadonlyMap<string, NpyTensor>) {
        this.tensors = tensors;
    }


    /**
     * Creates a new {@link NpzFile} from a {@link Blob}.
     * @param file
     *  A blob containing an NPZ file.
     * @returns
     *  A Promise that resolves with the {@link NpzFile}.
     */
    public static async fromBlob(file: Blob): Promise<NpzFile> {
        const tensors = new Map<string, NpyTensor>();
        // Decompress NPZ File
        for await (const npyFile of this.iterateZipContents(file)) {
            try {
                const name = npyFile.filename.replace(/\.npy$/, "")
                const tensor = NpyFile.fromArrayBuffer(npyFile.contents).fileContents;
                tensors.set(name, tensor);
            } catch (ex: any) {
                const name = npyFile.filename;
                const msg = ex.message;
                throw new Error(`Failed to decode NPZ entry '${name}': ${msg}'`);
            }
        }
        return new NpzFile(tensors);
    }

    /**
     * Disposes all Tensors contained within the {@link NpzFile}.
     */
    public dispose() {
        for (const tensor of this.tensors.values()) {
            tensor.dispose();
        }
    }

    /**
     * Iterates over the contents of a zip File.
     * @param blob
     *  A blob contain a zip file.
     * @returns
     *  An asynchronous generator that iterates over the contents of the zip file.
     */
    private static async *iterateZipContents(blob: Blob): AsyncGenerator<ZipEntry> {
        const reader = new ZipReader(new BlobReader(blob));
        for await (const entry of reader.getEntriesGenerator()) {
            if (!entry.getData) {
                throw new Error(
                    `File entry '${entry.filename}' has no getData() method.`
                );
            }
            const uncompressedBlob = (await entry.getData(new BlobWriter()))
            yield {
                filename: entry.filename,
                contents: await uncompressedBlob.arrayBuffer()
            }
        }
    }

}

type ZipEntry = {

    /**
     * The entry's file name.
     */
    filename: string,

    /**
     * The entry's contents.
     */
    contents: ArrayBuffer

}
