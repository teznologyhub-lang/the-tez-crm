# Copyright (c) 2026, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe import _


@frappe.whitelist()
def is_enabled():
	return frappe.db.get_single_value("CRM FreeSWITCH Settings", "enabled")


@frappe.whitelist()
def get_freeswitch_agent_config():
	"""Returns the FreeSWITCH configuration and credentials for the logged-in agent."""
	settings = frappe.get_doc("CRM FreeSWITCH Settings")
	if not settings.enabled:
		return {
			"ok": False,
			"error": "freeswitch_disabled",
			"detail": _("FreeSWITCH integration is disabled."),
		}

	if not frappe.db.exists("CRM Telephony Agent", frappe.session.user):
		return {
			"ok": False,
			"error": "agent_settings_missing",
			"detail": _("Telephony agent settings not configured for this user."),
		}

	agent = frappe.get_doc("CRM Telephony Agent", frappe.session.user)
	extension = agent.freeswitch_extension
	password = agent.get_password("freeswitch_password") if agent.freeswitch_password else None

	if not extension or not password:
		return {
			"ok": False,
			"error": "credentials_missing",
			"detail": _("FreeSWITCH extension or password not set for the current user."),
		}

	return {
		"ok": True,
		"server_address": settings.server_address,
		"wss_url": settings.wss_url,
		"extension": extension,
		"password": password,
	}
