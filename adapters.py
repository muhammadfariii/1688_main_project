"""
Data Provider Adapters for 1688 Sourcing Tool.
Provides a pluggable adapter layer to abstract differences between
Demo/Mock data sources and real 1688 API providers (e.g., ParseBot, Open1688, etc.).
"""

import abc
import hashlib
import random
import requests
from typing import List, Dict, Any, Optional
from config import config, AppConfig

class BaseProviderAdapter(abc.ABC):
    """Abstract interface that all 1688 data providers must implement."""

    @abc.abstractmethod
    def search_single_product(self, query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        Search 1688 for a single product query.
        Returns a list of raw/standardized supplier and product records.
        """
        pass

    @abc.abstractmethod
    def search_multi_products(self, queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Search 1688 for multiple product queries.
        Returns a dictionary mapping each query to its matching supplier records.
        """
        pass

    @abc.abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Returns provider metadata and status."""
        pass


class DemoAdapter(BaseProviderAdapter):
    """
    Demo/Mock adapter delivering rich, realistic 1688 supplier data.
    Works completely offline without API keys for instant testing.
    """

    CHINESE_INDUSTRIAL_CLUSTERS = [
        ("Zhejiang Yongkang", "浙江永康", "Hardware & Drinkware Hub"),
        ("Zhejiang Yiwu", "浙江义乌", "Small Commodities & Daily Necessities"),
        ("Guangdong Dongguan", "广东东莞", "Plastics, Electronics & Moulding"),
        ("Guangdong Chaozhou", "广东潮州", "Ceramics & Stainless Steel Kitchenware"),
        ("Guangdong Shenzhen", "广东深圳", "Consumer Electronics & Tech"),
        ("Zhejiang Ningbo", "浙江宁波", "Small Appliances & Stationery Hub"),
        ("Zhejiang Cixi", "浙江慈溪", "Household Electrical Appliances"),
        ("Jiangsu Yangquan", "江苏阳泉", "Glassware & Borosilicate Products"),
        ("Fujian Dehua", "福建德化", "Ceramic & Kitchenware Crafting"),
        ("Hebei Cangzhou", "河北沧州", "Glass Products & Packaging")
    ]

    # Pre-defined mock vendor profiles for realistic multi-item coverage
    VENDOR_PROFILES = [
        {
            "brand_en": "Hengtai", "brand_cn": "恒泰",
            "cluster_idx": 0, "type_en": "Manufacturing & Industrial Group Co., Ltd.", "type_cn": "制造实业集团有限公司",
            "is_factory": True, "area": 25000, "staff": 320, "capital": 20000, "years": 14,
            "badges": ["超级工厂 (Super Factory)", "深度验厂 (Deep Audited)", "实力商家", "ISO9001:2015", "BSCI Certified"],
            "coverage_tier": 0.90
        },
        {
            "brand_en": "Jinyi", "brand_cn": "金亿",
            "cluster_idx": 3, "type_en": "Precision Hardware & Plastics Factory Co., Ltd.", "type_cn": "五金塑胶精密制造厂",
            "is_factory": True, "area": 16000, "staff": 210, "capital": 10000, "years": 11,
            "badges": ["超级工厂 (Super Factory)", "实力商家", "ISO9001:2015"],
            "coverage_tier": 0.80
        },
        {
            "brand_en": "Xinda", "brand_cn": "鑫达",
            "cluster_idx": 5, "type_en": "Industrial Products OEM/ODM Production Base", "type_cn": "实业制品定制制造基地",
            "is_factory": True, "area": 12000, "staff": 140, "capital": 8000, "years": 9,
            "badges": ["源头工厂 (Source Factory)", "深度验厂", "BSCI Certified"],
            "coverage_tier": 0.70
        },
        {
            "brand_en": "Haorun", "brand_cn": "浩润",
            "cluster_idx": 1, "type_en": "Global Supply Chain & Trading Co., Ltd.", "type_cn": "供应链商贸进出口有限公司",
            "is_factory": False, "area": 120, "staff": 8, "capital": 500, "years": 5,
            "badges": ["实力商家 (Powerful Merchant)"],
            "coverage_tier": 0.85
        },
        {
            "brand_en": "Yongchuang", "brand_cn": "永创",
            "cluster_idx": 2, "type_en": "Moulding & Technology Manufacturing Co., Ltd.", "type_cn": "模具科技制造实业有限公司",
            "is_factory": True, "area": 8500, "staff": 95, "capital": 5000, "years": 8,
            "badges": ["源头工厂 (Source Factory)", "ISO9001:2015"],
            "coverage_tier": 0.55
        },
        {
            "brand_en": "Meijia", "brand_cn": "美佳",
            "cluster_idx": 6, "type_en": "Household Goods & Hardware Factory", "type_cn": "家居五金制造实业厂",
            "is_factory": True, "area": 7000, "staff": 75, "capital": 3000, "years": 6,
            "badges": ["实力商家"],
            "coverage_tier": 0.50
        },
        {
            "brand_en": "Bosen", "brand_cn": "博森",
            "cluster_idx": 1, "type_en": "Commercial Wholesale & Distribution Firm", "type_cn": "商贸商行",
            "is_factory": False, "area": 60, "staff": 4, "capital": 100, "years": 3,
            "badges": [],
            "coverage_tier": 0.40
        },
        {
            "brand_en": "Sanhe", "brand_cn": "三和",
            "cluster_idx": 4, "type_en": "Electronics & Plastics Factory Co., Ltd.", "type_cn": "电子塑胶制造有限公司",
            "is_factory": True, "area": 5500, "staff": 60, "capital": 2000, "years": 5,
            "badges": ["源头工厂"],
            "coverage_tier": 0.35
        },
        {
            "brand_en": "Dongfang", "brand_cn": "东方",
            "cluster_idx": 1, "type_en": "E-Commerce Trade & Sourcing Center", "type_cn": "电子商务商贸商社",
            "is_factory": False, "area": 80, "staff": 5, "capital": 200, "years": 2,
            "badges": [],
            "coverage_tier": 0.30
        },
        {
            "brand_en": "Yongfa", "brand_cn": "永发",
            "cluster_idx": 7, "type_en": "Specialized Glass & Craft Products Factory", "type_cn": "特种玻璃五金制品厂",
            "is_factory": True, "area": 4500, "staff": 50, "capital": 1500, "years": 4,
            "badges": ["源头工厂"],
            "coverage_tier": 0.25
        }
    ]

    def __init__(self):
        self.provider_name = "demo"

    def get_provider_info(self) -> Dict[str, Any]:
        return {
            "name": "Demo Provider (Realistic Mock)",
            "is_demo": True,
            "connected": True,
            "description": "Built-in realistic sample data generator for instant testing without API credentials."
        }

    def _build_supplier_dict(self, profile: Dict[str, Any], query: str, seed_offset: int = 0) -> Dict[str, Any]:
        cluster_en, cluster_cn, cluster_specialty = self.CHINESE_INDUSTRIAL_CLUSTERS[profile["cluster_idx"]]
        city_name = cluster_en.split()[-1]
        
        brand_en = profile["brand_en"]
        brand_cn = profile["brand_cn"]
        type_en = profile["type_en"]
        type_cn = profile["type_cn"]
        cluster_idx = profile["cluster_idx"]

        company_name_en = f"{cluster_en} {brand_en} {type_en}"
        company_name_cn = f"{cluster_cn}{brand_cn}{type_cn}"
        supplier_name = f"{company_name_en} ({company_name_cn})"
        
        key_id = f"{brand_en}_{cluster_idx}"
        supplier_id = f"1688_sup_{abs(hash(key_id)) % 900000 + 100000}"
        shop_id = f"shop{abs(hash(supplier_id)) % 80000000 + 10000000}"
        
        rng = random.Random(abs(hash(f"{supplier_id}_{query}_{seed_offset}")))
        
        if profile["is_factory"]:
            business_scope = f"Production, OEM/ODM custom fabrication, mould opening, and R&D for {query} and industrial supplies. Full factory export standards."
            sample_products = [
                f"Custom OEM {query} (Food/Industrial Grade, Factory Direct)",
                f"Wholesale Commercial {query} (High Capacity Spec)",
                f"Eco-friendly {query} with Custom Silk Screen / Laser Logo",
                f"Heavy Duty Standard {query}"
            ]
            price_range = f"¥{rng.randint(6, 28)}.{rng.randint(10, 99)} - ¥{rng.randint(35, 75)}.{rng.randint(10, 99)}"
            moq = f"{rng.choice([100, 200, 500, 1000])} pcs"
            contact_note = "1688 AliWangWang (Direct Factory Manager: Mr. Chen) / 1688 Verified Shop"
        else:
            business_scope = f"Wholesale distribution, e-commerce retail, drop-shipping, and multi-category trading of {query} and daily commodities."
            sample_products = [
                f"Ready-to-Ship Spot {query} (Mixed Colors Available)",
                f"Low MOQ {query} for Online Sellers & Amazon/TikTok Shop",
                f"Popular Trend {query} Wholesale Batch"
            ]
            price_range = f"¥{rng.randint(12, 38)}.{rng.randint(10, 99)} - ¥{rng.randint(45, 95)}.{rng.randint(10, 99)}"
            moq = f"{rng.choice([2, 5, 10, 50])} pcs"
            contact_note = "1688 Trade Messenger (Online Customer Rep: Ms. Liu)"

        item_id = abs(hash(f"{supplier_id}_{query}")) % 800000000000 + 100000000000

        return {
            "supplier_id": supplier_id,
            "supplier_name": supplier_name,
            "company_name_en": company_name_en,
            "company_name_cn": company_name_cn,
            "location": f"{cluster_en} ({cluster_cn})",
            "city": city_name,
            "industrial_cluster": cluster_specialty,
            "business_scope": business_scope,
            "factory_area_sqm": profile["area"],
            "employees_count": profile["staff"],
            "registered_capital_k_rmb": profile["capital"],
            "years_in_business": profile["years"],
            "badges": profile["badges"],
            "products_matched": sample_products,
            "primary_product": sample_products[0],
            "price_range_rmb": price_range,
            "moq": moq,
            "contact_info": contact_note,
            "shop_url": f"https://{shop_id}.1688.com",
            "item_url": f"https://detail.1688.com/offer/{item_id}.html"
        }

    def search_single_product(self, query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        clean_q = (query or "").strip().title()
        if not clean_q:
            return []
        
        results = []
        for i, profile in enumerate(self.VENDOR_PROFILES):
            results.append(self._build_supplier_dict(profile, clean_q, seed_offset=i))
        return results

    def search_multi_products(self, queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        results_by_query = {}
        cleaned_queries = [q.strip().title() for q in queries if q and q.strip()]

        for q_idx, q in enumerate(cleaned_queries):
            results_for_item = []
            for v_idx, profile in enumerate(self.VENDOR_PROFILES):
                brand = profile["brand_en"]
                item_seed = int(hashlib.md5(f"{brand}_{q}".encode("utf-8")).hexdigest()[:6], 16)
                prob = (item_seed % 100) / 100.0
                
                # Top factory and broad trader have high coverage
                if prob <= profile["coverage_tier"] or (v_idx < 2 and q_idx < 4):
                    results_for_item.append(self._build_supplier_dict(profile, q, seed_offset=q_idx))
            
            results_by_query[q] = results_for_item

        return results_by_query


class ParseBotAdapter(BaseProviderAdapter):
    """
    Live 1688 data provider adapter (e.g. ParseBot or similar 1688 API service).
    Connects to external REST API using server-side API keys.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or config.provider_api_key
        self.base_url = (base_url or config.provider_base_url or "https://api.parsebot.com/v1").rstrip("/")
        self.provider_name = "parsebot"
        self.timeout = 15

    def get_provider_info(self) -> Dict[str, Any]:
        has_key = bool(self.api_key.strip())
        return {
            "name": "ParseBot 1688 Live API",
            "is_demo": False,
            "connected": has_key,
            "base_url": self.base_url,
            "description": "Connects to ParseBot 1688 REST API service for real-time live product queries."
        }

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "1688-Sourcing-Tool/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
            headers["X-API-Key"] = self.api_key
        return headers

    def search_single_product(self, query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        Executes live query against 1688 provider API.
        Maps returned vendor and product fields to standard schema.
        """
        if not self.api_key:
            raise ValueError("ParseBot API Key is missing. Please configure PROVIDER_API_KEY in environment.")

        endpoint = f"{self.base_url}/search/1688"
        payload = {
            "query": query,
            "page": page,
            "pageSize": page_size,
            "filter": {
                "factoryOnly": False
            }
        }

        try:
            resp = requests.post(endpoint, json=payload, headers=self._get_headers(), timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            items = data.get("data", {}).get("items", []) or data.get("items", []) or []
            return [self._map_raw_item_to_standard(item) for item in items]
        except requests.exceptions.RequestException as e:
            print(f"[ParseBotAdapter] API request failed: {e}")
            raise RuntimeError(f"Live 1688 API provider error: {str(e)}")

    def search_multi_products(self, queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        results = {}
        for q in queries:
            try:
                results[q] = self.search_single_product(q, page=1, page_size=15)
            except Exception as e:
                print(f"[ParseBotAdapter] Error searching '{q}': {e}")
                results[q] = []
        return results

    def _map_raw_item_to_standard(self, raw: Dict[str, Any]) -> Dict[str, Any]:
        """
        Maps raw JSON from third-party provider to our internal standard supplier schema.
        """
        supplier_name = raw.get("company_name") or raw.get("shop_name") or raw.get("seller_title") or "Unknown 1688 Seller"
        return {
            "supplier_id": str(raw.get("company_id") or raw.get("seller_id") or raw.get("member_id") or abs(hash(supplier_name))),
            "supplier_name": supplier_name,
            "company_name_en": raw.get("company_name_en", supplier_name),
            "company_name_cn": raw.get("company_name_cn", supplier_name),
            "location": raw.get("city") or raw.get("province") or raw.get("location", "China"),
            "city": raw.get("city", "China"),
            "industrial_cluster": raw.get("cluster", "N/A"),
            "business_scope": raw.get("business_scope") or raw.get("main_category") or raw.get("description", ""),
            "factory_area_sqm": raw.get("plant_area_sqm") or raw.get("factory_size", 0),
            "employees_count": raw.get("employee_count") or raw.get("staff_size", 0),
            "registered_capital_k_rmb": raw.get("registered_capital_rmb_k", 0),
            "years_in_business": raw.get("years_operating") or raw.get("shop_years", 0),
            "badges": raw.get("badges") or raw.get("tags") or [],
            "products_matched": [raw.get("title") or raw.get("product_name") or "1688 Listed Item"],
            "primary_product": raw.get("title") or "1688 Product",
            "price_range_rmb": str(raw.get("price") or raw.get("price_range") or "Inquire"),
            "moq": str(raw.get("moq") or raw.get("min_order_quantity") or "1"),
            "contact_info": raw.get("contact") or "1688 WangWang messaging system",
            "shop_url": raw.get("shop_url") or raw.get("company_url") or "",
            "item_url": raw.get("item_url") or raw.get("detail_url") or ""
        }


def get_adapter(app_cfg: Optional[AppConfig] = None) -> BaseProviderAdapter:
    """Factory helper to obtain the active provider adapter."""
    cfg = app_cfg or config
    if cfg.demo_mode or not cfg.provider_api_key:
        return DemoAdapter()
    
    if cfg.provider_name == "parsebot":
        return ParseBotAdapter(api_key=cfg.provider_api_key, base_url=cfg.provider_base_url)
    
    return DemoAdapter()
