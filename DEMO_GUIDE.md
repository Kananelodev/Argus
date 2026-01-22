# Argus Demo: Run Guide

Follow this sequence to record the "Full Loop" demo.

## Phase 1: Setup
1. **Reset Database** (Optional, to clear old requests):
   ```bash
   rm silverlock.db
   ```
2. **Start the API Server** (Terminal 1):
   ```bash
   python3 -m uvicorn sentinel.api.server:app --host 0.0.0.0 --port 8000
   ```
   *Wait for "Uvicorn running..."*

## Phase 2: User Action (The "Ask")
3. **Open Browser** to: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
   *   You should see the "SilverLock Portal" Login Screen.
4. **Login**:
   *   Username: `alice_risk`
   *   Password: `password123`
   *   Click **CONNECT IDENTITY**.
5. **Create Request**:
   *   Click the "NEW Run Analysis" card.
   *   Model: `Credit Risk v2`
   *   Input: `{"applicant_id": "77391", "score": 750, "income": 60000}`
   *   *(Note: This input will trigger the Privacy Engine to generate ZKPs for Score > 700)*
   *   Click **SUBMIT REQUEST**.
   *   *Result*: You will see the request in the list with status **PENDING** (Yellow).

## Phase 3: The System (The "Machine")
6. **Start the Sentinel Node** (Terminal 2):
   ```bash
   python3 -m sentinel.cli start-node
   ```
   *   **Action**: Watch the terminal. It will say "Syncing...", then "Received Job", then "PROOF GENERATED".
   *   *Cinematic*: Pause here to show the "Verifiable Credential" JSON in the terminal.

## Phase 4: Verification (The "Trust")
7. **Back to Browser (Portal)**:
   *   Click "REFRESH" (top right of table).
   *   *Result*: Status changes to **VERIFIED** (Green).
   *   Click **VIEW PROOF ↗**.
8. **View Dashboard**:
   *   This opens a new tab (`/dashboard?cid=Qm...`).
   *   Show the Green "VALID EXECUTION PROOF" banner.
   *   Scroll down to show valid hashes.

## Phase 5: Tamper Demo (Optional "Bonus")
9. **Tamper Run** (Terminal 2):
   *   Stop the node (Ctrl+C).
   *   Run a manual tamper command:
     ```bash
     python3 -m sentinel.cli run privacy_model.bin "Hack Attempt" --simulate-tamper --store
     ```
   *   Copy the CID.
   *   Paste into Dashboard Search.
   *   *Result*: **RED BANNER: TAMPER DETECTED**.

---
**Ready to record?**
