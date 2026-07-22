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

	function schedule_print_view_settings() {
		let attempts = 0;
		const apply_when_ready = async () => {
			const route = frappe.get_route();
			if (route[0] !== "print") return;

			const doctype = route[1];
			const docname = route.slice(2).join("/");
			const doc = frappe.get_doc(doctype, docname);
			const $selector = $(
				'.print-preview-sidebar [data-fieldname="print_format"] input, ' +
					'.print-preview-sidebar input[data-fieldname="print_format"]'
			).first();

			if (!doc || !$selector.length) {
				attempts += 1;
				if (attempts < 50) setTimeout(apply_when_ready, 100);
				return;
			}

			const response = await frappe.call({
				method: `${METHOD}.get_configuration`,
				args: { doctype, company: doc.company || null },
			});
			const print_format = response.message?.print_format;
			if (!print_format) {
				$selector.prop("disabled", false).removeAttr("title");
				return;
			}

			if ($selector.val() !== print_format) {
				$selector.val(print_format).trigger("change");
			}
			$selector
				.prop("disabled", true)
				.attr("title", __("Enforced by Company Specific Rule"));
		};

		apply_when_ready();
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

	frappe.router.on("change", schedule_print_view_settings);
	schedule_print_view_settings();
})();
