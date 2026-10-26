# ESP32 CSI Analysis

This project organizes Channel State Information (CSI) capture and
analysis using an ESP32, including plots and variance comparisons for
three scenarios.

## Scenarios

-   `motion_04.csv` --- active motion
-   `empty_01.csv` --- empty-room baseline
-   `stationary_01.csv` --- stationary person

## Reported results (preliminary)

These values are copied from the local `verify_variance.py` output and
have **not** been independently reproduced from the raw CSV files.

  Dataset                 Raw variance (pre-L2)   Post-L2 variance
  --------------------- ----------------------- ------------------
  `motion_04.csv`                         77.13           0.000601
  `empty_01.csv`                          68.83           0.000505
  `stationary_01.csv`                     63.69           0.000522

Raw variance ordering: motion \> empty room \> stationary person.
Post-L2 ordering: motion \> stationary person \> empty room.

## Suggested repository structure

``` text
esp32-csi-analysis/
├── README.md
├── INSTRUCTIONS.md
├── BOM.csv
├── verify_variance.py
├── plot_csi.py                 # if available
└── results/                    # charts and figures
```

## Method overview

1.  Collect CSI packets using firmware compatible with the ESP32 board.
2.  Parse valid packet records and extract amplitude values.
3.  Check that each accepted packet has the expected 384 subcarrier
    values.
4.  Build a packet-by-subcarrier matrix.
5.  Calculate variance using a documented, consistent method.
6.  Generate heatmaps, selected-subcarrier traces, and comparison
    charts.

A recommended per-subcarrier temporal variance method is to calculate
variance across packets for each subcarrier, then average the 384
variances. Confirm this matches your script before reporting it as the
method used.

## Requirements

-   Compatible ESP32 development board and USB data cable
-   Computer and appropriate ESP-IDF/toolchain for the firmware
-   Python and the packages required by the scripts
-   CSI CSV files

## Limitations

Board model, firmware/toolchain version, exact CSV schema, Python
package versions, and normalization implementation still need to be
documented. Do not publish passwords, credentials, private
configuration, or data you lack permission to share.

## License

No license has been selected. Until one is added, do not assume others
have permission to reuse this project.
