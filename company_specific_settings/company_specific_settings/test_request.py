from types import SimpleNamespace
from unittest.mock import patch

import frappe
from frappe.tests.utils import FrappeTestCase

from company_specific_settings.company_specific_settings.request import (
    apply_company_print_format,
)


class TestPrintRequest(FrappeTestCase):
    def setUp(self):
        self.original_form_dict = getattr(frappe.local, "form_dict", None)
        self.original_request = getattr(frappe.local, "request", None)

    def tearDown(self):
        frappe.local.form_dict = self.original_form_dict
        frappe.local.request = self.original_request

    @patch(
        "company_specific_settings.company_specific_settings.request.resolve_print_format",
        return_value="Company Sales Invoice",
    )
    def test_direct_printview_replaces_global_format(self, resolver):
        frappe.local.request = SimpleNamespace(path="/printview")
        frappe.local.form_dict = frappe._dict(
            {
                "doctype": "Sales Invoice",
                "name": "SINV-0001",
                "format": "Global Sales Invoice",
                "doc": frappe.as_json(
                    {
                        "doctype": "Sales Invoice",
                        "name": "SINV-0001",
                        "company": "Test Company",
                    }
                ),
            }
        )

        apply_company_print_format()

        self.assertEqual(frappe.form_dict.format, "Company Sales Invoice")
        resolver.assert_called_once()

    @patch(
        "company_specific_settings.company_specific_settings.request.resolve_print_format",
        return_value=None,
    )
    def test_route_keeps_original_when_company_has_no_format(self, resolver):
        frappe.local.request = SimpleNamespace(path="/printview")
        frappe.local.form_dict = frappe._dict(
            {
                "doctype": "Sales Invoice",
                "name": "SINV-0001",
                "format": "Global Sales Invoice",
                "doc": {"doctype": "Sales Invoice", "company": "Test Company"},
            }
        )

        apply_company_print_format()

        self.assertEqual(frappe.form_dict.format, "Global Sales Invoice")
        resolver.assert_called_once()

