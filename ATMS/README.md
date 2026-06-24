# ATMS Qualitative Examples

This folder contains compact ATMS HDF5 examples for public inference and plotting demonstrations.

These files are intended to help users test the released model workflow on ATMS-style brightness-temperature inputs. They are not the paired AMSR2 LR/HR training dataset and should not be used to report quantitative reconstruction metrics unless an aligned high-resolution target is available.

Expected inference field:

```text
bt    brightness temperature input, Kelvin
```

Some files may also include geolocation variables such as latitude and longitude. The plotting scripts use those variables automatically when their shape is compatible with the prediction grid.
