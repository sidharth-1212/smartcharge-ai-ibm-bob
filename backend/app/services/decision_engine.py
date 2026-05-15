"""
Decision Engine Service
Orchestrates the decision-making flow: Telemetry → Bob → Decision Storage
"""

import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Decision, Telemetry
from .bob_service import bob_service, BobDecisionRequest, BobDecisionResponse
from .telemetry_processor import telemetry_processor

# Configure logging
logger = logging.getLogger(__name__)


class DecisionEngine:
    """Core decision-making orchestration"""
    
    def __init__(self):
        logger.info("DecisionEngine initialized")
    
    async def make_decision(
        self,
        telemetry: Telemetry,
        db: Session,
        user_preferences: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Decision:
        """
        Make a charging decision based on telemetry
        
        Flow:
        1. Format telemetry for Bob
        2. Call Bob API for decision
        3. Store decision in database
        4. Return decision
        
        Args:
            telemetry: Current telemetry data
            db: Database session
            user_preferences: Optional user preferences
            constraints: Optional constraints
            
        Returns:
            Decision instance with Bob's recommendation
        """
        logger.info(f"Making decision for telemetry ID: {telemetry.id}")
        
        try:
            # Generate unique request ID
            request_id = str(uuid.uuid4())
            
            # Format telemetry for Bob
            telemetry_dict = telemetry_processor.format_for_bob(telemetry)
            
            # Create Bob request
            bob_request = BobDecisionRequest(
                request_id=request_id,
                telemetry=telemetry_dict,
                user_preferences=user_preferences,
                constraints=constraints
            )
            
            # Get decision from Bob
            logger.info(f"Requesting decision from Bob (request_id: {request_id})")
            bob_response = await bob_service.get_charging_decision(bob_request)
            
            # Store decision in database
            decision = self._store_decision(
                bob_response=bob_response,
                telemetry_id=telemetry.id,
                db=db
            )
            
            logger.info(
                f"Decision made: {decision.charging_mode} "
                f"(confidence: {decision.confidence:.2f}, ID: {decision.id})"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to make decision: {str(e)}")
            raise
    
    def _store_decision(
        self,
        bob_response: BobDecisionResponse,
        telemetry_id: int,
        db: Session
    ) -> Decision:
        """
        Store Bob's decision in the database
        
        Args:
            bob_response: Response from Bob API
            telemetry_id: ID of associated telemetry
            db: Database session
            
        Returns:
            Stored Decision instance
        """
        try:
            decision = Decision(
                request_id=bob_response.request_id,
                timestamp=datetime.utcnow(),
                charging_mode=bob_response.charging_mode.value,
                reasoning=bob_response.reasoning,
                confidence=bob_response.confidence,
                estimated_cost=bob_response.estimated_cost,
                estimated_time_hours=bob_response.estimated_time_hours,
                renewable_percentage=bob_response.renewable_percentage,
                telemetry_id=telemetry_id,
                metadata=bob_response.metadata,
                applied=False
            )
            
            db.add(decision)
            db.commit()
            db.refresh(decision)
            
            logger.info(f"Decision stored with ID: {decision.id}")
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to store decision: {str(e)}")
            db.rollback()
            raise
    
    async def get_decision_by_id(
        self,
        decision_id: int,
        db: Session
    ) -> Optional[Decision]:
        """
        Get a decision by ID
        
        Args:
            decision_id: Decision ID
            db: Database session
            
        Returns:
            Decision instance or None
        """
        try:
            decision = db.query(Decision).filter(
                Decision.id == decision_id
            ).first()
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to get decision: {str(e)}")
            return None
    
    async def get_decision_by_request_id(
        self,
        request_id: str,
        db: Session
    ) -> Optional[Decision]:
        """
        Get a decision by request ID
        
        Args:
            request_id: Request ID
            db: Database session
            
        Returns:
            Decision instance or None
        """
        try:
            decision = db.query(Decision).filter(
                Decision.request_id == request_id
            ).first()
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to get decision: {str(e)}")
            return None
    
    async def get_decision_history(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> list[Decision]:
        """
        Get decision history with pagination
        
        Args:
            db: Database session
            limit: Maximum number of records
            offset: Number of records to skip
            
        Returns:
            List of Decision instances
        """
        try:
            decisions = db.query(Decision).order_by(
                Decision.timestamp.desc()
            ).limit(limit).offset(offset).all()
            
            logger.info(f"Retrieved {len(decisions)} decisions")
            
            return decisions
            
        except Exception as e:
            logger.error(f"Failed to get decision history: {str(e)}")
            return []
    
    async def mark_decision_applied(
        self,
        decision_id: int,
        db: Session
    ) -> Optional[Decision]:
        """
        Mark a decision as applied
        
        Args:
            decision_id: Decision ID
            db: Database session
            
        Returns:
            Updated Decision instance or None
        """
        try:
            decision = db.query(Decision).filter(
                Decision.id == decision_id
            ).first()
            
            if decision:
                decision.applied = True
                decision.applied_at = datetime.utcnow()
                db.commit()
                db.refresh(decision)
                
                logger.info(f"Decision {decision_id} marked as applied")
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to mark decision as applied: {str(e)}")
            db.rollback()
            return None
    
    async def override_decision(
        self,
        decision_id: int,
        override_reason: str,
        db: Session
    ) -> Optional[Decision]:
        """
        Mark a decision as overridden by user
        
        Args:
            decision_id: Decision ID
            override_reason: Reason for override
            db: Database session
            
        Returns:
            Updated Decision instance or None
        """
        try:
            decision = db.query(Decision).filter(
                Decision.id == decision_id
            ).first()
            
            if decision:
                decision.overridden = True
                decision.override_reason = override_reason
                db.commit()
                db.refresh(decision)
                
                logger.info(f"Decision {decision_id} marked as overridden")
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to override decision: {str(e)}")
            db.rollback()
            return None
    
    async def get_latest_decision(self, db: Session) -> Optional[Decision]:
        """
        Get the most recent decision
        
        Args:
            db: Database session
            
        Returns:
            Latest Decision instance or None
        """
        try:
            decision = db.query(Decision).order_by(
                Decision.timestamp.desc()
            ).first()
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to get latest decision: {str(e)}")
            return None


# Global decision engine instance
decision_engine = DecisionEngine()

# Made with Bob