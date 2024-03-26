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
			frappe.throw("Cant Submit Document without Sales Invoice Detail")


	def set_is_commercial_invoice(self):
		if self.sales_invoice_number:
			for sales_invoice in self.sales_invoice_number:
				frappe.db.set_value("Sales Invoice", sales_invoice.get("sales_invoice"), "custom_is_commercial_invoice", 1)
				frappe.db.commit()
			# frappe.msgprint("The Following invoices are marked as Commercial Invoice {0}".format(self.sales_invoice_number))



	def get_items(self):
		self.get_sales_invoice_items()

	@frappe.whitelist()
	def get_sales_invoice_items(self):
		if self.sales_invoice_number:
			from frappe.utils import money_in_words, flt  # flt for floating point arithmetic
			total_amount = 0.0
			total_taxes_charges = 0.0
			item_aggregate = {}  # Dictionary to store item aggregates

			for sales_invoice in self.sales_invoice_number:
				sales_invoice_items = frappe.db.get_all(
					"Sales Invoice Item", 
					filters={'parent': sales_invoice.get("sales_invoice"), 'parenttype': 'Sales Invoice'}, 
					fields=["item_code", "item_name", "qty", "rate", "amount"]
				)
				taxes_and_charges = frappe.db.get_value("Sales Invoice", sales_invoice.get("sales_invoice"), "total_taxes_and_charges")
				for i in sales_invoice_items:
					# Check if item already added
					if i.get("item_code") in item_aggregate:
						item_aggregate[i.get("item_code")]["qty"] += i.get("qty")
						item_aggregate[i.get("item_code")]["amount"] += i.get("amount")
					else:
						item_aggregate[i.get("item_code")] = {
							"item_name": i.get("item_name"),
							"rate": i.get("rate"),  # Consider how to handle varying rates for the same item
							"qty": i.get("qty"),
							"amount": i.get("amount")
						}
					total_amount += i.get("amount")
				total_taxes_charges += taxes_and_charges if taxes_and_charges else 0

			# Append aggregated items
			for item_code, aggregated_data in item_aggregate.items():
				self.append("items", {
					"item": item_code,
					"item_name": aggregated_data["item_name"],  # If needed
					"rate": "${}".format(aggregated_data["rate"]),
					"qty": aggregated_data["qty"],
					"amount": "${}".format(aggregated_data["amount"])
				})

			self.total_vat_amount = "${}".format(total_taxes_charges)
			self.total_amount = "${}".format(total_amount)
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
