# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

For comprehensive developer documentation, see: https://developers.home-assistant.io/

## Development Commands

### Setup and Dependencies
```bash
# Initial environment setup
./script/setup

# Install development dependencies
uv pip install -r requirements_test.txt -c homeassistant/package_constraints.txt

# Install in development mode
uv pip install -e . --config-settings editable_mode=compat --constraint homeassistant/package_constraints.txt
```

### Testing
```bash
# Run all tests
pytest tests/

# Run specific component tests
pytest tests/components/[component_name]/

# Run single test file
pytest tests/components/[component_name]/test_[platform].py

# Run with coverage
pytest --cov=homeassistant tests/

# Run tests with specific markers
pytest -m "not network" tests/
```

### Code Quality
```bash
# Run linting (only on changed files)
./script/lint

# Format code with Ruff
ruff format .

# Check with Ruff
ruff check .

# Type checking with MyPy
mypy homeassistant/

# Run all pre-commit hooks
pre-commit run --all-files

# Validate integration manifests
python -m script.hassfest --action validate
```

### Running Home Assistant
```bash
# Start Home Assistant with config directory
hass --script ensure_config -c config

# Generate requirements
python3 -m script.gen_requirements_all
```

## Architecture Overview

### Core System
Home Assistant is an event-driven, component-based platform built on Python's asyncio. The core (`homeassistant/core.py`) manages:
- Event loop and state machine
- Service registry for inter-component communication  
- Entity registry for device state management
- Configuration entry lifecycle

### Component System
Each integration lives in `homeassistant/components/[domain]/` with standardized structure:
- `manifest.json`: Metadata, dependencies, IoT class, codeowners
- `__init__.py`: Integration setup/teardown, platform loading
- `config_flow.py`: UI-based configuration flows
- `[platform].py`: Platform implementations (sensor, switch, etc.)
- `const.py`: Integration-specific constants

### Platform Architecture
25+ supported platforms with standardized base classes:
- **sensor**: Read-only data from devices
- **switch**: Binary on/off control
- **light**: Lighting control with brightness/color
- **climate**: HVAC and temperature control
- **camera**: Video streaming and snapshots
- **binary_sensor**: Boolean state sensors

### Helpers System (`homeassistant/helpers/`)
Shared utilities for common patterns:
- **Entity**: Base class for all devices with state management
- **DataUpdateCoordinator**: Polling coordination with backoff/error handling
- **ConfigEntry**: Integration instance management
- **Storage**: Persistent data storage
- **Service**: Cross-integration service calls

### Configuration System
- **Config Flows**: UI-based setup via `config_flow.py`
- **Discovery**: Automatic device detection (SSDP, mDNS, etc.)
- **Import**: Migration from YAML to UI configuration
- **Options**: Runtime configuration changes

## Code Standards

### Python Requirements
- Python 3.13+ features preferred (pattern matching, type unions)
- Strict typing with MyPy - all functions must have type hints
- Async-first architecture - use `async def` and `await`
- No blocking I/O operations in the event loop

### Integration Development
- Follow the integration scaffold pattern in `script/scaffold/`
- Use DataUpdateCoordinator for polling external APIs
- Implement proper error handling and recovery
- Add comprehensive tests with mocks for external dependencies
- Include quality_scale.yaml if integration has known reliability issues

### Testing Patterns
- Use pytest with async fixtures
- Mock external dependencies with `pytest-homeassistant-custom-component`
- Test config flows, entity states, and error conditions
- Use snapshot testing with syrupy for complex data structures
- Group tests by platform type in separate files

### Code Quality
- Ruff for linting and formatting (replaces flake8, isort, black)
- PyLint with Home Assistant custom plugins
- Pre-commit hooks enforce standards automatically
- American English for all user-facing text
- Comprehensive docstrings required for all public functions

### Component Validation
The `hassfest` tool validates integration quality:
- Manifest.json structure and required fields
- Code owner assignments and GitHub usernames
- Dependency management and constraints
- Documentation requirements
- IoT class assignments for device categories

## File Structure Patterns

### Integration Structure
```
homeassistant/components/[domain]/
├── manifest.json           # Required metadata
├── __init__.py            # Setup/teardown logic
├── config_flow.py         # UI configuration
├── const.py               # Constants
├── coordinator.py         # Data update coordination
├── entity.py              # Base entity classes
├── [platform].py         # Platform implementations
├── services.yaml          # Service definitions
├── strings.json          # UI translations
└── quality_scale.yaml    # Reliability indicators
```

### Test Structure
```
tests/components/[domain]/
├── conftest.py            # Fixtures and mocks
├── test_config_flow.py    # Configuration testing
├── test_init.py          # Integration setup/teardown
└── test_[platform].py    # Platform-specific tests
```

### Key Files to Check
- `pyproject.toml`: Build configuration and tool settings
- `homeassistant/const.py`: Global constants and platform definitions
- `homeassistant/generated/`: Auto-generated code (don't edit directly)
- `.strict-typing`: List of modules with strict MyPy enforcement
- `requirements*.txt`: Dependency specifications with constraints

## Development Workflow

1. **Component Development**: Use the scaffold system for new integrations
2. **Testing**: Write tests first, use mocks for external dependencies  
3. **Validation**: Run hassfest to validate manifest and code structure
4. **Quality**: Pre-commit hooks automatically enforce code standards
5. **Integration**: Components must support config flows for UI setup
6. **Documentation**: All public APIs require comprehensive docstrings

The system prioritizes reliability, type safety, and maintainability across 1500+ integrations while providing a consistent user experience through standardized configuration flows and entity management.