# SilverLock Portal: User-Centric Roadmap

We are moving from a "Backend Verification Tool" to a "User-Facing Platform".

**The Vision:** Bank employees (HR, Traders, Risk Officers) don't run command-line tools. They log into a **Web Portal** to verify choices. The **Sentinel Node** runs in the background.

## 1. System Architecture
```mermaid
graph TD
    User[Bank Employee] -->|Web UI| Portal[SilverLock Portal App]
    Portal -->|REST API| API[Central Database API]
    API -->|SQL| DB[(PostgreSQL/SQLite)]
    
    Sentinel[Sentinel Node (Argus)] -->|Verifiable Trace| IPFS
    Sentinel -->|Update Status| API
```

## 2. Database Schema (What the DB is about)
We need to track **People, Departments, and Workflows**.

### Tables
1.  **`Departments`**: HR, Trading, Risk, IT.
2.  **`Users`**: The employees. Fields: `id`, `name`, `role`, `department_id`, `did` (their digital identity).
3.  **`ModelRegistry`**: Approved AI models. Fields: `id`, `name`, `version`, `ipfs_hash`, `required_privacy_level`.
4.  **`VerificationRequests`**: The core workflow.
    *   `id`: UUID
    *   `requester_id`: User FK
    *   `model_id`: Model FK
    *   `input_context`: "Loan App #12345"
    *   `status`: PENDING, VERIFIED, FLAGGED
    *   `proof_cid`: Link to IPFS (The bridge to our Sentinel Node)

## 3. Tasks for Teammates

### Teammate A: The Database Architect
**Goal:** Build the Memory of the system.
- [ ] Set up **SQLAlchemy** (Python ORM).
- [ ] Create the models: `User`, `Department`, `VerificationRequest`.
- [ ] Create a seed script to populate "SilverLock Financial" dummy data (e.g. "Department: High Frequency Trading").

### Teammate B: The API Builder
**Goal:** Connect the users to the data.
- [ ] Create endpoints: `POST /login`, `GET /models`, `POST /submit-request`.
- [ ] Implement "Role Based Access": Only *Risk Managers* can see *All Requests*. *Traders* see only *Their Requests*.

### Teammate C: The Frontend Designer
**Goal:** Make it look like a sleek Bank tool.
- [ ] Build the **SilverLock Portal** (HTML/JS or Streamlit/Dash if Python-only).
- [ ] Pages:
    *   **Login**: "Connect Identity".
    *   **Dashboard**: "My Pending Verifications".
    *   **Request Form**: "Run Model Check".

### Teammate D: The Integrator (You/Me)
**Goal:** Connect our Sentinel Node to this new world.
- [ ] Modify `sentinel.cli` to fetch "Pending Requests" from the DB.
- [ ] Automatically run the verification.
- [ ] Update the DB with the result (`status: VERIFIED`, `proof_cid: Qm...`).

## 4. Why this matters?
- **Auditable History**: The DB proves *who* asked for the verification.
- **Access Control**: We stop unauthorized people from running models.
- **Workflow**: We turn "running code" into "business process".
