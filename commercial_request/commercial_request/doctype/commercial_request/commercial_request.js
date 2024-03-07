// Copyright (c) 2024, abdul basit ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Commercial Request', {
	fetch_item: function (frm) {
		if (frm.doc.sales_invoice_number) {
			frm.call({
				doc: frm.doc,
				method: "get_sales_invoice_items",
				freeze: true,
				callback: function (r) {}
			})

		}
		else {
			frappe.throw("Please Select Sales Invoice")
		}

	},


	setup: function (frm) {
		frm.set_query("sales_invoice_number", function (doc) {
			return {
				filters: {
					customer: doc.customer,
					custom_is_commercial_invoice: 0
				}
			}

		})

		frm.set_query("project", function (doc) {
			return {
				filters: {
					customer: doc.customer,
				}
			}

		})

	}
});
