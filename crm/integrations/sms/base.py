# -*- coding: utf-8 -*-
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseSMSProvider(ABC):
	@abstractmethod
	def send_sms(self, mobile: str, message: str, time_to_send: Optional[str] = None) -> Dict[str, Any]:
		"""Send a single or scheduled SMS."""
		pass

	@abstractmethod
	def send_bulk_sms(self, sms_list: List[Dict[str, Any]]) -> Dict[str, Any]:
		"""Send bulk SMS messages."""
		pass

	@staticmethod
	def format_mobile(mobile: str) -> str:
		"""Clean and normalize phone numbers (e.g. removes +, spaces, hyphens)."""
		if not mobile:
			return ""
		cleaned = "".join(c for c in str(mobile).strip() if c.isdigit())
		return cleaned
