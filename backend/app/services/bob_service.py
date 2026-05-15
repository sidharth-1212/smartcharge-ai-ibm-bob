"""
IBM Bob Service - Local AI Simulation Engine (Hackathon Demo Mode)
Simulates dynamic, intelligent load-balancing decisions for the UI dashboard.
"""

import logging
import random
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum

# Configure logging
logger = logging.getLogger(__name__)

class ChargingMode(str, Enum):
    FAST_CHARGE = "FAST_CHARGE"
    ECO_MODE = "ECO_MODE"
    PAUSED = "PAUSED"

class BobDecisionRequest:
    def __init__(self, request_id: str, telemetry: Dict[str, Any], user_preferences: Optional[Dict[str, Any]] = None, constraints: Optional[Dict[str, Any]] = None):
        self.request_id = request_id
        self.telemetry = telemetry
        self.user_preferences = user_preferences or {}
        self.constraints = constraints or {}
        self.timestamp = datetime.utcnow().isoformat()

class BobDecisionResponse:
    def __init__(self, request_id: str, charging_mode: ChargingMode, reasoning: str, confidence: float, estimated_cost: float, estimated_time_hours: float, renewable_percentage: float, metadata: Optional[Dict[str, Any]] = None):
        self.request_id = request_id
        self.charging_mode = charging_mode
        self.reasoning = reasoning
        self.confidence = confidence
        self.estimated_cost = estimated_cost
        self.estimated_time_hours = estimated_time_hours
        self.renewable_percentage = renewable_percentage
        self.metadata = metadata or {}
        self.timestamp = datetime.utcnow().isoformat()

class BobService:
    def __init__(self):
        logger.info("BobService initialized in DEMO MODE (Local AI Simulation)")
    
    async def get_charging_decision(self, request: BobDecisionRequest) -> BobDecisionResponse:
        logger.info(f"Requesting AI decision for request_id: {request.request_id}")
        
        # Simulate API network latency (0.3s to 1.2s) so the UI looks like it's "thinking"
        await asyncio.sleep(random.uniform(0.3, 1.2))
        
        # Generate the dynamic simulated response
        decision = self._generate_simulated_ai_decision(request.request_id, request.telemetry)
        
        logger.info(f"Bob decision: {decision.charging_mode.value} (confidence: {decision.confidence:.2f})")
        return decision
    
    def _generate_simulated_ai_decision(self, request_id: str, telemetry: Dict[str, Any]) -> BobDecisionResponse:
        """Generates highly realistic, fluctuating AI logic for the dashboard"""
        solar_kw = telemetry.get("solar", {}).get("generation_kw", 0)
        if solar_kw == 0: 
            solar_kw = telemetry.get("solar_generation_kw", 0) # Handle flat JSON
            
        grid_price = telemetry.get("grid", {}).get("price_per_kwh", 0)
        if grid_price == 0:
            grid_price = telemetry.get("grid_price_per_kwh", 0) # Handle flat JSON
            
        battery_soc = telemetry.get("ev_battery", {}).get("soc_percent", 0)
        if battery_soc == 0:
            battery_soc = telemetry.get("battery_soc_percent", 0) # Handle flat JSON
            
        # Add dynamic confidence so the dashboard gauges fluctuate naturally
        confidence = round(random.uniform(0.82, 0.98), 2)
        
        # Scenario 1: Battery is full
        if battery_soc > 90:
            mode = ChargingMode.PAUSED
            reasons = [
                f"Battery is at optimal health ({battery_soc}%). Pausing cycle to prevent degradation.",
                f"Target SoC reached. Disengaging load draw to balance local grid.",
                f"Vehicle fully charged. Shifting local surplus back to primary household load."
            ]
            reasoning = random.choice(reasons)
            cost, time, pct = 0.0, 0.0, 100.0
            
        # Scenario 2: Peak Evening Prices (Expensive Grid)
        elif grid_price > 0.25:
            mode = ChargingMode.PAUSED
            reasons = [
                f"Grid price spike detected (${grid_price:.2f}/kWh). Pausing charge to maximize savings.",
                f"Evening peak hours active. Deferring EV load until grid costs drop below $0.15/kWh.",
                f"High grid strain. AI has halted charging to avoid peak tariff penalties."
            ]
            reasoning = random.choice(reasons)
            cost, time, pct = 0.0, 0.0, 0.0
            
        # Scenario 3: High Solar Output (Midday)
        elif solar_kw > 3.5 and battery_soc < 80:
            mode = ChargingMode.FAST_CHARGE
            reasons = [
                f"Strong solar yield ({solar_kw:.1f}kW). Engaging Fast Charge to capture renewable surplus.",
                f"Optimal weather conditions detected. Funneling excess solar directly into EV battery.",
                f"Maximizing green energy utilization. Drawing 11kW while solar arrays are peaking."
            ]
            reasoning = random.choice(reasons)
            cost = grid_price * 1.5 # Blended cost
            time = 75.0 * ((100 - battery_soc)/100) / 11.0
            pct = min(100, (solar_kw / 11.0) * 100)
            
        # Scenario 4: Standard/Nighttime Eco Charging
        else:
            mode = ChargingMode.ECO_MODE
            reasons = [
                f"Grid stabilized at ${grid_price:.2f}/kWh. Resuming slow charge on Eco Mode.",
                f"Balancing household load. Trickle charging at 3.5kW to prevent breaker trips.",
                f"Optimal overnight charging window. Eco Mode active to preserve battery chemistry."
            ]
            reasoning = random.choice(reasons)
            cost = grid_price * 3.5
            time = 75.0 * ((100 - battery_soc)/100) / 3.5
            pct = 0.0 if solar_kw == 0 else min(100, (solar_kw / 3.5) * 100)
        
        return BobDecisionResponse(
            request_id=request_id,
            charging_mode=mode,
            reasoning=reasoning,
            confidence=confidence,
            estimated_cost=round(cost, 2),
            estimated_time_hours=round(time, 1),
            renewable_percentage=round(pct, 1),
            metadata={"source": "simulated_ai_core"}
        )

# Global service instance
bob_service = BobService()