"""
Automated Test Suite for 1688 Sourcing Tool.
Verifies classifier, adapters, search engine, exporter, and FastAPI endpoints.
"""

import io
import unittest
from fastapi.testclient import TestClient
from openpyxl import load_workbook

from config import config, AppConfig
from classifier import classifier, HeuristicSupplierClassifier
from adapters import DemoAdapter, ParseBotAdapter, get_adapter
from search_engine import SourcingSearchEngine
from exporter import SourcingDataExporter
from app import app


class TestConfig(unittest.TestCase):
    def test_default_config(self):
        status = config.get_public_status()
        self.assertTrue(status["demo_mode"])
        self.assertIn("Demo Mode", status["status_label"])
        self.assertFalse(status["has_api_key"])


class TestClassifier(unittest.TestCase):
    def setUp(self):
        self.clf = HeuristicSupplierClassifier()

    def test_factory_classification(self):
        factory_supplier = {
            "supplier_name": "Yongkang Hengtai Hardware & Stainless Steel Manufacturing Co., Ltd. (永康恒泰五金制造有限公司)",
            "business_scope": "Production, custom processing, and R&D for stainless steel vacuum bottles.",
            "badges": ["超级工厂 (Super Factory)", "ISO9001"],
            "factory_area_sqm": 15000,
            "employees_count": 180,
            "registered_capital_k_rmb": 10000,
            "years_in_business": 10
        }
        res = self.clf.classify(factory_supplier)
        self.assertEqual(res.type, "Factory")
        self.assertGreaterEqual(res.confidence, 80.0)
        self.assertTrue(res.is_factory)
        self.assertGreater(len(res.signals), 2)

    def test_trading_company_classification(self):
        trading_supplier = {
            "supplier_name": "Yiwu Haorun International Trading Firm (义乌市浩润商贸商行)",
            "business_scope": "Wholesale distribution and e-commerce retail of general goods.",
            "badges": [],
            "factory_area_sqm": 80,
            "employees_count": 3,
            "registered_capital_k_rmb": 100,
            "years_in_business": 2
        }
        res = self.clf.classify(trading_supplier)
        self.assertEqual(res.type, "Trading Company")
        self.assertGreaterEqual(res.confidence, 70.0)
        self.assertFalse(res.is_factory)


class TestSearchEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SourcingSearchEngine()

    def test_single_product_search(self):
        res = self.engine.search_single_product("Stainless Steel Water Bottle")
        self.assertEqual(res["query"], "Stainless Steel Water Bottle")
        self.assertGreater(res["total_count"], 0)
        self.assertGreaterEqual(res["factories_count"], 1)
        
        # Verify first result is ranked factory
        first_item = res["results"][0]
        self.assertEqual(first_item["classification"], "Factory")
        self.assertIn("confidence_percent", first_item)
        self.assertIn("shop_url", first_item)

    def test_single_product_factory_only_filter(self):
        res_all = self.engine.search_single_product("Stainless Steel Water Bottle", factory_only=False)
        res_factory_only = self.engine.search_single_product("Stainless Steel Water Bottle", factory_only=True)
        self.assertEqual(res_factory_only["total_count"], res_all["factories_count"])
        for item in res_factory_only["results"]:
            self.assertEqual(item["classification"], "Factory")

    def test_multi_product_coverage_search(self):
        queries = [
            "Stainless steel water bottle",
            "Silicone kitchen spatula",
            "Borosilicate glass storage jar",
            "Ceramic coffee mug",
            "Bamboo cutting board"
        ]
        res = self.engine.search_multi_products(queries)
        self.assertEqual(res["total_queries"], 5)
        self.assertGreater(res["total_suppliers_found"], 0)
        
        # Check sorting order: top suppliers should have high product coverage count
        top_supplier = res["results"][0]
        self.assertGreaterEqual(top_supplier["products_covered_count"], 1)
        self.assertIn("coverage_percent", top_supplier)
        self.assertIn("score", top_supplier)
        self.assertIn("covered_products_list", top_supplier)


class TestExporter(unittest.TestCase):
    def setUp(self):
        self.engine = SourcingSearchEngine()

    def test_single_excel_export(self):
        data = self.engine.search_single_product("Glass Jar")
        excel_io = SourcingDataExporter.export_single_to_excel(data)
        excel_io.seek(0)
        wb = load_workbook(excel_io)
        ws = wb.active
        self.assertEqual(ws.cell(row=1, column=1).value, "Supplier Name")
        self.assertGreater(ws.max_row, 1)

    def test_single_csv_export(self):
        data = self.engine.search_single_product("Glass Jar")
        csv_io = SourcingDataExporter.export_single_to_csv(data)
        content = csv_io.getvalue()
        self.assertTrue(content.startswith(b'\xef\xbb\xbf'))  # UTF-8 BOM
        self.assertIn("Supplier Name", content.decode("utf-8-sig"))

    def test_multi_excel_export(self):
        data = self.engine.search_multi_products(["Bottle", "Mug", "Plate"])
        excel_io = SourcingDataExporter.export_multi_to_excel(data)
        excel_io.seek(0)
        wb = load_workbook(excel_io)
        ws = wb.active
        self.assertEqual(ws.cell(row=1, column=1).value, "Supplier Name")
        self.assertEqual(ws.cell(row=1, column=2).value, "Products Covered")
        self.assertGreater(ws.max_row, 1)

    def test_multi_csv_export(self):
        data = self.engine.search_multi_products(["Bottle", "Mug", "Plate"])
        csv_io = SourcingDataExporter.export_multi_to_csv(data)
        content = csv_io.getvalue()
        self.assertTrue(content.startswith(b'\xef\xbb\xbf'))
        self.assertIn("Products Covered", content.decode("utf-8-sig"))


class TestFastAPIEndpoints(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_get_index(self):
        resp = self.client.post("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("1688 Sourcing Tool", resp.text)

    def test_get_status(self):
        resp = self.client.post("/api/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["demo_mode"])

    def test_single_search_api(self):
        resp = self.client.post("/api/search/single", json={"product": "Ceramic Mug", "factory_only": False})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["query"], "Ceramic Mug")
        self.assertGreater(data["total_count"], 0)

    def test_multi_search_api(self):
        resp = self.client.post("/api/search/multi", json={"products": ["Pen", "Notebook", "Eraser"]})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["total_queries"], 3)
        self.assertGreater(data["total_suppliers_found"], 0)

    def test_export_single_excel_api(self):
        search_resp = self.client.post("/api/search/single", json={"product": "Tea Kettle"})
        data = search_resp.json()
        export_resp = self.client.post("/api/export/single/excel", json=data)
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn("application/vnd.openxmlformats", export_resp.headers["content-type"])
        self.assertGreater(len(export_resp.content), 1000)

    def test_export_multi_csv_api(self):
        search_resp = self.client.post("/api/search/multi", json={"products": ["A", "B"]})
        data = search_resp.json()
        export_resp = self.client.post("/api/export/multi/csv", json=data)
        self.assertEqual(export_resp.status_code, 200)
        self.assertIn("text/csv", export_resp.headers["content-type"])
        self.assertGreater(len(export_resp.content), 200)


if __name__ == "__main__":
    unittest.main()
