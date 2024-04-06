// Copyright (c) 2024, abdul basit ali and contributors
// For license information, please see license.txt

frappe.ui.form.on('Sales Invoice Pdf Download', {
	onload:function(frm){
		frm.doc.sales_invoice_list = []
	},

	refresh: function(frm) {
		var sales_invoice_list = frm.doc.sales_invoice_list.slice(); 
		if (sales_invoice_list.length >= 1) {
			frm.add_custom_button(__("Download Sales Invoice PDF"), function() {
				downloadInvoice(sales_invoice_list, function() {
					frm.set_value('sales_invoice_list', sales_invoice_list);
					frm.refresh_field('sales_invoice_list'); 
					frappe.msgprint(__("All selected sales invoices have been downloaded."));
				});
			});
		}
	
		function downloadInvoice(list, onComplete) {
			if (list.length === 0) {
				onComplete(); 
				return;
			}
	
			
			var currentInvoice = list.shift(); 
	
			var downloadUrl = frappe.urllib.get_full_url("/api/method/commercial_request.commercial_request.doctype.sales_invoice_pdf_download.sales_invoice_pdf_download.pdf_download_custom?" +
				new URLSearchParams({
					name: currentInvoice.sales_invoice,
					print_format: frm.doc.print_format || "Standard",
					language: frappe.boot.lang,
					letterhead: frm.doc.letter_head || "",
				}).toString()
			);
	
			
			var link = document.createElement('a');
			link.href = downloadUrl;
			link.download = currentInvoice.sales_invoice + '.pdf'; 
			document.body.appendChild(link); 
			link.click(); 
			document.body.removeChild(link);
	
			setTimeout(function() {
				downloadInvoice(list, onComplete); 
			}, 1000); 
		}
	},
	
	
	
	setup:function(frm){
		frm.set_query("print_format",function(){
			return {
				filters: {
					doc_type: "Sales Invoice",
					
				}
			}

		})

	}

});


