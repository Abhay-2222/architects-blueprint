# Chapter 7 — Authentication: The ID Card at the Door

*Part 2: The MCP Registry — A Real Backend, Explained*

---

## The Analogy

You go to a music festival. At the entrance, you show your ticket. The security guard scans it, confirms it is valid, and puts a wristband on your arm.

For the rest of the day, you don't show your ticket again. You show your wristband. The wristband proves: "This person paid. This person is allowed here." Security at each stage (the food area, the VIP section, the backstage) checks the wristband — not the original ticket.

At the end of the night, the wristband expires. Tomorrow, it means nothing.

This is exactly how JWT (JSON Web Token) authentication works:
- **Your ticket** = your GitHub account or other login credentials
- **The wristband** = a JWT token
- **The registry booth** = the authentication server
- **The festival security** = every API endpoint that checks "is this person allowed?"

---

## The Concept

**Authentication** answers the question: *Who are you?*

It is different from **Authorization**, which answers: *What are you allowed to do?*

The MCP Registry uses **JWT (JSON Web Tokens)** — a widely used, battle-tested method for proving identity without having to send your password with every request.

### How a JWT Works

A JWT is a string of text, split into three parts separated by dots:

```
eyJhbGciOiJFZERTQSJ9.eyJpc3MiOiJtY3AtcmVnaXN0cnkiLCJwZXJtaXNzaW9ucyI6W119.SomeSignatureHere
```

The three parts are:
1. **Header** — what type of token this is and what signing method was used
2. **Payload** (Claims) — the actual information: who you are, what you're allowed to do, when this expires
3. **Signature** — a cryptographic proof that the token hasn't been tampered with

The signature is the magic part. It is created using a **private key** — a secret number only the Registry server knows. Anyone can read a JWT (it is just base64-encoded text), but only the Registry can create a valid one, because only the Registry has the private key.

If someone tries to change the payload (e.g., to give themselves admin permissions), the signature becomes invalid. The Registry detects this and rejects the token. The wristband cannot be forged.

### The MCP Registry's JWT in Real Code

From `registry-main/internal/auth/jwt.go`:

```go
// JWTClaims is what gets stamped into the wristband
type JWTClaims struct {
    jwt.RegisteredClaims              // Standard fields: who issued it, when it expires
    AuthMethod        Method          // How you proved who you are (GitHub, DNS, etc.)
    AuthMethodSubject string          // Your username/identifier
    Permissions       []Permission    // What you're allowed to do
}

type Permission struct {
    Action          PermissionAction  // "publish" or "edit"
    ResourcePattern string            // Which resources, e.g. "io.github.yourname/*"
}
```

The `Permissions` field is powerful. It doesn't just say "this person is logged in." It says "this person can publish tools under the namespace `io.github.yourname`." This means even if your token were stolen, the thief could only publish under your name — not as anyone else.

### Token Expiry: The Wristband That Fades

Notice in the JWT manager:

```go
tokenDuration: 5 * time.Minute, // 5-minute tokens
```

MCP Registry tokens last only **5 minutes**. This is intentional. If a token is intercepted or stolen, it becomes useless in at most 5 minutes. This is a security choice — convenience versus safety, and safety wins.

### The Signing Method: Ed25519

The Registry uses **Ed25519** — an advanced cryptographic signing algorithm. It is faster and more secure than older methods like RSA. Think of it as a lock so complex that even knowing what type of lock it is doesn't help you pick it.

From the real code:

```go
// Create the key pair from a secret seed
privateKey := ed25519.NewKeyFromSeed(seed)
publicKey := privateKey.Public().(ed25519.PublicKey)

// Sign the token (only possible with the private key)
token := jwt.NewWithClaims(&jwt.SigningMethodEd25519{}, claims)
tokenString, _ := token.SignedString(privateKey)

// Validate the token (only needs the public key — can be shared)
jwt.ParseWithClaims(tokenString, &JWTClaims{},
    func(_ *jwt.Token) (interface{}, error) { return publicKey, nil },
)
```

The private key signs. The public key verifies. You can share the public key with the world — it cannot be used to create tokens, only to verify them.

---

## 🔬 Lab Activity — Build and Verify a JWT Token

**What you'll build:** A Python script that creates a JWT-style token (encode + sign), decodes it, checks expiry, and demonstrates what happens when someone tampers with the payload.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell (uses only stdlib — `base64`, `json`, `hmac`, `hashlib`)

---

**1. Create the project folder.**

```powershell
mkdir C:\labs\ch07-auth
cd C:\labs\ch07-auth
```

---

**2. Create the file `jwt_demo.py`.**

```powershell
notepad jwt_demo.py
```
Paste:
```python
import base64
import json
import hmac
import hashlib
import time

SECRET_KEY = b"this-is-the-registry-secret-never-share-it"

def b64url_encode(data: bytes) -> str:
    """Base64URL encode (URL-safe, no padding)."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def b64url_decode(s: str) -> bytes:
    """Base64URL decode with padding fix."""
    padding = 4 - len(s) % 4
    if padding != 4:
        s += "=" * padding
    return base64.urlsafe_b64decode(s)

def create_token(user: str, permissions: list, duration_seconds: int = 300) -> str:
    """Create a signed JWT-style token."""
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {
        "iss": "mcp-registry",
        "sub": user,
        "permissions": permissions,
        "iat": int(time.time()),               # issued at
        "exp": int(time.time()) + duration_seconds  # expiry
    }
    h = b64url_encode(json.dumps(header).encode())
    p = b64url_encode(json.dumps(payload).encode())
    signing_input = f"{h}.{p}"
    sig = hmac.new(SECRET_KEY, signing_input.encode(), hashlib.sha256).digest()
    s = b64url_encode(sig)
    return f"{h}.{p}.{s}"

def verify_token(token: str) -> dict:
    """Verify and decode a token. Returns payload or raises error."""
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token format")

    h, p, s = parts
    # Re-compute expected signature
    expected_sig = hmac.new(
        SECRET_KEY, f"{h}.{p}".encode(), hashlib.sha256
    ).digest()
    actual_sig = b64url_decode(s)

    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("SIGNATURE INVALID — token was tampered with!")

    payload = json.loads(b64url_decode(p))

    if payload["exp"] < time.time():
        raise ValueError(f"TOKEN EXPIRED at {time.ctime(payload['exp'])}")

    return payload

# ---- Demo ----
print("=== JWT Authentication Demo ===\n")

# Create a token
print("Step 1: Client logs in. Registry issues a token.")
token = create_token(
    user="github:yourname",
    permissions=["publish:io.github.yourname/*"],
    duration_seconds=300   # 5 minutes
)
print(f"Token issued:\n  {token[:40]}...{token[-10:]}\n")
print(f"Token has 3 parts separated by dots: HEADER.PAYLOAD.SIGNATURE\n")

# Decode and show the parts
parts = token.split(".")
header  = json.loads(b64url_decode(parts[0]))
payload = json.loads(b64url_decode(parts[1]))
print(f"Header:  {json.dumps(header)}")
print(f"Payload: {json.dumps(payload, indent=2)}")
print(f"\nNote: expiry = {time.ctime(payload['exp'])} (5 minutes from now)\n")

# Verify the token
print("Step 2: Client uses the token for a request.")
try:
    claims = verify_token(token)
    print(f"  ✓ Signature valid")
    print(f"  ✓ Token not expired")
    print(f"  ✓ User: {claims['sub']}")
    print(f"  ✓ Permissions: {claims['permissions']}")
except ValueError as e:
    print(f"  ✗ {e}")

# Tamper with the payload
print("\nStep 3: Attacker tries to change permissions to 'publish:*'")
tampered_payload = payload.copy()
tampered_payload["permissions"] = ["publish:*"]  # trying to gain full access
tampered_p = b64url_encode(json.dumps(tampered_payload).encode())
tampered_token = f"{parts[0]}.{tampered_p}.{parts[2]}"  # old signature, new payload

print(f"  Tampered token: {tampered_token[:40]}...{tampered_token[-10:]}")
try:
    verify_token(tampered_token)
    print("  ✓ Accepted (BUG — this should not happen)")
except ValueError as e:
    print(f"  ✗ REJECTED: {e}")

# Simulate expired token
print("\nStep 4: Simulate an expired token")
expired_token = create_token(
    user="github:attacker",
    permissions=["publish:*"],
    duration_seconds=-10   # already expired 10 seconds ago
)
try:
    verify_token(expired_token)
    print("  ✓ Accepted (BUG)")
except ValueError as e:
    print(f"  ✗ REJECTED: {e}")

print("\n=== Summary ===")
print("  Valid token + correct signature + not expired → ALLOWED")
print("  Tampered payload → signature mismatch → REJECTED")
print("  Expired token → REJECTED")
print("  The signature makes the token tamper-proof without storing it server-side.")
```

**3. Run it.**

```powershell
python jwt_demo.py
```
✅ You should see:
```
=== JWT Authentication Demo ===

Step 1: Client logs in. Registry issues a token.
Token issued:
  eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9...

Header:  {"alg": "HS256", "typ": "JWT"}
Payload: {
  "iss": "mcp-registry",
  "sub": "github:yourname",
  "permissions": ["publish:io.github.yourname/*"],
  ...
}

Step 2: Client uses the token for a request.
  ✓ Signature valid
  ✓ Token not expired
  ✓ User: github:yourname
  ✓ Permissions: ['publish:io.github.yourname/*']

Step 3: Attacker tries to change permissions to 'publish:*'
  ✗ REJECTED: SIGNATURE INVALID — token was tampered with!

Step 4: Simulate an expired token
  ✗ REJECTED: TOKEN EXPIRED at ...

=== Summary ===
  Valid token + correct signature + not expired → ALLOWED
  Tampered payload → signature mismatch → REJECTED
  Expired token → REJECTED
```

The tamper attempt is blocked because changing the payload invalidates the signature. The original signature was computed over the original payload — a different payload produces a different signature that doesn't match.

**What you just built:** A working JWT implementation with create, verify, tamper detection, and expiry checking — the same logic that runs in `registry-main/internal/auth/jwt.go`, using HMAC-SHA256 instead of Ed25519 for simplicity.

---

> **🌍 Real World**
> GitHub uses JWTs for its API authentication. When you run `gh auth login`, GitHub issues a JWT. Every GitHub API call your code makes sends that JWT in the `Authorization: Bearer <token>` header. GitHub validates the signature to confirm it was issued by GitHub, checks the expiry, and checks which repositories the token has access to — exactly the three checks you just implemented. The MCP Registry's 5-minute token expiry is shorter than most services (GitHub tokens last hours). This is a deliberate security tradeoff: a stolen MCP token is only useful for 5 minutes, limiting the damage window.

---

## Research Spotlight

> **"Learning representations by back-propagating errors"** — Rumelhart, D. E., Hinton, G. E., & Williams, R. J. (1986).

Wait — why is a paper about neural networks in a chapter about authentication?

Because this paper introduced a key insight that applies far beyond AI: **systems that can detect errors in their own internal representations can self-correct.** The same mathematical principle — comparing what you expected versus what you got, and adjusting — underlies modern cryptography and digital signatures. The Registry "expects" a certain signature given a certain payload. If reality doesn't match expectation, it rejects the token.

The paper is available through Hinton's archive at: https://www.cs.toronto.edu/~hinton/pages/publications.html

---

## The Takeaway

Authentication is the wristband system of software. A JWT token is issued once (at login), carries proof of identity and permissions inside it, expires after a short time, and is signed so it cannot be forged or modified. The MCP Registry uses 5-minute Ed25519-signed tokens — a modern, secure approach to knowing who is on the other side of the API.

---

## The Connection

You are authenticated. The system knows who you are. But now your request needs to find its way to the right handler inside the server. In Chapter 8, we follow your request through the **routing** system — the postal sorting office that reads the address on every incoming envelope and delivers it to the right desk.

---

*→ Continue to [Chapter 8 — Routing: The Postal Sorting Office](./ch08-routing.md)*
