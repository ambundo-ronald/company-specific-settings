from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from company_specific_settings.company_specific_settings.printing import get_html_and_style


class TestPrintPreview(FrappeTestCase):
    @patch(
        "company_specific_settings.company_specific_settings.printing.frappe_get_html_and_style",
        return_value={"html": "company format", "style": ""},
    )
    @patch(
        "company_specific_settings.company_specific_settings.printing.resolve_print_format",
        return_value="Company Sales Invoice",
    )
    @patch("company_specific_settings.company_specific_settings.printing.frappe.get_doc")
    def test_company_format_replaces_requested_preview_format(
        self, get_doc, resolver, frappe_renderer
    ):
        document = frappe._dict(
            doctype="Sales Invoice",
            name="SINV-0001",
            company="Test Company",
        )
        get_doc.return_value = document

        result = get_html_and_style(
            doc="Sales Invoice",
            name="SINV-0001",
            print_format="Global Sales Invoice",
        )

        resolver.assert_called_once_with("Sales Invoice", doc=document)
        frappe_renderer.assert_called_once_with(
            doc="Sales Invoice",
            name="SINV-0001",
            print_format="Company Sales Invoice",
            no_letterhead=None,
            letterhead=None,
            trigger_print=False,
            style=None,
            settings=None,
        )
        self.assertEqual(result["html"], "company format")
