# Release Assets

This directory is the local destination for pretrained MW-SR model files after users download them from GitHub Releases. The large model binaries are intentionally ignored by Git, so they do not appear in this folder when browsing the repository source tree on GitHub.

Download the model artifacts from:

[MW-SR v0.1.0 model release](https://github.com/Kaitou0309/MW-SR/releases/tag/v0.1.0)

Place the downloaded files here:

```text
release_assets/bt-sr-rrdn-9rrdb-composite-ssim-a08-v0.1.0.weights.h5
release_assets/bt-sr-rrdn-9rrdb-composite-ssim-a08-v0.1.0.keras
release_assets/bt-sr-rrdn-gan-9rrdb-bn-generator-v0.1.0.weights.h5
release_assets/bt-sr-rrdn-gan-9rrdb-bn-generator-v0.1.0.keras
release_assets/SHA256SUMS.txt
```

Then verify the installation and downloaded artifacts from the repository root:

```bash
python tests/test_installation.py
```

## Selected Release Models

- MW-SR: RRDN composite-SSIM alpha 0.8, 9 RRDB blocks, 3 RDBs per RRDB, 5 convolutional layers per RDB, 64 filters.
- MW-SR-GAN: MW-SR generator refined with adversarial training using the BatchNorm discriminator.

The HPC training environment did not support the newer `.keras` format, so both selected models were originally stored as weights-only `.weights.h5` checkpoints. Keep those original checkpoints for reproducible architecture reconstruction, fine-tuning, and HPC compatibility. The corresponding `.keras` exports package each generator architecture with its weights for easier loading and prediction. Discriminator weights are not required for inference.

The `.keras` exports contain the complete Functional generator architecture, generator weights, and Keras serialization metadata. They are inference-focused and do not contain compile configuration, optimizer state, training losses or metrics, external normalization statistics, YAML metadata, the GAN discriminator, datasets, or training history. Keep the config files and `metadata/unified_global_stats.json` with the model release workflow.

## Maintainer Release Checklist

1. Commit and push the tracked source, configs, documentation, and checksum manifest.
2. From the repository root, run `(cd release_assets && shasum -a 256 -c SHA256SUMS.txt)`.
3. Create release tag `v0.1.0`, or edit that release if it already exists.
4. Upload the four model files listed in `SHA256SUMS.txt` plus the checksum manifest.
5. Confirm that the release page shows all five downloadable assets.

For a new release with GitHub CLI:

```bash
gh release create v0.1.0 \
    release_assets/*.weights.h5 \
    release_assets/*.keras \
    release_assets/SHA256SUMS.txt \
    --title "v0.1.0 - Initial model release" \
    --notes "Pretrained MW-SR and MW-SR-GAN generators in weights-only and complete Keras formats."
```

If `v0.1.0` already exists, upload or replace its model assets:

```bash
gh release upload v0.1.0 \
    release_assets/*.weights.h5 \
    release_assets/*.keras \
    release_assets/SHA256SUMS.txt \
    --clobber
```
