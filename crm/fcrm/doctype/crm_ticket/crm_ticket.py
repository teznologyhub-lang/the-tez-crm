import frappe
from frappe.model.document import Document
from frappe.utils import now_datetime


class CRMTicket(Document):
	def validate(self):
		if self.status in ("Resolved", "Closed") and not self.resolved_on:
			self.resolved_on = now_datetime()
		elif self.status not in ("Resolved", "Closed"):
			self.resolved_on = None

		# Track first response timestamp if comments/notes exist and not set
		if self.assigned_to and not self.first_responded_on and self.status != "Open":
			self.first_responded_on = now_datetime()

	@staticmethod
	def default_list_data():
		columns = [
			{
				"label": "Ticket ID",
				"type": "Data",
				"key": "name",
				"width": "8rem",
			},
			{
				"label": "Subject",
				"type": "Data",
				"key": "subject",
				"width": "16rem",
			},
			{
				"label": "Status",
				"type": "Select",
				"key": "status",
				"width": "8rem",
			},
			{
				"label": "Priority",
				"type": "Select",
				"key": "priority",
				"width": "8rem",
			},
			{
				"label": "Type",
				"type": "Select",
				"key": "ticket_type",
				"width": "9rem",
			},
			{
				"label": "Assigned Owner",
				"type": "Link",
				"options": "User",
				"key": "assigned_to",
				"width": "11rem",
			},
			{
				"label": "Customer Contact",
				"type": "Link",
				"options": "Contact",
				"key": "customer_contact",
				"width": "11rem",
			},
			{
				"label": "Last Modified",
				"type": "Datetime",
				"key": "modified",
				"width": "9rem",
			},
		]
		rows = [
			"name",
			"subject",
			"status",
			"priority",
			"ticket_type",
			"assigned_to",
			"customer_contact",
			"organization",
			"lead",
			"deal",
			"description",
			"resolution",
			"first_responded_on",
			"resolved_on",
			"modified",
			"_assign",
		]
		return {"columns": columns, "rows": rows}

	@staticmethod
	def default_kanban_settings():
		return {
			"column_field": "status",
			"title_field": "subject",
			"kanban_fields": '["priority", "ticket_type", "customer_contact", "assigned_to", "modified"]',
		}
