"""
Database models for SmartCharge AI
Defines SQLAlchemy ORM models for telemetry, decisions, and users
"""

from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class Telemetry(Base):
    """Telemetry data from EV charging system"""
    __tablename__ = "telemetry"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Solar generation data
    solar_generation_kw = Column(Float, nullable=False, default=0.0)
    solar_capacity_kw = Column(Float, nullable=False, default=10.0)
    
    # Grid data
    grid_price_per_kwh = Column(Float, nullable=False, default=0.0)
    grid_carbon_intensity = Column(Float, nullable=True)
    
    # EV Battery data
    battery_soc_percent = Column(Float, nullable=False, default=0.0)
    battery_capacity_kwh = Column(Float, nullable=False, default=75.0)
    battery_health_percent = Column(Float, nullable=True, default=100.0)
    
    # Charging data
    charging_power_kw = Column(Float, nullable=False, default=0.0)
    charging_mode = Column(String(50), nullable=True)
    
    # Weather data (optional)
    temperature_celsius = Column(Float, nullable=True)
    cloud_cover_percent = Column(Float, nullable=True)
    
    # Additional metadata
    extra_metadata = Column(JSON, nullable=True)
    
    # Relationships
    decisions = relationship("Decision", back_populates="telemetry")
    
    def __repr__(self):
        return f"<Telemetry(id={self.id}, timestamp={self.timestamp}, soc={self.battery_soc_percent}%)>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "solar": {
                "generation_kw": self.solar_generation_kw,
                "capacity_kw": self.solar_capacity_kw
            },
            "grid": {
                "price_per_kwh": self.grid_price_per_kwh,
                "carbon_intensity": self.grid_carbon_intensity
            },
            "ev_battery": {
                "soc_percent": self.battery_soc_percent,
                "capacity_kwh": self.battery_capacity_kwh,
                "health_percent": self.battery_health_percent
            },
            "charging": {
                "power_kw": self.charging_power_kw,
                "mode": self.charging_mode
            },
            "weather": {
                "temperature_celsius": self.temperature_celsius,
                "cloud_cover_percent": self.cloud_cover_percent
            },
            "metadata": self.extra_metadata
        }


class Decision(Base):
    """AI-generated charging decisions from IBM Bob"""
    __tablename__ = "decisions"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Decision details
    charging_mode = Column(String(50), nullable=False)
    reasoning = Column(Text, nullable=False)
    confidence = Column(Float, nullable=False, default=0.0)
    
    # Estimates
    estimated_cost = Column(Float, nullable=True)
    estimated_time_hours = Column(Float, nullable=True)
    renewable_percentage = Column(Float, nullable=True)
    
    # Telemetry reference
    telemetry_id = Column(Integer, ForeignKey("telemetry.id"), nullable=True)
    telemetry = relationship("Telemetry", back_populates="decisions")
    
    # Execution tracking
    applied = Column(Boolean, default=False)
    applied_at = Column(DateTime, nullable=True)
    
    # Additional metadata from Bob
    extra_metadata = Column(JSON, nullable=True)
    
    # User override tracking
    overridden = Column(Boolean, default=False)
    override_reason = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Decision(id={self.id}, mode={self.charging_mode}, confidence={self.confidence})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "charging_mode": self.charging_mode,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "estimated_cost": self.estimated_cost,
            "estimated_time_hours": self.estimated_time_hours,
            "renewable_percentage": self.renewable_percentage,
            "telemetry_id": self.telemetry_id,
            "applied": self.applied,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "overridden": self.overridden,
            "override_reason": self.override_reason,
            "metadata": self.extra_metadata
        }


class User(Base):
    """User accounts and preferences (optional for MVP)"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # User preferences
    preferred_charging_mode = Column(String(50), nullable=True)
    max_charging_cost_per_day = Column(Float, nullable=True)
    min_battery_soc_percent = Column(Float, default=20.0)
    target_battery_soc_percent = Column(Float, default=80.0)
    
    # Notification preferences
    notifications_enabled = Column(Boolean, default=True)
    notification_email = Column(String(255), nullable=True)
    
    # User preferences JSON
    preferences_json = Column(JSON, nullable=True)
    
    # Account status
    active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, user_id={self.user_id}, email={self.email})>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "preferred_charging_mode": self.preferred_charging_mode,
            "max_charging_cost_per_day": self.max_charging_cost_per_day,
            "min_battery_soc_percent": self.min_battery_soc_percent,
            "target_battery_soc_percent": self.target_battery_soc_percent,
            "notifications_enabled": self.notifications_enabled,
            "notification_email": self.notification_email,
            "preferences": self.preferences_json,
            "active": self.active
        }


class ChargingSession(Base):
    """Track charging sessions for analytics"""
    __tablename__ = "charging_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # Session timing
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Energy metrics
    energy_delivered_kwh = Column(Float, default=0.0)
    energy_from_solar_kwh = Column(Float, default=0.0)
    energy_from_grid_kwh = Column(Float, default=0.0)
    
    # Cost metrics
    total_cost = Column(Float, default=0.0)
    average_price_per_kwh = Column(Float, nullable=True)
    
    # Battery metrics
    starting_soc_percent = Column(Float, nullable=True)
    ending_soc_percent = Column(Float, nullable=True)
    soc_gained_percent = Column(Float, nullable=True)
    
    # Session metadata
    charging_modes_used = Column(JSON, nullable=True)  # List of modes used during session
    decisions_count = Column(Integer, default=0)
    extra_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<ChargingSession(id={self.id}, session_id={self.session_id}, energy={self.energy_delivered_kwh}kWh)>"
    
    def to_dict(self):
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_minutes": self.duration_minutes,
            "energy_delivered_kwh": self.energy_delivered_kwh,
            "energy_from_solar_kwh": self.energy_from_solar_kwh,
            "energy_from_grid_kwh": self.energy_from_grid_kwh,
            "total_cost": self.total_cost,
            "average_price_per_kwh": self.average_price_per_kwh,
            "starting_soc_percent": self.starting_soc_percent,
            "ending_soc_percent": self.ending_soc_percent,
            "soc_gained_percent": self.soc_gained_percent,
            "charging_modes_used": self.charging_modes_used,
            "decisions_count": self.decisions_count,
            "metadata": self.extra_metadata
        }

# Made with Bob