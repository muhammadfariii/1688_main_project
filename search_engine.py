"""
Search Engine and Aggregation Module for 1688 Sourcing Tool.
Orchestrates single-product factory search and multi-product coverage aggregation.
Includes supplier and factory deduplication logic to ensure distinct, non-redundant shortlists,
preserving accurate https 1688 product offer links and verified supplier contact channels.
"""

from typing import List, Dict, Any, Optional
from classifier import classifier, HeuristicSupplierClassifier
from adapters import BaseProviderAdapter, get_adapter

class SourcingSearchEngine:
    def __init__(self, adapter: Optional[BaseProviderAdapter] = None, classifier_instance: Optional[HeuristicSupplierClassifier] = None):
        self._explicit_adapter = adapter
        self.classifier = classifier_instance or classifier

    @property
    def adapter(self) -> BaseProviderAdapter:
        if self._explicit_adapter is not None:
            return self._explicit_adapter
        return get_adapter()

    @staticmethod
    def _normalize_key(item: Dict[str, Any]) -> str:
        sup_id = str(item.get("supplier_id") or "").strip().lower()
        shop_url = str(item.get("shop_url") or "").replace("http://", "").replace("https://", "").rstrip("/").strip().lower()
        name = str(item.get("supplier_name") or item.get("company_name_cn") or "").strip().lower()
        return sup_id or shop_url or name

    def search_single_product(self, product_query: str, factory_only: bool = False, pages: int = 1) -> Dict[str, Any]:
        """
        Executes single product search, deduplicates suppliers/factories, classifies each,
        and ranks by factory confidence.
        """
        query = (product_query or "").strip()
        active_adapter = self.adapter
        provider_info = active_adapter.get_provider_info()
        data_source = "demo" if provider_info.get("is_demo") else "live"

        num_pages = max(1, min(10, int(pages or 1)))
        if not query:
            return {
                "query": "",
                "pages_requested": num_pages,
                "total_count": 0,
                "factories_count": 0,
                "trading_count": 0,
                "data_source": data_source,
                "provider_info": provider_info,
                "results": []
            }

        raw_suppliers = active_adapter.search_single_product(query, page=num_pages, page_size=20 * num_pages)

        # 1. Deduplicate suppliers across raw results
        deduped_suppliers: Dict[str, Dict[str, Any]] = {}
        for item in raw_suppliers:
            sup_key = self._normalize_key(item)
            if not sup_key:
                continue

            if sup_key not in deduped_suppliers:
                deduped_suppliers[sup_key] = dict(item)
            else:
                existing = deduped_suppliers[sup_key]
                # Merge matched products
                existing_prods = list(existing.get("products_matched", []))
                for p in item.get("products_matched", []):
                    if p and p not in existing_prods:
                        existing_prods.append(p)
                existing["products_matched"] = existing_prods

                # Merge sample offers
                existing_offers = list(existing.get("sample_offers", []))
                existing_urls = {o.get("url") for o in existing_offers if o.get("url")}
                for off in item.get("sample_offers", []):
                    if off.get("url") and off.get("url") not in existing_urls:
                        existing_offers.append(off)
                        existing_urls.add(off.get("url"))
                existing["sample_offers"] = existing_offers

                # Merge badges
                existing_badges = list(existing.get("badges", []))
                for b in item.get("badges", []):
                    if b and b not in existing_badges:
                        existing_badges.append(b)
                existing["badges"] = existing_badges

                # Contact info & links
                if not existing.get("contact_phone") and item.get("contact_phone"):
                    existing["contact_phone"] = item.get("contact_phone")
                    existing["contact_info"] = item.get("contact_info")
                if not existing.get("contact_person") and item.get("contact_person"):
                    existing["contact_person"] = item.get("contact_person")
                if not existing.get("factory_address") and item.get("factory_address"):
                    existing["factory_address"] = item.get("factory_address")
                if not existing.get("contact_page_url") and item.get("contact_page_url"):
                    existing["contact_page_url"] = item.get("contact_page_url")
                if not existing.get("chat_url") and item.get("chat_url"):
                    existing["chat_url"] = item.get("chat_url")
                if not existing.get("item_url") and item.get("item_url"):
                    existing["item_url"] = item.get("item_url")
                if not existing.get("mobile_item_url") and item.get("mobile_item_url"):
                    existing["mobile_item_url"] = item.get("mobile_item_url")

                # Retain verified signals
                if item.get("is_super_factory"):
                    existing["is_super_factory"] = True
                if item.get("is_factory_inspected"):
                    existing["is_factory_inspected"] = True

        processed_results = []
        factories_count = 0
        trading_count = 0

        # 2. Classify and rank deduplicated suppliers
        for item in deduped_suppliers.values():
            classification = self.classifier.classify(item)
            if classification.type == "Factory":
                factories_count += 1
            elif classification.type == "Trading Company":
                trading_count += 1

            rank_score = classification.confidence
            if classification.type == "Factory":
                rank_score += 1000
            elif classification.type == "Trading Company":
                rank_score += 100

            if factory_only and classification.type != "Factory":
                continue

            record = {
                "supplier_id": item.get("supplier_id"),
                "supplier_name": item.get("supplier_name"),
                "company_name_en": item.get("company_name_en"),
                "company_name_cn": item.get("company_name_cn"),
                "location": item.get("location"),
                "city": item.get("city"),
                "industrial_cluster": item.get("industrial_cluster"),
                "classification": classification.type,
                "confidence": classification.confidence,
                "confidence_percent": classification.to_dict()["confidence_percent"],
                "score": classification.score,
                "signals": classification.signals,
                "business_scope": item.get("business_scope"),
                "factory_area_sqm": item.get("factory_area_sqm"),
                "employees_count": item.get("employees_count"),
                "registered_capital_k_rmb": item.get("registered_capital_k_rmb"),
                "years_in_business": item.get("years_in_business"),
                "badges": item.get("badges", []),
                "matched_products": item.get("products_matched", []),
                "primary_product": item.get("primary_product"),
                "price_range_rmb": item.get("price_range_rmb"),
                "moq": item.get("moq"),
                "contact_info": item.get("contact_info"),
                "contact_phone": item.get("contact_phone", ""),
                "contact_person": item.get("contact_person", ""),
                "factory_address": item.get("factory_address") or item.get("location", ""),
                "contact_page_url": item.get("contact_page_url", ""),
                "chat_url": item.get("chat_url", ""),
                "shop_url": item.get("shop_url", ""),
                "item_url": item.get("item_url", ""),
                "mobile_item_url": item.get("mobile_item_url", ""),
                "sample_offers": item.get("sample_offers", []),
                "_rank_score": rank_score
            }
            processed_results.append(record)

        processed_results.sort(key=lambda x: x["_rank_score"], reverse=True)
        for res in processed_results:
            res.pop("_rank_score", None)

        return {
            "query": query,
            "pages_requested": num_pages,
            "total_count": len(processed_results),
            "factories_count": factories_count,
            "trading_count": trading_count,
            "data_source": data_source,
            "provider_info": provider_info,
            "results": processed_results
        }

    def search_multi_products(self, product_lines: List[str], pages: int = 1) -> Dict[str, Any]:
        """
        Executes multi-product search, calculates supplier coverage across the full product list,
        and ranks deduplicated suppliers by product coverage and capability score.
        """
        cleaned_queries = [line.strip() for line in product_lines if line and line.strip()]
        unique_queries = []
        for q in cleaned_queries:
            if q not in unique_queries:
                unique_queries.append(q)

        active_adapter = self.adapter
        provider_info = active_adapter.get_provider_info()
        data_source = "demo" if provider_info.get("is_demo") else "live"

        num_pages = max(1, min(10, int(pages or 1)))
        total_queries_count = len(unique_queries)
        if total_queries_count == 0:
            return {
                "queries": [],
                "pages_requested": num_pages,
                "total_queries": 0,
                "total_suppliers_found": 0,
                "data_source": data_source,
                "provider_info": provider_info,
                "results": []
            }

        results_by_query = active_adapter.search_multi_products(unique_queries, pages=num_pages)

        supplier_map: Dict[str, Dict[str, Any]] = {}

        for query_item, suppliers_for_item in results_by_query.items():
            for sup in suppliers_for_item:
                sup_id = self._normalize_key(sup)
                if not sup_id:
                    continue

                if sup_id not in supplier_map:
                    classification = self.classifier.classify(sup)
                    supplier_map[sup_id] = {
                        "supplier_id": sup.get("supplier_id"),
                        "supplier_name": sup.get("supplier_name"),
                        "company_name_en": sup.get("company_name_en"),
                        "company_name_cn": sup.get("company_name_cn"),
                        "location": sup.get("location"),
                        "classification": classification.type,
                        "confidence": classification.confidence,
                        "confidence_percent": classification.to_dict()["confidence_percent"],
                        "signals": classification.signals,
                        "business_scope": sup.get("business_scope"),
                        "factory_area_sqm": sup.get("factory_area_sqm"),
                        "employees_count": sup.get("employees_count"),
                        "registered_capital_k_rmb": sup.get("registered_capital_k_rmb"),
                        "years_in_business": sup.get("years_in_business"),
                        "badges": sup.get("badges", []),
                        "contact_info": sup.get("contact_info"),
                        "contact_phone": sup.get("contact_phone", ""),
                        "contact_person": sup.get("contact_person", ""),
                        "factory_address": sup.get("factory_address") or sup.get("location", ""),
                        "contact_page_url": sup.get("contact_page_url", ""),
                        "chat_url": sup.get("chat_url", ""),
                        "shop_url": sup.get("shop_url", ""),
                        "item_url": sup.get("item_url", ""),
                        "mobile_item_url": sup.get("mobile_item_url", ""),
                        "covered_products": set(),
                        "sample_offers": []
                    }

                supplier_map[sup_id]["covered_products"].add(query_item)

                # Collect all unique sample offers for this query
                existing_urls = {o.get("url") for o in supplier_map[sup_id]["sample_offers"] if o.get("url")}
                offers_to_add = sup.get("sample_offers", [])
                if not offers_to_add and sup.get("primary_product"):
                    offers_to_add = [{
                        "title": sup.get("primary_product"),
                        "price": sup.get("price_range_rmb"),
                        "url": sup.get("item_url"),
                        "mobile_url": sup.get("mobile_item_url")
                    }]

                for off in offers_to_add:
                    off_url = off.get("url") or off.get("item_url")
                    if off_url and off_url not in existing_urls:
                        supplier_map[sup_id]["sample_offers"].append({
                            "query": query_item,
                            "title": off.get("title") or sup.get("primary_product"),
                            "price": off.get("price") or sup.get("price_range_rmb"),
                            "url": off_url,
                            "mobile_url": off.get("mobile_url") or ""
                        })
                        existing_urls.add(off_url)

        # Calculate coverage metrics and composite scores
        ranked_suppliers = []
        for sup_id, data in supplier_map.items():
            covered_list = sorted(list(data["covered_products"]))
            covered_count = len(covered_list)
            coverage_pct = round((covered_count / total_queries_count) * 100, 1)

            type_bonus = 30 if data["classification"] == "Factory" else (15 if data["classification"] == "Uncertain" else 10)
            composite_score = round((coverage_pct * 0.70) + type_bonus)

            ranked_suppliers.append({
                "supplier_id": data["supplier_id"],
                "supplier_name": data["supplier_name"],
                "company_name_en": data["company_name_en"],
                "company_name_cn": data["company_name_cn"],
                "location": data["location"],
                "products_covered_count": covered_count,
                "coverage_percent": coverage_pct,
                "coverage_percent_str": f"{round(coverage_pct)}%",
                "score": composite_score,
                "classification": data["classification"],
                "confidence": data["confidence"],
                "confidence_percent": data["confidence_percent"],
                "covered_products_list": covered_list,
                "missing_products_list": [q for q in unique_queries if q not in covered_list],
                "sample_offers": data["sample_offers"],
                "factory_area_sqm": data["factory_area_sqm"],
                "employees_count": data["employees_count"],
                "years_in_business": data["years_in_business"],
                "badges": data["badges"],
                "contact_info": data["contact_info"],
                "contact_phone": data.get("contact_phone", ""),
                "contact_person": data.get("contact_person", ""),
                "factory_address": data.get("factory_address", ""),
                "contact_page_url": data.get("contact_page_url", ""),
                "chat_url": data.get("chat_url", ""),
                "shop_url": data["shop_url"],
                "item_url": data.get("item_url", ""),
                "mobile_item_url": data.get("mobile_item_url", "")
            })

        ranked_suppliers.sort(
            key=lambda x: (x["products_covered_count"], x["score"], x["confidence"]),
            reverse=True
        )

        return {
            "queries": unique_queries,
            "pages_requested": num_pages,
            "total_queries": total_queries_count,
            "total_suppliers_found": len(ranked_suppliers),
            "data_source": data_source,
            "provider_info": provider_info,
            "results": ranked_suppliers
        }
