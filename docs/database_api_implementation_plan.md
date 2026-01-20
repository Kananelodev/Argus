# API Implementation Plan

## Goal Description
Implement the REST API layer for Argus using **FastAPI**. This usually corresponds to "Teammate B" in the roadmap. The API will serve as the bridge between the Database, the (future) User Portal, and the Sentinel Node.

## User Review Required
> [!NOTE]
> I will use **FastAPI's automatic documentation** (Swagger UI) for verification.
> For Authentication (`/login`), I will implement a **simple simulated login** (entering a username returns a user ID if found) to keep things simple for now, as full OAuth/JWT might be overkill for this stage unless requested.

## Proposed Changes

### Structure
Create a new directory `api/` to contain the application logic.

#### [NEW] [api/main.py](file:///c:/Users/bmokone/Argus/api/main.py)
- Initialize FastAPI app.
- Configure Database Session dependency (`get_db` from `database.connection`).
- Define Pydantic schemas for request/response models (validating inputs).

#### [NEW] [api/schemas.py](file:///c:/Users/bmokone/Argus/api/schemas.py)
- `UserLogin`: for login inputs.
- `VerificationRequestCreate`: for submitting new requests.
- `ModelRead`: for listing models.
- `RequestRead`: for viewing status.

#### [NEW] [api/routes.py](file:///c:/Users/bmokone/Argus/api/routes.py) (Optional, or keep in main.py for simplicity)
- **`POST /login`**: Accepts `username`, returns `user_id` context.
- **`GET /models`**: Returns list of available AI models from `ModelRegistry`.
- **`POST /submit-request`**: Accepts `model_id`, `input_context`. Creates a `VerificationRequest` with status `PENDING`.
- **`GET /requests`**: distinct logic:
    - If User is "Risk Officer" -> Returns ALL requests.
    - If User is "Trader" -> Returns ONLY their requests.

## Verification Plan

### Automated Tests
- Create `tests/test_api.py` (using `TestClient`).
- Test login flow.
- Test creating a request.
- Test query filtering (RBAC).

### Manual Verification
1.  Run `uvicorn api.main:app --reload`.
2.  Open Browser at `http://127.0.0.1:8000/docs`.
3.  Use "Try it out" feature to make calls.
