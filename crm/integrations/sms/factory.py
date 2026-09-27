# -*- coding: utf-8 -*-
import frappe
from crm.integrations.sms.base import BaseSMSProvider
from crm.integrations.sms.textsms import TextSMSProvider


def get_sms_provider(provider_name: str = None) -> BaseSMSProvider:
	sms_settings = frappe.get_single("CRM SMS Settings")
	
	if not provider_name:
		provider_name = sms_settings.default_provider or "TextSMS"

	if provider_name == "TextSMS":
		textsms_doc = frappe.get_single("CRM TextSMS Settings")
		if not textsms_doc.enabled:
			frappe.throw("TextSMS integration is currently disabled in Settings.")
		
		api_key = textsms_doc.get_password("api_key") if hasattr(textsms_doc, "get_password") else textsms_doc.api_key
		if not api_key:
			api_key = textsms_doc.api_key

		if not api_key or not textsms_doc.partner_id or not textsms_doc.shortcode:
			frappe.throw("TextSMS credentials (API Key, Partner ID, Shortcode) are incomplete in Settings.")

		return TextSMSProvider(
			api_key=api_key,
			partner_id=textsms_doc.partner_id,
			shortcode=textsms_doc.shortcode
		)
	elif provider_name == "HostPinnacle":
		# Placeholder for HostPinnacle Bulk SMS integration
		frappe.throw("HostPinnacle SMS integration will be available soon.")
	else:
		frappe.throw(f"Unsupported SMS Provider: {provider_name}")
