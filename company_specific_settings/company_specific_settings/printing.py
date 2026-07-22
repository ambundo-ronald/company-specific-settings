from typing import Literal

import frappe
from frappe.translate import print_language
from frappe.www.printview import get_html_and_style as frappe_get_html_and_style
from frappe.www.printview import validate_print_permission

from company_specific_settings.company_specific_settings.rules import (
    resolve_letter_head,
    resolve_print_format,
)


@frappe.whitelist()
def get_html_and_style(
    doc: str,
    name: str | None = None,
    print_format: str | None = None,
    no_letterhead: bool | None = None,
    letterhead: str | None = None,
    trigger_print: bool = False,
    style: str | None = None,
    settings: str | None = None,
):
    """Make the configured company format authoritative in Print Preview."""
    if isinstance(name, str):
        document = frappe.get_doc(doc, name)
    else:
        document_data = frappe.parse_json(doc) if isinstance(doc, str) else doc
        document = frappe.get_doc(document_data)

    company_letter_head = resolve_letter_head(document.doctype, doc=document)
    print_format = resolve_print_format(document.doctype, doc=document) or print_format
    if company_letter_head:
        letterhead = company_letter_head
        no_letterhead = 0
    return frappe_get_html_and_style(
        doc=doc,
        name=name,
        print_format=print_format,
        no_letterhead=no_letterhead,
        letterhead=letterhead,
        trigger_print=trigger_print,
        style=style,
        settings=settings,
    )


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
    company_letter_head = resolve_letter_head(doctype, doc=doc)
    format = resolve_print_format(doctype, doc=doc) or format
    if company_letter_head:
        letterhead = company_letter_head
        no_letterhead = 0

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

