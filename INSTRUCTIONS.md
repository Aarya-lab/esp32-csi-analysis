# Instructions --- ESP32 CSI Analysis

These are starter instructions. Adapt firmware steps to the exact board
and ESP-IDF version in your setup.

## 1. Prepare hardware

1.  Connect the ESP32 using a USB data cable.
2.  Confirm the board appears as a serial/COM port.
3.  Build and flash the CSI capture firmware appropriate for your board.
4.  Keep the capture environment consistent across empty-room,
    stationary-person, and motion recordings.

## 2. Organize captures

Use clear filenames such as `empty_01.csv`, `stationary_01.csv`, and
`motion_04.csv`. Record board model, firmware/toolchain version, packet
count, capture duration, and scenario notes.

## 3. Run Python analysis

Open PowerShell in the project directory. The previously used folder
was:

``` powershell
cd C:\esp_projects\esp-csi\examples\get-started\csi_recv
```

Check Python:

``` powershell
py --version
```

Run the script when it and its input CSV files are in the expected
location:

``` powershell
py verify_variance.py
```

If your script uses different paths or arguments, follow its
configuration.

## 4. Current reported output

  Dataset                 Raw variance   Post-L2 variance
  --------------------- -------------- ------------------
  `motion_04.csv`                77.13           0.000601
  `empty_01.csv`                 68.83           0.000505
  `stationary_01.csv`            63.69           0.000522

These are preliminary console results, not independently verified
values.

## 5. Validate before final reporting

-   Confirm each accepted packet has 384 subcarrier amplitude values.
-   Record valid and rejected packet counts.
-   Confirm the variance axis and convention (`ddof`).
-   Document exactly how and along which axis L2 normalization is
    applied.
-   Run the same preprocessing on all datasets.
-   Keep pre-L2 and post-L2 scores separate.

For a common per-subcarrier temporal metric, calculate variance across
packets for each subcarrier and average those variances. Use this only
if it matches the intended method in your script.

## 6. Generate plots

Use your available plotting script to create heatmaps and subcarrier
traces. Keep axes and scales comparable, label raw versus normalized
data, and save figures in a `results/` folder.

## 7. Upload safely

Upload the README, instructions, BOM, analysis scripts, and useful
plots. Exclude credentials, secrets, unnecessary build files, and data
that you are not allowed to publish. Suggested commit message:
`Add CSI analysis documentation and results`.

## 8. Details to complete

-   ESP32 board/model: TODO
-   ESP-IDF and firmware version: TODO
-   CSI configuration: TODO
-   Python and package versions: TODO
-   CSV schema and packet counts: TODO
-   Exact variance and normalization implementation: TODO
-   Project license: TODO
