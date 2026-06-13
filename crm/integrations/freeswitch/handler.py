# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.integrations.utils import create_request_log

from crm.integrations.api import get_contact_by_phone_number


@frappe.whitelist(allow_guest=True)
def handle_request(**kwargs):
	"""Webhook endpoint for FreeSWITCH call events."""
	request_log = create_request_log(
		kwargs,
		request_description="FreeSWITCH Call Webhook",
		service_name="FreeSWITCH",
		request_headers=frappe.request.headers,
		is_remote_request=1,
	)

	try:
		request_log.status = "Completed"
		settings = frappe.get_doc("CRM FreeSWITCH Settings")
		if not settings.enabled:
			return

		call_payload = kwargs
		frappe.publish_realtime("freeswitch_call", call_payload)

		call_id = call_payload.get("CallSid") or call_payload.get("uuid")
		if not call_id:
			return

		if frappe.db.exists("CRM Call Log", call_id):
			call_log = frappe.get_doc("CRM Call Log", call_id)
			update_call_log(call_payload, call_log)
		else:
			create_call_log(call_payload)

	except Exception:
		request_log.status = "Failed"
		request_log.error = frappe.get_traceback()
		frappe.db.rollback()
		frappe.log_error(title="Error while creating/updating FreeSWITCH call record")
		frappe.db.commit()
	finally:
		request_log.save(ignore_permissions=True)
		frappe.db.commit()


def create_call_log(call_payload):
	call_id = call_payload.get("CallSid") or call_payload.get("uuid")
	from_number = call_payload.get("from") or call_payload.get("caller_id_number")
	to_number = call_payload.get("to") or call_payload.get("callee_id_number")
	direction = call_payload.get("direction") or "Incoming"
	status = call_payload.get("status") or "Ringing"
	agent_email = call_payload.get("agent_email") or call_payload.get("user")

	call_log = frappe.new_doc("CRM Call Log")
	call_log.id = call_id
	call_log.to = to_number
	call_log.type = direction
	call_log.status = status
	call_log.telephony_medium = "FreeSWITCH"
	setattr(call_log, "from", from_number)

	if direction == "Incoming":
		call_log.receiver = agent_email
	else:
		call_log.caller = agent_email

	# link call log with lead/deal
	contact_number = from_number if direction == "Incoming" else to_number
	link(contact_number, call_log)

	call_log.save(ignore_permissions=True)
	frappe.db.commit()
	return call_log


def update_call_log(call_payload, call_log):
	call_log.status = call_payload.get("status") or call_log.status
	call_log.duration = call_payload.get("duration") or call_log.duration
	call_log.recording_url = call_payload.get("recording_url") or call_log.recording_url
	call_log.start_time = call_payload.get("start_time") or call_log.start_time
	call_log.end_time = call_payload.get("end_time") or call_log.end_time

	call_log.save(ignore_permissions=True)
	frappe.db.commit()


def link(contact_number, call_log):
	contact = get_contact_by_phone_number(contact_number)
	if contact.get("name"):
		doctype = "Contact"
		docname = contact.get("name")
		if contact.get("lead"):
			doctype = "CRM Lead"
			docname = contact.get("lead")
		elif contact.get("deal"):
			doctype = "CRM Deal"
			docname = contact.get("deal")
		call_log.link_with_reference_doc(doctype, docname)
