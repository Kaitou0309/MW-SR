# Tomorrow.io Qualitative Examples

This folder contains compact Tomorrow.io-style HDF5 examples for public inference and plotting demonstrations.

These files are intended for qualitative model-use examples only. They are not part of the paired AMSR2 LR/HR training dataset and should not be used to report quantitative reconstruction metrics unless an aligned high-resolution target is available.

Expected inference field:

```text
bt    brightness temperature input, Kelvin
```

Some files may also include geolocation variables such as latitude and longitude. The plotting scripts use those variables automatically when their shape is compatible with the prediction grid.

Before public release, confirm that redistribution of these example files is allowed under the applicable Tomorrow.io data-access or collaboration terms.
