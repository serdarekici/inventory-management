from __future__ import annotations

import os
import pandas as pd
from flask import Flask, render_template, abort

APP_PORT = int(os.getenv("PORT", "5011"))
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "sample")

def load_frames():
    inv_params = pd.read_csv(os.path.join(DATA_DIR, "inventory_params.csv"), dtype={"PartNum": str})
    rec = pd.read_csv(os.path.join(DATA_DIR, "recommendations.csv"), dtype={"PartNum": str})
    sales = pd.read_csv(os.path.join(DATA_DIR, "sales.csv"), dtype={"PartNum": str})
    return inv_params, rec, sales

inv_params_df, rec_df, sales_df = load_frames()

@app.route("/")
def index():
    current_val = float((inv_params_df["OnHandQty"] * inv_params_df["UnitCost"]).sum())
    orders_total = float(rec_df.loc[rec_df["Action"] == "Order", "ChangeValue"].sum())
    reduce_total = float(rec_df.loc[rec_df["Action"] == "Reduce Stock", "ChangeValue"].sum())
    projected_val = current_val + orders_total - reduce_total

    category_counts = inv_params_df["Category"].value_counts().to_dict()
    nine_counts = inv_params_df["9_box"].value_counts().to_dict()
    agg = rec_df.groupby(["Action","Category"]).size().reset_index(name="Count").to_dict("records")

    return render_template(
        "index.html",
        summary=dict(
            current_inventory_value=current_val,
            projected_inventory_value=projected_val,
            orders_total=orders_total,
            reduce_total=reduce_total,
            category_counts=category_counts,
            nine_box_counts=nine_counts,
        ),
        aggregated=agg,
        recommendations=rec_df.sort_values(["Action","ChangeValue"], ascending=[True, False]).head(200).to_dict("records"),
    )

@app.route("/part/<part_num>")
def part(part_num: str):
    row = inv_params_df[inv_params_df["PartNum"] == part_num]
    if row.empty:
        abort(404)
    part_dict = row.iloc[0].to_dict()
    rec_row = rec_df[rec_df["PartNum"] == part_num]
    rec_dict = rec_row.iloc[0].to_dict() if not rec_row.empty else None
    return render_template("part.html", part=part_dict, rec=rec_dict)

if __name__ == "__main__":
    app.run(debug=True, port=APP_PORT)
