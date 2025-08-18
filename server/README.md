# 🤖 Invoice Agent API Server

A clean, production-ready FastAPI implementation following **Clean Architecture** principles with **SOLID** design patterns.

## 🏗️ **Architecture Overview**

```
┌─────────────────────────────────────────┐
│              API Layer                  │  ← FastAPI routes, models
├─────────────────────────────────────────┤
│           Application Layer             │  ← Use cases, interfaces  
├─────────────────────────────────────────┤
│             Domain Layer                │  ← Entities, business logic
├─────────────────────────────────────────┤
│          Infrastructure Layer           │  ← Repositories, services
└─────────────────────────────────────────┘
```

### **SOLID Principles Applied**

- ✅ **Single Responsibility**: Each class has one reason to change
- ✅ **Open/Closed**: Easy to extend, closed for modification  
- ✅ **Liskov Substitution**: Interfaces properly implemented
- ✅ **Interface Segregation**: Focused, minimal interfaces
- ✅ **Dependency Inversion**: Depend on abstractions, not concretions

## 📁 **Project Structure**

```
server/
├── api/                    # FastAPI routes and models
│   ├── __init__.py
│   ├── models.py          # Request/Response schemas
│   └── routes.py          # HTTP endpoints
├── application/           # Business logic layer
│   ├── __init__.py
│   ├── interfaces.py      # Abstract interfaces
│   └── use_cases.py       # Business use cases
├── domain/               # Core business entities
│   ├── __init__.py
│   └── entities.py       # Domain models
├── infrastructure/       # External dependencies
│   ├── __init__.py
│   ├── invoice_agent_service.py
│   └── repositories.py   # Data storage
├── tests/               # Test suite
│   ├── __init__.py
│   └── test_api.py      # API integration tests
├── config.py           # Application configuration
├── dependencies.py     # Dependency injection
├── server.py          # Main FastAPI application
├── start_server.py    # Development server launcher
└── README.md          # This file
```

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
# From project root
pip install -r requirements.txt
```

### **2. Configure Environment (Optional)**

```bash
# Create .env file in project root
echo "ANTHROPIC_API_KEY=your_api_key_here" > .env
```

### **3. Start the Server**

**Option A: Using the startup script**
```bash
cd server
python start_server.py
```

**Option B: Direct uvicorn**
```bash
# From project root
cd server
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Option C: Using Python module**
```bash
# From project root
python -m server.server
```

### **4. Test the API**

Visit: [http://localhost:8000/docs](http://localhost:8000/docs) for interactive API documentation

## 📚 **API Endpoints**

### **Core Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and status |
| `GET` | `/api/v1/health` | Health check |
| `POST` | `/api/v1/conversation` | Process user conversation |
| `POST` | `/api/v1/invoice/approve` | Approve invoice creation |
| `GET` | `/api/v1/session/{id}` | Get session information |
| `POST` | `/api/v1/session/{id}/reset` | Reset session data |

### **Debug Endpoints** (Development only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/debug/sessions` | View all sessions |
| `GET` | `/debug/invoices` | View all invoices |

## 🧪 **Testing**

### **Run Tests**

```bash
# From server directory
python -m pytest tests/ -v

# Or run specific test file
python tests/test_api.py
```

### **Manual Testing with curl**

```bash
# Health check
curl http://localhost:8000/api/v1/health

# Start conversation
curl -X POST http://localhost:8000/api/v1/conversation \
  -H "Content-Type: application/json" \
  -d '{"user_input": "I need an invoice for $500", "user_id": "test"}'

# Continue conversation with session
curl -X POST http://localhost:8000/api/v1/conversation \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Customer is John Doe", "session_id": "your-session-id"}'
```

## 🔧 **Configuration**

Configuration is handled in `config.py` using Pydantic settings:

```python
# Environment variables
ANTHROPIC_API_KEY=your_api_key
LOG_LEVEL=INFO
DEBUG=true
```

## 🏗️ **Architecture Deep Dive**

### **Domain Layer** (`domain/`)
- **Pure business logic** - no external dependencies
- **Entities**: Core data models (`InvoiceData`, `ConversationSession`)
- **Business rules**: Validation, domain-specific logic

### **Application Layer** (`application/`)
- **Use Cases**: Orchestrate business workflows
- **Interfaces**: Define contracts for external dependencies
- **No framework dependencies** - pure Python

### **Infrastructure Layer** (`infrastructure/`)
- **External integrations**: Invoice Agent, storage
- **Repositories**: Data persistence implementations
- **Services**: Third-party API integrations

### **API Layer** (`api/`)
- **HTTP interface**: FastAPI routes and models
- **Request/Response handling**: Validation, serialization
- **Framework-specific code**: FastAPI dependencies

## 🔄 **Dependency Injection**

Clean dependency injection using a container pattern:

```python
# dependencies.py
container = Container()

# Use cases get their dependencies injected
conversation_use_case = ConversationUseCase(
    agent_service=container.agent_service,
    session_repository=container.session_repository
)

# Easy to swap implementations for testing
container.session_repository = MockSessionRepository()
```

## 📊 **Key Features**

### ✅ **Production Ready**
- Structured logging
- Error handling & validation
- Health checks
- CORS support
- Environment configuration

### ✅ **Clean Architecture**
- Dependency inversion
- Testable design
- Framework independence
- Clear separation of concerns

### ✅ **Developer Experience**
- Auto-generated API docs
- Debug endpoints
- Comprehensive tests
- Type hints throughout

### ✅ **Extensible Design**
- Interface-driven development
- Easy to add new features
- Pluggable repositories
- Mockable for testing

## 🔧 **Extending the API**

### **Adding a New Repository**

```python
# 1. Define interface in application/interfaces.py
class ICustomerRepository(ABC):
    @abstractmethod
    async def get_customer(self, customer_id: str) -> Customer:
        pass

# 2. Implement in infrastructure/repositories.py
class InMemoryCustomerRepository(ICustomerRepository):
    async def get_customer(self, customer_id: str) -> Customer:
        # Implementation here
        pass

# 3. Register in dependencies.py
@property
def customer_repository(self) -> ICustomerRepository:
    return InMemoryCustomerRepository()
```

### **Adding a New Use Case**

```python
# 1. Create use case in application/use_cases.py
class CustomerManagementUseCase:
    def __init__(self, customer_repo: ICustomerRepository):
        self._customer_repo = customer_repo
    
    async def get_customer_details(self, customer_id: str) -> dict:
        # Business logic here
        pass

# 2. Add to dependencies.py
def get_customer_use_case(self) -> CustomerManagementUseCase:
    return CustomerManagementUseCase(self.customer_repository)

# 3. Create routes in api/routes.py
@router.get("/customers/{customer_id}")
async def get_customer(customer_id: str, use_case = Depends(get_customer_use_case)):
    return await use_case.get_customer_details(customer_id)
```

## 🚀 **Deployment**

### **Docker**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "server.server:app", "--host", "0.0.0.0", "--port", "8000"]
```

### **Environment Variables**

```bash
# Production settings
ANTHROPIC_API_KEY=prod_api_key
LOG_LEVEL=WARNING
DEBUG=false
CORS_ORIGINS=["https://yourapp.com"]
```

## 🤝 **Contributing**

1. Follow the clean architecture patterns
2. Add tests for new features
3. Update this README for significant changes
4. Ensure all tests pass before submitting

---

## 🎯 **Next Steps**

- [ ] Add database persistence (PostgreSQL/SQLite)
- [ ] Implement authentication/authorization
- [ ] Add rate limiting
- [ ] Implement caching (Redis)
- [ ] Add monitoring and metrics
- [ ] Create Docker deployment configs

**This server provides a solid, scalable foundation for your Invoice Agent API!** 🚀
