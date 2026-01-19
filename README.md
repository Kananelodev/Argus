# Argus: Decentralized AI Verification Node

> **Note**: This system is deployed at **SilverLock Financial** to ensure cryptographic auditability of AI-driven decisions in Banking, Loans, and High-Frequency Trading.

Argus is a **verifiable execution proof system** for AI models. It wraps model execution, hashes the inputs/outputs, and stores a signed trace on IPFS. This allows for:
- **Immutable Audit Trails**: Prove exactly what input caused an AI decision.
- **Tamper Detection**: Detect "Man-in-the-Middle" attacks on model serving infrastructure.
- **Regulatory Compliance**: Satisfy GDPR and Fair Banking requirements for AI explainability.

---

## 🚀 Quick Start

### 1. Installation
This is a Python project. You do not need `npm`.

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Verification Node
Start the local dashboard and API server:

```bash
python3 -m uvicorn sentinel.api.server:app --reload
```
View the dashboard at: **http://127.0.0.1:8000**

### 3. Generate a Proof (Simulate Traffic)
In a new terminal, simulate a departmental AI task:

```bash
# Scenario: Credit Analyst running a Loan Approval model
python3 -m sentinel.cli run scenarios/loan_approval_model_v1.bin "Applicant: Jane Doe, Score: 750" --store
```

---

## 🏭 Enterprise Scenarios (SilverLock Financial)

Argus is used across multiple departments to secure critical workflows:

| Department | Use Case | Why Verification Matters |
| :--- | :--- | :--- |
| **FINANCE** | Loan Underwriting | Prove non-discrimination in lending decisions for regulators. |
| **IT / SEC** | Fraud Detection | Verify that account freezes were triggered by the AI, not rogue admins. |
| **HR** | Resume Screening | Audit hiring algorithms for bias and ensure consistent versioning. |
| **OPS** | Trading Bots | Replay crash inputs to debug high-frequency trading algorithms. |

---

## 🛠️ Architecture

- **Sentinel CLI**: Wraps the model, generates the SHA-256 Merkle trace, and signs it.
- **IPFS Storage**: Stores the content-addressed proof (CID).
- **Web Dashboard**: Visualizes the verification result and allows manual auditing.
