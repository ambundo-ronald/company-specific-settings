import frappe

from company_specific_settings.company_specific_settings.rules import (
    get_configuration as _get_configuration,
    rules_are_available,
)


@frappe.whitelist()
def get_configuration(doctype: str, company: str | None = None) -> dict:
    frappe.has_permission(doctype, "read", throw=True)
    return _get_configuration(doctype, company)


@frappe.whitelist()
def get_scoped_doctypes() -> list[str]:
    if not rules_are_available():
        return []
    doctypes = frappe.get_all(
        "Company Specific Rule", pluck="document_type", order_by="document_type asc"
    )
    # Include disabled rules too: their fields remain scoped (hidden everywhere)
    # instead of becoming global merely because a rule was temporarily disabled.
    return list(dict.fromkeys(doctypes))
