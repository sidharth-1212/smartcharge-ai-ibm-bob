-- SmartCharge AI - Database Initialization Script
-- PostgreSQL 15+

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create telemetry table
CREATE TABLE IF NOT EXISTS telemetry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    iteration INTEGER NOT NULL,
    time_of_day_factor DECIMAL(5,3),
    simulated_hour DECIMAL(4,1),
    
    -- Solar data
    solar_generation_kw DECIMAL(6,2),
    solar_max_capacity_kw DECIMAL(6,2),
    solar_utilization_percent DECIMAL(5,1),
    
    -- Grid data
    grid_price_per_kwh DECIMAL(6,3),
    grid_draw_kw DECIMAL(6,2),
    grid_status VARCHAR(20),
    
    -- EV Battery data
    battery_soc_percent DECIMAL(5,1),
    battery_capacity_kwh DECIMAL(6,2),
    battery_charging_rate_kw DECIMAL(6,2),
    battery_time_to_full_hours DECIMAL(6,2),
    
    -- Charging data
    charging_mode VARCHAR(20),
    charging_power_source VARCHAR(20),
    charging_cost_per_hour DECIMAL(8,3),
    
    -- Metadata
    location VARCHAR(100),
    timezone VARCHAR(50),
    
    -- Indexes
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create decisions table
CREATE TABLE IF NOT EXISTS decisions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Decision details
    decision_mode VARCHAR(20) NOT NULL,
    reasoning TEXT,
    confidence_score DECIMAL(3,2),
    
    -- Context snapshot
    context_solar_kw DECIMAL(6,2),
    context_grid_price DECIMAL(6,3),
    context_battery_soc DECIMAL(5,1),
    
    -- IBM Bob metadata
    bob_response_time_ms INTEGER,
    bob_model_version VARCHAR(50),
    bob_session_id VARCHAR(100),
    
    -- Outcome tracking
    estimated_cost_savings DECIMAL(8,2),
    estimated_renewable_percent DECIMAL(5,1),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create users table (for future multi-user support)
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- User preferences
    preferred_charging_mode VARCHAR(20) DEFAULT 'AUTO',
    max_charging_rate_kw DECIMAL(6,2) DEFAULT 11.0,
    target_soc_percent DECIMAL(5,1) DEFAULT 80.0,
    
    -- Subscription
    subscription_tier VARCHAR(20) DEFAULT 'BASIC',
    subscription_status VARCHAR(20) DEFAULT 'ACTIVE',
    subscription_expires_at TIMESTAMPTZ,
    
    -- Metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_login_at TIMESTAMPTZ
);

-- Create vehicles table
CREATE TABLE IF NOT EXISTS vehicles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    
    -- Vehicle details
    make VARCHAR(50),
    model VARCHAR(50),
    year INTEGER,
    vin VARCHAR(17) UNIQUE,
    
    -- Battery specs
    battery_capacity_kwh DECIMAL(6,2) NOT NULL,
    max_charging_rate_kw DECIMAL(6,2) NOT NULL,
    current_soc_percent DECIMAL(5,1),
    
    -- Charging preferences
    preferred_charging_schedule JSONB,
    home_charger_type VARCHAR(50),
    
    -- Metadata
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create analytics summary table
CREATE TABLE IF NOT EXISTS analytics_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    date DATE NOT NULL,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    vehicle_id UUID REFERENCES vehicles(id) ON DELETE CASCADE,
    
    -- Daily metrics
    total_energy_charged_kwh DECIMAL(8,2),
    total_cost_usd DECIMAL(8,2),
    estimated_savings_usd DECIMAL(8,2),
    renewable_energy_percent DECIMAL(5,1),
    
    -- Charging breakdown
    fast_charge_hours DECIMAL(6,2),
    eco_mode_hours DECIMAL(6,2),
    paused_hours DECIMAL(6,2),
    
    -- Grid impact
    peak_hour_usage_kwh DECIMAL(8,2),
    off_peak_usage_kwh DECIMAL(8,2),
    
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    UNIQUE(date, user_id, vehicle_id)
);

-- Create indexes for performance
CREATE INDEX idx_telemetry_timestamp ON telemetry(timestamp DESC);
CREATE INDEX idx_telemetry_iteration ON telemetry(iteration);
CREATE INDEX idx_decisions_timestamp ON decisions(timestamp DESC);
CREATE INDEX idx_decisions_request_id ON decisions(request_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_vehicles_user_id ON vehicles(user_id);
CREATE INDEX idx_analytics_date ON analytics_summary(date DESC);
CREATE INDEX idx_analytics_user_id ON analytics_summary(user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_vehicles_updated_at BEFORE UPDATE ON vehicles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert demo user (password: demo123)
INSERT INTO users (email, username, password_hash, subscription_tier)
VALUES (
    'demo@smartcharge.ai',
    'demo_user',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqNqNqNqNq', -- demo123
    'PREMIUM'
) ON CONFLICT (email) DO NOTHING;

-- Insert demo vehicle
INSERT INTO vehicles (
    user_id,
    make,
    model,
    year,
    battery_capacity_kwh,
    max_charging_rate_kw,
    current_soc_percent,
    home_charger_type
)
SELECT 
    id,
    'Tesla',
    'Model 3',
    2024,
    75.0,
    11.0,
    65.0,
    'Level 2 (240V)'
FROM users WHERE email = 'demo@smartcharge.ai'
ON CONFLICT (vin) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO smartcharge;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO smartcharge;

-- Create view for recent telemetry
CREATE OR REPLACE VIEW recent_telemetry AS
SELECT 
    t.*,
    d.decision_mode as bob_decision,
    d.reasoning as bob_reasoning
FROM telemetry t
LEFT JOIN decisions d ON d.timestamp >= t.timestamp - INTERVAL '5 seconds'
    AND d.timestamp <= t.timestamp + INTERVAL '5 seconds'
ORDER BY t.timestamp DESC
LIMIT 100;

-- Create view for daily analytics
CREATE OR REPLACE VIEW daily_analytics AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_readings,
    AVG(solar_generation_kw) as avg_solar_kw,
    AVG(grid_price_per_kwh) as avg_grid_price,
    AVG(battery_soc_percent) as avg_battery_soc,
    SUM(CASE WHEN charging_mode = 'FAST_CHARGE' THEN 1 ELSE 0 END) as fast_charge_count,
    SUM(CASE WHEN charging_mode = 'ECO_MODE' THEN 1 ELSE 0 END) as eco_mode_count,
    SUM(CASE WHEN charging_mode = 'PAUSED' THEN 1 ELSE 0 END) as paused_count,
    SUM(charging_cost_per_hour * 5.0 / 3600.0) as total_cost_usd
FROM telemetry
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'SmartCharge AI database initialized successfully!';
    RAISE NOTICE 'Demo user created: demo@smartcharge.ai (password: demo123)';
END $$;

-- Made with Bob
