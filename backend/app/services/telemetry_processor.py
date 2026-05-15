"""
Telemetry Processor Service
Validates, processes, and stores incoming telemetry data
"""

import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from ..models import Telemetry
from ..database import cache_set, cache_get
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class TelemetryData(BaseModel):
    """Pydantic model for telemetry validation"""
    
    # Solar data
    solar_generation_kw: float = Field(ge=0, le=50, description="Solar generation in kW")
    solar_capacity_kw: float = Field(default=10.0, ge=0, le=50)
    
    # Grid data
    grid_price_per_kwh: float = Field(ge=0, le=2.0, description="Grid price per kWh")
    grid_carbon_intensity: Optional[float] = Field(default=None, ge=0, le=1000)
    
    # EV Battery data
    battery_soc_percent: float = Field(ge=0, le=100, description="Battery state of charge")
    battery_capacity_kwh: float = Field(default=75.0, ge=10, le=200)
    battery_health_percent: Optional[float] = Field(default=100.0, ge=0, le=100)
    
    # Charging data
    charging_power_kw: float = Field(default=0.0, ge=0, le=50)
    charging_mode: Optional[str] = Field(default=None)
    
    # Weather data (optional)
    temperature_celsius: Optional[float] = Field(default=None, ge=-50, le=60)
    cloud_cover_percent: Optional[float] = Field(default=None, ge=0, le=100)
    
    # Additional metadata
    metadata: Optional[Dict[str, Any]] = Field(default=None)
    
    @validator("charging_mode")
    def validate_charging_mode(cls, v):
        """Validate charging mode is one of the allowed values"""
        if v is not None:
            allowed_modes = ["FAST_CHARGE", "ECO_MODE", "PAUSED"]
            if v.upper() not in allowed_modes:
                raise ValueError(f"Charging mode must be one of {allowed_modes}")
            return v.upper()
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "solar_generation_kw": 5.2,
                "solar_capacity_kw": 10.0,
                "grid_price_per_kwh": 0.15,
                "grid_carbon_intensity": 450.0,
                "battery_soc_percent": 65.0,
                "battery_capacity_kwh": 75.0,
                "battery_health_percent": 98.5,
                "charging_power_kw": 3.5,
                "charging_mode": "ECO_MODE",
                "temperature_celsius": 22.0,
                "cloud_cover_percent": 30.0
            }
        }


class TelemetryProcessor:
    """Process and store telemetry data"""
    
    CACHE_KEY_LATEST = "telemetry:latest"
    CACHE_KEY_PREFIX = "telemetry:"
    
    def __init__(self):
        logger.info("TelemetryProcessor initialized")
    
    async def process_telemetry(
        self,
        telemetry_data: TelemetryData,
        db: Session
    ) -> Telemetry:
        """
        Process and store telemetry data
        
        Args:
            telemetry_data: Validated telemetry data
            db: Database session
            
        Returns:
            Stored Telemetry model instance
        """
        logger.info("Processing new telemetry data")
        
        try:
            # Create telemetry record
            telemetry = Telemetry(
                timestamp=datetime.utcnow(),
                solar_generation_kw=telemetry_data.solar_generation_kw,
                solar_capacity_kw=telemetry_data.solar_capacity_kw,
                grid_price_per_kwh=telemetry_data.grid_price_per_kwh,
                grid_carbon_intensity=telemetry_data.grid_carbon_intensity,
                battery_soc_percent=telemetry_data.battery_soc_percent,
                battery_capacity_kwh=telemetry_data.battery_capacity_kwh,
                battery_health_percent=telemetry_data.battery_health_percent,
                charging_power_kw=telemetry_data.charging_power_kw,
                charging_mode=telemetry_data.charging_mode,
                temperature_celsius=telemetry_data.temperature_celsius,
                cloud_cover_percent=telemetry_data.cloud_cover_percent,
                metadata=telemetry_data.metadata
            )
            
            # Store in database
            db.add(telemetry)
            db.commit()
            db.refresh(telemetry)
            
            logger.info(f"Telemetry stored with ID: {telemetry.id}")
            
            # Cache latest telemetry
            await self._cache_latest_telemetry(telemetry)
            
            return telemetry
            
        except Exception as e:
            logger.error(f"Failed to process telemetry: {str(e)}")
            db.rollback()
            raise
    
    async def _cache_latest_telemetry(self, telemetry: Telemetry):
        """
        Cache the latest telemetry in Redis
        
        Args:
            telemetry: Telemetry instance to cache
        """
        try:
            telemetry_dict = telemetry.to_dict()
            telemetry_json = json.dumps(telemetry_dict)
            
            # Cache with 5 minute TTL
            cache_set(self.CACHE_KEY_LATEST, telemetry_json, ttl=300)
            
            logger.debug("Latest telemetry cached in Redis")
            
        except Exception as e:
            logger.warning(f"Failed to cache telemetry: {str(e)}")
            # Don't fail the request if caching fails
    
    async def get_latest_telemetry(self, db: Session) -> Optional[Telemetry]:
        """
        Get the most recent telemetry data
        First checks cache, then database
        
        Args:
            db: Database session
            
        Returns:
            Latest Telemetry instance or None
        """
        # Try cache first
        cached = cache_get(self.CACHE_KEY_LATEST)
        if cached:
            logger.debug("Retrieved latest telemetry from cache")
            # Note: This returns JSON, not a Telemetry object
            # For API responses, this is fine. For DB operations, query DB.
        
        # Query database
        try:
            telemetry = db.query(Telemetry).order_by(
                Telemetry.timestamp.desc()
            ).first()
            
            if telemetry:
                logger.debug(f"Retrieved latest telemetry from DB: ID {telemetry.id}")
                # Update cache
                await self._cache_latest_telemetry(telemetry)
            
            return telemetry
            
        except Exception as e:
            logger.error(f"Failed to get latest telemetry: {str(e)}")
            return None
    
    async def get_telemetry_history(
        self,
        db: Session,
        limit: int = 100,
        offset: int = 0
    ) -> list[Telemetry]:
        """
        Get historical telemetry data with pagination
        
        Args:
            db: Database session
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of Telemetry instances
        """
        try:
            telemetry_list = db.query(Telemetry).order_by(
                Telemetry.timestamp.desc()
            ).limit(limit).offset(offset).all()
            
            logger.info(f"Retrieved {len(telemetry_list)} telemetry records")
            
            return telemetry_list
            
        except Exception as e:
            logger.error(f"Failed to get telemetry history: {str(e)}")
            return []
    
    def validate_telemetry(self, data: Dict[str, Any]) -> TelemetryData:
        """
        Validate incoming telemetry data
        
        Args:
            data: Raw telemetry data dictionary
            
        Returns:
            Validated TelemetryData instance
            
        Raises:
            ValidationError: If data is invalid
        """
        return TelemetryData(**data)
    
    def format_for_bob(self, telemetry: Telemetry) -> Dict[str, Any]:
        """
        Format telemetry data for IBM Bob API
        
        Args:
            telemetry: Telemetry instance
            
        Returns:
            Dictionary formatted for Bob API
        """
        return {
            "solar": {
                "generation_kw": telemetry.solar_generation_kw,
                "capacity_kw": telemetry.solar_capacity_kw
            },
            "grid": {
                "price_per_kwh": telemetry.grid_price_per_kwh,
                "carbon_intensity": telemetry.grid_carbon_intensity
            },
            "ev_battery": {
                "soc_percent": telemetry.battery_soc_percent,
                "capacity_kwh": telemetry.battery_capacity_kwh,
                "health_percent": telemetry.battery_health_percent
            },
            "charging": {
                "power_kw": telemetry.charging_power_kw,
                "mode": telemetry.charging_mode
            },
            "weather": {
                "temperature_celsius": telemetry.temperature_celsius,
                "cloud_cover_percent": telemetry.cloud_cover_percent
            }
        }


# Global processor instance
telemetry_processor = TelemetryProcessor()

# Made with Bob