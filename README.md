# Inventory Optimization Demo (9-Box + EOQ + Safety Stock + Reorder Point)

A **GitHub-safe** demo project for spare parts inventory optimization:

- **ABC** (value-based Pareto) classification  
- **LMH** demand variability using **VOD = std / mean**  
- **9-Box** = ABC × LMH  
- Service level policy by 9-box  
- Safety Stock, Reorder Point (ROP), EOQ  
- A small **Flask dashboard** reading **sample CSVs** (no DB credentials)

✅ No DB host/user/password is stored in this repo.  
✅ SQL is provided only as **templates** with placeholders.

---

## Quickstart

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python scripts/build_demo_data.py
python app.py
```


---

## Safe DB integration pattern (later)

- Put the connection string only in environment variables (e.g., `DB_URL`)
- Keep SQL as templates
- Never commit `.env` (already ignored)

