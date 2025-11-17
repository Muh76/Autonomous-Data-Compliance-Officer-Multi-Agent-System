"""Compliance scenario test cases."""

from typing import List, Dict, Any

# Example compliance scenarios for testing
GDPR_SCENARIOS = [
    {
        "name": "Data Processing Consent",
        "description": "Check if data processing has proper consent",
        "expected_finding": "non_compliant",
    },
    {
        "name": "Right to Erasure",
        "description": "Verify data deletion capabilities",
        "expected_finding": "compliant",
    },
]

HIPAA_SCENARIOS = [
    {
        "name": "PHI Encryption",
        "description": "Check if PHI is encrypted at rest",
        "expected_finding": "non_compliant",
    },
]

SCENARIOS = {
    "GDPR": GDPR_SCENARIOS,
    "HIPAA": HIPAA_SCENARIOS,
}

