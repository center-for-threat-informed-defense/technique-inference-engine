# Updating ATT&CK in Technique Inference Engine

## Prerequisites

Run commands from the repository root, with Python 3.11, Poetry dependencies, and npm dependencies installed.

## Instructions

Complete these steps in the provided order to update ATT&CK for TIE.

1. Add the new version to the domain lists in `src/tie-web-interface/build_tools/download_sources.cjs`.
1. Update `src/tie-web-interface/build_tools/update_enrichment_file.cjs` to use the new version.

    ```js
    updateEnrichmentFile(ENRICHMENT_FILE, "enterprise", "NEW.VERSION");
    ```

1. Run the `update-enrichment` script.

    ```bash
    cd src/tie-web-interface
    npm run update-enrichment
    cd ../../
    ```

1. Update `data/stix/enterprise-attack.json`. Simply copy the new version from [attack-stix-data / enterprise-attack](https://github.com/mitre-attack/attack-stix-data/tree/master/enterprise-attack).

1. Migrate attack datasets.

    ```bash
    # Migrate the full-frequency dataset.
    poetry run python scripts/migrate_attack_datasets.py \
    --attack-data data/stix/enterprise-attack.json \
    --full-frequency data/combined_dataset_full_frequency.json \
    --output data/combined_dataset_full_frequency.next.json
    ```

    ```bash
    # Then regenerate the parent-only dataset.
    poetry run python scripts/create_parent_only_dataset.py \
    --full-frequency data/combined_dataset_full_frequency.next.json \
    --parent-only data/combined_dataset_parent_only.next.json
    ```

    Review both generated datasets, then replace the originals with the .next.json files.

1. Update `README.md` and `src/tie-web-interface/src/views/AboutView.vue` to reference the new version and metrics.
    * To get updated metrics, run `python3 scripts/dataset_metrics.py`. This depends on previous steps.

1. Rebuild the model. This may take several minutes.

    ```bash
    cd src/tie-web-interface
    npm run build-model
    ```

    When finished, `src/tie-web-interface/public/app.trained.model.zip` will be updated.

1. Check that the website compiles.

    ```bash
    npm run build
    ```
