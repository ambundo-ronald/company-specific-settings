frappe.ui.form.on("Company Specific Rule", {
	setup(frm) {
		frm.set_query("document_type", () => ({
			filters: { istable: 0 },
		}));
		frm.set_query("print_format", () => ({
			filters: { doc_type: frm.doc.document_type || "" },
		}));
		frm.set_query("letter_head", () => ({
			filters: { disabled: 0 },
		}));
		frm.set_query("custom_field", "fields", () => ({
			filters: { dt: frm.doc.document_type || "" },
		}));
	},

	document_type(frm) {
		frm.set_value("print_format", null);
		frm.set_value("letter_head", null);
		frm.clear_table("fields");
		frm.refresh_field("fields");
	},
});

