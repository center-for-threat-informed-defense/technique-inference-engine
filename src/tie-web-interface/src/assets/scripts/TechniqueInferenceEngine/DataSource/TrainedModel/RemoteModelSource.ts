import { NpzFile } from "../../Numpy";
import { Tensor } from "@tensorflow/tfjs";
import { ModelSource } from "./ModelSource";
import { ManagedModel } from "./ManagedModel";

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
     * The name of the exported technique ids.
     */
    private static EXPORTED_IDS_NAME = "technique_ids";

    /**
     * The name of the exported hyperparameters.
     */
    private static EXPORTED_PARAMS_NAME = "hyperparameters";


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
        this._url = `${import.meta.env.BASE_URL}${url}`;
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
                const err = `Cannot locate 'U' in NPZ file at '${this._url}'.`;
                throw new Error(err)
            }
            if (!npzFile.tensors.has(RemoteModelSource.EXPORTED_V_NAME)) {
                const err = `Cannot locate 'V' in NPZ file at '${this._url}'.`;
                throw new Error(err);
            }
            if (!npzFile.tensors.has(RemoteModelSource.EXPORTED_IDS_NAME)) {
                const err = `Cannot locate technique ids in NPZ file at '${this._url}'.`;
                throw new Error(err);
            }
            if (!npzFile.tensors.has(RemoteModelSource.EXPORTED_PARAMS_NAME)) {
                const err = `Cannot locate hyperparameters in NPZ file at '${this._url}'.`;
                throw new Error(err);
            }
            // Parse U component
            const u = npzFile.tensors.get(RemoteModelSource.EXPORTED_U_NAME)!;
            if (!(u instanceof Tensor) || u.dtype !== "float32") {
                throw new Error("Expected 'U' to be of type 'float32'.");
            }
            const U = u.clone();
            // Parse V component
            const v = npzFile.tensors.get(RemoteModelSource.EXPORTED_V_NAME)!;
            if (!(v instanceof Tensor) || v.dtype !== "float32") {
                throw new Error("Expected 'V' to be of type 'float32'.");
            }
            const V = v.clone();
            // Parse Technique IDs
            const IDs = npzFile.tensors.get(RemoteModelSource.EXPORTED_IDS_NAME)!;
            if (!(IDs instanceof Tensor) || IDs.dtype !== "string") {
                throw new Error("Expected technique ids to be of type 'string'.");
            }
            const T = new Map<string, number>();
            const ids = IDs.dataSync() as any as string[];
            for (let i = 0; i < ids.length; i++) {
                T.set(ids[i], i);
            }
            // Parse Hyperparameters
            const H = npzFile.tensors.get(RemoteModelSource.EXPORTED_PARAMS_NAME)!;
            if ((H instanceof Tensor) || H.length !== 1) {
                throw new Error("Expected hyperparameters to be a fielded tensor.");
            }
            const [C, RC] = ["c", "regularization_coefficient"].map(
                key => {
                    const v = H[0][key];
                    if (v instanceof Tensor && v.dtype === "float32" && v.size === 1) {
                        return v.dataSync()[0];
                    } else {
                        throw new Error(
                            `Expected '${key}' to be of type 'float32' with one value.`
                        )
                    }
                }
            );
            // Dispose of NPZ File
            npzFile.dispose();
            // Create trained model
            return this.newModel(T, U, V, C, RC);
        } else {
            throw new Error(`Failed to fetch '${this._url}'. [Status: ${file.status}]`);
        }

    }

}
