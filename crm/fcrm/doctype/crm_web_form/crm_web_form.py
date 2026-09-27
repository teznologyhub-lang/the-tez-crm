# Copyright (c) 2026, TezCRM and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CRMWebForm(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from crm.fcrm.doctype.crm_web_form_field.crm_web_form_field import CRMWebFormField
		from frappe.types import DF

		allowed_domains: DF.SmallText | None
		default_lead_owner: DF.Link | None
		fields: DF.Table[CRMWebFormField]
		is_active: DF.Check
		lead_source: DF.Link | None
		redirect_url: DF.Data | None
		success_message: DF.SmallText | None
		title: DF.Data
	# end: auto-generated types
	pass
