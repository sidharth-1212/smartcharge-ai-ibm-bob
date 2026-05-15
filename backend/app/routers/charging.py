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

from ..database import get_db, cache_set, cache_get
from ..config import CHARGING_MODES, get_charging_mode_config

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
    """Request model for setting charging mode"""
    mode: str = Field(..., description="Charging mode: FAST_CHARGE, ECO_MODE, or PAUSED")
    reason: Optional[str] = Field(default=None, description="Reason for mode change")
    manual_override: bool = Field(default=True, description="Whether this is a manual override")
    
    @validator("mode")
    def validate_mode(cls, v):
        """Validate charging mode is one of the allowed values"""
        allowed_modes = ["FAST_CHARGE", "ECO_MODE", "PAUSED"]
        v_upper = v.upper()
        if v_upper not in allowed_modes:
            raise ValueError(f"Charging mode must be one of {allowed_modes}")
        return v_upper


class ChargingStatus(BaseModel):
    """Current charging status"""
    mode: str
    power_kw: float
    description: str
    timestamp: str
    manual_override: bool
    reason: Optional[str] = None


@router.post("/mode", status_code=status.HTTP_200_OK)
async def set_charging_mode(
    request: ChargingModeRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Manually set the charging mode
    
    This overrides any AI-generated decisions
    
    Args:
        request: Charging mode request
        db: Database session
        
    Returns:
        Updated charging status
    """
    try:
        logger.info(f"Setting charging mode to: {request.mode}")
        
        # Get mode configuration
        mode_config = get_charging_mode_config(request.mode)
        
        # Create status object
        charging_status = {
            "mode": request.mode,
            "power_kw": mode_config["power_kw"],
            "description": mode_config["description"],
            "timestamp": datetime.utcnow().isoformat(),
            "manual_override": request.manual_override,
            "reason": request.reason or f"Manual override to {request.mode}"
        }
        
        # Cache the current mode
        import json
        cache_set(
            CURRENT_MODE_CACHE_KEY,
            json.dumps(charging_status),
            ttl=3600  # 1 hour TTL
        )
        
        logger.info(f"Charging mode set to {request.mode} ({mode_config['power_kw']}kW)")
        
        return {
            "success": True,
            "message": f"Charging mode set to {request.mode}",
            "status": charging_status
        }
        
    except Exception as e:
        logger.error(f"Failed to set charging mode: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set charging mode: {str(e)}"
        )


@router.get("/status")
async def get_charging_status(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get current charging status
    
    Returns the current charging mode and power level
    
    Args:
        db: Database session
        
    Returns:
        Current charging status
    """
    try:
        # Try to get from cache first
        cached_status = cache_get(CURRENT_MODE_CACHE_KEY)
        
        if cached_status:
            import json
            status_dict = json.loads(cached_status)
            logger.debug("Retrieved charging status from cache")
            
            return {
                "success": True,
                "status": status_dict
            }
        
        # If not in cache, return default ECO_MODE
        mode_config = get_charging_mode_config("ECO_MODE")
        default_status = {
            "mode": "ECO_MODE",
            "power_kw": mode_config["power_kw"],
            "description": mode_config["description"],
            "timestamp": datetime.utcnow().isoformat(),
            "manual_override": False,
            "reason": "Default mode (no status set)"
        }
        
        logger.debug("No cached status, returning default ECO_MODE")
        
        return {
            "success": True,
            "status": default_status
        }
        
    except Exception as e:
        logger.error(f"Failed to get charging status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get charging status: {str(e)}"
        )


@router.get("/modes")
async def get_available_modes() -> Dict[str, Any]:
    """
    Get all available charging modes and their configurations
    
    Returns:
        Dictionary of available charging modes
    """
    try:
        return {
            "success": True,
            "modes": CHARGING_MODES
        }
        
    except Exception as e:
        logger.error(f"Failed to get charging modes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get charging modes: {str(e)}"
        )


@router.post("/pause")
async def pause_charging(
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Pause charging (convenience endpoint)
    
    Args:
        reason: Optional reason for pausing
        db: Database session
        
    Returns:
        Updated charging status
    """
    try:
        request = ChargingModeRequest(
            mode="PAUSED",
            reason=reason or "Charging paused by user",
            manual_override=True
        )
        
        return await set_charging_mode(request, db)
        
    except Exception as e:
        logger.error(f"Failed to pause charging: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause charging: {str(e)}"
        )


@router.post("/resume")
async def resume_charging(
    mode: str = "ECO_MODE",
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Resume charging (convenience endpoint)
    
    Args:
        mode: Charging mode to resume with (default: ECO_MODE)
        reason: Optional reason for resuming
        db: Database session
        
    Returns:
        Updated charging status
    """
    try:
        request = ChargingModeRequest(
            mode=mode,
            reason=reason or f"Charging resumed in {mode} mode",
            manual_override=True
        )
        
        return await set_charging_mode(request, db)
        
    except Exception as e:
        logger.error(f"Failed to resume charging: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume charging: {str(e)}"
        )


@router.post("/fast-charge")
async def enable_fast_charge(
    reason: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Enable fast charging (convenience endpoint)
    
    Args:
        reason: Optional reason for fast charging
        db: Database session
        
    Returns:
        Updated charging status
    """
    try:
        request = ChargingModeRequest(
            mode="FAST_CHARGE",
            reason=reason or "Fast charging enabled by user",
            manual_override=True
        )
        
        return await set_charging_mode(request, db)
        
    except Exception as e:
        logger.error(f"Failed to enable fast charge: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable fast charge: {str(e)}"
        )

# Made with Bob