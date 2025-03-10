# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.17] - 2024-01-11

### Added
- Added code examples and use cases for all components in README.md
- Added detailed documentation for value objects and core components
- Improved code examples with error handling and expected outputs

### Changed
- Restructured security module:
  - Separated JWT, password, and policy into distinct files
  - Enhanced TokenManager with better token type handling
  - Improved PasswordHasher with policy validation
  - Added comprehensive SecurityPolicy configuration

- Restructured models module:
  - Enhanced BaseModel with better JSON encoding
  - Added Entity as base class for domain entities
  - Improved AggregateRoot with event management
  - Enhanced DomainEvent with better type safety

- Updated README.md structure with better organization
- Enhanced documentation with practical examples

### Fixed
- Fixed circular imports in models module
- Improved error handling in security components
- Enhanced type hints across all modules

## [0.1.16] - 2025-01-11

### Added
- New value objects:
  - `Email`: Email validation and formatting
  - `PasswordHash`: Secure password hash handling
  - `Token`: JWT token management
  - `PhoneNumber`: Phone number validation
  - `Money`: Currency handling
  - `Address`: Address formatting

- Enhanced domain models:
  - `BaseModel`: Improved base model with JSON serialization
  - `DomainEvent`: Event tracking with automatic type assignment
  - `AggregateRoot`: Aggregate root pattern implementation

- Security improvements:
  - `SecurityPolicy`: Configurable security policies
  - `TokenManager`: Enhanced JWT token handling
  - Strong password validation

- Metrics enhancements:
  - Standardized metrics collection
  - Prometheus integration
  - Custom decorators for easy metrics tracking

### Changed
- Reorganized package structure for better modularity
- Improved documentation with detailed examples
- Enhanced type hints and validation

### Fixed
- Fixed linter errors across modules
- Corrected import statements
- Resolved circular dependencies

## [0.1.15] - 2024-01-11

### Added
- Initial release
- Basic utilities and helpers
- Core infrastructure components 

### Changed
- Updated README.md
- Updated pyproject.toml
- Updated CHANGELOG.md

## [0.1.18] - 2024-01-11

### Added
- Added retry mechanism using tenacity for database operations
- Added type hints improvements for MongoDB client
- Added better error handling for database connections

### Fixed
- Fixed type checking issues in MongoDB client
- Fixed potential None access in database operations
- Fixed connection handling in MongoDB client


## [0.2.0] - 2024-01-12

### Added
- New `BaseContainer` class in `containers` module for standardized dependency injection
- Common providers for MongoDB, Redis, and Metrics
- Resource lifecycle management with `init_resources` and `shutdown_resources`
- Improved config handling with safe attribute access

### Changed
- Refactored MongoDB client to use connection pooling
- Enhanced Redis client with better error handling
- Updated metrics manager with standardized configuration

### Fixed
- Fixed type hints and linter errors in container module
- Improved error handling in resource initialization
- Better handling of optional Redis configuration

## [0.2.7] - 2024-01-12

### Changed
- Updated README.md
- Updated documentation