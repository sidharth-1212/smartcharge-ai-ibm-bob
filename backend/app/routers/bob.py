"""
Bob API Router
Endpoints for IBM Bob decision-making
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import logging

from ..database import get_db
from ..models import Decision, Telemetry
from ..services.decision_engine import decision_engine
from ..services.bob_service import BobDecisionRequest

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/bob",
    tags=["bob"]
)


class DecisionRequest(BaseModel):
    """Request model for manual decision requests"""
    telemetry_id: int = Field(..., description="ID of telemetry to base decision on")
    user_preferences: Optional[Dict[str, Any]] = Field(default=None)
    constraints: Optional[Dict[str, Any]] = Field(default=None)


@router.post("/decision", status_code=status.HTTP_201_CREATED)
async def request_decision(
    request: DecisionRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Request a charging decision from IBM Bob
    
    Args:
        request: Decision request with telemetry ID and optional preferences
        db: Database session
        
    Returns:
        Decision from Bob with reasoning and confidence
    """
    try:
        logger.info(f"Received decision request for telemetry ID: {request.telemetry_id}")
        
        # Get telemetry
        telemetry = db.query(Telemetry).filter(
            Telemetry.id == request.telemetry_id
        ).first()
        
        if not telemetry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Telemetry with ID {request.telemetry_id} not found"
            )
        
        # Make decision
        decision = await decision_engine.make_decision(
            telemetry=telemetry,
            db=db,
            user_preferences=request.user_preferences,
            constraints=request.constraints
        )
        
        return {
            "success": True,
            "decision": decision.to_dict(),
            "telemetry": telemetry.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to request decision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to request decision: {str(e)}"
        )


@router.get("/decisions/latest")
async def get_latest_decision(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the most recent decision from Bob
    
    Args:
        db: Database session
        
    Returns:
        Latest decision
    """
    try:
        decision = await decision_engine.get_latest_decision(db)
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No decisions found"
            )
        
        return {
            "success": True,
            "decision": decision.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest decision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest decision: {str(e)}"
        )


@router.get("/decisions/history")
async def get_decision_history(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get decision history with pagination
    
    Args:
        limit: Maximum number of records to return (default: 100, max: 1000)
        offset: Number of records to skip (default: 0)
        db: Database session
        
    Returns:
        List of decisions
    """
    try:
        # Validate and cap limit
        if limit < 1:
            limit = 100
        if limit > 1000:
            limit = 1000
        
        if offset < 0:
            offset = 0
        
        decisions = await decision_engine.get_decision_history(
            db=db,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "count": len(decisions),
            "limit": limit,
            "offset": offset,
            "decisions": [d.to_dict() for d in decisions]
        }
        
    except Exception as e:
        logger.error(f"Failed to get decision history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get decision history: {str(e)}"
        )


@router.get("/decisions/{decision_id}")
async def get_decision_by_id(
    decision_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get a specific decision by ID
    
    Args:
        decision_id: Decision ID
        db: Database session
        
    Returns:
        Decision details
    """
    try:
        decision = await decision_engine.get_decision_by_id(decision_id, db)
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision with ID {decision_id} not found"
            )
        
        return {
            "success": True,
            "decision": decision.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get decision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get decision: {str(e)}"
        )


@router.post("/decisions/{decision_id}/apply")
async def apply_decision(
    decision_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Mark a decision as applied
    
    Args:
        decision_id: Decision ID
        db: Database session
        
    Returns:
        Updated decision
    """
    try:
        decision = await decision_engine.mark_decision_applied(decision_id, db)
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision with ID {decision_id} not found"
            )
        
        return {
            "success": True,
            "message": f"Decision {decision_id} marked as applied",
            "decision": decision.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply decision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to apply decision: {str(e)}"
        )


class OverrideRequest(BaseModel):
    """Request model for overriding a decision"""
    reason: str = Field(..., description="Reason for overriding the decision")


@router.post("/decisions/{decision_id}/override")
async def override_decision(
    decision_id: int,
    request: OverrideRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Mark a decision as overridden by user
    
    Args:
        decision_id: Decision ID
        request: Override request with reason
        db: Database session
        
    Returns:
        Updated decision
    """
    try:
        decision = await decision_engine.override_decision(
            decision_id=decision_id,
            override_reason=request.reason,
            db=db
        )
        
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision with ID {decision_id} not found"
            )
        
        return {
            "success": True,
            "message": f"Decision {decision_id} marked as overridden",
            "decision": decision.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to override decision: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to override decision: {str(e)}"
        )

# Made with Bob