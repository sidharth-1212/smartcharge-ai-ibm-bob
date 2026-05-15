"""
Test script for IBM Bob API integration
Run this to verify your IBM Bob API credentials are working
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.bob_service import BobService, BobDecisionRequest
from app.config import settings


async def test_bob_connection():
    """Test basic connection to IBM Bob API"""
    print("=" * 60)
    print("IBM Bob API Connection Test")
    print("=" * 60)
    print()
    
    # Display configuration
    print("Configuration:")
    print(f"  API URL: {settings.ibm_bob_api_url}")
    print(f"  Project ID: {settings.ibm_bob_project_id}")
    print(f"  Model ID: {settings.ibm_bob_model_id}")
    print(f"  API Key: {'*' * 20}{settings.ibm_bob_api_key[-4:] if len(settings.ibm_bob_api_key) > 4 else '****'}")
    print()
    
    # Create Bob service
    bob = BobService()
    
    # Create a test telemetry scenario
    test_telemetry = {
        "solar": {
            "generation_kw": 4.5,
            "capacity_kw": 5.5
        },
        "grid": {
            "price_per_kwh": 0.18,
            "peak_hours": False
        },
        "ev_battery": {
            "soc_percent": 45.0,
            "capacity_kwh": 75.0,
            "charging_rate_kw": 0.0
        }
    }
    
    print("Test Scenario:")
    print(f"  Solar Generation: {test_telemetry['solar']['generation_kw']} kW")
    print(f"  Grid Price: ${test_telemetry['grid']['price_per_kwh']:.3f}/kWh")
    print(f"  Battery Level: {test_telemetry['ev_battery']['soc_percent']}%")
    print()
    
    # Create decision request
    request = BobDecisionRequest(
        request_id="test_001",
        telemetry=test_telemetry,
        user_preferences={
            "priority": "cost_savings",
            "renewable_preference": "high"
        }
    )
    
    print("Requesting decision from IBM Bob...")
    print()
    
    try:
        # Get decision from Bob
        decision = await bob.get_charging_decision(request)
        
        # Display results
        print("✅ SUCCESS! IBM Bob API is working!")
        print()
        print("Decision Details:")
        print(f"  Charging Mode: {decision.charging_mode.value}")
        print(f"  Confidence: {decision.confidence:.1%}")
        print(f"  Estimated Cost: ${decision.estimated_cost:.2f}/hour")
        print(f"  Time to Full: {decision.estimated_time_hours:.1f} hours")
        print(f"  Renewable Energy: {decision.renewable_percentage:.1f}%")
        print()
        print("Reasoning:")
        print(f"  {decision.reasoning}")
        print()
        
        if decision.metadata.get("fallback"):
            print("⚠️  Note: This was a fallback decision (rule-based)")
            print("   Check your IBM Bob API credentials if this persists")
        
        return True
        
    except Exception as e:
        print("❌ ERROR: Failed to get decision from IBM Bob")
        print()
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        print()
        print("Troubleshooting:")
        print("  1. Check your .env file has correct IBM_BOB_API_KEY")
        print("  2. Verify IBM_BOB_PROJECT_ID is correct")
        print("  3. Ensure your IBM Cloud account has access to watsonx.ai")
        print("  4. Check your internet connection")
        print("  5. Verify the API endpoint URL is correct")
        print()
        return False


async def test_multiple_scenarios():
    """Test Bob with multiple different scenarios"""
    print("=" * 60)
    print("Testing Multiple Scenarios")
    print("=" * 60)
    print()
    
    bob = BobService()
    
    scenarios = [
        {
            "name": "High Solar, Low Battery",
            "telemetry": {
                "solar": {"generation_kw": 5.2, "capacity_kw": 5.5},
                "grid": {"price_per_kwh": 0.15, "peak_hours": False},
                "ev_battery": {"soc_percent": 25.0, "capacity_kwh": 75.0, "charging_rate_kw": 0.0}
            }
        },
        {
            "name": "Peak Pricing, Full Battery",
            "telemetry": {
                "solar": {"generation_kw": 0.5, "capacity_kw": 5.5},
                "grid": {"price_per_kwh": 0.35, "peak_hours": True},
                "ev_battery": {"soc_percent": 92.0, "capacity_kwh": 75.0, "charging_rate_kw": 0.0}
            }
        },
        {
            "name": "No Solar, Cheap Grid",
            "telemetry": {
                "solar": {"generation_kw": 0.0, "capacity_kw": 5.5},
                "grid": {"price_per_kwh": 0.12, "peak_hours": False},
                "ev_battery": {"soc_percent": 55.0, "capacity_kwh": 75.0, "charging_rate_kw": 0.0}
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"Scenario {i}: {scenario['name']}")
        print("-" * 60)
        
        request = BobDecisionRequest(
            request_id=f"test_{i:03d}",
            telemetry=scenario["telemetry"]
        )
        
        try:
            decision = await bob.get_charging_decision(request)
            print(f"  Mode: {decision.charging_mode.value}")
            print(f"  Reasoning: {decision.reasoning[:100]}...")
            print()
        except Exception as e:
            print(f"  ❌ Error: {str(e)}")
            print()


def main():
    """Main test function"""
    print()
    print("🔌 SmartCharge AI - IBM Bob API Test")
    print()
    
    # Check if .env file exists
    env_file = Path(__file__).parent / ".env"
    if not env_file.exists():
        print("❌ ERROR: .env file not found!")
        print()
        print("Please create a .env file in the backend directory with:")
        print("  IBM_BOB_API_KEY=your_api_key")
        print("  IBM_BOB_PROJECT_ID=your_project_id")
        print()
        print("You can copy .env.example and fill in your credentials.")
        return
    
    # Run basic connection test
    success = asyncio.run(test_bob_connection())
    
    if success:
        print()
        response = input("Would you like to test multiple scenarios? (y/n): ")
        if response.lower() == 'y':
            asyncio.run(test_multiple_scenarios())
    
    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()

# Made with Bob
