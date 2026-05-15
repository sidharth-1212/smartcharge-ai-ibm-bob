"""
Charging Control API Router
Endpoints for managing charging modes and status
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime
import logging
import uuid # Added for manual override ID

from ..database import get_db, cache_set, cache_get
from ..config import CHARGING_MODES, get_charging_mode_config
from ..models import Decision, Telemetry # Added to write to DB

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/charging",
    tags=["charging"]
)

# Cache key for current charging mode
CURRENT_MODE_CACHE_KEY = "charging:current_mode"

class ChargingModeRequest(BaseModel):
    mode: str = Field(..., description="Charging mode: FAST_CHARGE, ECO_MODE, or PAUSED")
    reason: Optional[str] = Field(default=None, description="Reason for mode change")
    manual_override: bool = Field(default=True, description="Whether this is a manual override")
    
    @validator("mode")
    def validate_mode(cls, v):
        allowed_modes = ["FAST_CHARGE", "ECO_MODE", "PAUSED"]
        v_upper = v.upper()
        if v_upper not in allowed_modes:
            raise ValueError(f"Charging mode must be one of {allowed_modes}")
        return v_upper

@router.post("/mode", status_code=status.HTTP_200_OK)
async def set_charging_mode(
    request: ChargingModeRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    try:
        logger.info(f"Setting charging mode to: {request.mode}")
        mode_config = get_charging_mode_config(request.mode)
        
        # --- THE HACKATHON DATABASE FIX ---
        # Inject the manual decision into the DB so the frontend Event Log picks it up!
        latest_tel = db.query(Telemetry).order_by(Telemetry.timestamp.desc()).first()
        tel_id = latest_tel.id if latest_tel else None

        override_decision = Decision(
            request_id=f"manual-{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow(),
            charging_mode=request.mode,
            reasoning=request.reason or f"👨‍💻 USER OVERRIDE: AI suspended. Forcing system into {request.mode}.",
            confidence=1.0,  # 100% confidence for human override
            estimated_cost=0.0,
            estimated_time_hours=0.0,
            renewable_percentage=0.0,
            telemetry_id=tel_id,
            applied=True,
            overridden=True,
            override_reason="User clicked manual override"
        )
        db.add(override_decision)
        db.commit()
        # ----------------------------------
        
        charging_status = {
            "mode": request.mode,
            "power_kw": mode_config["power_kw"],
            "description": mode_config["description"],
            "timestamp": datetime.utcnow().isoformat(),
            "manual_override": request.manual_override,
            "reason": request.reason or f"Manual override to {request.mode}"
        }
        
        import json
        cache_set(
            CURRENT_MODE_CACHE_KEY,
            json.dumps(charging_status),
            ttl=3600
        )
        
        return {
            "success": True,
            "message": f"Charging mode set to {request.mode}",
            "status": charging_status
        }
        
    except Exception as e:
        logger.error(f"Failed to set charging mode: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to set charging mode: {str(e)}")

@router.get("/status")
async def get_charging_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        cached_status = cache_get(CURRENT_MODE_CACHE_KEY)
        if cached_status:
            import json
            return {"success": True, "status": json.loads(cached_status)}
            
        mode_config = get_charging_mode_config("ECO_MODE")
        return {
            "success": True,
            "status": {
                "mode": "ECO_MODE",
                "power_kw": mode_config["power_kw"],
                "description": mode_config["description"],
                "timestamp": datetime.utcnow().isoformat(),
                "manual_override": False,
                "reason": "Default mode (no status set)"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/modes")
async def get_available_modes() -> Dict[str, Any]:
    return {"success": True, "modes": CHARGING_MODES}

@router.post("/pause")
async def pause_charging(reason: Optional[str] = None, db: Session = Depends(get_db)):
    return await set_charging_mode(ChargingModeRequest(mode="PAUSED", reason=reason, manual_override=True), db)

@router.post("/resume")
async def resume_charging(mode: str = "ECO_MODE", reason: Optional[str] = None, db: Session = Depends(get_db)):
    return await set_charging_mode(ChargingModeRequest(mode=mode, reason=reason, manual_override=True), db)

@router.post("/fast-charge")
async def enable_fast_charge(reason: Optional[str] = None, db: Session = Depends(get_db)):
    return await set_charging_mode(ChargingModeRequest(mode="FAST_CHARGE", reason=reason, manual_override=True), db)