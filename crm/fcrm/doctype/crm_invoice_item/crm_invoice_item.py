# Copyright (c) 2026, TezCRM and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMInvoiceItem(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		amount: DF.Currency
		description: DF.Text | None
		parent: DF.Data
		parentfield: DF.Data
		parenttype: DF.Data
		product: DF.Link
		qty: DF.Float
		rate: DF.Currency
	# end: auto-generated types
	pass
