"""
Search Engine and Aggregation Module for 1688 Sourcing Tool.
Orchestrates single-product factory search and multi-product coverage aggregation.
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

    def search_single_product(self, product_query: str, factory_only: bool = False) -> Dict[str, Any]:
        query = (product_query or "").strip()
        active_adapter = self.adapter
        provider_info = active_adapter.get_provider_info()
        data_source = "demo" if provider_info.get("is_demo") else "live"

        if not query:
            return {
                "query": "",
                "total_count": 0,
                "factories_count": 0,
                "trading_count": 0,
                "data_source": data_source,
                "provider_info": provider_info,
                "results": []
            }

        raw_suppliers = active_adapter.search_single_product(query)
        processed_results = []
        factories_count = 0
        trading_count = 0

        for item in raw_suppliers:
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
                "shop_url": item.get("shop_url"),
                "item_url": item.get("item_url"),
                "_rank_score": rank_score
            }
            processed_results.append(record)

        processed_results.sort(key=lambda x: x["_rank_score"], reverse=True)
        for res in processed_results:
            res.pop("_rank_score", None)

        return {
            "query": query,
            "total_count": len(processed_results),
            "factories_count": factories_count,
            "trading_count": trading_count,
            "data_source": data_source,
            "provider_info": provider_info,
            "results": processed_results
        }

    def search_multi_products(self, product_lines: List[str]) -> Dict[str, Any]:
        cleaned_queries = [line.strip() for line in product_lines if line and line.strip()]
        unique_queries = []
        for q in cleaned_queries:
            if q not in unique_queries:
                unique_queries.append(q)

        active_adapter = self.adapter
        provider_info = active_adapter.get_provider_info()
        data_source = "demo" if provider_info.get("is_demo") else "live"

        total_queries_count = len(unique_queries)
        if total_queries_count == 0:
            return {
                "queries": [],
                "total_queries": 0,
                "total_suppliers_found": 0,
                "data_source": data_source,
                "provider_info": provider_info,
                "results": []
            }

        results_by_query = active_adapter.search_multi_products(unique_queries)
        supplier_map: Dict[str, Dict[str, Any]] = {}

        for query_item, suppliers_for_item in results_by_query.items():
            for sup in suppliers_for_item:
                sup_id = sup.get("supplier_id") or sup.get("supplier_name")
                
                if sup_id not in supplier_map:
                    classification = self.classifier.classify(sup)
                    supplier_map[sup_id] = {
                        "supplier_id": sup_id,
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
                        "shop_url": sup.get("shop_url"),
                        "covered_products": set(),
                        "sample_offers": []
                    }
                
                supplier_map[sup_id]["covered_products"].add(query_item)
                if sup.get("primary_product"):
                    supplier_map[sup_id]["sample_offers"].append({
                        "query": query_item,
                        "title": sup.get("primary_product"),
                        "price": sup.get("price_range_rmb"),
                        "item_url": sup.get("item_url")
                    })

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
                "sample_offers": data["sample_offers"][:4],
                "factory_area_sqm": data["factory_area_sqm"],
                "employees_count": data["employees_count"],
                "years_in_business": data["years_in_business"],
                "badges": data["badges"],
                "contact_info": data["contact_info"],
                "shop_url": data["shop_url"]
            })

        ranked_suppliers.sort(
            key=lambda x: (x["products_covered_count"], x["score"], x["confidence"]),
            reverse=True
        )

        return {
            "queries": unique_queries,
            "total_queries": total_queries_count,
            "total_suppliers_found": len(ranked_suppliers),
            "data_source": data_source,
            "provider_info": provider_info,
            "results": ranked_suppliers
        }