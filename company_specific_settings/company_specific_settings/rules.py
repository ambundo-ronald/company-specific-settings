from __future__ import annotations

from typing import Any

import frappe
from frappe import _

RULE_DOCTYPE = "Company Specific Rule"


def rules_are_available() -> bool:
    """Return False during installation/migration before the rule table exists."""
    return bool(
        frappe.db.table_exists(RULE_DOCTYPE)
        and frappe.db.table_exists("Company Specific Field")
    )


def get_company(doc: Any) -> str | None:
    company = doc.get("company") if hasattr(doc, "get") else None
    return company or None


def get_rule(doctype: str, company: str | None) -> dict | None:
    if not company or not rules_are_available():
        return None

    name = frappe.db.get_value(
        RULE_DOCTYPE,
        {"document_type": doctype, "company": company, "enabled": 1},
        "name",
    )
    if not name:
        return None

    rule = frappe.get_doc(RULE_DOCTYPE, name)
    return {
        "name": rule.name,
        "print_format": rule.print_format,
        "fields": [
            {
                "custom_field": row.custom_field,
                "fieldname": custom_fieldname(row.custom_field),
                "mandatory": bool(row.mandatory),
            }
            for row in rule.fields
        ],
    }


def custom_fieldname(custom_field: str) -> str:
    return frappe.get_cached_value("Custom Field", custom_field, "fieldname") or ""


def get_configuration(doctype: str, company: str | None = None) -> dict:
    """Return applicable values and every field scoped on this DocType."""
    if not rules_are_available():
        return {"print_format": None, "active_fields": [], "scoped_fields": []}

    all_parents = frappe.get_all(
        RULE_DOCTYPE,
        filters={"document_type": doctype},
        fields=["name", "company", "print_format", "enabled"],
    )
    if not all_parents:
        return {"print_format": None, "active_fields": [], "scoped_fields": []}

    rows = frappe.get_all(
        "Company Specific Field",
        filters={
            "parenttype": RULE_DOCTYPE,
            "parent": ["in", [parent.name for parent in all_parents]],
        },
        fields=["custom_field", "parent"],
    )
    scoped_fields = sorted(
        {custom_fieldname(row.custom_field) for row in rows if row.custom_field}
    )
    active_parent = next(
        (parent for parent in all_parents if parent.enabled and parent.company == company), None
    )
    active_rule = get_rule(doctype, company) if active_parent else None
    return {
        "print_format": active_rule.get("print_format") if active_rule else None,
        "active_fields": active_rule.get("fields", []) if active_rule else [],
        "scoped_fields": [fieldname for fieldname in scoped_fields if fieldname],
    }


def resolve_print_format(
    doctype: str,
    name: str | None = None,
    doc: Any | None = None,
    company: str | None = None,
) -> str | None:
    if doc is None and name:
        doc = frappe.get_doc(doctype, name)
    company = company or (get_company(doc) if doc else None)
    rule = get_rule(doctype, company)
    return rule.get("print_format") if rule else None


def validate_company_fields(doc, method=None) -> None:
    """Enforce only mandatory fields configured for this document's company."""
    if not rules_are_available() or doc.doctype in {RULE_DOCTYPE, "Company Specific Field"}:
        return

    company = get_company(doc)
    if not company:
        return

    rule = get_rule(doc.doctype, company)
    if not rule:
        return

    missing = []
    for field in rule["fields"]:
        if not field["mandatory"] or not field["fieldname"]:
            continue
        value = doc.get(field["fieldname"])
        if value is None or value == "" or value == []:
            label = frappe.get_meta(doc.doctype).get_label(field["fieldname"])
            missing.append(label or field["fieldname"])

    if missing:
        frappe.throw(
            _("The following fields are mandatory for Company {0}: {1}").format(
                frappe.bold(company), ", ".join(frappe.bold(label) for label in missing)
            ),
            title=_("Missing Company Fields"),
        )
