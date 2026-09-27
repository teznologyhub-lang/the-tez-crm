# -*- coding: utf-8 -*-
import json
import requests
import frappe
from typing import Any, Dict, List, Optional
from crm.integrations.sms.base import BaseSMSProvider


class TextSMSProvider(BaseSMSProvider):
	SINGLE_URL = "https://sms.textsms.co.ke/api/services/sendsms/"
	BULK_URL = "https://sms.textsms.co.ke/api/services/sendbulk/"

	def __init__(self, api_key: str, partner_id: str, shortcode: str):
		self.api_key = api_key
		self.partner_id = partner_id
		self.shortcode = shortcode

	def send_sms(self, mobile: str, message: str, time_to_send: Optional[str] = None) -> Dict[str, Any]:
		cleaned_mobile = self.format_mobile(mobile)
		if not cleaned_mobile:
			return {
				"success": False,
				"error": "Invalid or missing mobile number"
			}

		payload = {
			"apikey": self.api_key,
			"partnerID": self.partner_id,
			"message": message,
			"shortcode": self.shortcode,
			"mobile": cleaned_mobile
		}

		if time_to_send:
			payload["timeToSend"] = str(time_to_send)

		headers = {
			"Content-Type": "application/json",
			"Accept": "application/json"
		}

		try:
			response = requests.post(self.SINGLE_URL, json=payload, headers=headers, timeout=15)
			res_data = response.json()
			
			# Check TextSMS response format
			responses = res_data.get("responses", [])
			if responses:
				first_resp = responses[0]
				code = first_resp.get("respose-code") or first_resp.get("response-code")
				desc = first_resp.get("response-description", "")
				if str(code) == "200":
					return {
						"success": True,
						"message_id": first_resp.get("messageid"),
						"mobile": cleaned_mobile,
						"description": desc,
						"raw": res_data
					}
				else:
					return {
						"success": False,
						"error": f"API Error ({code}): {desc}",
						"raw": res_data
					}
			
			return {
				"success": True,
				"raw": res_data
			}
		except Exception as e:
			frappe.log_error(f"TextSMS send error: {str(e)}", "TextSMS Integration")
			return {
				"success": False,
				"error": str(e)
			}

	def send_bulk_sms(self, sms_list: List[Dict[str, Any]]) -> Dict[str, Any]:
		if not sms_list:
			return {"success": False, "error": "No SMS items provided"}

		formatted_smslist = []
		for idx, item in enumerate(sms_list):
			mobile = self.format_mobile(item.get("mobile", ""))
			if not mobile:
				continue
			formatted_smslist.append({
				"partnerID": self.partner_id,
				"apikey": self.api_key,
				"pass_type": "plain",
				"clientsmsid": item.get("clientsmsid", idx + 1),
				"mobile": mobile,
				"message": item.get("message", ""),
				"shortcode": self.shortcode
			})

		if not formatted_smslist:
			return {"success": False, "error": "No valid mobile numbers in SMS list"}

		payload = {
			"count": len(formatted_smslist),
			"smslist": formatted_smslist
		}

		headers = {
			"Content-Type": "application/json",
			"Accept": "application/json"
		}

		try:
			response = requests.post(self.BULK_URL, json=payload, headers=headers, timeout=20)
			res_data = response.json()
			return {
				"success": True,
				"responses": res_data.get("responses", []),
				"raw": res_data
			}
		except Exception as e:
			frappe.log_error(f"TextSMS bulk send error: {str(e)}", "TextSMS Integration")
			return {
				"success": False,
				"error": str(e)
			}
