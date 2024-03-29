# Copyright (c) 2024, abdul basit ali and contributors
# For license information, please see license.txt

import erpnext
import frappe
from frappe.model.document import Document

class CommercialRequest(Document):
    def validate(self):
        if self.sales_invoice_number:
            self.set_is_commercial_invoice()
        else:
            frappe.throw("Can't Submit Document without Sales Invoice Detail")

    def set_is_commercial_invoice(self):
        if self.sales_invoice_number:
            for sales_invoice in self.sales_invoice_number:
                frappe.db.set_value("Sales Invoice", sales_invoice.get("sales_invoice"), "custom_is_commercial_invoice", 1)
                frappe.db.commit()

    def get_items(self):
        self.get_sales_invoice_items()

    @frappe.whitelist()
    def get_sales_invoice_items(self):
        if self.sales_invoice_number:
            from frappe.utils import money_in_words, flt  # flt for floating point arithmetic
            total_amount = 0.0
            item_aggregate = {}  # Dictionary to store item aggregates
            tax_aggregate = {}

            for sales_invoice in self.sales_invoice_number:
                
                sales_invoice_items = frappe.db.get_all(
                    "Sales Invoice Item", 
                    filters={'parent': sales_invoice.get("sales_invoice"), 'parenttype': 'Sales Invoice'}, 
                    fields=["item_code", "item_name", "qty", "rate", "amount"]
                )
                taxes_and_charges = frappe.db.get_all(
                    "Sales Taxes and Charges",
                    filters={'parent': sales_invoice.get("sales_invoice"), 'parenttype': 'Sales Invoice'},
                    fields=["charge_type", "account_head", "rate", "tax_amount", "total"]
                )
                sales_invoice_data = frappe.db.get_value("Sales Invoice", sales_invoice.get("sales_invoice"), ["taxes_and_charges", "total","total_taxes_and_charges"],as_dict=1)
                tax_template = sales_invoice_data.taxes_and_charges
                total = sales_invoice_data.total
                total_taxes_and_charges = sales_invoice_data.total_taxes_and_charges
                
                if tax_template not in tax_aggregate:
                    tax_aggregate[tax_template] = {}
                    for d in taxes_and_charges:
                        # Initialize each account head within the tax template if it does not exist
                        account_head = d.get('account_head')
                        if account_head not in tax_aggregate[tax_template]:
                            tax_aggregate[tax_template][account_head] = {
                                "charge_type": d.get('charge_type'),
                                "account_head": d.get('account_head'),  # This becomes redundant but kept for consistency
                                "rate": d.get('rate'),
                                "tax_amount": d.get('tax_amount'),
                                "total": d.get('total'),
                            }
                        else:
                            # If the account head exists, only sum up the tax_amount
                            tax_aggregate[tax_template][account_head]["tax_amount"] += d.get("tax_amount")
                else:
                    for d in taxes_and_charges:
                        account_head = d.get('account_head')
                        # Check if the account head is already part of the tax template
                        if account_head in tax_aggregate[tax_template]:
                            # If so, just update the tax_amount
                            tax_aggregate[tax_template][account_head]["tax_amount"] += d.get("tax_amount")
                        else:
                            # If this is a new account head for the existing tax template, initialize it
                            tax_aggregate[tax_template][account_head] = {
                                "charge_type": d.get('charge_type'),
                                "account_head": d.get('account_head'),
                                "rate": d.get('rate'),
                                "tax_amount": d.get('tax_amount'),
                                "total": d.get('total'),
                            }

                for i in sales_invoice_items:
                    # Check if item already added
                    if i.get("item_code") in item_aggregate:
                        item_aggregate[i.get("item_code")]["qty"] += i.get("qty")
                        item_aggregate[i.get("item_code")]["amount"] += i.get("amount")
                        if sales_invoice.get("sales_invoice") in item_aggregate[i.get("item_code")]["sales_invoices"]:
                            item_aggregate[i.get("item_code")]["sales_invoices"][sales_invoice.get("sales_invoice")] += i.get("qty")
                        else:
                            item_aggregate[i.get("item_code")]["sales_invoices"][sales_invoice.get("sales_invoice")] = i.get("qty")
                    else:
                        item_aggregate[i.get("item_code")] = {
                            "item_name": i.get("item_name"),
                            "rate": i.get("rate"),
                            "qty": i.get("qty"),
                            "amount": i.get("amount"),
                            "count": i.get("amount"),
                            "sales_invoices": {
                                sales_invoice.get("sales_invoice"): i.get("qty")
                            }
                        }
                    # total_amount += i.get("amount")

            # Append aggregated items
            for item_code, aggregated_data in item_aggregate.items():
                sales_invoices_qty = ", ".join(
                    f"{invoice}: {qty}" 
                    for invoice, qty in aggregated_data["sales_invoices"].items()
                )
                self.append("items", {
                    "item": item_code,
                    "item_name": aggregated_data["item_name"],  # If needed
                    "rate": "${}".format(aggregated_data["rate"]),
                    "qty": aggregated_data["qty"],
                    "amount": "${}".format(aggregated_data["amount"]),
                    "sales_invoice": sales_invoices_qty
                })

            # Append aggregate Templates
            # Append aggregate Templates
            for tax_template, tax_charges in tax_aggregate.items():
                tax_template_description = f"{tax_template} (Count : {len(tax_aggregate)})"
                self.append("sales_tax_and_charges_commercial_request", {
                    "custom_tax_template": tax_template_description  # Tax template on the first row
                })
                for account_head, details in tax_charges.items():
                    if account_head != "tax_template":  # Skip the key used for tax template
                        self.append("sales_tax_and_charges_commercial_request", {
                            "charge_type": details["charge_type"],
                            "account_head": account_head,
                            "rate": details["rate"],
                            "tax_amount": details["tax_amount"],
                            "total": details["total"]
                        })
            # Add Total Amount to footer
            total_amount += total + total_taxes_and_charges
            self.total_amount = "${:.2f}".format(total_amount)
            self.amount_in_words = money_in_words(int(total_amount))  # Ensure this function exists or use an equivalent

        else:
            frappe.throw("Sales Invoice Not Found")
            self.items = []


def number_to_words(amount):
    """
    Convert a given numerical amount into words.

    Parameters:
        amount (float): The numerical amount to convert.

    Returns:
        str: The textual representation of the amount in words.
    """
    # Define word representations of numbers from 0 to 19
    units = ["", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
             "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
             "Seventeen", "Eighteen", "Nineteen"]

    # Define word representations of tens from 20 to 90
    tens = ["", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy", "Eighty", "Ninety"]

    # Define word representations of higher order units
    higher_units = ["", "Thousand", "Million", "Billion", "Trillion"]

    # Function to convert a number less than 1000 to words
    def convert_less_than_thousand(num):
        if num == 0:
            return "Zero"
        words = ""
        if num // 100 > 0:
            words += units[num // 100] + " Hundred "
        num %= 100
        if num >= 20:
            words += tens[num // 10] + " "
            num %= 10
        if num > 0:
            words += units[num] + " "
        return words

    # Convert the given amount into words
    if amount == 0:
        return "Zero Dollars"
    words = ""
    num_segments = []
    while amount > 0:
        num_segments.append(amount % 1000)
        amount //= 1000
    for i in range(len(num_segments)):
        segment = convert_less_than_thousand(num_segments[i])
        if segment != "":
            words = segment + higher_units[i] + " " + words
    return words.strip() + " Dollars"
