// Copyright (c) 2024, abdul basit ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice Pdf Download', {
	refresh: function(frm) {
	if(frm.doc.sales_invoice_list){
		frm.add_custom_button(__("Download Sales Invoice PDF"), function () {
			frm.call({
				doc: frm.doc,
				method: "download_sales_invoice_pdf",
				freeze: true,
				callback: function (r) {}
			})

		});
	}	
	}

});


