app_name = "company_specific_settings"
app_title = "Company Specific Settings"
app_publisher = "Norwa Africa"
app_description = "Company-scoped print formats and custom fields for ERPNext"
app_email = ""
app_license = "MIT"

required_apps = ["erpnext"]

app_include_js = "/assets/company_specific_settings/js/company_specific_settings.js"

before_request = [
    "company_specific_settings.company_specific_settings.request.apply_company_print_format"
]

doc_events = {
    "*": {
        "before_validate": "company_specific_settings.company_specific_settings.rules.validate_company_fields"
    }
}

override_whitelisted_methods = {
    "frappe.utils.print_format.download_pdf":
        "company_specific_settings.company_specific_settings.printing.download_pdf"
}

