# Copyright (c) 2024, Abdul Basit Ali and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document
from urllib.parse import urlencode, quote
from frappe.utils.weasyprint import download_pdf, get_html


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

    @frappe.whitelist()
    def download_sales_invoice_pdf(self):
        if len(self.sales_invoice_list) > 0:
             for invoice in self.sales_invoice_list:
                download_pdf("Sales Invoice", invoice.get("sales_invoice"), self.print_format, letterhead=None)

    