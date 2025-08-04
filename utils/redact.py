import re

SENSITIVE_KEYS = [
    "password",
    "token",
    "secret",
    "key",
    "passphrase",
    "credential",
    "PRIVATE",
    "SSH",
]
ANONYMIZE_KEYS = ["hostname", "user", "username", "login", "ip", "mac", "host"]


def redact_snapshot(snapshot, redact=True, anonymize=False):
    def recursive_redact(d):
        if isinstance(d, dict):
            return {
                k: (
                    "[REDACTED]"
                    if redact and any(s in k.lower() for s in SENSITIVE_KEYS)
                    else (
                        "[ANONYMIZED]"
                        if anonymize and any(a in k.lower() for a in ANONYMIZE_KEYS)
                        else recursive_redact(v)
                    )
                )
                for k, v in d.items()
            }
        elif isinstance(d, list):
            return [recursive_redact(x) for x in d]
        elif isinstance(d, str) and anonymize:
            # Simple anonymization for IPs, hostnames, etc.
            d = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[ANONYMIZED_IP]", d)
            d = re.sub(
                r"\b[a-fA-F0-9]{2}(?::[a-fA-F0-9]{2}){5}\b", "[ANONYMIZED_MAC]", d
            )
            return d
        return d

    return recursive_redact(snapshot)
