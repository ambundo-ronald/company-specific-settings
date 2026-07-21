from typing import Literal

import frappe
from frappe.translate import print_language
from frappe.www.printview import validate_print_permission

from company_specific_settings.company_specific_settings.rules import resolve_print_format


@frappe.whitelist(allow_guest=True)
def download_pdf(
    doctype: str,
    name: str,
    format=None,
    doc=None,
    no_letterhead=0,
    language=None,
    letterhead=None,
    pdf_generator: Literal["wkhtmltopdf", "chrome"] | None = None,
):
    """Make the configured company format authoritative for PDF downloads."""
    doc = doc or frappe.get_doc(doctype, name)
    validate_print_permission(doc)
    format = resolve_print_format(doctype, doc=doc) or format

    with print_language(language):
        pdf_file = frappe.get_print(
            doctype,
            name,
            format,
            doc=doc,
            as_pdf=True,
            letterhead=letterhead,
            no_letterhead=no_letterhead,
            pdf_generator=pdf_generator,
        )

    frappe.local.response.filename = f"{name.replace(' ', '-').replace('/', '-')}.pdf"
    frappe.local.response.filecontent = pdf_file
    frappe.local.response.type = "pdf"

