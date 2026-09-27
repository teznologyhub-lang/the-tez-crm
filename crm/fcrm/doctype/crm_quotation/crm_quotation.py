# Copyright (c) 2026, TezCRM and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMQuotation(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from crm.fcrm.doctype.crm_quotation_item.crm_quotation_item import CRMQuotationItem
		from frappe.types import DF

		customer: DF.Link | None
		date: DF.Date | None
		deal: DF.Link | None
		grand_total: DF.Currency
		items: DF.Table[CRMQuotationItem]
		naming_series: DF.Literal["CRM-QTN-.YYYY.-"]
		status: DF.Literal["Draft", "Sent", "Accepted", "Rejected"]
		valid_till: DF.Date | None
	# end: auto-generated types
	def validate(self):
		self.grand_total = 0
		for item in self.items:
			item.amount = (item.qty or 0) * (item.rate or 0)
			self.grand_total += item.amount
