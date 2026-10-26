# ESP32 CSI Analysis and Real-Time Activity Monitoring

A Python-based project for analyzing Channel State Information (CSI) captured with an ESP32. The repository contains scripts for visualizing CSI amplitude patterns, comparing variance across recorded scenarios, and monitoring incoming CSI packets in 30-second windows.

> **Status: Prototype; variance values reproduced from the included CSV files.** The three uploaded CSVs were parsed using the current `verify_variance.py` method and the reported rounded scores were reproduced. This confirms the current script's arithmetic on these files; it does not by itself validate the activity-classification thresholds or establish general detection accuracy.

## Project goals

- Capture or ingest ESP32 CSI packets and extract amplitude values.
- Visualize CSI patterns using heatmaps and selected-subcarrier plots.
- Compare recordings from an empty room, a stationary person, and a motion scenario.
- Explore a simple rule-based activity indicator from live CSI data.
- Keep processing steps and reported results documented and reproducible.

## Scenarios currently analyzed

| File | Scenario |
|---|---|
| `empty_01.csv` | Empty-room baseline |
| `stationary_01.csv` | Person present but stationary |
| `motion_04.csv` | Active motion |

The scenario labels describe the recordings. The results should not be interpreted as proof of reliable human detection until validated on additional recordings and conditions.

## Reported variance results

The values below were recomputed from the CSV files in this repository using the current `verify_variance.py` method (absolute values from each parsed 384-value packet array; NumPy population variance with `ddof=0` across packets for each subcarrier; then mean across subcarriers). For the post-L2 score, each packet row is first divided by its L2 norm.

| Dataset | Raw variance (pre-L2) | Variance after L2 normalization |
|---|---:|---:|
| `motion_04.csv` | 77.13 | 0.000601 |
| `empty_01.csv` | 68.83 | 0.000505 |
| `stationary_01.csv` | 63.69 | 0.000522 |

For that run, raw variance ranked `motion_04.csv` highest, followed by `empty_01.csv`, then `stationary_01.csv`. After normalization, the stationary-person score was slightly higher than the empty-room score.

**Reproduction check:** The current calculation reproduced the rounded figures above from the included CSVs:

| Dataset | Parsed packet arrays | Values per array | Malformed bracketed arrays |
|---|---:|---:|---:|
| `motion_04.csv` | 2,084 | 384 | 0 |
| `empty_01.csv` | 2,074 | 384 | 0 |
| `stationary_01.csv` | 2,089 | 384 | 0 |

These results verify the script's reported arithmetic on the currently uploaded data. They do **not** independently validate that the metric reliably distinguishes people or motion in other rooms or conditions. Keep pre-normalization and post-normalization metrics separate.

## Live monitor

`live_math_monitor.py` reads serial data from an ESP32 and processes packets in windows of 30 seconds.

Current settings in the script:

- Serial port: `COM8` (change this to the receiver's actual COM port)
- Baud rate: `921600`
- Processing window: `30` seconds
- Activity score: mean of per-subcarrier standard deviations after row-wise L2 normalization, multiplied by `1000`
- Outputs: a console status and PNG snapshots, including `latest_csi_summary.png`

The script expects serial lines containing a JSON array of numeric CSI values. It ignores lines that cannot be parsed as a JSON array. The first accepted array sets the expected subcarrier count for that run.

### Important distinction between metrics

The live monitor's activity score is **not the same metric** as the variance values in the table above. It uses normalized packet data and standard deviations, while the offline variance script may use a different calculation. Do not compare the live score directly with the offline variance numbers.

The current `thresholds.json` contains:

- `EMPTY_THRESHOLD`: `20.327696789838598`
- `SITTING_THRESHOLD`: `20.723424602327704`

The thresholds must be calibrated using the exact same preprocessing and score formula as the live monitor. They are preliminary until this has been confirmed against labelled recordings. This is a simple rule-based prototype, not a validated occupancy or security system.

## Repository contents

| File | Purpose |
|---|---|
| `live_math_monitor.py` | Reads serial CSI data and produces a 30-second rule-based status report |
| `calibrate_thresholds.py` | Calibration-related script; inspect its input/output assumptions before use |
| `verify_variance.py` | Calculates the current offline variance comparison |
| `plot_all.py` | Plotting script for CSI datasets |
| `plot_detailed.py` | Detailed plotting script |
| `plot_showcase.py` | Showcase plotting script |
| `thresholds.json` | Threshold values used by the live monitor |
| `variance_results.csv` | Table of reported variance values |
| `variance_method_and_results.txt` | Notes on variance method and validation |
| `motion_04.csv` | CSI recording labeled active motion |
| `empty_01.csv` | Empty-room CSI baseline recording |
| `stationary_01.csv` | CSI recording labeled stationary person |
| `BOM.csv` | Preliminary bill of materials |
| `INSTRUCTIONS.md` | Setup and usage notes |
| `*_detailed.png` | Detailed plots for individual scenarios |
| `raw_variance_comparison.png` | Comparison of pre-normalization variance |
| `l2_variance_comparison.png` | Comparison of post-normalization variance |

The analysis scripts may still require settings or dependencies specific to your local ESP32/ESP-IDF setup.

## Requirements

- ESP32 development board and compatible CSI receiver firmware
- USB data cable
- Windows computer (the example configuration uses a COM port)
- Python 3
- Python packages: `pyserial`, `numpy`, and `matplotlib`

Install the Python dependencies:

```powershell
py -m pip install pyserial numpy matplotlib
```

Use the Python version and firmware/toolchain compatible with your actual ESP32 setup. Record the exact versions before making a final reproducibility claim.

## Running the scripts

Run commands from the directory containing the relevant script and its required input files.

### 1. Verify offline variance

```powershell
py verify_variance.py
```

Make sure the three CSV files are in the location the script expects. Inspect the script if it uses hard-coded paths.

### 2. Generate plots

```powershell
py plot_all.py
```

Other plotting scripts are available for detailed or showcase views. Check their inputs and output paths before running them.

### 3. Run the live monitor

1. Connect and flash the appropriate ESP32 CSI receiver firmware.
2. Confirm the correct serial/COM port in Windows Device Manager or your serial terminal.
3. Update `SERIAL_PORT` in `live_math_monitor.py` if the port is not `COM8`.
4. Ensure the device sends parseable JSON arrays at the configured baud rate.
5. Run:

```powershell
py live_math_monitor.py
```

6. Stop the monitor with `Ctrl+C`.

The live monitor writes PNG snapshots to its current working directory. Ensure the serial port is not already open in another program.

## Recommended verification checklist

Before presenting final results:

- [ ] Verify each accepted packet contains the intended number of CSI values (expected to be 384 for the analysis described so far).
- [ ] Record valid and rejected packet counts for every CSV.
- [ ] Confirm the offline variance definition and axis. For a per-subcarrier temporal metric, calculate variance across packets for each subcarrier and average those variances, if that is the intended method.
- [ ] Document the variance convention (`ddof`) and whether absolute amplitudes or another representation is used.
- [ ] Document exactly how L2 normalization is applied and along which axis.
- [ ] Confirm the calibration script uses the same score formula and normalization as `live_math_monitor.py`.
- [ ] Test thresholds against multiple labelled recordings, not just one recording per scenario.
- [ ] Report classification errors and limitations instead of relying only on example plots.
- [ ] Re-run the analysis from the original CSV files and update the results table from verified output.

## Limitations

- The exact ESP32 board model, firmware version, CSI configuration, and capture environment still need to be documented.
- The three CSV datasets are included in this repository, allowing readers with repository access to rerun the current variance calculation. Reproducing the numbers does not establish classification accuracy; that requires held-out recordings and documented evaluation.
- Thresholds may depend on device placement, room geometry, packet rate, channel conditions, and preprocessing.
- A small number of recordings is not enough to establish general classification performance.
- This prototype should not be used for safety-critical decisions or covert monitoring.

## Privacy and data handling

Review CSI recordings before publishing them. They can reflect activity patterns in a physical space. Obtain any required consent, and do not upload Wi-Fi passwords, API keys, authentication tokens, or private configuration files.

## Bill of materials

See [`BOM.csv`](BOM.csv). The BOM is preliminary until the exact ESP32 model, connection setup, and firmware/toolchain are confirmed.

## Instructions

See [`INSTRUCTIONS.md`](INSTRUCTIONS.md) for the initial setup and workflow.

## License

No license has been selected yet. Until a license is added, others should not assume they have permission to reuse, modify, or redistribute this project.
