import json
import frappe
from frappe import _


@frappe.whitelist()
def get_ticket_summary():
	"""Returns summary counts of tickets grouped by status."""
	open_count = frappe.db.count("CRM Ticket", filters={"status": "Open"})
	pending_count = frappe.db.count("CRM Ticket", filters={"status": "Pending"})
	resolved_count = frappe.db.count("CRM Ticket", filters={"status": "Resolved"})
	closed_count = frappe.db.count("CRM Ticket", filters={"status": "Closed"})
	total_count = frappe.db.count("CRM Ticket")

	return {
		"open": open_count,
		"pending": pending_count,
		"resolved": resolved_count,
		"closed": closed_count,
		"total": total_count,
	}


@frappe.whitelist()
def update_ticket_status(name, status, resolution=None):
	"""Updates ticket status and optional resolution notes."""
	if not frappe.db.exists("CRM Ticket", name):
		frappe.throw(_("Ticket not found"))

	doc = frappe.get_doc("CRM Ticket", name)
	doc.status = status
	if resolution:
		doc.resolution = resolution
	doc.save()
	frappe.db.commit()
	return doc.as_dict()
