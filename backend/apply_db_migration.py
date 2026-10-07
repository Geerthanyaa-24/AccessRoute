import re
import os

filepath = 'backend/main.py'
with open(filepath, 'r') as f:
    content = f.read()

# Add imports if they don't exist
if 'from backend.database import SessionLocal' not in content:
    imports_to_add = """
import datetime
from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models import ObstacleReport
"""
    content = re.sub(r'(from fastapi import.*)', r'\1' + imports_to_add, content, count=1)

# We will create a helper function `get_all_reports()` and `add_report()` that hits the DB, 
# and fallbacks to OBSTACLE_REPORTS if the DB connection fails.
# Since we need to replace all `OBSTACLE_REPORTS` usages, let's inject a dynamic property or a function.

helper_code = """
# --- DB ABSTRACTION LAYER ---
def _db_get_reports():
    try:
        db = SessionLocal()
        reports = db.query(ObstacleReport).all()
        db.close()
        return [
            {
                "id": r.id, "latitude": r.geom.centroid.y if r.geom else 0.0, "longitude": r.geom.centroid.x if r.geom else 0.0,
                "obstacle_type": r.obstacle_type, "description": r.description,
                "severity": r.severity, "status": r.status, "timestamp": str(r.timestamp)
            } for r in reports
        ]
    except Exception as e:
        # Fallback to local memory if DB not configured (PostGIS not running)
        return _load_reports()

def _db_add_report(data):
    try:
        db = SessionLocal()
        new_report = ObstacleReport(
            obstacle_type=data.get('obstacle_type'),
            description=data.get('description'),
            severity=data.get('severity'),
            status=data.get('status', 'pending_verification')
        )
        db.add(new_report)
        db.commit()
        db.refresh(new_report)
        db.close()
        return {"id": new_report.id, **data, "status": new_report.status}
    except Exception:
        report = {"id": len(_load_reports()) + 1, **data, "status": data.get("status", "pending_verification")}
        OBSTACLE_REPORTS_MEM = _load_reports()
        OBSTACLE_REPORTS_MEM.append(report)
        REPORTS_PATH.write_text(json.dumps(OBSTACLE_REPORTS_MEM, indent=2), encoding="utf-8")
        return report

def _db_update_status(report_id, new_status):
    try:
        db = SessionLocal()
        report = db.query(ObstacleReport).filter(ObstacleReport.id == report_id).first()
        if report:
            report.status = new_status
            db.commit()
            db.close()
            return True
    except Exception:
        pass
    # Fallback
    OBSTACLE_REPORTS_MEM = _load_reports()
    for r in OBSTACLE_REPORTS_MEM:
        if r.get("id") == report_id:
            r["status"] = new_status
            REPORTS_PATH.write_text(json.dumps(OBSTACLE_REPORTS_MEM, indent=2), encoding="utf-8")
            return True
    return False

# Replace OBSTACLE_REPORTS global variable with a dynamic getter for reads.
class DynamicReportsList(list):
    def __iter__(self):
        return iter(_db_get_reports())
    def __len__(self):
        return len(_db_get_reports())
    def __getitem__(self, key):
        return _db_get_reports()[key]
    def append(self, item):
        pass # Handle manually

OBSTACLE_REPORTS = DynamicReportsList()
"""

# We can replace the `OBSTACLE_REPORTS = _load_reports()` line with our abstraction.
content = re.sub(r'OBSTACLE_REPORTS: list\[dict\[str, Any\]\] = _load_reports\(\)', helper_code, content)

# Update report_obstacle endpoint
content = re.sub(
    r'report = \{"id": len\(OBSTACLE_REPORTS\) \+ 1, \*\*request.model_dump\(\), "status": "pending_verification"\}\n\s*OBSTACLE_REPORTS\.append\(report\)\n\s*_save_reports\(\)',
    r'report = _db_add_report(request.model_dump())',
    content
)

# Update resolve_obstacle endpoint
content = re.sub(
    r'for report in OBSTACLE_REPORTS:\n\s*if report.get\("id"\) == report_id:\n\s*report\["status"\] = "resolved"\n\s*_save_reports\(\)',
    r'if _db_update_status(report_id, "resolved"):\n        report = next((r for r in OBSTACLE_REPORTS if r.get("id") == report_id), {"id": report_id, "status": "resolved"})',
    content
)

# Update verify_report endpoint
content = re.sub(
    r'for report in OBSTACLE_REPORTS:\n\s*if report.get\(\'id\'\) == report_id:\n\s*report\[\'status\'\] = \'verified\'\n\s*_save_reports\(\)',
    r'if _db_update_status(report_id, "verified"):\n        report = next((r for r in OBSTACLE_REPORTS if r.get("id") == report_id), {"id": report_id, "status": "verified"})',
    content
)

# Update reject_report endpoint
content = re.sub(
    r'for report in OBSTACLE_REPORTS:\n\s*if report.get\(\'id\'\) == report_id:\n\s*report\[\'status\'\] = \'rejected\'\n\s*_save_reports\(\)',
    r'if _db_update_status(report_id, "rejected"):\n        report = next((r for r in OBSTACLE_REPORTS if r.get("id") == report_id), {"id": report_id, "status": "rejected"})',
    content
)

with open(filepath, 'w') as f:
    f.write(content)
print("Migration applied successfully.")
