(() => {
	const METHOD = "company_specific_settings.company_specific_settings.api";
	const originals = new Map();

	function remember_originals(frm) {
		if (!originals.has(frm.doctype)) {
			originals.set(frm.doctype, {
				default_print_format: frm.meta.default_print_format || null,
				fields: {},
			});
		}
		return originals.get(frm.doctype);
	}

	function restore_field(frm, fieldname, original) {
		if (!frm.fields_dict[fieldname]) return;
		frm.set_df_property(fieldname, "hidden", original.hidden || 0);
		frm.set_df_property(fieldname, "reqd", original.reqd || 0);
	}

	async function apply_company_settings(frm) {
		if (!frm || !frm.fields_dict.company) return;

		const state = remember_originals(frm);
		const requested_company = frm.doc.company || null;
		const request_id = (frm.__company_settings_request_id || 0) + 1;
		frm.__company_settings_request_id = request_id;
		const response = await frappe.call({
			method: `${METHOD}.get_configuration`,
			args: { doctype: frm.doctype, company: requested_company },
		});
		if (
			request_id !== frm.__company_settings_request_id ||
			requested_company !== (frm.doc.company || null)
		) return;
		const config = response.message || {};

		for (const fieldname of config.scoped_fields || []) {
			const df = frm.fields_dict[fieldname]?.df;
			if (!df) continue;
			if (!state.fields[fieldname]) {
				state.fields[fieldname] = { hidden: df.hidden || 0, reqd: df.reqd || 0 };
			}
			frm.set_df_property(fieldname, "hidden", 1);
			frm.set_df_property(fieldname, "reqd", 0);
		}

		for (const field of config.active_fields || []) {
			const original = state.fields[field.fieldname] || { hidden: 0, reqd: 0 };
			restore_field(frm, field.fieldname, original);
			frm.set_df_property(field.fieldname, "hidden", 0);
			frm.set_df_property(field.fieldname, "reqd", field.mandatory ? 1 : 0);
		}

		frm.meta.default_print_format = config.print_format || state.default_print_format;
	}

	function register_doctype(doctype) {
		frappe.ui.form.on(doctype, {
			refresh(frm) {
				apply_company_settings(frm);
			},
			company(frm) {
				apply_company_settings(frm);
			},
		});
	}

	frappe.after_ajax(() => {
		frappe.call({
			method: `${METHOD}.get_scoped_doctypes`,
			callback: (response) => {
				const doctypes = response.message || [];
				doctypes.forEach(register_doctype);
				if (window.cur_frm && doctypes.includes(cur_frm.doctype)) {
					apply_company_settings(cur_frm);
				}
			},
		});
	});
})();
