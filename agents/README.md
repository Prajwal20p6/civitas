# CIVITAS — Python Agents Module

This subproject implements the agent logic, schemas, and simulation core for the CIVITAS Emergency Traffic Coordinator.

## Module Structure

```text
agents/
├── src/
│   ├── agents/               # Multi-agent coordination logic
│   │   ├── route_agents/     # Competitive routing algorithms (Speed vs Fairness)
│   │   ├── perception.py     # Incident classification
│   │   ├── orchestrator.py   # ADK SequentialAgent workflow
│   │   ├── simulation.py     # Deterministic negotiation resolver
│   │   └── explainability.py # Operator feedback generator
│   ├── tools/
│   │   └── maps.py           # Google Maps API utility client
│   ├── adk_setup.py          # Google ADK 2.0 pipeline config
│   ├── schemas.py            # Pydantic validation models
│   └── shared_state.py       # Global whiteboard session state manager
├── tests/                    # Agent unit and integration tests
├── pyproject.toml            # Project and dependencies definition
└── pytest.ini                # Pytest configuration
```

## Quick Start

### 1. Install Dependencies
```bash
cd agents
pip install -r requirements.txt
pip install -e .[dev]
```

### 2. Verify Imports
```bash
python3 -c "from src import schemas; print('OK')"
```

### 3. Run Test Suite
```bash
pytest tests/ -v
```
