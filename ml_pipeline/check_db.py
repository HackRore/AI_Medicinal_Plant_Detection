"""
Quick DB sanity check for Plant rows.
"""

import sqlite3


def main() -> None:
    db_path = "backend/medicinal_plants.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    tables = [r[0] for r in cur.execute('SELECT name FROM sqlite_master WHERE type="table"').fetchall()]
    print("tables:", tables)

    rows = cur.execute(
        "SELECT id, species_name, common_name_en FROM plants WHERE species_name=? LIMIT 5",
        ("Ginger",),
    ).fetchall()
    print("Ginger rows:", rows)


if __name__ == "__main__":
    main()

