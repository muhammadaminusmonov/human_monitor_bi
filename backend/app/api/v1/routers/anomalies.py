from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db
from app.models.anomalies_and_alert import AnomaliesAndAlert
from app.models.enums import AlertSeverity

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.post("/")
def create_alert(
    camera_id: int,
    anomaly_type: str,
    severity: AlertSeverity,
    db: Session = Depends(get_db)
):
    alert = AnomaliesAndAlert(
        camera_id=camera_id,
        anomaly_type=anomaly_type,
        severity=severity
    )

    db.add(alert)
    db.commit()
    db.refresh(alert)

    return alert    