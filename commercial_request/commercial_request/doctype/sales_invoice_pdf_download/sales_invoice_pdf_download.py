# Copyright (c) 2024, Abdul Basit Ali and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document
from urllib.parse import urlencode, quote
# from frappe.utils.weasyprint import download_pdf, get_html
# from frappe.utils.pdf import get_pdf
from frappe.utils.print_format import download_pdf
from frappe.utils import get_url
from typing import Optional


class SalesInvoicePdfDownload(Document):
    def validate(self):
        self.sales_invoice_list = []
        self.populate_sales_invoice_table()

    def populate_sales_invoice_table(self):
        if self.from_date and self.to_date and self.customer:
            sales_invoice_list = frappe.db.sql("""
                SELECT
                    name
                FROM
                    `tabSales Invoice`
                WHERE
                    docstatus = 1 AND posting_date BETWEEN '{0}' AND '{1}' AND customer = '{2}'
                """.format(self.from_date, self.to_date, self.customer), as_dict=1)
            if sales_invoice_list:
                for sales_invoice in sales_invoice_list:
                    self.append("sales_invoice_list", {
                        "sales_invoice": sales_invoice.get("name")
                    })

    @frappe.whitelist(allow_guest = True)
    def download_sales_invoice_pdf(self):
        if len(self.sales_invoice_list) > 0:
             for invoice in self.sales_invoice_list:
                doc = frappe.get_doc("Sales Invoice", invoice.get("sales_invoice"))
                download_pdf("Sales Invoice", invoice.get("sales_invoice"), self.print_format, doc =doc,language=None,letterhead=None)




# @frappe.whitelist()
# def get_pdf(
# 	name: str,
# 	supplier: str,
# 	print_format: Optional[str] = None,
# 	language: Optional[str] = None,
# 	letterhead: Optional[str] = None,
# ):
# 	doc = frappe.get_doc("Request for Quotation", name)
# 	if supplier:
# 		doc.update_supplier_part_no(supplier)

# 	# permissions get checked in `download_pdf`
# 	download_pdf(
# 		doc.doctype,
# 		doc.name,
# 		print_format,
# 		doc=doc,
# 		language=language,
# 		letterhead=letterhead or None,
# 	)





#     @frappe.whitelist(allow_guest = True)		
#     def download_sales_invoice_pdf(self):
#         if len(self.sales_invoice_list) > 0:
#             for i in self.sales_invoice_list:
#                 download_pdf(i.get("sales_invoice"),self.print_format)


# def download_pdf(name,format):
#     # base_url = "https://pvhmiddleeast.codeplus.solutions/api/method/frappe.utils.print_format.download_pdf"
#     base_url = "http://mysite.localhost:8000/api/method/frappe.utils.print_format.download_pdf"
#     params = {
#         'doctype': 'Sales Invoice',
#         'name': name,  # Example name
#         'format': format,
#         'no_letterhead': '1',
#         'letterhead': 'No Letterhead',
#         'settings': '%',  # The settings parameter you provided, note that it's "%"
#         '_lang': 'en'
#     }
#     url = f"{base_url}?{urlencode(params)}"
#     generated_secret = frappe.utils.password.get_decrypted_password("User", "Administrator", fieldname='api_secret')
#     api_key = frappe.db.get_value("User", "Administrator", "api_key")
#     header = {"Authorization": "token {}:{}".format(api_key, generated_secret)}
#     # doc = get_pdf(url)
#     res = requests.get(url, headers=header,verify=False)
#     if res.status_code == 200:
#         frappe.msgprint(res)
#         with open('file.pdf', 'wb') as f:
#             f.write(res.content)
#         return f
#     else:
#         print("Failed to download PDF:", res.status_code)
#         return None