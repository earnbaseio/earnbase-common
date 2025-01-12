# Dependency Injection Containers

## Overview

The containers module provides a standardized way to manage dependencies across services using the dependency-injector package. It implements the Dependency Injection pattern to make services more modular, testable, and maintainable.

## Features

### Base Container

The `BaseContainer` class serves as the foundation for service-specific containers:

```python
from earnbase_common.containers import BaseContainer
from dependency_injector import providers

class ServiceContainer(BaseContainer):
    """Service-specific container."""
    
    # Configuration
    config = providers.Singleton(BaseSettings)
    
    # Common providers
    mongodb = providers.Resource(
        MongoDB.connect,
        url=config.provided.MONGODB_URL,
        db_name=config.provided.MONGODB_DB_NAME,
        min_pool_size=config.provided.MONGODB_MIN_POOL_SIZE,
        max_pool_size=config.provided.MONGODB_MAX_POOL_SIZE,
    )
```

### Common Providers

The `BaseContainer` includes several pre-configured providers:

1. **Configuration**:
```python
# Automatically configured from settings
config = providers.Singleton(BaseSettings)
```

2. **MongoDB**:
```python
mongodb = providers.Resource(
    MongoDB.connect,
    url=config.provided.MONGODB_URL,
    db_name=config.provided.MONGODB_DB_NAME,
    min_pool_size=config.provided.MONGODB_MIN_POOL_SIZE,
    max_pool_size=config.provided.MONGODB_MAX_POOL_SIZE,
)
```

3. **Redis**:
```python
redis = providers.Resource(
    RedisClient.connect,
    url=config.provided.REDIS_URL,
    db=config.provided.REDIS_DB,
    prefix=config.provided.REDIS_PREFIX,
    ttl=config.provided.REDIS_TTL,
)
```

4. **Metrics**:
```python
metrics = providers.Singleton(
    MetricsManager,
    enabled=config.provided.METRICS_ENABLED,
)
```

## Usage

### 1. Creating Service Container

```python
from earnbase_common.containers import BaseContainer
from dependency_injector import providers

class UserServiceContainer(BaseContainer):
    """User service container."""
    
    # Service-specific providers
    user_repository = providers.Singleton(
        UserRepository,
        mongodb=mongodb,
    )
    
    user_service = providers.Singleton(
        UserService,
        repository=user_repository,
        redis=redis,
    )
```

### 2. Resource Lifecycle Management

```python
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    container = ServiceContainer()
    
    try:
        # Initialize resources
        await container.init_resources()
        
        # Wire container
        container.wire(packages=["my_service"])
        
        yield
        
    finally:
        # Cleanup resources
        await container.shutdown_resources()
```

### 3. Dependency Injection in FastAPI

```python
from dependency_injector.wiring import inject, Provide

@app.get("/users/{user_id}")
@inject
async def get_user(
    user_id: str,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    return await user_service.get_user(user_id)
```

## Best Practices

### 1. Resource Management

- Always use `init_resources()` and `shutdown_resources()`
- Handle optional resources gracefully
- Implement proper error handling for resource initialization

```python
class ServiceContainer(BaseContainer):
    async def init_resources(self):
        """Initialize container resources."""
        await super().init_resources()
        
        # Initialize additional resources
        if self.config.FEATURE_FLAG:
            await self.feature_client.init()
    
    async def shutdown_resources(self):
        """Cleanup container resources."""
        try:
            # Cleanup additional resources
            if self.feature_client.initialized:
                await self.feature_client.shutdown()
        finally:
            await super().shutdown_resources()
```

### 2. Configuration Integration

```python
class ServiceContainer(BaseContainer):
    """Service container with custom config."""
    
    config = providers.Singleton(ServiceSettings)
    
    # Use config values in providers
    feature_client = providers.Singleton(
        FeatureClient,
        api_key=config.provided.FEATURE_API_KEY,
        enabled=config.provided.FEATURE_ENABLED,
    )
```

### 3. Testing Support

```python
@pytest.fixture
def container():
    """Create test container."""
    container = ServiceContainer()
    
    # Override providers for testing
    container.config.override(TestSettings())
    container.mongodb.override(MockMongoDB())
    
    return container

def test_service(container):
    """Test service with mocked dependencies."""
    service = container.service()
    assert service.config.TEST_MODE is True
    assert isinstance(service.mongodb, MockMongoDB)
```

## Advanced Features

### 1. Async Resource Providers

```python
class AsyncContainer(BaseContainer):
    """Container with async resources."""
    
    async_client = providers.Resource(
        AsyncClient.connect,
        url=config.provided.CLIENT_URL,
        timeout=config.provided.CLIENT_TIMEOUT,
    )
```

### 2. Factory Providers

```python
class FactoryContainer(BaseContainer):
    """Container with factory providers."""
    
    repository_factory = providers.Factory(
        Repository,
        mongodb=mongodb,
    )
```

### 3. Contextual Providers

```python
class ContextContainer(BaseContainer):
    """Container with contextual providers."""
    
    request_context = providers.Contextual()
    
    current_user = providers.Contextual(
        lambda context: context.request.user
    )
```

## Integration Examples

### 1. With FastAPI Middleware

```python
from fastapi import FastAPI
from dependency_injector.wiring import inject, Provide

app = FastAPI()
container = ServiceContainer()

@app.middleware("http")
@inject
async def metrics_middleware(
    request: Request,
    call_next,
    metrics: MetricsManager = Depends(Provide[Container.metrics]),
):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    metrics.request_duration.observe(duration)
    return response
```

### 2. With Background Tasks

```python
class WorkerContainer(BaseContainer):
    """Container for background workers."""
    
    task_queue = providers.Singleton(
        TaskQueue,
        redis=redis,
    )
    
    worker = providers.Singleton(
        Worker,
        queue=task_queue,
        metrics=metrics,
    )

# In your worker
@inject
async def process_tasks(
    worker: Worker = Depends(Provide[Container.worker])
):
    await worker.run()
``` 