"""
FinGuard AI - Contextual Risk Engine
Evaluates gateway environmental signals: Merchant risk, Device familiarity,
IP network intelligence, Geolocation consistency, KYC, and Account Age.
Transparently demarcates simulated demonstration inputs from dataset ML signals.
"""

import sys
import logging
from typing import Dict, Any, List

# Add project root to sys.path
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

logger = logging.getLogger("FinGuard_Contextual")


class ContextualRiskEngine:
    """
    Evaluates real-time environmental context around a transaction.
    """

    # Merchant Category Base Risk Matrix (0 - 100)
    MERCHANT_RISK_MAP = {
        "crypto": 85.0,
        "gambling": 90.0,
        "luxury_jewelry": 65.0,
        "p2p_transfer": 55.0,
        "electronics": 40.0,
        "travel_airline": 35.0,
        "retail": 20.0,
        "grocery": 10.0,
        "utilities": 5.0,
        "other": 30.0,
    }

    # Device Status Risk Matrix
    DEVICE_RISK_MAP = {
        "trusted_device": 5.0,
        "new_device": 45.0,
        "emulator_rooted": 90.0,
        "unknown": 35.0,
    }

    # IP Network Reputation Matrix
    IP_REPUTATION_MAP = {
        "clean_residential": 5.0,
        "datacenter_cloud": 40.0,
        "vpn_proxy": 65.0,
        "tor_blacklisted": 95.0,
        "unknown": 30.0,
    }

    # Geolocation Consistency Matrix
    LOCATION_RISK_MAP = {
        "home_location": 5.0,
        "domestic_travel": 25.0,
        "international_travel": 60.0,
        "impossible_velocity": 95.0,  # e.g., location changed 8,000 km in 30 mins
        "unknown": 30.0,
    }

    # KYC & Security Verification Matrix
    KYC_RISK_MAP = {
        "fully_verified": 5.0,       # Government ID + Biometrics
        "tier_1_verified": 30.0,     # Phone / Email verified only
        "unverified": 80.0,          # Incomplete documentation
    }

    def evaluate_contextual_risk(self, ctx_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes composite contextual risk (0-100).
        """
        factors: List[str] = []

        # 1. Merchant Category Risk (Weight: 25%)
        merchant_cat = str(ctx_input.get("merchant_category", "retail")).lower().strip()
        m_score = self.MERCHANT_RISK_MAP.get(merchant_cat, self.MERCHANT_RISK_MAP["other"])
        if m_score >= 80:
            factors.append(
                f"High-risk merchant industry: '{merchant_cat.replace('_', ' ').title()}' is a frequent vector for irreversible fraud (+{m_score:.0f} pts)."
            )
        elif m_score <= 15:
            factors.append(
                f"Low-risk routine merchant: '{merchant_cat.replace('_', ' ').title()}' (essential services / utilities)."
            )

        # 2. Device Fingerprint Familiarity (Weight: 20%)
        device_status = str(ctx_input.get("device_status", "trusted_device")).lower().strip()
        d_score = self.DEVICE_RISK_MAP.get(device_status, self.DEVICE_RISK_MAP["unknown"])
        if d_score >= 80:
            factors.append(
                "Critical device threat: Device fingerprint indicates rooted OS, virtual environment, or emulator (+90 pts)."
            )
        elif d_score >= 40:
            factors.append(
                "New device detected: Transaction initiated from previously unrecognized hardware fingerprint (+45 pts)."
            )
        else:
            factors.append("Recognized hardware: Authenticated from established trusted device.")

        # 3. IP Network Reputation (Weight: 20%)
        ip_status = str(ctx_input.get("ip_status", "clean_residential")).lower().strip()
        ip_score = self.IP_REPUTATION_MAP.get(ip_status, self.IP_REPUTATION_MAP["unknown"])
        if ip_score >= 80:
            factors.append(
                "Severe network threat: Connection originated from Tor exit node or blacklisted proxy network (+95 pts)."
            )
        elif ip_score >= 50:
            factors.append(
                "Anonymizing proxy/VPN detected: Commercial VPN hiding true client origin (+65 pts)."
            )
        else:
            factors.append("Legitimate network: Clean residential ISP connection.")

        # 4. Geolocation Consistency (Weight: 15%)
        loc_status = str(ctx_input.get("location_status", "home_location")).lower().strip()
        l_score = self.LOCATION_RISK_MAP.get(loc_status, self.LOCATION_RISK_MAP["unknown"])
        if l_score >= 80:
            factors.append(
                "Impossible travel speed: Geographic distance from last active session exceeds physical travel speed (+95 pts)."
            )
        elif l_score >= 50:
            factors.append(
                "Cross-border international location: Transaction originating outside account domicile (+60 pts)."
            )

        # 5. Account Age Risk (Weight: 10%)
        account_age_days = int(ctx_input.get("account_age_days", 180))
        if account_age_days < 7:
            a_score = 75.0
            factors.append(f"Newly registered account ({account_age_days} days old) has elevated chargeback vulnerability.")
        elif account_age_days < 30:
            a_score = 45.0
        elif account_age_days < 90:
            a_score = 25.0
        else:
            a_score = 5.0
            factors.append(f"Matured account history ({account_age_days} days old).")

        # 6. KYC & Account Security Status (Weight: 10%)
        kyc_status = str(ctx_input.get("kyc_status", "fully_verified")).lower().strip()
        k_score = self.KYC_RISK_MAP.get(kyc_status, 40.0)
        if k_score >= 70:
            factors.append("Unverified KYC profile: Account lacks government identification verification (+80 pts).")
        else:
            factors.append("Verified KYC profile: Customer identity fully verified.")

        # Multi-factor Weighted Composite
        composite_score = (
            m_score * 0.25
            + d_score * 0.20
            + ip_score * 0.20
            + l_score * 0.15
            + a_score * 0.10
            + k_score * 0.10
        )

        composite_score = max(0.0, min(100.0, composite_score))

        return {
            "contextual_risk_score": round(composite_score, 2),
            "signal_origin": "simulated_gateway_context",
            "component_scores": {
                "merchant_score": m_score,
                "device_score": d_score,
                "ip_score": ip_score,
                "location_score": l_score,
                "account_age_score": a_score,
                "kyc_score": k_score,
            },
            "factors": factors,
        }


# Singleton
_contextual_engine = None


def get_contextual_engine() -> ContextualRiskEngine:
    global _contextual_engine
    if _contextual_engine is None:
        _contextual_engine = ContextualRiskEngine()
    return _contextual_engine


if __name__ == "__main__":
    engine = get_contextual_engine()
    sample_ctx = {
        "merchant_category": "crypto",
        "device_status": "new_device",
        "ip_status": "vpn_proxy",
        "location_status": "international_travel",
        "account_age_days": 4,
        "kyc_status": "unverified",
    }
    res = engine.evaluate_contextual_risk(sample_ctx)
    print("Contextual Assessment Result:")
    for k, v in res.items():
        print(f"  {k}: {v}")
