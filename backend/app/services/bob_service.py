"""
IBM Bob Service - Integration with IBM watsonx.ai Bob API
Handles all communication with IBM Bob for intelligent decision-making
"""

import httpx
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

from ..config import settings, get_bob_headers, get_bob_api_endpoint


# Configure logging
logger = logging.getLogger(__name__)


class ChargingMode(str, Enum):
    """Available charging modes"""
    FAST_CHARGE = "FAST_CHARGE"
    ECO_MODE = "ECO_MODE"
    PAUSED = "PAUSED"


class BobDecisionRequest:
    """Structure for IBM Bob decision requests"""
    
    def __init__(
        self,
        request_id: str,
        telemetry: Dict[str, Any],
        user_preferences: Optional[Dict[str, Any]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ):
        self.request_id = request_id
        self.telemetry = telemetry
        self.user_preferences = user_preferences or {}
        self.constraints = constraints or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API request"""
        return {
            "request_id": self.request_id,
            "timestamp": self.timestamp,
            "telemetry": self.telemetry,
            "user_preferences": self.user_preferences,
            "constraints": self.constraints
        }


class BobDecisionResponse:
    """Structure for IBM Bob decision responses"""
    
    def __init__(
        self,
        request_id: str,
        charging_mode: ChargingMode,
        reasoning: str,
        confidence: float,
        estimated_cost: float,
        estimated_time_hours: float,
        renewable_percentage: float,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.request_id = request_id
        self.charging_mode = charging_mode
        self.reasoning = reasoning
        self.confidence = confidence
        self.estimated_cost = estimated_cost
        self.estimated_time_hours = estimated_time_hours
        self.renewable_percentage = renewable_percentage
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/API response"""
        return {
            "request_id": self.request_id,
            "charging_mode": self.charging_mode.value,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "estimated_cost": self.estimated_cost,
            "estimated_time_hours": self.estimated_time_hours,
            "renewable_percentage": self.renewable_percentage,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class BobService:
    """Service for interacting with IBM Bob API"""
    
    def __init__(self):
        self.api_url = settings.ibm_bob_api_url
        self.api_key = settings.ibm_bob_api_key
        self.project_id = settings.ibm_bob_project_id
        self.model_id = settings.ibm_bob_model_id
        self.timeout = settings.decision_timeout_seconds
        self.max_retries = settings.max_decision_retries
        
        logger.info(f"BobService initialized with model: {self.model_id}")
    
    async def get_charging_decision(
        self,
        request: BobDecisionRequest
    ) -> BobDecisionResponse:
        """
        Get a charging decision from IBM Bob based on current telemetry
        
        Args:
            request: BobDecisionRequest containing telemetry and context
            
        Returns:
            BobDecisionResponse with charging mode and reasoning
            
        Raises:
            Exception: If Bob API call fails after retries
        """
        logger.info(f"Requesting decision from Bob for request_id: {request.request_id}")
        
        # Build the prompt for Bob
        prompt = self._build_decision_prompt(request)
        
        # Call IBM Bob API
        try:
            response = await self._call_bob_api(prompt)
            
            # Parse Bob's response
            decision = self._parse_bob_response(
                response,
                request.request_id,
                request.telemetry
            )
            
            logger.info(
                f"Bob decision: {decision.charging_mode.value} "
                f"(confidence: {decision.confidence:.2f})"
            )
            
            return decision
            
        except Exception as e:
            logger.error(f"Failed to get Bob decision: {str(e)}")
            # Return a safe fallback decision
            return self._get_fallback_decision(request)
    
    def _build_decision_prompt(self, request: BobDecisionRequest) -> str:
        """
        Build a comprehensive prompt for IBM Bob with all context
        
        Args:
            request: BobDecisionRequest with telemetry and preferences
            
        Returns:
            Formatted prompt string for Bob
        """
        telemetry = request.telemetry
        
        # Extract key telemetry values
        solar_kw = telemetry.get("solar", {}).get("generation_kw", 0)
        grid_price = telemetry.get("grid", {}).get("price_per_kwh", 0)
        battery_soc = telemetry.get("ev_battery", {}).get("soc_percent", 0)
        battery_capacity = telemetry.get("ev_battery", {}).get("capacity_kwh", 75)
        
        # Calculate derived metrics
        solar_available = solar_kw > 0.5
        grid_expensive = grid_price > 0.25
        battery_low = battery_soc < 30
        battery_full = battery_soc > 90
        
        prompt = f"""You are an intelligent EV charging optimizer. Analyze the current situation and recommend the best charging mode.

CURRENT TELEMETRY:
- Solar Generation: {solar_kw:.2f} kW
- Grid Price: ${grid_price:.3f}/kWh
- Battery State of Charge: {battery_soc:.1f}%
- Battery Capacity: {battery_capacity:.1f} kWh

AVAILABLE CHARGING MODES:
1. FAST_CHARGE (11 kW): Maximum charging speed, uses grid power if needed
2. ECO_MODE (3.5 kW): Balanced charging, prioritizes solar energy
3. PAUSED (0 kW): No charging, wait for better conditions

OPTIMIZATION GOALS:
- Minimize electricity costs
- Maximize renewable energy usage
- Ensure battery is charged when needed
- Avoid grid strain during peak hours

CURRENT CONDITIONS:
- Solar available: {"Yes" if solar_available else "No"}
- Grid pricing: {"Expensive (peak hours)" if grid_expensive else "Moderate/Low"}
- Battery level: {"Low (needs charging)" if battery_low else "Full (no charging needed)" if battery_full else "Normal"}

USER PREFERENCES:
{json.dumps(request.user_preferences, indent=2) if request.user_preferences else "None specified"}

CONSTRAINTS:
{json.dumps(request.constraints, indent=2) if request.constraints else "None specified"}

Please respond in the following JSON format:
{{
    "charging_mode": "FAST_CHARGE" | "ECO_MODE" | "PAUSED",
    "reasoning": "Detailed explanation of why this mode was chosen",
    "confidence": 0.0-1.0,
    "estimated_cost_per_hour": 0.00,
    "estimated_time_to_full_hours": 0.0,
    "renewable_percentage": 0-100
}}

Provide your recommendation:"""
        
        return prompt
    
    async def _call_bob_api(self, prompt: str) -> Dict[str, Any]:
        """
        Make the actual API call to IBM Bob
        
        Args:
            prompt: The formatted prompt for Bob
            
        Returns:
            Raw API response from Bob
            
        Raises:
            Exception: If API call fails after retries
        """
        headers = get_bob_headers()
        
        payload = {
            "model_id": self.model_id,
            "input": prompt,
            "parameters": {
                "max_new_tokens": 500,
                "temperature": 0.7,
                "top_p": 0.9,
                "top_k": 50
            }
        }
        
        # Add project_id only if it's provided
        if self.project_id:
            payload["project_id"] = self.project_id
        
        endpoint = get_bob_api_endpoint("text/generation")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for attempt in range(self.max_retries):
                try:
                    logger.debug(f"Calling Bob API (attempt {attempt + 1}/{self.max_retries})")
                    
                    response = await client.post(
                        endpoint,
                        headers=headers,
                        json=payload
                    )
                    
                    response.raise_for_status()
                    
                    result = response.json()
                    logger.debug(f"Bob API response received: {result}")
                    
                    return result
                    
                except httpx.HTTPStatusError as e:
                    logger.error(f"Bob API HTTP error: {e.response.status_code} - {e.response.text}")
                    if attempt == self.max_retries - 1:
                        raise
                    
                except httpx.TimeoutException:
                    logger.warning(f"Bob API timeout on attempt {attempt + 1}")
                    if attempt == self.max_retries - 1:
                        raise
                    
                except Exception as e:
                    logger.error(f"Bob API error: {str(e)}")
                    if attempt == self.max_retries - 1:
                        raise
        
        raise Exception("Failed to call Bob API after all retries")
    
    def _parse_bob_response(
        self,
        api_response: Dict[str, Any],
        request_id: str,
        telemetry: Dict[str, Any]
    ) -> BobDecisionResponse:
        """
        Parse IBM Bob's API response into a structured decision
        
        Args:
            api_response: Raw response from Bob API
            request_id: Original request ID
            telemetry: Original telemetry data
            
        Returns:
            Structured BobDecisionResponse
        """
        try:
            # Extract the generated text from Bob's response
            generated_text = api_response.get("results", [{}])[0].get("generated_text", "")
            
            # Try to parse JSON from the response
            # Bob might return JSON wrapped in markdown code blocks
            json_str = generated_text
            if "```json" in generated_text:
                json_str = generated_text.split("```json")[1].split("```")[0].strip()
            elif "```" in generated_text:
                json_str = generated_text.split("```")[1].split("```")[0].strip()
            
            decision_data = json.loads(json_str)
            
            # Extract and validate fields
            charging_mode = ChargingMode(decision_data.get("charging_mode", "ECO_MODE"))
            reasoning = decision_data.get("reasoning", "No reasoning provided")
            confidence = float(decision_data.get("confidence", 0.7))
            estimated_cost = float(decision_data.get("estimated_cost_per_hour", 0.0))
            estimated_time = float(decision_data.get("estimated_time_to_full_hours", 0.0))
            renewable_pct = float(decision_data.get("renewable_percentage", 0.0))
            
            return BobDecisionResponse(
                request_id=request_id,
                charging_mode=charging_mode,
                reasoning=reasoning,
                confidence=confidence,
                estimated_cost=estimated_cost,
                estimated_time_hours=estimated_time,
                renewable_percentage=renewable_pct,
                metadata={"raw_response": generated_text}
            )
            
        except Exception as e:
            logger.error(f"Failed to parse Bob response: {str(e)}")
            logger.debug(f"Raw response: {api_response}")
            
            # Return a fallback decision based on telemetry
            return self._create_rule_based_decision(request_id, telemetry)
    
    def _get_fallback_decision(self, request: BobDecisionRequest) -> BobDecisionResponse:
        """
        Generate a safe fallback decision when Bob API is unavailable
        
        Args:
            request: Original decision request
            
        Returns:
            Rule-based BobDecisionResponse
        """
        logger.warning("Using fallback decision logic (Bob API unavailable)")
        return self._create_rule_based_decision(request.request_id, request.telemetry)
    
    def _create_rule_based_decision(
        self,
        request_id: str,
        telemetry: Dict[str, Any]
    ) -> BobDecisionResponse:
        """
        Create a simple rule-based decision as fallback
        
        Args:
            request_id: Request identifier
            telemetry: Current telemetry data
            
        Returns:
            Rule-based BobDecisionResponse
        """
        solar_kw = telemetry.get("solar", {}).get("generation_kw", 0)
        grid_price = telemetry.get("grid", {}).get("price_per_kwh", 0)
        battery_soc = telemetry.get("ev_battery", {}).get("soc_percent", 0)
        
        # Simple rule-based logic
        if battery_soc > 90:
            mode = ChargingMode.PAUSED
            reasoning = "Battery is nearly full (>90%). Pausing to avoid overcharging."
        elif grid_price > 0.30:
            mode = ChargingMode.PAUSED
            reasoning = f"Grid price is high (${grid_price:.3f}/kWh). Waiting for lower rates."
        elif solar_kw > 4.0 and battery_soc < 80:
            mode = ChargingMode.FAST_CHARGE
            reasoning = f"Strong solar generation ({solar_kw:.1f}kW). Using FAST_CHARGE to maximize renewable energy."
        elif solar_kw > 2.0:
            mode = ChargingMode.ECO_MODE
            reasoning = f"Moderate solar generation ({solar_kw:.1f}kW). Using ECO_MODE for balanced charging."
        elif battery_soc < 30:
            mode = ChargingMode.ECO_MODE
            reasoning = f"Battery low ({battery_soc:.1f}%). Using ECO_MODE to ensure minimum charge."
        else:
            mode = ChargingMode.ECO_MODE
            reasoning = "Normal conditions. Using ECO_MODE for cost-effective charging."
        
        return BobDecisionResponse(
            request_id=request_id,
            charging_mode=mode,
            reasoning=reasoning,
            confidence=0.6,  # Lower confidence for rule-based decisions
            estimated_cost=grid_price * 3.5,  # Rough estimate
            estimated_time_hours=5.0,
            renewable_percentage=min(100, (solar_kw / 3.5) * 100),
            metadata={"fallback": True, "method": "rule_based"}
        )


# Global service instance
bob_service = BobService()

# Made with Bob
