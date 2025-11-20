# 📊 CL-RAM Thesis Visualization - Web Interface

A specialized **Flask Web Application** designed to automate the generation of statistical visualizations for the CL-RAM Thesis. This tool allows users to upload raw test logs (CSV, JSON, or TXT) via a browser interface and automatically generates comprehensive analytical charts, heatmaps, and HTML reports.

## 🚀 Key Features

* **Web-Based Interface:** User-friendly drag-and-drop upload system running on a local server.
* **Multi-Format Support:** Accepts data in:
    * `CSV` (Structured data)
    * `JSON` (Exported logs)
    * `TXT` (Raw logs with "Model:", "Category:", "Success:" parsing logic)
* **Real-Time Progress:** Displays a progress bar and status updates while the backend generates heavy visualizations.
* **Comprehensive Analytics:** Triggers the `visualization_engine` to produce:
    * 📈 Linear Progression Charts
    * 🌡️ Temperature & Language Heatmaps
    * 📊 Comparative Bar & Pie Charts
    * 📑 Statistical Tables (CSV)
    * 📄 Auto-generated HTML Summary Report
* **Instant Access:** View generated charts and tables directly in the browser or download them.

## 🛠️ Prerequisites

To run this application, you need **Python 3.x** and the following dependencies:

```bash
pip install flask pandas matplotlib seaborn
