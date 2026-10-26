"""Audit published D-I player coverage; never silently label incomplete seasons complete.

Run: python scripts/audit_player_coverage.py
Writes data/processed/coverage_audit.csv and exits nonzero on coverage gaps.
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "d1_player_percentiles"
MANIFEST = DATA / "manifest.csv"
OUTPUT = ROOT / "data" / "processed" / "coverage_audit.csv"

def main():
    manifest = pd.read_csv(MANIFEST)
    required = {"season", "division1_teams", "teams_with_player_data", "players"}
    if not required.issubset(manifest.columns):
        raise ValueError(f"Missing manifest columns: {sorted(required - set(manifest.columns))}")
    if manifest.season.duplicated().any():
        raise ValueError("Duplicate season entries in manifest")
    results = []
    for row in manifest.itertuples(index=False):
        year = int(row.season)
        expected = int(row.division1_teams)
        present = int(row.teams_with_player_data)
        path = DATA / f"player_percentiles_{year}.csv"
        exists = path.is_file()
        results.append({
            "season": year,
            "expected_d1_teams": expected,
            "teams_with_player_data": present,
            "missing_team_count": max(expected - present, 0),
            "player_rows_reported": int(row.players),
            "player_file_exists": exists,
            "coverage_pct": round(100 * present / expected, 2) if expected else None,
            "coverage_status": "GAP" if present != expected or not exists else "REPORTED_COMPLETE_UNVERIFIED",
        })
    report = pd.DataFrame(results).sort_values("season")
    report.to_csv(OUTPUT, index=False)
    print(report.to_string(index=False))
    print("\nNOTE: Manifest counts are self-reported; this does NOT independently certify D-I membership, IDs, or player completeness.")
    if (report.coverage_status == "GAP").any():
        raise SystemExit("Coverage gaps detected; inspect coverage_audit.csv")

if __name__ == "__main__":
    main()
