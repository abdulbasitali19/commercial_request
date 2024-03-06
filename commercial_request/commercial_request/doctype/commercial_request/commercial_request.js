// Copyright (c) 2024, abdul basit ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Commercial Request', {

	sales_invoice_number:function(frm){
		if(frm.doc.sales_invoice_number){
			frm.call({
				doc:frm.doc,
				method:"get_sales_invoice_items",
				freeze: true,
				callback: function(r) {

				}
			})
		}

	},

	setup:function(frm){
		frm.set_query("sales_invoice_number",function(doc){
			return{
				filters : {
					customer:doc.customer,
					custom_is_commercial_invoice: 0
				}
			}

		})

	}
});
