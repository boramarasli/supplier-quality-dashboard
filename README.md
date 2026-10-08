# Supplier Quality & Delivery Dashboard

Aug – Sep 2025 · TU Berlin, team of three · Python · pandas · Dash · Plotly

Which suppliers deliver on time and which ones ship parts that fail. Interactive dashboard over an OEM's manufacturing data, for comparing suppliers month by month on market share, failing parts and delivery gaps.

TU Berlin, Introduction to Data Analytics case study.

**My part:** I led the data pipeline, parsing and joining six manufacturing datasets that didn't line up into one table of 7.9 million rows, and built the dashboard.

<!-- SCREENSHOT GOES HERE. Run the app, screenshot the browser, save as docs/dashboard.png,
     then delete these comment markers:
![Dashboard](docs/dashboard.png)
-->

## The data

Six separate datasets, none of them lining up: parts, vehicles, components, registrations, logistics delays, plant geodata. Semicolon-separated, inconsistently quoted, mixed `.csv` and `.txt`, IDs and dates that didn't match across files.

Most of the work was here, not in the charts.

`pipeline/` runs it in five stages:

| | |
|---|---|
| `step1_vehicle_bom.py` | vehicle bill of materials — which components went into which vehicle |
| `step2_registration.py` | join registrations so each vehicle has a market entry date |
| `step3_parts_sample.py` | parse the parts files, link each part to its manufacturer |
| `step4_final_assembly.py` | assemble into one table, derive component categories |
| `step5_fix_delivery_data.py` | recompute missing delivery days from production dates |

Output is one table, 7.9 million rows, 1.08 GB.

`check_data.py` and `file_inspector.py` are the diagnostic scripts from working out what was actually inside the source files. Kept them because that was most of the job.

## The dashboard

- **Market share** — one supplier against competitors, month by month, absolute or percentage
- **Defect frequency** — which component categories fail most and whose they were
- **JIT delivery** — days between component production and vehicle build, over a date range you pick
- Everything filters by component category

## Data isn't in this repo

The source datasets and the assembled table aren't here. They're course material and not mine to publish, and the 1.08 GB file is far over GitHub's limit anyway.

So the app won't start from a fresh clone — it expects `Final_dataset_group_09.csv` in the root. The code is here to be read.

## Run, with the data in place

```bash
pip install -r requirements.txt
python app.py
# http://127.0.0.1:8050
```

Python, pandas, NumPy, Dash, Plotly.

## Credits

Group project. See [CONTRIBUTIONS.md](CONTRIBUTIONS.md).

---

Bora Marasli · Information Technology in Mechanical Engineering, TU Berlin · [LinkedIn](https://www.linkedin.com/in/boramarasli) · [More projects](https://github.com/boramarasli)
