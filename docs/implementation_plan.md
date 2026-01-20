# Argus Implementation Plan: Hackathon Focus Areas

We will upgrade Argus to a full Self-Sovereign Identity (SSI) compliant Verification Node.

## User Review Required
> [!IMPORTANT]
> This upgrade changes the `proof` format from a simple JSON to a W3C Verifiable Credential (JSON-LD). This may break existing dashboard parsers if they expect the old format.

## Proposed Changes

### 1. Identity & DIDs (Focus Area: DIDs)
We need a persistent identity for the Sentinel Node.
#### [NEW] [sentinel/core/identity.py](file:///home/wethinkcode/Argus/sentinel/core/identity.py)
- `DIDManager` class.
- Generates a persistent keypair (saved to disk or derived).
- Creates a `did:key` or `did:web` identifier.
- Provides `sign(payload)` capability.

### 2. Verifiable Credentials (Focus Area: VCs)
Transform the Execution Trace into a standard Credential.
#### [MODIFY] [sentinel/core/proof.py](file:///home/wethinkcode/Argus/sentinel/core/proof.py)
- Import `DIDManager`.
- Change `generate_proof` to return a VC structure:
    ```json
    {
      "@context": ["https://www.w3.org/2018/credentials/v1"],
      "type": ["VerifiableCredential", "AIExecutionCertificate"],
      "issuer": "did:key:...",
      "credentialSubject": { ...trace... },
      "proof": { ...signature... }
    }
    ```

### 3. Privacy & ZKPs (Focus Area: ZKP)
Allow verifying attributes without leaking input data.
#### [MODIFY] [sentinel/core/constraints.py](file:///home/wethinkcode/Argus/sentinel/core/constraints.py)
- Add `PrivacyEngine`.
- Allow rules like `ALLOW IF input.age > 18` where the trace records `age_check: PASS` but DOES NOT record `age: 25`.

#### [MODIFY] [sentinel/core/runtime.py](file:///home/wethinkcode/Argus/sentinel/core/runtime.py)
- Integrate `PrivacyEngine`.
- Ensure sensitive inputs are hashed or redacted in the final trace, replaced by the "Privacy Proof" (the fact that constraints passed).

## Verification Plan
### Automated Tests
- Run `sentinel.cli` with a sample scenario.
- Verify the output JSON contains `did:key` and valid VC structure.
- Verify sensitive data is NOT in the output if using privacy constraints.
