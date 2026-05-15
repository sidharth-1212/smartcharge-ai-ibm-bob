"""
Quick test script for the telemetry simulator
Tests telemetry generation without requiring backend connection
"""

import json
from simulator import TelemetrySimulator

def test_telemetry_generation():
    """Test that simulator generates valid telemetry data"""
    print("Testing SmartCharge AI Telemetry Simulator...")
    print("=" * 80)
    
    # Create simulator instance
    simulator = TelemetrySimulator(backend_url="http://localhost:8000")
    
    # Generate a few telemetry samples
    print("\nGenerating 3 telemetry samples...\n")
    
    for i in range(3):
        telemetry = simulator.generate_telemetry()
        
        # Validate structure
        assert "timestamp" in telemetry, "Missing timestamp"
        assert "solar" in telemetry, "Missing solar data"
        assert "grid" in telemetry, "Missing grid data"
        assert "ev_battery" in telemetry, "Missing battery data"
        assert "charging" in telemetry, "Missing charging data"
        assert "metadata" in telemetry, "Missing metadata"
        
        # Validate solar data
        assert 0 <= telemetry["solar"]["generation_kw"] <= 5.5, "Solar generation out of range"
        assert telemetry["solar"]["max_capacity_kw"] == 5.5, "Solar max capacity incorrect"
        
        # Validate grid data
        assert 0.12 <= telemetry["grid"]["price_per_kwh"] <= 0.35, "Grid price out of range"
        assert telemetry["grid"]["draw_kw"] >= 0, "Grid draw cannot be negative"
        
        # Validate battery data
        assert 0 <= telemetry["ev_battery"]["soc_percent"] <= 100, "Battery SOC out of range"
        assert telemetry["ev_battery"]["capacity_kwh"] == 75.0, "Battery capacity incorrect"
        
        # Validate charging mode
        assert telemetry["charging"]["mode"] in ["FAST_CHARGE", "ECO_MODE", "PAUSED"], "Invalid charging mode"
        
        print(f"Sample {i+1}:")
        print(f"  Solar: {telemetry['solar']['generation_kw']} kW")
        print(f"  Grid Price: ${telemetry['grid']['price_per_kwh']}/kWh")
        print(f"  Battery SOC: {telemetry['ev_battery']['soc_percent']}%")
        print(f"  Charging Mode: {telemetry['charging']['mode']}")
        print(f"  Simulated Hour: {telemetry['simulated_hour']}")
        print()
    
    print("=" * 80)
    print("[PASS] All tests passed!")
    print("[PASS] Telemetry structure is valid")
    print("[PASS] All values are within expected ranges")
    print("[PASS] Simulator is ready to use")
    print("=" * 80)

if __name__ == "__main__":
    test_telemetry_generation()

# Made with Bob
