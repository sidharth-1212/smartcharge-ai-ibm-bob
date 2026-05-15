"""
Telemetry API Router
Endpoints for receiving and querying telemetry data
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import logging

from ..database import get_db
from ..models import Telemetry
from ..services.telemetry_processor import telemetry_processor, TelemetryData
from ..services.decision_engine import decision_engine

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/telemetry",
    tags=["telemetry"]
)


@router.post("/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(
    telemetry_data: TelemetryData,
    db: Session = Depends(get_db),
    auto_decide: bool = True
) -> Dict[str, Any]:
    """
    Ingest telemetry data from the simulator
    
    Optionally triggers automatic decision-making via IBM Bob
    
    Args:
        telemetry_data: Validated telemetry data
        db: Database session
        auto_decide: Whether to automatically request a decision from Bob
        
    Returns:
        Stored telemetry and optional decision
    """
    try:
        logger.info("Received telemetry ingestion request")
        
        # Process and store telemetry
        telemetry = await telemetry_processor.process_telemetry(
            telemetry_data=telemetry_data,
            db=db
        )
        
        response = {
            "success": True,
            "telemetry": telemetry.to_dict(),
            "decision": None
        }
        
        # Automatically request decision if enabled
        if auto_decide:
            try:
                logger.info("Auto-decision enabled, requesting decision from Bob")
                decision = await decision_engine.make_decision(
                    telemetry=telemetry,
                    db=db
                )
                response["decision"] = decision.to_dict()
                
            except Exception as e:
                logger.error(f"Failed to auto-generate decision: {str(e)}")
                # Don't fail the telemetry ingestion if decision fails
                response["decision_error"] = str(e)
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to ingest telemetry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest telemetry: {str(e)}"
        )


@router.get("/latest")
async def get_latest_telemetry(
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the most recent telemetry data
    
    Args:
        db: Database session
        
    Returns:
        Latest telemetry data
    """
    try:
        telemetry = await telemetry_processor.get_latest_telemetry(db)
        
        if not telemetry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No telemetry data found"
            )
        
        return {
            "success": True,
            "telemetry": telemetry.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get latest telemetry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get latest telemetry: {str(e)}"
        )


@router.get("/history")
async def get_telemetry_history(
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get historical telemetry data with pagination
    
    Args:
        limit: Maximum number of records to return (default: 100, max: 1000)
        offset: Number of records to skip (default: 0)
        db: Database session
        
    Returns:
        List of telemetry records
    """
    try:
        # Validate and cap limit
        if limit < 1:
            limit = 100
        if limit > 1000:
            limit = 1000
        
        if offset < 0:
            offset = 0
        
        telemetry_list = await telemetry_processor.get_telemetry_history(
            db=db,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "count": len(telemetry_list),
            "limit": limit,
            "offset": offset,
            "telemetry": [t.to_dict() for t in telemetry_list]
        }
        
    except Exception as e:
        logger.error(f"Failed to get telemetry history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get telemetry history: {str(e)}"
        )


@router.get("/{telemetry_id}")
async def get_telemetry_by_id(
    telemetry_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get specific telemetry record by ID
    
    Args:
        telemetry_id: Telemetry record ID
        db: Database session
        
    Returns:
        Telemetry record
    """
    try:
        telemetry = db.query(Telemetry).filter(
            Telemetry.id == telemetry_id
        ).first()
        
        if not telemetry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Telemetry with ID {telemetry_id} not found"
            )
        
        return {
            "success": True,
            "telemetry": telemetry.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get telemetry: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get telemetry: {str(e)}"
        )


@router.delete("/{telemetry_id}")
async def delete_telemetry(
    telemetry_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Delete a telemetry record
    
    Args:
        telemetry_id: Telemetry record ID
        db: Database session
        
    Returns:
        Success message
    """
    try:
        telemetry = db.query(Telemetry).filter(
            Telemetry.id == telemetry_id
        ).first()
        
        if not telemetry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Telemetry with ID {telemetry_id} not found"
            )
        
        db.delete(telemetry)
        db.commit()
        
        logger.info(f"Deleted telemetry ID: {telemetry_id}")
        
        return {
            "success": True,
            "message": f"Telemetry {telemetry_id} deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete telemetry: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete telemetry: {str(e)}"
        )

# Made with Bob