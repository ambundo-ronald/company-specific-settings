# Company Specific Settings

A Frappe/ERPNext app that adds company-level configuration without modifying
ERPNext core.

## Features

- Select the Print Format enforced for each Company + DocType combination.
- Select the Letter Head enforced for each Company + DocType combination.
- Scope Custom Fields to one or more companies.
- Make a scoped Custom Field mandatory only for the matching company.
- Enforce conditional mandatory fields on the server (Desk, imports, and API).
- Hide non-applicable scoped fields on Desk forms.

The app targets Frappe/ERPNext v15 and v16.

## Installation

From the bench directory:

```bash
bench get-app /path/to/company_specific_settings
bench --site your-site install-app company_specific_settings
bench --site your-site migrate
bench build --app company_specific_settings
bench restart
```

## Configuration

1. Create the Custom Field normally, but leave its standard **Mandatory** flag
   off. The app will also turn that flag off when the field is added to a rule.
2. Open **Company Specific Rule** and create one record for the Company and
   DocType.
3. Optionally select the company's Print Format and Letter Head.
4. Add the Custom Fields that apply to the company and tick **Mandatory** where
   required.
5. Reload Desk after adding a rule for a DocType for the first time.

You can add the same Custom Field to several company rules when it should be
visible in several companies.

## Scope and security

Field visibility is applied to standard Desk forms. Server validation prevents
non-matching companies from being affected by conditional mandatory rules.
Frappe metadata is site-wide, so scoped fields can still exist in reports,
exports, custom scripts, and direct API payloads. Do not use this feature as a
data-secrecy boundary; use permissions or separate DocTypes for sensitive data.

The app resolves the company on the server for `/printview`, the standard print
preview request, and PDF downloads. When a matching rule has a Print Format, it
replaces the site-wide DocType default and any `format` query argument.
When it has a Letter Head, that Letter Head is enabled and replaces the document,
site-wide, or request selection.

Code that calls `frappe.get_print` directly does not pass through an HTTP print
route and should resolve both settings first with:

```python
from company_specific_settings.company_specific_settings.rules import (
    resolve_letter_head,
    resolve_print_format,
)

print_format = resolve_print_format(doctype, name=document_name)
letter_head = resolve_letter_head(doctype, name=document_name)
html = frappe.get_print(doctype, document_name, print_format, letterhead=letter_head)
```

