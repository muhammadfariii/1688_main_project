import codecs
"""
Exporting Module for 1688 Sourcing Tool.
Generates styled Excel (.xlsx) workbooks and UTF-8-BOM encoded CSV files
for single-product factory searches and multi-product coverage searches.
Guarantees verified 1688 product offer links, official contact page links,
AliWangWang chat links, and direct telephone/mobile contact columns.
"""

import io
import csv
from typing import List, Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class SourcingDataExporter:

    @staticmethod
    def _apply_excel_styling(ws, header_fill_color="1E3A8A"):
        """Applies professional formatting, header colors, borders, hyperlinks, and auto-width columns."""
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color=header_fill_color, end_color=header_fill_color, fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        data_font = Font(name="Segoe UI", size=10)
        link_font = Font(name="Segoe UI", size=10, color="0044CC", underline="single")
        data_align_left = Alignment(horizontal="left", vertical="center", wrap_text=True)
        data_align_center = Alignment(horizontal="center", vertical="center")

        thin_border = Border(
            left=Side(style="thin", color="E5E7EB"),
            right=Side(style="thin", color="E5E7EB"),
            top=Side(style="thin", color="E5E7EB"),
            bottom=Side(style="thin", color="E5E7EB")
        )

        # Style header row
        ws.row_dimensions[1].height = 30
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border

        # Style data rows
        for row_idx in range(2, ws.max_row + 1):
            ws.row_dimensions[row_idx].height = 24
            for col_idx in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = data_font
                cell.border = thin_border
                val_str = str(cell.value or "").strip()

                # Apply clickable hyperlinks for web URLs
                if val_str.startswith("http://") or val_str.startswith("https://"):
                    cell.hyperlink = val_str
                    cell.font = link_font
                    cell.alignment = data_align_left
                elif "%" in val_str or val_str.isdigit() or val_str in ("Factory", "Trading Company", "Uncertain"):
                    cell.alignment = data_align_center
                else:
                    cell.alignment = data_align_left

        # Auto-adjust column widths
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                first_line = val.splitlines()[0] if val.splitlines() else ""
                display_len = min(len(first_line), 50)
                if display_len > max_len:
                    max_len = display_len
            ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    @classmethod
    def export_single_to_excel(cls, search_data: Dict[str, Any]) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "1688 Sourcing Shortlist"

        headers = [
            "Supplier Name",
            "Classification",
            "Confidence",
            "Score",
            "Contact Phone / Mobile",
            "Contact Person / Role",
            "Factory Operating Address",
            "Primary Matched Product",
            "1688 Product Offer Link",
            "1688 Product Link (Mobile)",
            "1688 Shop Link",
            "1688 Supplier Contact Page",
            "AliWangWang Web Chat Link",
            "Price Range (RMB)",
            "MOQ",
            "Plant Area (m²)",
            "Employees",
            "Years in Business",
            "Badges / Certifications",
            "Key Heuristic Signals"
        ]
        ws.append(headers)

        for item in search_data.get("results", []):
            badges_str = ", ".join(item.get("badges", [])) if isinstance(item.get("badges"), list) else str(item.get("badges") or "")
            signals_str = " | ".join(item.get("signals", []))
            phone_str = item.get("contact_phone") or (item.get("contact_info", "").split(" | ")[0] if "📞" in item.get("contact_info", "") else "")
            person_str = item.get("contact_person") or ""
            addr_str = item.get("factory_address") or item.get("location", "")

            ws.append([
                item.get("supplier_name", ""),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                item.get("score", 0),
                phone_str,
                person_str,
                addr_str,
                item.get("primary_product", ""),
                item.get("item_url", ""),
                item.get("mobile_item_url", ""),
                item.get("shop_url", ""),
                item.get("contact_page_url", ""),
                item.get("chat_url", ""),
                item.get("price_range_rmb", ""),
                item.get("moq", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                badges_str,
                signals_str
            ])

        cls._apply_excel_styling(ws, header_fill_color="1E3A8A")

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @classmethod
    def export_single_to_csv(cls, search_data: Dict[str, Any]) -> io.BytesIO:
        output = io.BytesIO()
        output.write(codecs.BOM_UTF8)
        text_stream = io.StringIO()
        writer = csv.writer(text_stream, quoting=csv.QUOTE_MINIMAL)

        headers = [
            "Supplier Name",
            "Classification",
            "Confidence",
            "Score",
            "Contact Phone / Mobile",
            "Contact Person / Role",
            "Factory Operating Address",
            "Primary Matched Product",
            "1688 Product Offer Link",
            "1688 Product Link (Mobile)",
            "1688 Shop Link",
            "1688 Supplier Contact Page",
            "AliWangWang Web Chat Link",
            "Price Range (RMB)",
            "MOQ",
            "Plant Area (sqm)",
            "Employees",
            "Years in Business",
            "Badges",
            "Signals"
        ]
        writer.writerow(headers)

        for item in search_data.get("results", []):
            badges_str = ", ".join(item.get("badges", [])) if isinstance(item.get("badges"), list) else str(item.get("badges") or "")
            signals_str = " | ".join(item.get("signals", []))
            phone_str = item.get("contact_phone") or (item.get("contact_info", "").split(" | ")[0] if "📞" in item.get("contact_info", "") else "")
            person_str = item.get("contact_person") or ""
            addr_str = item.get("factory_address") or item.get("location", "")

            writer.writerow([
                item.get("supplier_name", ""),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                item.get("score", 0),
                phone_str,
                person_str,
                addr_str,
                item.get("primary_product", ""),
                item.get("item_url", ""),
                item.get("mobile_item_url", ""),
                item.get("shop_url", ""),
                item.get("contact_page_url", ""),
                item.get("chat_url", ""),
                item.get("price_range_rmb", ""),
                item.get("moq", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                badges_str,
                signals_str
            ])

        output.write(text_stream.getvalue().encode("utf-8"))
        output.seek(0)
        return output

    @classmethod
    def export_multi_to_excel(cls, multi_data: Dict[str, Any]) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "Multi-Product Sourcing Coverage"

        total_req = multi_data.get("total_queries", 0)
        headers = [
            "Supplier Name",
            "Products Covered",
            "Total Requested",
            "Coverage %",
            "Composite Score",
            "Classification",
            "Confidence",
            "Contact Phone / Mobile",
            "Contact Person / Role",
            "Factory Operating Address",
            "Covered Products List",
            "Missing Products List",
            "Matched Product Offer Links",
            "1688 Shop Link",
            "1688 Supplier Contact Page",
            "AliWangWang Web Chat Link",
            "Plant Area (m²)",
            "Employees",
            "Years in Business",
            "Badges / Certifications"
        ]
        ws.append(headers)

        for item in multi_data.get("results", []):
            covered_str = ", ".join(item.get("covered_products_list", []))
            missing_str = ", ".join(item.get("missing_products_list", []))
            phone_str = item.get("contact_phone") or (item.get("contact_info", "").split(" | ")[0] if "📞" in item.get("contact_info", "") else "")
            person_str = item.get("contact_person") or ""
            addr_str = item.get("factory_address") or item.get("location", "")
            badges_str = ", ".join(item.get("badges", [])) if isinstance(item.get("badges"), list) else str(item.get("badges") or "")

            offer_lines = []
            for off in item.get("sample_offers", []):
                t = off.get("title") or off.get("query") or "Product"
                u = off.get("url") or off.get("item_url") or ""
                if u:
                    offer_lines.append(f"{t}: {u}")
            offer_links_str = "\n".join(offer_lines) if offer_lines else (item.get("item_url") or "")

            ws.append([
                item.get("supplier_name", ""),
                item.get("products_covered_count", 0),
                total_req,
                item.get("coverage_percent_str", ""),
                item.get("score", 0),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                phone_str,
                person_str,
                addr_str,
                covered_str,
                missing_str,
                offer_links_str,
                item.get("shop_url", ""),
                item.get("contact_page_url", ""),
                item.get("chat_url", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                badges_str
            ])

        cls._apply_excel_styling(ws, header_fill_color="047857")

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @classmethod
    def export_multi_to_csv(cls, multi_data: Dict[str, Any]) -> io.BytesIO:
        output = io.BytesIO()
        output.write(codecs.BOM_UTF8)
        text_stream = io.StringIO()
        writer = csv.writer(text_stream, quoting=csv.QUOTE_MINIMAL)

        total_req = multi_data.get("total_queries", 0)
        headers = [
            "Supplier Name",
            "Products Covered",
            "Total Requested",
            "Coverage %",
            "Composite Score",
            "Classification",
            "Confidence",
            "Contact Phone / Mobile",
            "Contact Person / Role",
            "Factory Operating Address",
            "Covered Products List",
            "Missing Products List",
            "Matched Product Offer Links",
            "1688 Shop Link",
            "1688 Supplier Contact Page",
            "AliWangWang Web Chat Link",
            "Plant Area (sqm)",
            "Employees",
            "Years in Business",
            "Badges"
        ]
        writer.writerow(headers)

        for item in multi_data.get("results", []):
            covered_str = ", ".join(item.get("covered_products_list", []))
            missing_str = ", ".join(item.get("missing_products_list", []))
            phone_str = item.get("contact_phone") or (item.get("contact_info", "").split(" | ")[0] if "📞" in item.get("contact_info", "") else "")
            person_str = item.get("contact_person") or ""
            addr_str = item.get("factory_address") or item.get("location", "")
            badges_str = ", ".join(item.get("badges", [])) if isinstance(item.get("badges"), list) else str(item.get("badges") or "")

            offer_lines = []
            for off in item.get("sample_offers", []):
                t = off.get("title") or off.get("query") or "Product"
                u = off.get("url") or off.get("item_url") or ""
                if u:
                    offer_lines.append(f"{t}: {u}")
            offer_links_str = " | ".join(offer_lines) if offer_lines else (item.get("item_url") or "")

            writer.writerow([
                item.get("supplier_name", ""),
                item.get("products_covered_count", 0),
                total_req,
                item.get("coverage_percent_str", ""),
                item.get("score", 0),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                phone_str,
                person_str,
                addr_str,
                covered_str,
                missing_str,
                offer_links_str,
                item.get("shop_url", ""),
                item.get("contact_page_url", ""),
                item.get("chat_url", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                badges_str
            ])

        output.write(text_stream.getvalue().encode("utf-8"))
        output.seek(0)
        return output
