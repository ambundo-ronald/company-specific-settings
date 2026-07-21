import unittest

import frappe
from frappe.tests.utils import FrappeTestCase

from company_specific_settings.company_specific_settings.rules import (
    get_configuration,
    resolve_print_format,
    validate_company_fields,
)


class TestCompanySpecificRule(FrappeTestCase):
    """Integration coverage; ERPNext supplies Company and Sales Invoice."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = frappe.db.get_value("Company", {}, "name")
        if not cls.company:
            raise unittest.SkipTest("No Company exists on the test site")
        if frappe.db.exists(
            "Company Specific Rule",
            {"company": cls.company, "document_type": "Sales Invoice"},
        ):
            raise unittest.SkipTest("The test company already has a Sales Invoice rule")

        cls.fieldname = f"test_company_note_{frappe.generate_hash(6).lower()}"
        cls.custom_field = f"Sales Invoice-{cls.fieldname}"
        frappe.get_doc(
            {
                "doctype": "Custom Field",
                "dt": "Sales Invoice",
                "label": "Test Company Note",
                "fieldname": cls.fieldname,
                "fieldtype": "Data",
                "insert_after": "company",
            }
        ).insert(ignore_permissions=True)

        cls.rule = frappe.get_doc(
            {
                "doctype": "Company Specific Rule",
                "company": cls.company,
                "document_type": "Sales Invoice",
                "fields": [{"custom_field": cls.custom_field, "mandatory": 1}],
            }
        ).insert(ignore_permissions=True)

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "rule", None):
            cls.rule.delete(ignore_permissions=True)
        if frappe.db.exists("Custom Field", getattr(cls, "custom_field", "")):
            frappe.delete_doc("Custom Field", cls.custom_field, force=True)
        super().tearDownClass()

    def test_configuration_contains_scoped_mandatory_field(self):
        config = get_configuration("Sales Invoice", self.company)
        self.assertIn(self.fieldname, config["scoped_fields"])
        self.assertTrue(config["active_fields"][0]["mandatory"])

    def test_company_mandatory_validation(self):
        doc = frappe._dict(doctype="Sales Invoice", company=self.company)
        doc[self.fieldname] = ""
        with self.assertRaises(frappe.ValidationError):
            validate_company_fields(doc)

    def test_no_print_format_when_rule_has_none(self):
        self.assertIsNone(resolve_print_format("Sales Invoice", company=self.company))
