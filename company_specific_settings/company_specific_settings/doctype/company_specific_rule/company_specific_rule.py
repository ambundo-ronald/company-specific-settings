import frappe
from frappe import _
from frappe.model.document import Document


class CompanySpecificRule(Document):
    def validate(self):
        self._validate_unique_rule()
        self._validate_document_type()
        self._validate_print_format()
        self._validate_fields()

    def on_update(self):
        changed = False
        for row in self.fields:
            if frappe.db.get_value("Custom Field", row.custom_field, "reqd"):
                frappe.db.set_value("Custom Field", row.custom_field, "reqd", 0, update_modified=False)
                changed = True
        if changed:
            frappe.clear_cache(doctype=self.document_type)

    def _validate_unique_rule(self):
        duplicate = frappe.db.exists(
            self.doctype,
            {
                "company": self.company,
                "document_type": self.document_type,
                "name": ["!=", self.name or ""],
            },
        )
        if duplicate:
            frappe.throw(
                _("A Company Specific Rule already exists for Company {0} and DocType {1}.").format(
                    frappe.bold(self.company), frappe.bold(self.document_type)
                )
            )

    def _validate_document_type(self):
        meta = frappe.get_meta(self.document_type)
        if not meta.has_field("company"):
            frappe.throw(
                _("DocType {0} has no Company field, so a company-specific rule cannot be resolved.").format(
                    frappe.bold(self.document_type)
                )
            )

    def _validate_print_format(self):
        if not self.print_format:
            return
        print_doctype = frappe.db.get_value("Print Format", self.print_format, "doc_type")
        if print_doctype != self.document_type:
            frappe.throw(
                _("Print Format {0} belongs to {1}, not {2}.").format(
                    frappe.bold(self.print_format),
                    frappe.bold(print_doctype),
                    frappe.bold(self.document_type),
                )
            )

    def _validate_fields(self):
        seen = set()
        for row in self.fields:
            if row.custom_field in seen:
                frappe.throw(_("Custom Field {0} is listed more than once.").format(frappe.bold(row.custom_field)))
            seen.add(row.custom_field)

            field_doctype = frappe.db.get_value("Custom Field", row.custom_field, "dt")
            if field_doctype != self.document_type:
                frappe.throw(
                    _("Custom Field {0} belongs to {1}, not {2}.").format(
                        frappe.bold(row.custom_field),
                        frappe.bold(field_doctype),
                        frappe.bold(self.document_type),
                    )
                )

