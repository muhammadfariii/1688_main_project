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
        pass

    @abc.abstractmethod
    def search_multi_products(self, queries: List[str]) -> Dict[str, List[Dict[str, Any]]]:
        pass

    @abc.abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        pass

    def test_connection(self) -> Dict[str, Any]:
        return {"success": True, "message": "Provider operational"}


class DemoAdapter(BaseProviderAdapter):
    """Demo/Mock adapter delivering rich, realistic 1688 supplier data."""

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
            "description": "Built-in realistic sample data generator for testing without API credentials."
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
            business_scope = f"Production, OEM/ODM custom fabrication, mould opening, and R&D for {query} and industrial supplies."
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
            business_scope = f"Wholesale distribution, e-commerce retail, drop-shipping, and multi-category trading of {query}."
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
                
                if prob <= profile["coverage_tier"] or (v_idx < 2 and q_idx < 4):
                    results_for_item.append(self._build_supplier_dict(profile, q, seed_offset=q_idx))
            
            results_by_query[q] = results_for_item

        return results_by_query


class ParseBotAdapter(BaseProviderAdapter):
    """
    Live 1688 data provider adapter (e.g. ParseBot / Parse.bot scraper API service).
    Connects to external REST API / Scraper endpoint using server-side API keys.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key if api_key is not None else config.provider_api_key
        self.base_url = (base_url if base_url is not None else config.provider_base_url) or "https://api.parse.bot"
        self.base_url = self.base_url.rstrip("/")
        self.provider_name = "parsebot"
        self.timeout = 20

    def get_provider_info(self) -> Dict[str, Any]:
        has_key = bool(self.api_key.strip())
        return {
            "name": "ParseBot 1688 Live API",
            "is_demo": False,
            "connected": has_key,
            "base_url": self.base_url,
            "description": f"Connects to ParseBot 1688 scraper API ({self.base_url}) for real-time product queries."
        }

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "1688-Sourcing-Tool/2.1"
        }
        if self.api_key:
            headers["X-API-Key"] = self.api_key
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _get_endpoint(self) -> str:
        """Resolves target API endpoint URL based on base_url structure."""
        url = self.base_url.rstrip("/")
        return f"{url}/search_by_keyword"

    def test_connection(self) -> Dict[str, Any]:
        """Performs a test call or ping against the configured 1688 API provider."""
        if not self.api_key or not self.api_key.strip():
            return {
                "success": False,
                "is_demo": False,
                "error": "API Key is missing. Please configure PROVIDER_API_KEY in environment or config.local.json."
            }
        
        endpoint = self._get_endpoint()
        payload = {"keywords": "test", "page": 1, "pageSize": 1}
        try:
            resp = requests.get(endpoint, params=payload, headers=self._get_headers(), timeout=10)
            if resp.status_code == 200:
                return {
                    "success": True,
                    "is_demo": False,
                    "status_code": resp.status_code,
                    "message": f"Successfully connected to 1688 API endpoint at {endpoint}"
                }
            elif resp.status_code in (401, 403):
                return {
                    "success": False,
                    "is_demo": False,
                    "status_code": resp.status_code,
                    "error": f"Authentication failed ({resp.status_code}). Please verify your PROVIDER_API_KEY."
                }
            else:
                return {
                    "success": False,
                    "is_demo": False,
                    "status_code": resp.status_code,
                    "error": f"Provider returned HTTP {resp.status_code}: {resp.text[:250]}"
                }
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "is_demo": False,
                "error": f"Could not connect to live API endpoint ({endpoint}): {str(e)}."
            }

    def _extract_items_from_response(self, data: Any) -> List[Dict[str, Any]]:
        """Extracts item list from diverse 1688 / ParseBot API JSON schemas."""
        if isinstance(data, list):
            return data
        if not isinstance(data, dict):
            return []

        for key in ("items", "offers", "products", "results", "list", "suppliers", "data", "records", "rows"):
            if key in data:
                val = data[key]
                if isinstance(val, list):
                    return val
                if isinstance(val, dict):
                    for subkey in ("items", "offers", "products", "results", "list", "suppliers", "data", "records", "rows"):
                        if subkey in val and isinstance(val[subkey], list):
                            return val[subkey]

        if "result" in data:
            r = data["result"]
            if isinstance(r, list):
                return r
            if isinstance(r, dict):
                for subkey in ("items", "offers", "products", "results", "list", "suppliers"):
                    if subkey in r and isinstance(r[subkey], list):
                        return r[subkey]

        if any(k in data for k in ("company_name", "companyName", "shop_name", "shopName", "title", "product_name", "subject")):
            return [data]

        return []

    def search_single_product(self, query: str, page: int = 1, page_size: int = 20) -> List[Dict[str, Any]]:
        """
        Executes live query against 1688 provider API.
        Maps returned vendor and product fields to standard internal schema.
        """
        if not self.api_key or not self.api_key.strip():
            raise ValueError("API Key is missing. Please configure PROVIDER_API_KEY or switch to Demo Mode.")

        endpoint = self._get_endpoint()
        payload = {
            "keywords": query,
            "page": page
        }

        try:
            resp = requests.get(endpoint, params=payload, headers=self._get_headers(), timeout=self.timeout)
            resp.raise_for_status()
            data = resp.json()
            items = self._extract_items_from_response(data)
            return [self._map_raw_item_to_standard(item) for item in items]
        except requests.exceptions.HTTPError as e:
            msg = f"1688 API HTTP Error ({resp.status_code}): {resp.text[:300]}"
            print(f"[ParseBotAdapter] {msg}")
            raise RuntimeError(msg)
        except requests.exceptions.RequestException as e:
            msg = f"Could not reach live API endpoint at '{endpoint}' ({str(e)}). If testing without live provider connection, switch to Demo Mode in the header settings."
            print(f"[ParseBotAdapter] {msg}")
            raise RuntimeError(msg)

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
        Handles diverse Chinese and English API response keys.
        """
        supplier_name = (
            raw.get("company_name") or
            raw.get("companyName") or
            raw.get("shop_name") or
            raw.get("shopName") or
            raw.get("seller_title") or
            raw.get("sellerTitle") or
            raw.get("seller_name") or
            raw.get("supplier_name") or
            raw.get("supplierName") or
            raw.get("vendor_name") or
            raw.get("company") or
            "1688 Verified Seller"
        )
        
        sup_id = str(
            raw.get("company_id") or
            raw.get("companyId") or
            raw.get("seller_id") or
            raw.get("sellerId") or
            raw.get("member_id") or
            raw.get("memberId") or
            raw.get("shop_id") or
            abs(hash(supplier_name))
        )
        
        title = (
            raw.get("title") or
            raw.get("subject") or
            raw.get("product_name") or
            raw.get("productTitle") or
            raw.get("name") or
            raw.get("offer_name") or
            "1688 Listed Item"
        )

        location = (
            raw.get("city") or
            raw.get("province") or
            raw.get("location") or
            raw.get("address") or
            raw.get("region") or
            "China"
        )

        shop_url = (
            raw.get("shop_url") or
            raw.get("shopUrl") or
            raw.get("company_url") or
            raw.get("companyUrl") or
            raw.get("store_url") or
            f"https://shop{sup_id}.1688.com"
        )

        item_url = (
            raw.get("item_url") or
            raw.get("itemUrl") or
            raw.get("detail_url") or
            raw.get("detailUrl") or
            raw.get("offer_url") or
            raw.get("offerUrl") or
            raw.get("url") or
            raw.get("link") or
            ""
        )

        price = str(raw.get("price") or raw.get("price_range") or raw.get("unitPrice") or raw.get("priceRange") or raw.get("offer_price") or "Inquire")
        moq = str(raw.get("moq") or raw.get("min_order_quantity") or raw.get("minOrderQuantity") or raw.get("quantityBegin") or raw.get("start_amount") or "1")

        badges = raw.get("badges") or raw.get("tags") or raw.get("certifications") or raw.get("services") or []
        if isinstance(badges, str):
            badges = [badges]

        return {
            "supplier_id": sup_id,
            "supplier_name": supplier_name,
            "company_name_en": raw.get("company_name_en", supplier_name),
            "company_name_cn": raw.get("company_name_cn", supplier_name),
            "location": location,
            "city": raw.get("city", location),
            "industrial_cluster": raw.get("cluster") or raw.get("industrial_cluster") or "N/A",
            "business_scope": raw.get("business_scope") or raw.get("main_category") or raw.get("businessScope") or raw.get("description") or "",
            "factory_area_sqm": raw.get("plant_area_sqm") or raw.get("plantArea") or raw.get("factory_size") or raw.get("area") or 0,
            "employees_count": raw.get("employee_count") or raw.get("employeeCount") or raw.get("staff_size") or raw.get("employees") or 0,
            "registered_capital_k_rmb": raw.get("registered_capital_rmb_k") or raw.get("registeredCapital") or raw.get("capital") or 0,
            "years_in_business": raw.get("years_operating") or raw.get("shop_years") or raw.get("yearsInBusiness") or raw.get("operating_years") or 0,
            "badges": badges,
            "products_matched": [title],
            "primary_product": title,
            "price_range_rmb": price,
            "moq": moq,
            "contact_info": raw.get("contact") or raw.get("contact_info") or "1688 AliWangWang Messaging System",
            "shop_url": shop_url,
            "item_url": item_url
        }


def get_adapter(app_cfg: Optional[AppConfig] = None) -> BaseProviderAdapter:
    """Factory helper to obtain the active provider adapter based on current configuration."""
    cfg = app_cfg or config
    if cfg.demo_mode or not cfg.provider_api_key.strip():
        return DemoAdapter()
    return ParseBotAdapter(api_key=cfg.provider_api_key, base_url=cfg.provider_base_url)