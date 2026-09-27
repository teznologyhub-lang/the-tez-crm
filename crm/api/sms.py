# -*- coding: utf-8 -*-
import frappe
from typing import Any, Dict, List, Optional
from crm.integrations.sms.factory import get_sms_provider


@frappe.whitelist()
def get_sms_settings() -> Dict[str, Any]:
	sms_settings = frappe.get_single("CRM SMS Settings")
	textsms_settings = frappe.get_single("CRM TextSMS Settings")
	
	api_key = textsms_settings.get_password("api_key") if hasattr(textsms_settings, "get_password") else textsms_settings.api_key
	if not api_key:
		api_key = textsms_settings.api_key

	return {
		"sms_enabled": bool(sms_settings.enabled),
		"default_provider": sms_settings.default_provider or "TextSMS",
		"textsms": {
			"enabled": bool(textsms_settings.enabled),
			"partner_id": textsms_settings.partner_id or "",
			"shortcode": textsms_settings.shortcode or "",
			"api_key_set": bool(api_key),
			"api_key": api_key if api_key else ""
		}
	}


@frappe.whitelist()
def save_sms_settings(sms_enabled: int = 0, default_provider: str = "TextSMS", textsms_enabled: int = 0, partner_id: str = "", shortcode: str = "", api_key: str = ""):
	if "System Manager" not in frappe.get_roles() and "Sales Manager" not in frappe.get_roles():
		frappe.throw("You are not authorized to update SMS Settings.")

	sms_settings = frappe.get_single("CRM SMS Settings")
	sms_settings.enabled = int(sms_enabled)
	sms_settings.default_provider = default_provider
	sms_settings.save()

	textsms_settings = frappe.get_single("CRM TextSMS Settings")
	textsms_settings.enabled = int(textsms_enabled)
	textsms_settings.partner_id = partner_id
	textsms_settings.shortcode = shortcode
	if api_key and api_key != "*****":
		textsms_settings.api_key = api_key
	textsms_settings.save()

	frappe.db.commit()
	return {"success": True, "message": "SMS Settings saved successfully."}


@frappe.whitelist()
def send_sms(mobile: str, message: str, time_to_send: Optional[str] = None, ref_doctype: Optional[str] = None, ref_docname: Optional[str] = None) -> Dict[str, Any]:
	if not mobile:
		frappe.throw("Mobile phone number is required.")
	if not message:
		frappe.throw("SMS message content cannot be empty.")

	sms_settings = frappe.get_single("CRM SMS Settings")
	if not sms_settings.enabled:
		frappe.throw("SMS sending is currently disabled in Global SMS Settings.")

	provider = get_sms_provider(sms_settings.default_provider)
	result = provider.send_sms(mobile=mobile, message=message, time_to_send=time_to_send)

	if result.get("success") and ref_doctype and ref_docname:
		log_content = f"📱 <b>SMS Sent to {mobile}</b><br>{message}"
		if time_to_send:
			log_content += f"<br><i>Scheduled for: {time_to_send}</i>"
		try:
			frappe.get_doc({
				"doctype": "Comment",
				"comment_type": "Info",
				"reference_doctype": ref_doctype,
				"reference_name": ref_docname,
				"content": log_content,
			}).insert(ignore_permissions=True)
		except Exception as e:
			frappe.log_error(f"Failed to log SMS activity: {str(e)}")

	return result


@frappe.whitelist()
def send_bulk_sms(sms_list: Any, ref_doctype: Optional[str] = None, ref_docname: Optional[str] = None) -> Dict[str, Any]:
	if isinstance(sms_list, str):
		import json
		sms_list = json.loads(sms_list)

	sms_settings = frappe.get_single("CRM SMS Settings")
	if not sms_settings.enabled:
		frappe.throw("SMS sending is currently disabled in Global SMS Settings.")

	provider = get_sms_provider(sms_settings.default_provider)
	result = provider.send_bulk_sms(sms_list=sms_list)

	return result


@frappe.whitelist()
def send_test_sms(mobile: str, message: str = "TezCRM Test SMS - TextSMS integration working successfully!") -> Dict[str, Any]:
	provider = get_sms_provider("TextSMS")
	return provider.send_sms(mobile=mobile, message=message)
