# Copyright (c) 2026, TezCRM and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMSalesOrder(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from crm.fcrm.doctype.crm_sales_order_item.crm_sales_order_item import CRMSalesOrderItem
		from frappe.types import DF

		customer: DF.Link | None
		date: DF.Date | None
		deal: DF.Link | None
		delivery_date: DF.Date | None
		grand_total: DF.Currency
		items: DF.Table[CRMSalesOrderItem]
		naming_series: DF.Literal["CRM-SO-.YYYY.-"]
		quotation: DF.Link | None
		status: DF.Literal["Draft", "Confirmed", "Completed", "Cancelled"]
	# end: auto-generated types
	def validate(self):
		self.grand_total = 0
		for item in self.items:
			item.amount = (item.qty or 0) * (item.rate or 0)
			self.grand_total += item.amount
