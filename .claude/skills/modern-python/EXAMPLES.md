# Modern Python - Code Examples

Practical code examples for LLM applications, FastAPI, testing, and architecture patterns.

## Table of Contents

- [LLM Patterns](#llm-patterns)
- [FastAPI Patterns](#fastapi-patterns)
- [Testing Examples](#testing-examples)
- [Architecture Examples](#architecture-examples)
- [TypeScript-Python Mapping](#typescript-python-mapping)

---

## LLM Patterns

### Pydantic for Structured Outputs

```python
from pydantic import BaseModel, Field
from typing import Literal

class SentimentAnalysis(BaseModel):
    """Structured sentiment analysis output"""
    sentiment: Literal["positive", "neutral", "negative"]
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    reasoning: str = Field(description="Why this sentiment was chosen")

class ExtractedEntities(BaseModel):
    """Named entity extraction"""
    persons: list[str] = Field(default_factory=list)
    organizations: list[str] = Field(default_factory=list)
    locations: list[str] = Field(default_factory=list)

class SummaryOutput(BaseModel):
    """Document summary with metadata"""
    summary: str = Field(min_length=50, max_length=500)
    key_points: list[str] = Field(min_length=3, max_length=10)
    tags: list[str] = Field(default_factory=list)
    word_count: int = Field(gt=0)
```

### Instructor Pattern (Type-Safe LLM Calls)

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

client = instructor.from_openai(OpenAI())

class UserIntent(BaseModel):
    action: Literal["search", "create", "update", "delete"]
    entity: str
    parameters: dict[str, str]

def parse_user_command(command: str) -> UserIntent:
    """Parse natural language command into structured intent"""
    response = client.chat.completions.create(
        model="gpt-4o",
        response_model=UserIntent,
        messages=[
            {
                "role": "system",
                "content": "Extract the user's intent from their command."
            },
            {
                "role": "user",
                "content": command
            }
        ]
    )
    # response is typed as UserIntent ✓
    return response

# Usage
intent = parse_user_command("create a new user named John with email john@example.com")
print(intent.action)  # "create"
print(intent.entity)  # "user"
print(intent.parameters)  # {"name": "John", "email": "john@example.com"}
```

### LangChain with Pydantic Parser

```python
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

class ProductReview(BaseModel):
    product_name: str
    rating: int = Field(ge=1, le=5)
    pros: list[str]
    cons: list[str]
    recommendation: str

# Setup parser and prompt
parser = PydanticOutputParser(pydantic_object=ProductReview)
prompt = PromptTemplate(
    template="Analyze this product review:\n{review}\n\n{format_instructions}",
    input_variables=["review"],
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

# Create chain
llm = ChatOpenAI(model="gpt-4o")
chain = prompt | llm | parser

# Usage
review_text = "This laptop is amazing! Fast, lightweight, but battery life could be better."
result: ProductReview = chain.invoke({"review": review_text})
```

### Streaming with Instructor

```python
import instructor
from openai import OpenAI
from pydantic import BaseModel

client = instructor.from_openai(OpenAI())

class StoryChunk(BaseModel):
    chapter: str
    content: str

def generate_story(prompt: str):
    """Stream story generation in chunks"""
    for chunk in client.chat.completions.create_partial(
        model="gpt-4o",
        response_model=StoryChunk,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    ):
        if chunk.content:
            yield chunk.content

# Usage
for content in generate_story("Write a sci-fi story about AI"):
    print(content, end="", flush=True)
```

---

## FastAPI Patterns

### Complete API Example with Dependency Injection

```python
# src/my_api/domain/models.py
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime

class CreateUserRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

# src/my_api/domain/services.py
from typing import Protocol

class UserRepository(Protocol):
    """Interface for user storage"""
    def get(self, user_id: str) -> User | None: ...
    def save(self, user: User) -> None: ...
    def list(self) -> list[User]: ...

class UserService:
    """Business logic for user management"""

    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def create_user(self, name: str, email: str) -> User:
        user = User(
            id=self._generate_id(),
            name=name,
            email=email,
            created_at=datetime.now()
        )
        self.repo.save(user)
        return user

    def get_user(self, user_id: str) -> User | None:
        return self.repo.get(user_id)

    def _generate_id(self) -> str:
        import uuid
        return str(uuid.uuid4())

# src/my_api/adapters/memory_repository.py
class InMemoryUserRepository:
    """Simple in-memory implementation"""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        self._users[user.id] = user

    def list(self) -> list[User]:
        return list(self._users.values())

# src/my_api/adapters/api.py
from fastapi import FastAPI, Depends, HTTPException, status
from typing import Annotated

app = FastAPI(title="User API")

# Dependency: Repository
def get_repository() -> InMemoryUserRepository:
    # In production, this would create a database connection
    return InMemoryUserRepository()

# Dependency: Service
def get_user_service(
    repo: Annotated[InMemoryUserRepository, Depends(get_repository)]
) -> UserService:
    return UserService(repo)

# Routes
@app.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: CreateUserRequest,
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """Create a new user"""
    user = service.create_user(request.name, request.email)
    return UserResponse.model_validate(user)

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    service: Annotated[UserService, Depends(get_user_service)]
) -> UserResponse:
    """Get user by ID"""
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return UserResponse.model_validate(user)

@app.get("/users", response_model=list[UserResponse])
async def list_users(
    service: Annotated[UserService, Depends(get_user_service)]
) -> list[UserResponse]:
    """List all users"""
    users = service.repo.list()
    return [UserResponse.model_validate(u) for u in users]
```

### FastAPI with LLM Integration

```python
from fastapi import FastAPI, Depends
from pydantic import BaseModel
import instructor
from openai import OpenAI

app = FastAPI()

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    sentiment: Literal["positive", "neutral", "negative"]
    summary: str
    topics: list[str]

# Dependency: LLM Client
def get_llm_client() -> instructor.Instructor:
    return instructor.from_openai(OpenAI())

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(
    request: AnalysisRequest,
    client: Annotated[instructor.Instructor, Depends(get_llm_client)]
) -> AnalysisResponse:
    """Analyze text using LLM"""
    response = client.chat.completions.create(
        model="gpt-4o",
        response_model=AnalysisResponse,
        messages=[
            {"role": "system", "content": "Analyze the provided text."},
            {"role": "user", "content": request.text}
        ]
    )
    return response
```

---

## Testing Examples

### Unit Tests (Fast, No I/O)

```python
# tests/unit/test_services.py
from datetime import datetime
from my_api.domain.models import User
from my_api.domain.services import UserService

class MockUserRepository:
    """Test double for UserRepository"""

    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def get(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def save(self, user: User) -> None:
        self._users[user.id] = user

    def list(self) -> list[User]:
        return list(self._users.values())

def test_create_user():
    """Test user creation logic"""
    repo = MockUserRepository()
    service = UserService(repo)

    user = service.create_user("Alice", "alice@example.com")

    assert user.name == "Alice"
    assert user.email == "alice@example.com"
    assert user.id is not None
    assert isinstance(user.created_at, datetime)

def test_get_user_returns_none_when_not_found():
    """Test getting non-existent user"""
    repo = MockUserRepository()
    service = UserService(repo)

    result = service.get_user("non-existent-id")

    assert result is None

def test_get_user_returns_user_when_exists():
    """Test getting existing user"""
    repo = MockUserRepository()
    service = UserService(repo)

    # Arrange
    created_user = service.create_user("Bob", "bob@example.com")

    # Act
    found_user = service.get_user(created_user.id)

    # Assert
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.name == "Bob"
```

### Integration Tests (With Dependencies)

```python
# tests/integration/test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from my_api.adapters.postgres_repository import PostgresUserRepository
from my_api.domain.models import User

@pytest.fixture
def db_session():
    """Create test database session"""
    engine = create_engine("sqlite:///:memory:")
    # Create tables
    Base.metadata.create_all(engine)

    session = Session(engine)
    yield session

    session.close()

def test_save_and_retrieve_user(db_session):
    """Test database operations"""
    repo = PostgresUserRepository(db_session)

    user = User(
        id="test-123",
        name="Charlie",
        email="charlie@example.com",
        created_at=datetime.now()
    )

    repo.save(user)
    retrieved = repo.get("test-123")

    assert retrieved is not None
    assert retrieved.id == user.id
    assert retrieved.name == user.name
    assert retrieved.email == user.email
```

### Functional Tests (E2E API Tests)

```python
# tests/functional/test_api.py
import pytest
from fastapi.testclient import TestClient
from my_api.adapters.api import app

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

def test_create_user_flow(client):
    """Test complete user creation flow"""
    # Create user
    response = client.post(
        "/users",
        json={"name": "Diana", "email": "diana@example.com"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Diana"
    assert data["email"] == "diana@example.com"
    assert "id" in data

    user_id = data["id"]

    # Verify user exists
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_get_nonexistent_user_returns_404(client):
    """Test error handling"""
    response = client.get("/users/nonexistent-id")
    assert response.status_code == 404

def test_list_users(client):
    """Test listing users"""
    # Create multiple users
    client.post("/users", json={"name": "User1", "email": "user1@example.com"})
    client.post("/users", json={"name": "User2", "email": "user2@example.com"})

    # List all
    response = client.get("/users")
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2
```

### Testing with pytest Fixtures

```python
# tests/conftest.py
import pytest
from my_api.domain.services import UserService
from tests.unit.test_services import MockUserRepository

@pytest.fixture
def user_service():
    """Shared fixture for UserService"""
    repo = MockUserRepository()
    return UserService(repo)

@pytest.fixture
def sample_user():
    """Sample user for testing"""
    return User(
        id="sample-123",
        name="Sample User",
        email="sample@example.com",
        created_at=datetime.now()
    )

# tests/unit/test_with_fixtures.py
def test_using_fixtures(user_service, sample_user):
    """Test using shared fixtures"""
    user_service.repo.save(sample_user)
    found = user_service.get_user(sample_user.id)
    assert found == sample_user
```

---

## Architecture Examples

### Ports and Adapters Pattern

```python
# ports/llm_client.py - Interface
from typing import Protocol
from pydantic import BaseModel

class LLMClient(Protocol):
    """Port for LLM interactions"""

    def generate(self, prompt: str, response_model: type[BaseModel]) -> BaseModel:
        """Generate structured response"""
        ...

# adapters/openai_client.py - OpenAI Implementation
import instructor
from openai import OpenAI
from pydantic import BaseModel

class OpenAIClient:
    """OpenAI adapter implementing LLMClient"""

    def __init__(self, api_key: str | None = None) -> None:
        self.client = instructor.from_openai(OpenAI(api_key=api_key))

    def generate(self, prompt: str, response_model: type[BaseModel]) -> BaseModel:
        return self.client.chat.completions.create(
            model="gpt-4o",
            response_model=response_model,
            messages=[{"role": "user", "content": prompt}]
        )

# adapters/anthropic_client.py - Anthropic Implementation
class AnthropicClient:
    """Anthropic adapter implementing LLMClient"""

    def __init__(self, api_key: str | None = None) -> None:
        # Initialize Anthropic client
        ...

    def generate(self, prompt: str, response_model: type[BaseModel]) -> BaseModel:
        # Anthropic-specific implementation
        ...

# domain/services.py - Business logic is provider-agnostic
class TextAnalyzer:
    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm  # Depends on interface, not implementation

    def analyze(self, text: str) -> AnalysisResult:
        return self.llm.generate(
            f"Analyze: {text}",
            response_model=AnalysisResult
        )

# Usage - Easy to swap implementations
from ports.llm_client import LLMClient
from adapters.openai_client import OpenAIClient
from adapters.anthropic_client import AnthropicClient

# Use OpenAI
analyzer = TextAnalyzer(llm=OpenAIClient())

# Or switch to Anthropic
analyzer = TextAnalyzer(llm=AnthropicClient())
```

---

## TypeScript-Python Mapping

### Interfaces and Types

| TypeScript | Python | Example |
|------------|--------|---------|
| `interface User { name: string; age: number }` | `class User(BaseModel): name: str; age: int` | Pydantic models |
| `type Status = "active" \| "inactive"` | `Status = Literal["active", "inactive"]` | Union types |
| `type ID = string` | `ID = str` or `ID: TypeAlias = str` | Type aliases |
| `interface Repo { get(id: string): User }` | `class Repo(Protocol): def get(self, id: str) -> User: ...` | Protocols |

### Type Annotations

```typescript
// TypeScript
function greet(name: string): string {
    return `Hello, ${name}`;
}

const numbers: number[] = [1, 2, 3];
const user: User | null = getUser();
```

```python
# Python
def greet(name: str) -> str:
    return f"Hello, {name}"

numbers: list[int] = [1, 2, 3]
user: User | None = get_user()
```

### Validation (Zod ↔ Pydantic)

```typescript
// TypeScript with Zod
import { z } from "zod";

const UserSchema = z.object({
    name: z.string().min(1).max(100),
    email: z.string().email(),
    age: z.number().int().positive().optional()
});

type User = z.infer<typeof UserSchema>;
```

```python
# Python with Pydantic
from pydantic import BaseModel, Field, EmailStr

class User(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int | None = Field(default=None, gt=0)
```

### Dependency Injection

```typescript
// TypeScript (NestJS)
@Injectable()
class UserService {
    constructor(private repo: UserRepository) {}

    getUser(id: string): User {
        return this.repo.findById(id);
    }
}
```

```python
# Python (FastAPI)
class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo

    def get_user(self, id: str) -> User:
        return self.repo.find_by_id(id)

# Dependency injection in route
@app.get("/users/{id}")
def get_user(
    id: str,
    service: Annotated[UserService, Depends(get_user_service)]
):
    return service.get_user(id)
```

### Async/Await

```typescript
// TypeScript
async function fetchUser(id: string): Promise<User> {
    const response = await fetch(`/users/${id}`);
    return response.json();
}
```

```python
# Python
async def fetch_user(id: str) -> User:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/users/{id}")
        return User.model_validate(response.json())
```

### Error Handling

```typescript
// TypeScript
class UserNotFoundError extends Error {
    constructor(id: string) {
        super(`User ${id} not found`);
    }
}

try {
    const user = getUser(id);
} catch (error) {
    if (error instanceof UserNotFoundError) {
        console.error(error.message);
    }
}
```

```python
# Python
class UserNotFoundError(Exception):
    def __init__(self, id: str) -> None:
        super().__init__(f"User {id} not found")

try:
    user = get_user(id)
except UserNotFoundError as error:
    print(error)
```

### Testing

| TypeScript (Jest/Vitest) | Python (pytest) |
|-------------------------|-----------------|
| `describe("UserService", () => { ... })` | Just write `test_` functions |
| `test("should create user", () => { ... })` | `def test_should_create_user(): ...` |
| `expect(result).toBe(expected)` | `assert result == expected` |
| `beforeEach(() => { ... })` | `@pytest.fixture def setup(): ...` |

---

## Additional Patterns

### Configuration Management

```python
# Use Pydantic Settings
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    database_url: str
    openai_api_key: str
    debug: bool = False

# Usage
settings = Settings()  # Automatically loads from .env
```

### Retry Logic with LLM

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
def call_llm_with_retry(prompt: str) -> str:
    """Retry on failure"""
    return client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
```

This completes the examples! These patterns should cover most common use cases in modern Python development.
