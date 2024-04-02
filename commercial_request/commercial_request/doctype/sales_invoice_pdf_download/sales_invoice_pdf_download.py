# Copyright (c) 2024, Abdul Basit Ali and contributors
# For license information, please see license.txt

import frappe
import requests
from frappe.model.document import Document
from urllib.parse import urlencode, quote

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
        self.download_pdf()

    def download_pdf(self):
        if len(self.sales_invoice_list) > 0:
            generated_secret = frappe.utils.password.get_decrypted_password("User", "Administrator", fieldname='api_secret')
            api_key = frappe.db.get_value("User", "Administrator", "api_key")
            header = {"Authorization": "token {}:{}".format(api_key, generated_secret)}
            for invoice in self.sales_invoice_list:  # Assuming `invoice` contains the invoice details
                name = invoice.get('sales_invoice')  # Adjust according to your data structure
                # base_url = "http://127.0.0.1:8000/api/method/frappe.utils.print_format.download_pdf"
                base_url = "https://pvhmiddleeast.codeplus.solutions/api/method/frappe.utils.print_format.download_pdf"
                params = {
                    'doctype': 'Sales Invoice',
                    'name': name,
                    'format': 'Tax Invoice 2',  # Adjusted to match your desired output
                    'no_letterhead': '1',  # '1' for no letterhead as per your desired URL
                    'letterhead': 'No Letterhead',
                    'settings': '{}',
                    '_lang': 'en'
                }

                # Use quote_via=quote to ensure spaces are encoded as %20
                url = f"{base_url}?{urlencode(params, quote_via=quote)}"

                res = requests.get(url, headers=header, verify=False)  # verify=False should be used with caution
                if res.status_code == 200:
                    pdf_filename = f"{name}.pdf"
                    with open(pdf_filename, 'wb') as f:
                        f.write(res.content)
                    frappe.msgprint(f"Downloaded '{pdf_filename}' successfully.")
                else:
                    frappe.msgprint("Failed to download PDF for '{}': Status code {}".format(name, res.status_code))
        else:
            frappe.msgprint("No sales invoices to download.")
