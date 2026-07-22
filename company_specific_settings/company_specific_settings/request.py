from __future__ import annotations

from typing import Any

import frappe

from company_specific_settings.company_specific_settings.rules import (
    resolve_letter_head,
    resolve_print_format,
)

PRINT_ENDPOINTS = {
    "frappe.www.printview.get_html_and_style",
    "frappe.utils.print_format.download_pdf",
}


def apply_company_print_format() -> None:
    """Make the company rule authoritative for Print View requests."""
    if not _is_print_request():
        return

    doctype = frappe.form_dict.get("doctype")
    name = frappe.form_dict.get("name")
    if not doctype or not (name or frappe.form_dict.get("doc")):
        return

    doc = _get_request_document(doctype, name, frappe.form_dict.get("doc"))
    if not doc:
        return

    company_letter_head = resolve_letter_head(doctype, doc=doc)
    company_format = resolve_print_format(doctype, doc=doc)
    if company_format:
        frappe.form_dict["format"] = company_format
    if company_letter_head:
        frappe.form_dict["letterhead"] = company_letter_head
        frappe.form_dict["no_letterhead"] = 0


def _is_print_request() -> bool:
    request = getattr(frappe.local, "request", None)
    path = (getattr(request, "path", "") or "").rstrip("/")
    command = frappe.form_dict.get("cmd")
    return (
        path.endswith("/printview")
        or command in PRINT_ENDPOINTS
        or any(path.endswith(f"/api/method/{endpoint}") for endpoint in PRINT_ENDPOINTS)
    )


def _get_request_document(doctype: str, name: str | None, doc_data: Any):
    if doc_data:
        try:
            parsed = frappe.parse_json(doc_data) if isinstance(doc_data, str) else doc_data
            if isinstance(parsed, dict):
                return frappe._dict(parsed)
        except (TypeError, ValueError):
            return None

    if not name:
        return None

    try:
        return frappe.get_doc(doctype, name)
    except frappe.DoesNotExistError:
        return None

