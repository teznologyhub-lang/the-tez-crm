# Copyright (c) 2026, TezCRM and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMInvoice(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from crm.fcrm.doctype.crm_invoice_item.crm_invoice_item import CRMInvoiceItem
		from frappe.types import DF

		customer: DF.Link | None
		date: DF.Date | None
		deal: DF.Link | None
		due_date: DF.Date | None
		grand_total: DF.Currency
		items: DF.Table[CRMInvoiceItem]
		naming_series: DF.Literal["CRM-INV-.YYYY.-"]
		sales_order: DF.Link | None
		status: DF.Literal["Draft", "Unpaid", "Paid", "Overdue", "Cancelled"]
	# end: auto-generated types
	def validate(self):
		self.grand_total = 0
		for item in self.items:
			item.amount = (item.qty or 0) * (item.rate or 0)
			self.grand_total += item.amount
