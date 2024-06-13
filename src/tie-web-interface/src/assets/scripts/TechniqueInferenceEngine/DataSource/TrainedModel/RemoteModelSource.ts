import { NpzFile } from "../../Numpy";
import { ModelSource } from "./ModelSource";
import { ManagedModel } from "./ManagedModel";
import { Tensor, tensor } from "@tensorflow/tfjs";

export class RemoteModelSource extends ModelSource {

    /**
     * The name of the exported U component.
     */
    private static EXPORTED_U_NAME = "U";

    /**
     * The name of the exported V component.
     */
    private static EXPORTED_V_NAME = "V";


    /**
     * The url of the model's NPZ file.
     */
    private _url: string;


    /**
     * Creates a new {@link RemoteModelSource}.
     * @param url
     *  The url of the model's NPZ file.
     * @param enableCaching
     *  Whether the source should cache the model after it's retrieved.
     *  (Default: false)
     */
    constructor(url: string, enableCaching?: boolean) {
        super(enableCaching);
        this._url = url;
    }


    /**
     * Returns the {@link Model} from its source.
     * @returns
     *  A Promise that resolves with the {@link Model}.
     */
    public async getDataFromSource(): Promise<ManagedModel> {
        const file = await fetch(this._url);
        if (file.status === 200) {
            const npzFile = await NpzFile.fromBlob(await file.blob());
            if (!npzFile.tensors.has(RemoteModelSource.EXPORTED_U_NAME)) {
                throw new Error(`Cannot locate 'U' in NPZ file at '${this._url}'.`)
            }
            if (!npzFile.tensors.has(RemoteModelSource.EXPORTED_V_NAME)) {
                throw new Error(`Cannot locate 'V' in NPZ file at '${this._url}'.`)
            }
            // Parse U component
            const U = npzFile.tensors.get(RemoteModelSource.EXPORTED_U_NAME)!;
            if (!(U instanceof Tensor) || U.dtype !== "float32") {
                throw new Error("Expected 'U' to be of type 'float32'.");
            }
            // Parse V component
            const v = npzFile.tensors.get(RemoteModelSource.EXPORTED_V_NAME)!;
            if (!(v instanceof Tensor) || v.dtype !== "string") {
                throw new Error("Expected 'V' to be of type 'string'.");
            }
            if (v.shape.length !== 2) {
                throw new Error("Expected 'V' to be 2-dimensional matrix.");
            }
            // Separate header from data
            const data = v.dataSync() as any as string[];
            const f32 = new Float32Array(v.shape[0] * (v.shape[1] - 1));
            const T = new Map<string, number>();
            const V = tensor(f32, [v.shape[0], v.shape[1] - 1], "float32");
            for (let i = 0, j = 0; i < data.length; i++) {
                if (i % v.shape[1] === 0) {
                    T.set(data[i], j++)
                } else {
                    f32[i - j] = parseFloat(data[i])
                }
            }
            // Free intermediate tensors from memory
            v.dispose();
            // Create trained model
            return this.newModel(T, U, V);
        } else {
            throw new Error(`Failed to fetch '${this._url}'. [Status: ${file.status}]`);
        }

    }

}
