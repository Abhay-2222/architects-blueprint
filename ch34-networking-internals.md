# Chapter 34 — Networking Internals: How Data Actually Travels

*Part 8: Under the Hood*

---

## The Analogy

You send a letter from your bedroom in Delhi to a company in Tokyo.

You don't hand it directly to anyone in Tokyo. You write the address on the envelope, drop it at your local post office, and let the postal system handle the rest. Your post office looks at the postal code (Tokyo's starts with a different prefix) and forwards it to the international sorting hub. That hub routes it to Japan. Japan's postal system routes it to Tokyo's district office. Tokyo's postman delivers it to the exact building.

Every step, someone reads the address and decides: *"This is not for me — forward it closer to the destination."*

The internet works identically. When you type `registry.modelcontextprotocol.io` into a browser:

1. **DNS** finds the IP address — like looking up Tokyo's postal code
2. **IP routing** forwards your request hop-by-hop — like postal sorting offices
3. **TCP** guarantees delivery and order — like registered mail with tracking
4. **TLS** seals the envelope so no one can read it in transit — like a tamper-evident security pouch
5. **HTTP** defines what the letter says — like the format of a business letter

Every connection you have ever made to the internet follows this exact chain. Every time. In under a second.

---

## The Concept

### IP Addresses: The Postal Code of the Internet

Every device on the internet has an **IP address** — a unique number that identifies it.

An IPv4 address looks like: `104.21.47.33`  
An IPv6 address looks like: `2606:4700:3030::6815:2f21`

Just like a postal code narrows down delivery from "somewhere in the world" to "this specific district," an IP address narrows down from "the internet" to "this exact computer."

Your home router has a public IP address (given by your ISP). Your laptop, phone, and devices on your home network have private IP addresses (assigned by your router, typically `192.168.x.x`). When you send a request to a server, your router translates between your private IP and the public IP — this is called **NAT (Network Address Translation)**.

### DNS: The Phone Book of the Internet

Humans remember names. Computers use numbers. DNS bridges the gap.

**DNS (Domain Name System)** translates human-readable names like `registry.modelcontextprotocol.io` into IP addresses like `104.21.47.33`.

The translation happens in steps, using a hierarchy of DNS servers:

```
You type: registry.modelcontextprotocol.io
          │
          ▼
Your computer checks its local cache. Not there.
          │
          ▼
Asks your router's DNS resolver (usually your ISP's)
          │
          ▼
Root DNS server: "I handle '.io' — ask the .io nameserver"
          │
          ▼
.io nameserver: "I handle 'modelcontextprotocol.io' — ask Cloudflare"
          │
          ▼
Cloudflare DNS: "registry.modelcontextprotocol.io → 104.21.47.33"
          │
          ▼
Your computer caches this. Connects to 104.21.47.33.
```

This entire lookup takes 10–50 milliseconds. After the first lookup, the result is cached so subsequent requests are instant.

### TCP: The Reliable Postal System

IP tells you *where* to send data. TCP tells you *how* to send it reliably.

Without TCP, you would send packets of data into the network with no guarantee they arrive, arrive in order, or aren't duplicated. TCP solves this with:

- **Sequencing**: every packet is numbered, so they can be reassembled in order
- **Acknowledgement**: the receiver confirms every packet received; the sender re-sends if no confirmation arrives
- **Flow control**: the sender slows down if the receiver is overwhelmed
- **Connection establishment**: before sending any data, both sides agree they're ready

The **TCP 3-way handshake** establishes a connection before any data flows:

```
Client                          Server
  │                               │
  │──── SYN (I want to connect) ──►│
  │                               │
  │◄── SYN-ACK (OK, I'm ready) ───│
  │                               │
  │──── ACK (Great, let's go) ───►│
  │                               │
  │  [Connection established]     │
  │  [Data can now flow]          │
```

**SYN** = "synchronise" — client says "I want to talk, here's my starting sequence number"  
**SYN-ACK** = server says "OK, I heard you, here's my starting sequence number"  
**ACK** = client says "Got it, starting now"

After this handshake, data flows in both directions. When the conversation is done, a similar 4-step process closes the connection.

### TLS: The Sealed Security Pouch

TCP guarantees delivery, but anyone can read the data in transit. **TLS (Transport Layer Security)** encrypts it.

When a connection uses HTTPS, TLS runs on top of TCP:

```
Step 1 — Client Hello
Client → Server: "Hello, I support TLS 1.3. Here's a random number."

Step 2 — Server Hello + Certificate
Server → Client: "Hello. Here's my TLS certificate, signed by Let's Encrypt.
                  Here's my public key."

Step 3 — Client Verifies Certificate
Client checks: Is this certificate signed by a trusted authority?
               Is it for the right domain?
               Has it expired?
If yes → continue. If no → abort with "Your connection is not private."

Step 4 — Key Exchange
Both sides generate a shared secret key using asymmetric cryptography.
Nobody watching the network can compute this key.

Step 5 — Encrypted Channel Open
All further data is encrypted with the shared secret.
Even if someone captures every packet, they see only random bytes.
```

A **TLS certificate** contains:
- The domain name it's valid for (e.g., `*.modelcontextprotocol.io`)
- The organisation that owns it
- The public key
- The signature from a trusted Certificate Authority (CA) like Let's Encrypt or DigiCert
- The expiry date

Your browser (and your Python `ssl` module) has a built-in list of trusted CAs. If a certificate is signed by any of them, it is trusted.

### The Full Journey: One HTTP Request

```
┌─────────────────────────────────────────────────────────────┐
│           What happens when you call the MCP Registry        │
└─────────────────────────────────────────────────────────────┘

Your code:
  requests.get("https://registry.modelcontextprotocol.io/v0/servers")

Step 1: DNS
  registry.modelcontextprotocol.io → 104.21.47.33
  (10–50ms, then cached)

Step 2: TCP Handshake with 104.21.47.33:443
  SYN → SYN-ACK → ACK
  (1–3 round trips, ~20–100ms)

Step 3: TLS Handshake
  ClientHello → ServerHello + Certificate → Key exchange
  (1–2 round trips, ~20–100ms)

Step 4: HTTP Request (encrypted)
  GET /v0/servers HTTP/1.1
  Host: registry.modelcontextprotocol.io
  Accept: application/json

Step 5: HTTP Response (encrypted)
  200 OK
  Content-Type: application/json
  {"servers": [...], "total": 247}

Step 6: TCP Connection Close (or Keep-Alive for reuse)

Total: 50–300ms for a cold connection
       5–20ms for a warm connection (TCP + TLS already established)
```

---

## The Real Code

Python's standard library exposes the full networking stack. Here is a raw TCP + TLS connection — no `requests`, no HTTP library — just the socket layer:

```python
import socket
import ssl
import json

# Step 1: Resolve DNS
hostname = "registry.modelcontextprotocol.io"
ip_address = socket.gethostbyname(hostname)
print(f"DNS resolved: {hostname} → {ip_address}")

# Step 2: Create a raw TCP socket
raw_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
raw_socket.settimeout(10)

# Step 3: Wrap in TLS (creates an encrypted tunnel)
context = ssl.create_default_context()
secure_socket = context.wrap_socket(raw_socket, server_hostname=hostname)

# Step 4: Connect (TCP handshake + TLS handshake happen here)
secure_socket.connect((hostname, 443))
print(f"Connected. TLS version: {secure_socket.version()}")

# Step 5: Inspect the certificate
cert = secure_socket.getpeercert()
print(f"Certificate subject: {dict(x[0] for x in cert['subject'])}")
print(f"Certificate issuer:  {dict(x[0] for x in cert['issuer'])}")
print(f"Valid until:         {cert['notAfter']}")

# Step 6: Send an HTTP request (manually, over the encrypted socket)
request = (
    "GET /v0/servers?limit=2 HTTP/1.1\r\n"
    f"Host: {hostname}\r\n"
    "Accept: application/json\r\n"
    "Connection: close\r\n"
    "\r\n"
)
secure_socket.sendall(request.encode())

# Step 7: Receive the response
response = b""
while chunk := secure_socket.recv(4096):
    response += chunk

secure_socket.close()

# Parse HTTP response
headers, body = response.split(b"\r\n\r\n", 1)
print(f"\nHTTP Status: {headers.splitlines()[0].decode()}")
data = json.loads(body)
print(f"Servers returned: {data.get('total', 'N/A')} total")
if data.get("servers"):
    print(f"First server: {data['servers'][0].get('name', 'N/A')}")
```

This is what `requests.get()` does under the hood — every time. The library just wraps these 7 steps in a convenient function.

---

## 🔬 Lab Activity — Tracing a Real Network Connection

**What you'll build:** A Python script that shows the complete DNS → TLS journey to the MCP Registry, plus a network path trace showing every router hop between you and the server.

**Time:** ~20 minutes  
**You'll need:** Python 3.10+ · Windows PowerShell · Internet connection

---

**1. Create the project folder.**

Open PowerShell and run:
```powershell
mkdir C:\labs\ch34-networking
cd C:\labs\ch34-networking
```
✅ The folder is created. No output expected.

---

**2. Look up the DNS record manually.**

```powershell
nslookup registry.modelcontextprotocol.io
```
✅ You should see something like:
```
Server:  UnKnown
Address:  192.168.1.1

Non-authoritative answer:
Name:    registry.modelcontextprotocol.io
Addresses:  104.21.47.33
          172.67.190.148
```
These are the actual IP addresses the registry runs on. Write them down — you'll see them again in the next step.

---

**3. Trace the network path to the registry.**

```powershell
tracert registry.modelcontextprotocol.io
```
✅ You should see a list of router hops, something like:
```
Tracing route to registry.modelcontextprotocol.io [104.21.47.33]
over a maximum of 30 hops:

  1     1 ms    <1 ms    <1 ms  192.168.1.1        ← Your router
  2     5 ms     4 ms     5 ms  10.20.x.x           ← Your ISP
  3    12 ms    11 ms    12 ms  103.x.x.x           ← ISP backbone
  ...
 12    18 ms    17 ms    18 ms  104.21.47.33        ← Cloudflare (MCP Registry)
```
Each row is one router that forwarded your packets. This is the physical path your data takes. The `<1 ms` lines are local. Latency grows as packets travel further.

---

**4. Create the file `inspect_tls.py`.**

In PowerShell, open Notepad or your editor:
```powershell
notepad inspect_tls.py
```
Paste this content exactly and save:
```python
import socket
import ssl
import datetime

hostname = "registry.modelcontextprotocol.io"

# Resolve DNS
ip = socket.gethostbyname(hostname)
print(f"[DNS] {hostname} resolves to {ip}")

# Connect with TLS
ctx = ssl.create_default_context()
with socket.create_connection((hostname, 443), timeout=10) as sock:
    with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
        print(f"[TCP] Connected to {ip}:443")
        print(f"[TLS] Protocol: {ssock.version()}")
        print(f"[TLS] Cipher:   {ssock.cipher()[0]}")

        cert = ssock.getpeercert()

        # Subject (who this cert is for)
        subject = dict(x[0] for x in cert["subject"])
        print(f"[CERT] Domain:  {subject.get('commonName', 'N/A')}")

        # Issuer (who signed it)
        issuer = dict(x[0] for x in cert["issuer"])
        print(f"[CERT] Issuer:  {issuer.get('organizationName', 'N/A')}")

        # Expiry
        expiry_str = cert["notAfter"]
        print(f"[CERT] Expires: {expiry_str}")

        # SANs (all domains this cert covers)
        sans = [v for t, v in cert.get("subjectAltName", []) if t == "DNS"]
        print(f"[CERT] Covers:  {', '.join(sans[:3])}{'...' if len(sans) > 3 else ''}")

print("\n[OK] Full TLS handshake completed successfully.")
print("[OK] This is the same handshake your browser does every time you visit HTTPS sites.")
```

---

**5. Run the script.**

```powershell
python inspect_tls.py
```
✅ You should see output like:
```
[DNS] registry.modelcontextprotocol.io resolves to 104.21.47.33
[TCP] Connected to 104.21.47.33:443
[TLS] Protocol: TLSv1.3
[TLS] Cipher:   TLS_AES_256_GCM_SHA384
[CERT] Domain:  registry.modelcontextprotocol.io
[CERT] Issuer:  Google Trust Services
[CERT] Expires: May 30 12:00:00 2026 GMT
[CERT] Covers:  *.modelcontextprotocol.io, modelcontextprotocol.io...

[OK] Full TLS handshake completed successfully.
[OK] This is the same handshake your browser does every time you visit HTTPS sites.
```

If you see a different IP or issuer — that is correct. CDN providers like Cloudflare use many IPs, and certificate issuers rotate.

---

**6. Create the file `raw_http_request.py`.**

This script sends a real HTTP request over the raw socket — exactly what `requests.get()` does internally:
```powershell
notepad raw_http_request.py
```
Paste:
```python
import socket
import ssl
import json

hostname = "registry.modelcontextprotocol.io"
path = "/v0/servers?limit=3"

ctx = ssl.create_default_context()
with socket.create_connection((hostname, 443), timeout=10) as sock:
    with ctx.wrap_socket(sock, server_hostname=hostname) as ssock:
        # Build the HTTP request manually
        http_request = (
            f"GET {path} HTTP/1.1\r\n"
            f"Host: {hostname}\r\n"
            "Accept: application/json\r\n"
            "User-Agent: ch34-lab/1.0\r\n"
            "Connection: close\r\n"
            "\r\n"
        )
        ssock.sendall(http_request.encode())
        print(f"[SENT] HTTP request to {hostname}{path}")

        # Receive response
        response = b""
        while True:
            chunk = ssock.recv(4096)
            if not chunk:
                break
            response += chunk

# Split headers from body
header_part, _, body_part = response.partition(b"\r\n\r\n")
status_line = header_part.splitlines()[0].decode()
print(f"[RECV] Status: {status_line}")

# Show headers
print("[RECV] Headers:")
for line in header_part.splitlines()[1:6]:
    print(f"       {line.decode()}")

# Parse JSON body
try:
    data = json.loads(body_part)
    total = data.get("total", "unknown")
    servers = data.get("servers", [])
    print(f"\n[DATA] Total MCP servers in registry: {total}")
    print("[DATA] First 3 servers:")
    for s in servers[:3]:
        print(f"       - {s.get('name', 'N/A')}: {s.get('description', '')[:60]}")
except Exception as e:
    print(f"[WARN] Could not parse JSON: {e}")
    print(f"[RAW] Body starts with: {body_part[:200]}")
```

---

**7. Run the raw HTTP request.**

```powershell
python raw_http_request.py
```
✅ You should see:
```
[SENT] HTTP request to registry.modelcontextprotocol.io/v0/servers?limit=3
[RECV] Status: HTTP/1.1 200 OK
[RECV] Headers:
       Content-Type: application/json
       ...

[DATA] Total MCP servers in registry: 247
[DATA] First 3 servers:
       - FileReader MCP: Reads files from your local computer
       - Web Search MCP: Searches the internet
       - ...
```

You just made a real HTTP request to a live production API — manually, at the socket level. No library. No abstraction. Just bytes.

---

**What you just built:** Two Python scripts that perform the complete networking journey: DNS resolution, TCP connection, TLS handshake, certificate inspection, and raw HTTP. Every connection your AI agent makes to the MCP Registry goes through exactly these steps.

---

> **🌍 Real World**
> Every HTTPS connection you make — to the MCP Registry, to GitHub, to your bank — follows the DNS → TCP → TLS → HTTP chain you just implemented manually. Cloudflare sits in front of the MCP Registry and handles TLS termination, DDoS protection, and global routing. When your AI agent calls `GET /v0/servers`, its traffic physically travels through routers across the internet, just like the `tracert` output you saw. The `TLSv1.3` you saw in your certificate inspection is the same protocol that protects your banking data.

---

## Research Spotlight

> **"Attention Is All You Need"** — Vaswani, A., et al. (2017). *NeurIPS*.

This paper introduced the Transformer architecture — the foundation of every large language model including GPT-4, Claude, and Llama. Its relevance here: the Transformer's attention mechanism is deeply related to how TCP manages reliable delivery. Both solve the same fundamental problem — *how do you know what's important, and what order does it belong in?* TCP uses sequence numbers and acknowledgements. The Transformer uses attention weights to determine which tokens in a long sequence deserve the most focus. Understanding networking deepens your intuition for how AI models handle sequences of information.

---

## The Takeaway

Every HTTP request your code makes goes through five layers: DNS translates the name to an IP address, TCP establishes a reliable connection with a 3-way handshake, TLS encrypts the channel with a certificate-based key exchange, and HTTP carries the actual request and response. You can see all of this with `nslookup`, `tracert`, and Python's `socket` + `ssl` modules — the same tools that production engineers use to debug network issues.

---

## The Connection

You can see the network layer. Now: what happens when that network is used as a vector for attack? Chapter 35 opens the castle gates — and then shows you how to close them. Security is the other side of every networking concept you just learned.

---

*→ Continue to [Chapter 35 — Security & Threat Models](./ch35-security-and-threat-models.md)*
