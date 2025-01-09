# Earnbase Common

Common utilities for Earnbase microservices.

## Features

- Structured logging with JSON format
- Log rotation and error logging
- Development and production logging modes
- Sensitive data filtering
- Service information injection

## Installation

```bash
pip install earnbase-common
```

## Usage

### Basic Usage

```python
from earnbase_common.logging import setup_logging, get_logger

# Configure logging
setup_logging(
    service_name="my-service",
    log_file="logs/my-service.log",
    log_level="INFO",
    debug=False
)

# Get logger
logger = get_logger(__name__)

# Use logger
logger.info("Service started", extra={"version": "1.0.0"})
```

### Configuration

The logging system can be configured with the following parameters:

- `service_name`: Name of the service
- `log_file`: Path to log file
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `debug`: Debug mode flag (enables colored console output)

## Development

1. Clone the repository
2. Install dependencies with PDM:
```bash
pdm install
```

3. Run tests:
```bash
pdm run test
```

## License

MIT License 