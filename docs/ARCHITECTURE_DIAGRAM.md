# SmartCharge AI - System Architecture

## High-Level Architecture Diagram

```mermaid
graph TB
    subgraph "Edge Layer"
        SIM[Simulator Container<br/>Python + Docker<br/>Generates Telemetry]
    end
    
    subgraph "Backend Layer"
        API[FastAPI Backend<br/>Port 8000]
        BOB[IBM Bob Service<br/>Decision Engine]
        DB[(PostgreSQL<br/>Telemetry & Decisions)]
        CACHE[Redis Cache<br/>Real-time Data]
    end
    
    subgraph "Frontend Layer"
        UI[React + Vite<br/>Port 5173]
        CHARTS[Recharts<br/>Real-time Visualization]
    end
    
    subgraph "External Services"
        IBM[IBM Bob API<br/>watsonx.ai]
        GRID[Grid Pricing API<br/>Optional]
        SOLAR[Solar API<br/>Optional]
    end
    
    SIM -->|JSON Telemetry<br/>Every 5s| API
    API -->|Store Data| DB
    API -->|Cache Latest| CACHE
    API -->|Decision Request| BOB
    BOB -->|AI Analysis| IBM
    IBM -->|Decision Response| BOB
    BOB -->|Store Decision| DB
    API <-->|WebSocket<br/>Real-time Stream| UI
    UI -->|Render Charts| CHARTS
    API -.->|Optional| GRID
    API -.->|Optional| SOLAR
    
    style SIM fill:#e1f5ff
    style API fill:#fff4e1
    style BOB fill:#ffe1f5
    style UI fill:#e1ffe1
    style IBM fill:#f5e1ff
```

## Data Flow Sequence

```mermaid
sequenceDiagram
    participant S as Simulator
    participant B as Backend
    participant Bob as IBM Bob
    participant DB as Database
    participant UI as Frontend
    
    loop Every 5 seconds
        S->>B: POST /api/telemetry/ingest<br/>{solar, grid, battery}
        B->>DB: Store telemetry
        B->>Bob: Request decision<br/>with context
        Bob->>IBM: Analyze telemetry<br/>+ constraints
        IBM-->>Bob: Recommended mode<br/>+ reasoning
        Bob->>DB: Store decision
        Bob-->>B: Decision response
        B->>UI: WebSocket push<br/>{telemetry + decision}
        UI->>UI: Update gauges<br/>+ event log
    end
    
    UI->>B: GET /api/analytics/summary
    B->>DB: Query historical data
    DB-->>B: Aggregated metrics
    B-->>UI: Cost savings, renewable %
```

## Component Architecture

```mermaid
graph LR
    subgraph "Simulator Service"
        SIMPY[simulator.py]
        SIMCONF[Configuration]
        SIMLOG[Logging]
    end
    
    subgraph "Backend Service"
        MAIN[main.py<br/>FastAPI App]
        
        subgraph "Routers"
            RTEL[telemetry.py]
            RCHARGE[charging.py]
            RBOB[bob.py]
        end
        
        subgraph "Services"
            SBOB[bob_service.py]
            SDEC[decision_engine.py]
            STEL[telemetry_processor.py]
        end
        
        subgraph "Models"
            MTEL[Telemetry Model]
            MDEC[Decision Model]
            MUSER[User Model]
        end
    end
    
    subgraph "Frontend Service"
        APP[App.jsx]
        
        subgraph "Components"
            DASH[Dashboard]
            GAUGE[PowerGauge]
            BOBUI[BobController]
            LOG[EventLog]
        end
        
        subgraph "Hooks"
            HWS[useWebSocket]
            HTEL[useTelemetry]
        end
        
        subgraph "Services"
            FAPI[api.js]
        end
    end
    
    SIMPY --> MAIN
    MAIN --> RTEL
    MAIN --> RCHARGE
    MAIN --> RBOB
    RTEL --> STEL
    RBOB --> SBOB
    SBOB --> SDEC
    STEL --> MTEL
    SDEC --> MDEC
    MAIN --> APP
    APP --> DASH
    DASH --> GAUGE
    DASH --> BOBUI
    DASH --> LOG
    GAUGE --> HWS
    BOBUI --> HTEL
    HWS --> FAPI
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV[Docker Compose<br/>Local Development]
        DEVSIM[Simulator Container]
        DEVBACK[Backend Container]
        DEVFRONT[Frontend Dev Server]
        DEVDB[PostgreSQL Container]
        DEVREDIS[Redis Container]
    end
    
    subgraph "Production Environment"
        LB[Load Balancer<br/>NGINX/Traefik]
        
        subgraph "Application Tier"
            BACK1[Backend Instance 1]
            BACK2[Backend Instance 2]
            BACK3[Backend Instance 3]
        end
        
        subgraph "Data Tier"
            DBPROD[(PostgreSQL<br/>Primary)]
            DBREPLICA[(PostgreSQL<br/>Replica)]
            REDISPROD[Redis Cluster]
        end
        
        subgraph "Frontend Tier"
            CDN[CDN<br/>Vercel/Cloudflare]
            STATIC[Static Assets]
        end
    end
    
    subgraph "External Services"
        IBMPROD[IBM Bob API]
        MONITOR[Monitoring<br/>Datadog/Sentry]
    end
    
    DEV --> DEVSIM
    DEV --> DEVBACK
    DEV --> DEVFRONT
    DEV --> DEVDB
    DEV --> DEVREDIS
    
    LB --> BACK1
    LB --> BACK2
    LB --> BACK3
    BACK1 --> DBPROD
    BACK2 --> DBPROD
    BACK3 --> DBPROD
    DBPROD --> DBREPLICA
    BACK1 --> REDISPROD
    BACK2 --> REDISPROD
    BACK3 --> REDISPROD
    BACK1 --> IBMPROD
    BACK2 --> IBMPROD
    BACK3 --> IBMPROD
    CDN --> STATIC
    BACK1 --> MONITOR
    BACK2 --> MONITOR
    BACK3 --> MONITOR
    
    style DEV fill:#e1f5ff
    style LB fill:#fff4e1
    style DBPROD fill:#ffe1e1
    style CDN fill:#e1ffe1
```

## IBM Bob Integration Flow

```mermaid
graph TD
    START[Telemetry Received] --> VALIDATE[Validate Data]
    VALIDATE --> BUILD[Build Context Object]
    BUILD --> CONTEXT{Context Complete?}
    CONTEXT -->|No| ERROR[Return Error]
    CONTEXT -->|Yes| PROMPT[Generate Bob Prompt]
    PROMPT --> CALL[Call IBM Bob API]
    CALL --> WAIT[Wait for Response]
    WAIT --> PARSE[Parse Decision]
    PARSE --> VALIDATE_DEC[Validate Decision]
    VALIDATE_DEC --> STORE[Store in Database]
    STORE --> BROADCAST[Broadcast to WebSocket]
    BROADCAST --> LOG[Log Decision]
    LOG --> END[Return to Client]
    
    style START fill:#e1f5ff
    style CALL fill:#f5e1ff
    style BROADCAST fill:#e1ffe1
    style END fill:#fff4e1
```

## Security Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        BROWSER[Web Browser]
        MOBILE[Mobile App]
    end
    
    subgraph "Security Layer"
        WAF[Web Application Firewall]
        AUTH[Authentication Service<br/>JWT Tokens]
        RATE[Rate Limiter]
    end
    
    subgraph "Application Layer"
        API[FastAPI Backend]
        BOB[IBM Bob Service]
    end
    
    subgraph "Data Layer"
        DB[(Encrypted Database)]
        SECRETS[Secrets Manager<br/>API Keys]
    end
    
    BROWSER --> WAF
    MOBILE --> WAF
    WAF --> RATE
    RATE --> AUTH
    AUTH --> API
    API --> BOB
    BOB --> SECRETS
    API --> DB
    
    style WAF fill:#ffe1e1
    style AUTH fill:#fff4e1
    style SECRETS fill:#f5e1ff
```

## Technology Stack Overview

```mermaid
mindmap
  root((SmartCharge AI))
    Frontend
      React 18
      Vite
      Tailwind CSS
      Recharts
      WebSocket Client
    Backend
      Python 3.11+
      FastAPI
      Pydantic
      SQLAlchemy
      Redis
      WebSocket Server
    Simulator
      Python 3.11+
      Docker
      JSON Generation
      Time Series Simulation
    IBM Bob
      watsonx.ai
      Natural Language Processing
      Decision Engine
      Contextual AI
    Infrastructure
      Docker
      Docker Compose
      PostgreSQL
      Redis
      NGINX
    DevOps
      GitHub Actions
      Pytest
      ESLint
      Black
      Mypy
```

## Key Design Decisions

### 1. Microservices Architecture
- **Decision:** Separate simulator, backend, and frontend as independent services
- **Rationale:** Enables independent scaling, easier testing, and clear separation of concerns
- **Trade-off:** Increased complexity vs. better maintainability

### 2. WebSocket for Real-Time Updates
- **Decision:** Use WebSocket instead of polling for telemetry updates
- **Rationale:** Lower latency, reduced server load, better user experience
- **Trade-off:** More complex connection management vs. simpler HTTP polling

### 3. IBM Bob as Decision Engine
- **Decision:** Use IBM Bob for all charging decisions instead of rule-based logic
- **Rationale:** Contextual understanding, explainable AI, continuous learning
- **Trade-off:** API dependency vs. more intelligent decisions

### 4. Docker Containerization
- **Decision:** Containerize all services from the start
- **Rationale:** Consistent environments, easy deployment, scalability
- **Trade-off:** Initial setup complexity vs. long-term benefits

### 5. PostgreSQL for Persistence
- **Decision:** Use PostgreSQL instead of NoSQL
- **Rationale:** ACID compliance, complex queries for analytics, proven reliability
- **Trade-off:** Less flexible schema vs. better data integrity

## Performance Considerations

### Latency Targets
- **Telemetry Ingestion:** < 50ms
- **Bob Decision Request:** < 2 seconds
- **WebSocket Push:** < 100ms
- **UI Update:** < 200ms

### Scalability Targets
- **Concurrent Users:** 10,000+
- **Telemetry Events/sec:** 2,000+ (10,000 users × 1 event per 5 sec)
- **Database Size:** 100GB+ (1 year of telemetry)
- **API Throughput:** 5,000 requests/sec

### Optimization Strategies
1. **Redis Caching:** Cache latest telemetry for instant reads
2. **Database Indexing:** Index on timestamp, user_id for fast queries
3. **Connection Pooling:** Reuse database connections
4. **CDN for Frontend:** Serve static assets from edge locations
5. **Horizontal Scaling:** Add more backend instances as needed

---

*This architecture is designed for the IBM Bob Hackathon and can scale to production.*