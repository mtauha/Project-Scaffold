# SysSnap

A robust, extensible **Linux System Configuration Snapshot Utility** for DevOps, SRE, and AI Agent Context Management.

SysSnap captures a complete system configuration snapshot—hardware, OS, packages, running processes, Docker, user accounts, services, logs, and more—producing machine-readable output (JSON/YAML) for troubleshooting, auditing, or feeding LLM-based agents.

Inspired by Sysinternals for Windows, but for modern Linux environments.

---

## 🚀 Features

* **Comprehensive Collection:** CPU, memory, disks, network, OS, users, Docker, packages, services, logs, environment, Python, crontab, hardware, and more.
* **Modular Collectors:** Add new data sources as plugins or Python modules.
* **Privacy-Aware:** Redact or anonymize sensitive info by default (`--redact`, `--anonymize`).
* **Diff Snapshots:** Compare two system states to see what changed (`--diff`).
* **Automation-Ready:** CLI interface for scripting, CI, or agent-triggered calls.
* **Output Options:** JSON, YAML, plain text, compressed, encrypted.
* **API-Ready:** Upload snapshot directly to HTTP(S) endpoints (`--upload-url`).
* **Plugin Support:** Drop Python modules in `plugins/` to auto-extend capabilities.

---

## 📦 Installation

1. **Clone the repository:**

   ```sh
   git clone https://github.com/your-org/syssnap.git
   cd syssnap
   ```
2. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

   * Requires Python 3.7+ and typical Linux CLI utilities.
3. **(Optional) Add custom plugins:**

   * Place `.py` files with a `collect()` function in the `plugins/` directory.

---

## ⚡ Usage

```sh
python syssnap.py [OPTIONS]
```

### **Options**

| Option           | Description                                               |
| ---------------- | --------------------------------------------------------- |
| `--format`     | Output format:`json`,`yaml`,`txt`(default:`json`) |
| `--include`    | Comma-separated list of modules to collect                |
| `--exclude`    | Modules to skip (comma-separated)                         |
| `--out`        | Output file path (default: print to stdout)               |
| `--redact`     | Redact sensitive data (passwords, tokens, secrets, etc.)  |
| `--anonymize`  | Anonymize host/user/IP data                               |
| `--compress`   | Output as ZIP archive                                     |
| `--encrypt`    | Encrypt output (prompts for passphrase)                   |
| `--plugin-dir` | Additional plugin directory (default:`plugins/`)        |
| `--upload-url` | Upload snapshot to given HTTP(S) endpoint                 |
| `--diff A B`   | Diff mode: compare two snapshot files (JSON/YAML)         |
| `--quiet`      | Suppress progress output                                  |

### **Examples**

* **Capture full system snapshot in JSON:**
  ```sh
  python syssnap.py --format json --out snapshot.json
  ```
* **Capture only CPU, memory, disk (anonymized):**
  ```sh
  python syssnap.py --include cpu,memory,disk --anonymize
  ```
* **Diff two snapshots:**
  ```sh
  python syssnap.py --diff snapshot_old.json snapshot_new.json
  ```
* **Compress and encrypt snapshot, then upload:**
  ```sh
  python syssnap.py --compress --encrypt --upload-url https://api.example.com/upload
  ```

---

## 🧩 Architecture & Extensibility

* **Collectors:** Each subsystem has a collector in `collectors/`, exposing a `collect()` function that returns a Python dictionary.
* **ALL_COLLECTORS:** Registered in `collectors/__init__.py` for auto-discovery.
* **Plugins:** Drop-in modules with a `collect()` function, auto-loaded from `plugins/`.
* **Utils:** Modular code for shell execution, output formatting, redaction, diffing, compression, encryption, upload, etc.

**Add new collectors:**

Create `collectors/myfeature.py`:

```python
def collect():
    return {"myfeature": "value"}
```

Add to `ALL_COLLECTORS` in `collectors/__init__.py`.

---

## 🔒 Security & Privacy

* **Redaction:** `--redact` removes or masks common secrets, passwords, tokens, and private keys from output.
* **Anonymization:** `--anonymize` replaces hostnames, user names, IP/MAC addresses for privacy-friendly snapshots.
* **Encryption:** Output can be encrypted with a passphrase before saving or uploading.

---

## 🤖 Agent & CI Integration

* SysSnap is designed to integrate with LLM agents, troubleshooting bots, monitoring pipelines, or CI/CD jobs.
* Machine-readable, structured output.
* HTTP upload option for easy handoff to backend services or agent APIs.

---

## 💡 Example Output

```json
{
  "cpu": { ... },
  "memory": { ... },
  "disk": { ... },
  "network": { ... },
  "osinfo": { ... },
  "docker": { ... },
  "packages": { ... },
  "users": { ... },
  "processes": { ... },
  "env": { ... },
  ...
}
```

---

## 🛠️ Troubleshooting

* Some collectors require root privileges for full output (e.g., hardware, sudoers, some logs).
* Ensure all required Linux utilities are installed (`lscpu`, `lsblk`, `docker`, etc.).
* Custom plugins must define a top-level `collect()` function.

---


## ⭐ Roadmap & TODO

* [ ] Add Kubernetes & cloud environment collectors
* [ ] Real-time monitoring mode
* [ ] Agent API (FastAPI) interface
* [ ] GUI dashboard (future)
* [ ] More fine-grained privacy filters

---
