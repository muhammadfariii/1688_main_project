"""
Supplier Classifier for 1688 Sourcing Tool.
Uses a multi-factor heuristic signal engine to classify suppliers as
'Factory', 'Trading Company', or 'Uncertain' with confidence scoring.
"""

import re
from typing import Dict, List, Any, Optional

class SupplierClassification:
    def __init__(self, supplier_type: str, confidence: float, score: int, signals: List[str], details: Optional[Dict[str, Any]] = None):
        self.type = supplier_type  # "Factory", "Trading Company", "Uncertain"
        self.confidence = confidence  # 0.0 to 100.0
        self.score = score  # Raw heuristic score (-100 to +100)
        self.signals = signals
        self.details = details or {}

    @property
    def is_factory(self) -> bool:
        return self.type == "Factory"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type,
            "confidence": round(self.confidence, 1),
            "confidence_percent": f"{round(self.confidence)}%",
            "score": self.score,
            "signals": self.signals,
            "details": self.details
        }


class HeuristicSupplierClassifier:
    """
    Heuristic classifier based on company name patterns, business scope,
    audit badges, facility size, registered capital, and operational metrics.
    """

    # Chinese and English Strong Factory Keywords
    FACTORY_NAME_KEYWORDS = [
        "制造", "生产", "工厂", "实业", "制品", "机械", "五金", "电子", 
        "塑胶", "模具", "制衣", "包装", "纺织", "印染", "科技实业", "五金塑胶",
        "厂", "制造业", "工艺品厂", "加工厂",
        "manufacturing", "factory", "industrial", "machinery", "hardware",
        "plastics", "mould", "molding", "garment", "textile", "works", "mills"
    ]

    # Strong Trading / Reseller Keywords
    TRADING_NAME_KEYWORDS = [
        "贸易", "进出口", "商行", "百货", "商贸", "商务", "供应链", 
        "电子商务", "销售", "批发", "商社", "经贸",
        "trading", "trade", "commerce", "commercial", "import & export", 
        "supply chain", "e-commerce", "wholesaler", "distributor", "agency", "store"
    ]

    # Business scope positive signals
    FACTORY_SCOPE_KEYWORDS = [
        "生产", "加工", "制造", "定制", "开模", "组装", "研发生产", "设计制造",
        "production", "processing", "fabrication", "assembly", "oem", "odm", "customization"
    ]

    # Business scope negative signals
    TRADING_SCOPE_KEYWORDS = [
        "批发", "零售", "转口", "代理", "销售代理", "代销",
        "wholesale", "retail", "brokerage", "distribution"
    ]

    # Audit & Verification Badges
    FACTORY_BADGES = [
        "超级工厂", "源头工厂", "深度验厂", "实力商家", "SGS认证", "TUV认证", "BV认证",
        "super factory", "source factory", "verified factory", "deep audited factory",
        "iso9001", "bsci", "sedex", "ce", "rohs"
    ]

    def classify(self, supplier_data: Dict[str, Any]) -> SupplierClassification:
        name = str(supplier_data.get("supplier_name") or supplier_data.get("name") or "").strip()
        scope = str(supplier_data.get("business_scope") or "").strip()
        desc = str(supplier_data.get("description") or "").strip()
        badges = supplier_data.get("badges", [])
        if isinstance(badges, str):
            badges = [badges]
        badges_str = " ".join([str(b) for b in badges]).lower()
        
        area_sqm = supplier_data.get("factory_area_sqm") or supplier_data.get("plant_area", 0)
        staff_count = supplier_data.get("employees_count") or supplier_data.get("staff_count", 0)
        capital_rmb_k = supplier_data.get("registered_capital_k_rmb", 0)
        years_in_business = supplier_data.get("years_in_business", 0)

        signals: List[str] = []
        score = 0

        name_lower = name.lower()
        scope_lower = scope.lower()
        desc_lower = desc.lower()

        # 1. Evaluate Company Name
        has_factory_name = False
        for kw in self.FACTORY_NAME_KEYWORDS:
            if kw.lower() in name_lower:
                score += 35
                signals.append(f"Company name contains factory keyword: '{kw}' (+35)")
                has_factory_name = True
                break

        has_trading_name = False
        for kw in self.TRADING_NAME_KEYWORDS:
            if kw.lower() in name_lower:
                score -= 40
                signals.append(f"Company name contains trading keyword: '{kw}' (-40)")
                has_trading_name = True
                break

        # Edge case: Both present (e.g., "XX Manufacturing and Trading Co.")
        if has_factory_name and has_trading_name:
            signals.append("Hybrid name containing both manufacturing and trading terms")

        # 2. Evaluate Badges & Certifications
        for badge in self.FACTORY_BADGES:
            if badge.lower() in badges_str:
                score += 25
                signals.append(f"Verified platform badge/audit: '{badge}' (+25)")
                break

        # 3. Evaluate Business Scope
        scope_factory_hits = [kw for kw in self.FACTORY_SCOPE_KEYWORDS if kw.lower() in scope_lower or kw.lower() in desc_lower]
        if scope_factory_hits:
            score += 20
            signals.append(f"Business scope includes manufacturing activities: {', '.join(scope_factory_hits[:2])} (+20)")

        scope_trading_hits = [kw for kw in self.TRADING_SCOPE_KEYWORDS if kw.lower() in scope_lower or kw.lower() in desc_lower]
        if scope_trading_hits and not scope_factory_hits:
            score -= 20
            signals.append(f"Business scope primarily lists trading/reselling (+wholesale/retail) (-20)")

        # 4. Evaluate Physical Plant & Scale
        try:
            area_num = float(area_sqm)
            if area_num >= 5000:
                score += 20
                signals.append(f"Substantial facility size ({int(area_num):,} m²) (+20)")
            elif area_num >= 1000:
                score += 10
                signals.append(f"Dedicated workshop/plant space ({int(area_num):,} m²) (+10)")
            elif area_num > 0 and area_num < 200:
                score -= 10
                signals.append(f"Minimal office-only space footprint ({int(area_num)} m²) (-10)")
        except (ValueError, TypeError):
            pass

        # 5. Evaluate Workforce / Employees
        try:
            staff_num = int(staff_count)
            if staff_num >= 50:
                score += 15
                signals.append(f"Manufacturing workforce scale ({staff_num}+ personnel) (+15)")
            elif staff_num >= 20:
                score += 8
                signals.append(f"Active staff scale ({staff_num} personnel) (+8)")
            elif staff_num > 0 and staff_num <= 5:
                score -= 10
                signals.append(f"Very small micro-enterprise staff ({staff_num}) (-10)")
        except (ValueError, TypeError):
            pass

        # 6. Registered Capital & Longevity
        try:
            cap_num = float(capital_rmb_k)
            if cap_num >= 5000:  # 5 Million RMB+
                score += 10
                signals.append(f"High registered capital (¥{int(cap_num):,}k RMB) (+10)")
            elif cap_num >= 1000:  # 1 Million RMB+
                score += 5
                signals.append(f"Registered capital >= ¥1M RMB (+5)")
        except (ValueError, TypeError):
            pass

        if years_in_business >= 5:
            score += 5
            signals.append(f"Established supplier track record ({years_in_business} years in business) (+5)")

        # Normalization and Classification Logic
        # Raw score typically spans from -70 to +110
        if score >= 25:
            supplier_type = "Factory"
            # Map score 25..100 to confidence 65%..98%
            confidence = min(98.0, max(65.0, 65.0 + (score - 25) * 0.44))
        elif score <= -15:
            supplier_type = "Trading Company"
            # Map negative score to confidence 65%..98%
            confidence = min(98.0, max(65.0, 65.0 + (abs(score) - 15) * 0.45))
        else:
            supplier_type = "Uncertain"
            confidence = max(50.0, 50.0 + abs(score))

        return SupplierClassification(
            supplier_type=supplier_type,
            confidence=confidence,
            score=score,
            signals=signals,
            details={
                "area_sqm": area_sqm,
                "staff_count": staff_count,
                "years_in_business": years_in_business
            }
        )

# Global classifier instance
classifier = HeuristicSupplierClassifier()
