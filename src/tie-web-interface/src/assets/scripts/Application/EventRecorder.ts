import { SetViewFilter } from "../PredictionsView/Commands/SetViewFilter";
import { SetViewLimit } from "../PredictionsView/Commands/SetViewLimit";
import { SetViewOption } from "../PredictionsView/Commands/SetViewOption";
import type { EventStorage } from "./EventStorage";
import type { ControlCommand } from "../PredictionsView";

export class EventRecorder {

    /**
     * The recorder's event store.
     */
    private _storage: EventStorage;


    /**
     * Creates a new {@link EventRecorder}.
     * @param storage
     *  The recorder's event store.
     */
    constructor(storage: EventStorage) {
        this._storage = storage;
    }


    /**
     * Records an "add techniques" event.
     * @param method
     *  The method used to add the techniques.
     * @param techniques
     *  The techniques added.
     */
    public addTechniques(method: string, techniques: string[]) {
        // Sanitize techniques
        const sanitizedTechniques = techniques
            .filter(id => id.match(/^T[0-9]{4}(?:.[0-9]{3})?$/gi))
            .map(id => id.toLocaleUpperCase());
        // Record
        this._storage.record(
            "add_techniques",
            {
                "method": method,
                "techniques": sanitizedTechniques,
                "total_techniques": sanitizedTechniques.length
            }
        )
    }

    /**
     * Records a "technique prediction" event.
     * @param techniqueBasis
     *  The observed techniques provided for the prediction.
     * @param backend
     *  The prediction backend.
     * @param time
     *  The prediction time (in ms).
     */
    public makePrediction(techniques: string[], backend: string, time: number,) {
        this._storage.record(
            "make_prediction",
            {
                "observed_techniques": techniques,
                "total_observed_techniques": techniques.length,
                "prediction_backend": backend,
                "prediction_time": time
            }
        );
    }

    /**
     * Records an "apply view control" event.
     * @param cmd
     *  The applied control command.
     */
    public applyViewControl(cmd: ControlCommand) {
        // If view filter...
        if (cmd instanceof SetViewFilter) {
            this._storage.record(
                "apply_filter_control",
                {
                    "control": cmd.control.name,
                    "filter": cmd.filter ?? "all_filters",
                    "value": cmd.value
                }
            );
            return;
        }
        // If view option...
        if (cmd instanceof SetViewOption) {
            this._storage.record(
                "apply_organization_control",
                {
                    "control": cmd.control.name,
                    "value": cmd.value
                }
            );
            return;
        }
        // If view limit...
        if (cmd instanceof SetViewLimit) {
            this._storage.record(
                "apply_view_limit_control",
                {
                    "control": cmd.control.name,
                    "value": cmd.value
                }
            )
            return;
        }
    }

    /**
     * Records a "download file" event.
     * @param fileType
     *  The file's type.
     */
    public downloadArtifact(fileType: string) {
        this._storage.record(
            "download_file",
            {
                "file_type": fileType
            }
        )
    }

}
