"""
SmartCharge AI - Edge Telemetry Simulator
Generates realistic solar, grid, and EV battery telemetry data
Sends telemetry to backend API every 5 seconds
"""

import json
import time
import math
import random
import os
from datetime import datetime
from typing import Dict, Any
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelemetrySimulator:
    """Simulates real-time telemetry data for EV charging optimization"""
    
    def __init__(self, backend_url: str = None):
        self.start_time = time.time()
        self.iteration = 0
        
        # Backend API configuration (use localhost for local development)
        self.backend_url = backend_url or os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.api_endpoint = f"{self.backend_url}/api/telemetry/ingest"
        
        # Solar generation parameters (peaks at noon)
        self.solar_max_kw = 5.5  # Maximum solar generation
        self.solar_baseline_kw = 0.0
        
        # Grid pricing parameters (peaks in evening)
        self.grid_price_base = 0.12  # Base price per kWh
        self.grid_price_peak = 0.35  # Peak price per kWh
        
        # EV battery parameters
        self.battery_capacity_kwh = 75.0  # Tesla Model 3 Long Range
        self.battery_soc_percent = 20.0  # Starting state of charge
        self.charging_rate_kw = 0.0  # Current charging rate
        
        # Charging mode
        self.charging_mode = "PAUSED"  # FAST_CHARGE, ECO_MODE, PAUSED
        
    def get_time_of_day_factor(self) -> float:
        """Calculate time of day factor (0-1) for 24-hour cycle"""
        # Simulate 24-hour cycle in 5 minutes (288 seconds)
        cycle_duration = 288  # seconds for full 24-hour simulation
        elapsed = (time.time() - self.start_time) % cycle_duration
        return elapsed / cycle_duration
    
    def calculate_solar_generation(self) -> float:
        """Calculate solar generation based on time of day (sine wave)"""
        time_factor = self.get_time_of_day_factor()
        
        # Solar peaks at midday (0.5 in our cycle)
        # Use sine wave: peaks at 0.5, zero at 0 and 1
        solar_factor = math.sin(time_factor * 2 * math.pi)
        solar_factor = max(0, solar_factor)  # No negative solar
        
        # Add some realistic noise
        noise = random.uniform(-0.1, 0.1)
        solar_kw = self.solar_max_kw * solar_factor * (1 + noise)
        
        return max(0, min(self.solar_max_kw, solar_kw))
    
    def calculate_grid_price(self) -> float:
        """Calculate grid price based on time of day"""
        time_factor = self.get_time_of_day_factor()
        
        # Peak pricing in evening (0.7-0.9 in our cycle)
        # Use shifted cosine wave
        price_factor = -math.cos((time_factor - 0.8) * 2 * math.pi)
        price_factor = (price_factor + 1) / 2  # Normalize to 0-1
        
        # Calculate price
        price_range = self.grid_price_peak - self.grid_price_base
        grid_price = self.grid_price_base + (price_range * price_factor)
        
        return round(grid_price, 3)
    
    def update_battery_soc(self, charging_rate_kw: float, interval_seconds: float = 5):
        """Update battery state of charge based on charging rate"""
        if self.battery_soc_percent >= 100.0:
            self.battery_soc_percent = 100.0
            return
        
        # Calculate energy added in this interval
        hours = interval_seconds / 3600
        energy_added_kwh = charging_rate_kw * hours
        
        # Update SOC percentage
        soc_increase = (energy_added_kwh / self.battery_capacity_kwh) * 100
        self.battery_soc_percent = min(100.0, self.battery_soc_percent + soc_increase)
    
    def simulate_charging_response(self, mode: str) -> float:
        """Simulate charging rate based on mode"""
        if mode == "FAST_CHARGE":
            return 11.0  # 11 kW Level 2 charger
        elif mode == "ECO_MODE":
            return 3.5   # Reduced charging rate
        else:  # PAUSED
            return 0.0
    
    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate complete telemetry snapshot"""
        self.iteration += 1
        
        # Calculate current values
        solar_kw = self.calculate_solar_generation()
        grid_price = self.calculate_grid_price()
        time_factor = self.get_time_of_day_factor()
        
        # Simulate charging (in real system, this comes from Bob's decision)
        # For demo, use simple logic
        if solar_kw > 4.0 and self.battery_soc_percent < 80:
            self.charging_mode = "FAST_CHARGE"
        elif solar_kw > 2.0 and grid_price < 0.20 and self.battery_soc_percent < 90:
            self.charging_mode = "ECO_MODE"
        else:
            self.charging_mode = "PAUSED"
        
        self.charging_rate_kw = self.simulate_charging_response(self.charging_mode)
        self.update_battery_soc(self.charging_rate_kw)
        
        # Calculate grid draw (charging rate minus solar)
        grid_draw_kw = max(0, self.charging_rate_kw - solar_kw)
        
        # Build telemetry payload
        telemetry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "iteration": self.iteration,
            "time_of_day_factor": round(time_factor, 3),
            "simulated_hour": round(time_factor * 24, 1),
            
            "solar": {
                "generation_kw": round(solar_kw, 2),
                "max_capacity_kw": self.solar_max_kw,
                "utilization_percent": round((solar_kw / self.solar_max_kw) * 100, 1)
            },
            
            "grid": {
                "price_per_kwh": grid_price,
                "draw_kw": round(grid_draw_kw, 2),
                "status": "PEAK" if grid_price > 0.25 else "NORMAL"
            },
            
            "ev_battery": {
                "soc_percent": round(self.battery_soc_percent, 1),
                "capacity_kwh": self.battery_capacity_kwh,
                "charging_rate_kw": round(self.charging_rate_kw, 2),
                "estimated_time_to_full_hours": self._calculate_time_to_full()
            },
            
            "charging": {
                "mode": self.charging_mode,
                "power_source": "SOLAR" if solar_kw > self.charging_rate_kw else "GRID",
                "cost_per_hour": round(grid_draw_kw * grid_price, 3)
            },
            
            "metadata": {
                "simulator_version": "1.0.0",
                "location": "San Francisco, CA",
                "timezone": "America/Los_Angeles"
            }
        }
        
        return telemetry
    
    def _calculate_time_to_full(self) -> float:
        """Calculate estimated time to full charge"""
        if self.charging_rate_kw == 0 or self.battery_soc_percent >= 100:
            return 0.0
        
        remaining_kwh = self.battery_capacity_kwh * (100 - self.battery_soc_percent) / 100
        hours_to_full = remaining_kwh / self.charging_rate_kw
        return round(hours_to_full, 2)
    
    def send_telemetry(self, telemetry: Dict[str, Any]) -> bool:
        """Send telemetry data to backend API"""
        try:
            response = requests.post(
                self.api_endpoint,
                json=telemetry,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            if response.status_code == 200:
                logger.debug(f"Telemetry sent successfully: {response.json()}")
                return True
            else:
                logger.warning(f"Failed to send telemetry: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.ConnectionError:
            logger.warning(f"Cannot connect to backend at {self.api_endpoint}")
            return False
        except requests.exceptions.Timeout:
            logger.warning("Request timeout while sending telemetry")
            return False
        except Exception as e:
            logger.error(f"Error sending telemetry: {e}")
            return False
    
    def run(self, interval_seconds: int = 5, output_file: str = None):
        """Run continuous telemetry generation"""
        logger.info("=" * 80)
        logger.info("Starting SmartCharge AI Telemetry Simulator")
        logger.info("=" * 80)
        logger.info(f"Backend API: {self.api_endpoint}")
        logger.info(f"Interval: {interval_seconds} seconds")
        logger.info(f"Battery Capacity: {self.battery_capacity_kwh} kWh")
        logger.info(f"Solar Max: {self.solar_max_kw} kW")
        logger.info(f"Initial Battery SOC: {self.battery_soc_percent}%")
        logger.info("=" * 80)
        
        consecutive_failures = 0
        max_failures = 3
        
        try:
            while True:
                telemetry = self.generate_telemetry()
                
                # Print to console
                print(json.dumps(telemetry, indent=2))
                print("-" * 80)
                
                # Send to backend API
                success = self.send_telemetry(telemetry)
                
                if success:
                    consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    if consecutive_failures >= max_failures:
                        logger.warning(
                            f"Backend unavailable after {max_failures} attempts. "
                            "Continuing in offline mode..."
                        )
                        consecutive_failures = 0  # Reset to avoid spam
                
                # Optionally write to file
                if output_file:
                    with open(output_file, 'a') as f:
                        f.write(json.dumps(telemetry) + '\n')
                
                # Log key metrics
                logger.info(
                    f"Iteration {self.iteration} | "
                    f"Solar: {telemetry['solar']['generation_kw']}kW | "
                    f"Grid: ${telemetry['grid']['price_per_kwh']}/kWh | "
                    f"Battery: {telemetry['ev_battery']['soc_percent']}% | "
                    f"Mode: {telemetry['charging']['mode']} | "
                    f"API: {'✓' if success else '✗'}"
                )
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("\n" + "=" * 80)
            logger.info("Simulator stopped by user")
            logger.info("=" * 80)
        except Exception as e:
            logger.error(f"Simulator error: {e}", exc_info=True)


def main():
    """Main entry point"""
    # Allow backend URL override via environment variable
    backend_url = os.getenv('BACKEND_URL', 'http://backend:8000')
    
    simulator = TelemetrySimulator(backend_url=backend_url)
    simulator.run(interval_seconds=5)


if __name__ == "__main__":
    main()

# Made with Bob
