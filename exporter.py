"""
Exporting Module for 1688 Sourcing Tool.
Generates styled Excel (.xlsx) workbooks and UTF-8-BOM encoded CSV files.
"""

import io
import csv
from typing import Dict, Any
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

class SourcingDataExporter:

    @staticmethod
    def _apply_excel_styling(ws, header_fill_color="1E3A8A"):
        header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color=header_fill_color, end_color=header_fill_color, fill_type="solid")
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
        data_font = Font(name="Segoe UI", size=10)
        data_align_left = Alignment(horizontal="left", vertical="center")
        data_align_center = Alignment(horizontal="center", vertical="center")
        
        thin_border = Border(
            left=Side(style="thin", color="E5E7EB"),
            right=Side(style="thin", color="E5E7EB"),
            top=Side(style="thin", color="E5E7EB"),
            bottom=Side(style="thin", color="E5E7EB")
        )

        ws.row_dimensions.height = 28
        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=1, column=col_idx)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_align
            cell.border = thin_border

        for row_idx in range(2, ws.max_row + 1):
            ws.row_dimensions[row_idx].height = 22
            for col_idx in range(1, ws.max_column + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                cell.font = data_font
                cell.border = thin_border
                val_str = str(cell.value or "")
                if "%" in val_str or val_str.isdigit() or val_str in ("Factory", "Trading Company", "Uncertain"):
                    cell.alignment = data_align_center
                else:
                    cell.alignment = data_align_left

        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val = str(cell.value or "")
                display_len = min(len(val), 50)
                if display_len > max_len:
                    max_len = display_len
            ws.column_dimensions[col_letter].width = max(max_len + 5, 14)

    @classmethod
    def export_single_to_excel(cls, search_data: Dict[str, Any]) -> io.BytesIO:
        wb = Workbook()
        ws = wb.active
        ws.title = "1688 Single Product Sourcing"

        headers = [
            "Supplier Name", "Classification", "Confidence", "Score", "Location",
            "Primary Matched Product", "Price Range (RMB)", "MOQ", "Plant Area (m²)",
            "Employees", "Years Operating", "Badges / Certifications", "Key Heuristic Signals",
            "Contact Info", "1688 Shop Link"
        ]
        ws.append(headers)

        for item in search_data.get("results", []):
            badges_str = ", ".join(item.get("badges", [])) if isinstance(item.get("badges"), list) else str(item.get("badges") or "")
            signals_str = " | ".join(item.get("signals", []))
            ws.append([
                item.get("supplier_name", ""),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                item.get("score", 0),
                item.get("location", ""),
                item.get("primary_product", ""),
                item.get("price_range_rmb", ""),
                item.get("moq", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                badges_str,
                signals_str,
                item.get("contact_info", ""),
                item.get("shop_url", "")
            ])

        cls._apply_excel_styling(ws, header_fill_color="1E3A8A")
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @classmethod
    def export_single_to_csv(cls, search_data: Dict[str, Any]) -> io.BytesIO:
        output = io.BytesIO()
        output.write(b'\xef\xbb\xbf')
        text_stream = io.StringIO()
        writer = csv.writer(text_stream, quoting=csv.QUOTE_MINIMAL)

        headers = [
            "Supplier Name", "Classification", "Confidence", "Score", "Location",
            "Primary Matched Product", "Price Range (RMB)", "MOQ", "Plant Area (sqm)",
            "Employees", "Years Operating", "Badges", "Signals", "Contact Info", "1688 Shop Link"
        ]
        writer.writerow(headers)

        for item in search_data.get("results", []):
            badges_str = ", ".join(item.get("badges", [])) if isinstance(item.get("badges"), list) else str(item.get("badges") or "")
            signals_str = " | ".join(item.get("signals", []))
            writer.writerow([
                item.get("supplier_name", ""),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                item.get("score", 0),
                item.get("location", ""),
                item.get("primary_product", ""),
                item.get("price_range_rmb", ""),
                item.get("moq", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                badges_str,
                signals_str,
                item.get("contact_info", ""),
                item.get("shop_url", "")
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
            "Supplier Name", "Products Covered", "Total Requested", "Coverage %",
            "Composite Score", "Classification", "Confidence", "Covered Products List",
            "Missing Products List", "Location", "Plant Area (m²)", "Employees",
            "Years in Business", "Contact Info", "1688 Shop Link"
        ]
        ws.append(headers)

        for item in multi_data.get("results", []):
            covered_str = ", ".join(item.get("covered_products_list", []))
            missing_str = ", ".join(item.get("missing_products_list", []))
            ws.append([
                item.get("supplier_name", ""),
                item.get("products_covered_count", 0),
                total_req,
                item.get("coverage_percent_str", ""),
                item.get("score", 0),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                covered_str,
                missing_str,
                item.get("location", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                item.get("contact_info", ""),
                item.get("shop_url", "")
            ])

        cls._apply_excel_styling(ws, header_fill_color="047857")
        output = io.BytesIO()
        wb.save(output)
        output.seek(0)
        return output

    @classmethod
    def export_multi_to_csv(cls, multi_data: Dict[str, Any]) -> io.BytesIO:
        output = io.BytesIO()
        output.write(b'\xef\xbb\xbf')
        text_stream = io.StringIO()
        writer = csv.writer(text_stream, quoting=csv.QUOTE_MINIMAL)

        total_req = multi_data.get("total_queries", 0)
        headers = [
            "Supplier Name", "Products Covered", "Total Requested", "Coverage %",
            "Composite Score", "Classification", "Confidence", "Covered Products List",
            "Missing Products List", "Location", "Plant Area (sqm)", "Employees",
            "Years in Business", "Contact Info", "1688 Shop Link"
        ]
        writer.writerow(headers)

        for item in multi_data.get("results", []):
            covered_str = ", ".join(item.get("covered_products_list", []))
            missing_str = ", ".join(item.get("missing_products_list", []))
            writer.writerow([
                item.get("supplier_name", ""),
                item.get("products_covered_count", 0),
                total_req,
                item.get("coverage_percent_str", ""),
                item.get("score", 0),
                item.get("classification", ""),
                item.get("confidence_percent", ""),
                covered_str,
                missing_str,
                item.get("location", ""),
                item.get("factory_area_sqm", ""),
                item.get("employees_count", ""),
                item.get("years_in_business", ""),
                item.get("contact_info", ""),
                item.get("shop_url", "")
            ])

        output.write(text_stream.getvalue().encode("utf-8"))
        output.seek(0)
        return output