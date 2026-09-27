import frappe
from frappe import _
from frappe.utils.pdf import get_pdf


@frappe.whitelist()
def download_pdf(doctype, docname):
	"""Generate and return a PDF for a CPQ document (Quotation or Invoice)."""
	allowed_doctypes = {"CRM Quotation", "CRM Sales Order", "CRM Invoice"}
	if doctype not in allowed_doctypes:
		frappe.throw(_("PDF generation not supported for {0}").format(doctype))

	doc = frappe.get_doc(doctype, docname)
	doc.check_permission("print")

	# Determine which template to use
	template_map = {
		"CRM Quotation": "crm/fcrm/doctype/crm_quotation/crm_quotation_print.html",
		"CRM Sales Order": "crm/fcrm/doctype/crm_sales_order/crm_sales_order_print.html",  # reuse quotation template for now
		"CRM Invoice": "crm/fcrm/doctype/crm_invoice/crm_invoice_print.html",
	}

	template_path = template_map[doctype]
	html = frappe.render_template(template_path, {"doc": doc, "frappe": frappe})

	pdf_data = get_pdf(html)

	frappe.local.response.filename = f"{docname}.pdf"
	frappe.local.response.filecontent = pdf_data
	frappe.local.response.type = "download"
