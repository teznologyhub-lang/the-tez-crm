# Copyright (c) 2026, TezCRM and contributors
# For license information, please see license.txt

import json
import traceback
import frappe
from frappe.utils import add_days, today, now_datetime


def trigger_workflow_rules(doc, method):
	"""
	Central doc_events hook to evaluate active CRM Workflow Rules
	"""
	if frappe.flags.in_install or frappe.flags.in_migrate:
		return

	doctype = doc.doctype
	# Fetch active rules for this doctype
	rules = frappe.get_all(
		"CRM Workflow Rule",
		filters={"document_type": doctype, "is_active": 1},
		fields=["name", "rule_name", "trigger_type", "trigger_field"],
	)

	if not rules:
		return

	is_new = doc.is_new() or method == "after_insert"

	for r in rules:
		rule_doc = frappe.get_doc("CRM Workflow Rule", r.name)
		trigger = rule_doc.trigger_type

		# Trigger type matching
		matches_trigger = False
		if trigger == "On Creation" and is_new:
			matches_trigger = True
		elif trigger == "On Update" and not is_new:
			matches_trigger = True
		elif trigger == "On Creation or Update":
			matches_trigger = True
		elif trigger == "On Field Change":
			t_field = rule_doc.trigger_field
			if t_field and (is_new or doc.has_value_changed(t_field)):
				matches_trigger = True

		if not matches_trigger:
			continue

		# Evaluate conditions
		if not evaluate_rule_conditions(doc, rule_doc.conditions):
			continue

		# Execute actions
		execute_rule_actions(doc, rule_doc)


def evaluate_rule_conditions(doc, conditions):
	"""
	Evaluate all child conditions for a rule (AND logic)
	"""
	if not conditions:
		return True

	for cond in conditions:
		field = cond.field
		operator = cond.operator
		target_val = cond.value or ""
		actual_val = doc.get(field)

		if operator == "equals":
			if str(actual_val or "") != str(target_val):
				return False
		elif operator == "not_equals":
			if str(actual_val or "") == str(target_val):
				return False
		elif operator == "contains":
			if target_val.lower() not in str(actual_val or "").lower():
				return False
		elif operator == "greater_than":
			try:
				if float(actual_val or 0) <= float(target_val or 0):
					return False
			except Exception:
				return False
		elif operator == "less_than":
			try:
				if float(actual_val or 0) >= float(target_val or 0):
					return False
			except Exception:
				return False
		elif operator == "is_set":
			if not actual_val:
				return False
		elif operator == "is_not_set":
			if actual_val:
				return False
		elif operator == "changed_to":
			if not doc.has_value_changed(field) or str(actual_val or "") != str(target_val):
				return False

	return True


def execute_rule_actions(doc, rule_doc):
	"""
	Execute configured actions for a passing workflow rule
	"""
	executed_summary = []
	failed = False
	tb = ""

	for action in rule_doc.actions:
		atype = action.action_type
		try:
			if atype == "send_email":
				# Resolve recipient
				recipient = None
				if action.recipient_field == "Lead/Contact Email":
					recipient = doc.get("email") or doc.get("email_id") or doc.get("contact_email")
				elif action.recipient_field == "Owner Email":
					if doc.get("owner"):
						recipient = frappe.db.get_value("User", doc.owner, "email")
				elif action.recipient_field == "Custom Email":
					recipient = action.custom_recipient

				if recipient and action.email_template:
					template = frappe.get_doc("Email Template", action.email_template)
					subject = frappe.render_template(template.subject or "", {"doc": doc})
					message = frappe.render_template(
						template.response_html or template.response or "", {"doc": doc}
					)

					frappe.sendmail(
						recipients=[recipient],
						subject=subject,
						message=message,
						reference_doctype=doc.doctype,
						reference_name=doc.name,
					)
					executed_summary.append(f"Sent email ({action.email_template}) to {recipient}")

			elif atype == "update_field":
				if action.update_field_name:
					doc.db_set(action.update_field_name, action.update_field_value)
					executed_summary.append(
						f"Updated field '{action.update_field_name}' to '{action.update_field_value}'"
					)

			elif atype == "create_task":
				task_subject = action.task_subject or f"Follow up on {doc.doctype} {doc.name}"
				due_date = add_days(today(), action.task_due_in_days or 1)
				assignee = action.assign_to_user or doc.get("owner") or frappe.session.user

				# Create CRM Task if doctype exists, else ToDo
				if frappe.db.exists("DocType", "CRM Task"):
					t = frappe.get_doc(
						{
							"doctype": "CRM Task",
							"title": task_subject,
							"reference_doctype": doc.doctype,
							"reference_docname": doc.name,
							"due_date": due_date,
							"assigned_to": assignee,
							"status": "Todo",
						}
					)
					t.insert(ignore_permissions=True)
				else:
					frappe.get_doc(
						{
							"doctype": "ToDo",
							"description": task_subject,
							"reference_type": doc.doctype,
							"reference_name": doc.name,
							"date": due_date,
							"allocated_to": assignee,
							"status": "Open",
						}
					).insert(ignore_permissions=True)

				executed_summary.append(f"Created task '{task_subject}' due on {due_date}")

			elif atype == "assign_owner":
				if action.assign_to_user:
					if hasattr(doc, "assigned_to"):
						doc.db_set("assigned_to", action.assign_to_user)
					doc.db_set("owner", action.assign_to_user)
					executed_summary.append(f"Assigned owner to {action.assign_to_user}")

			elif atype == "webhook":
				if action.webhook_url:
					import requests

					payload = doc.as_dict()
					requests.post(action.webhook_url, json=payload, timeout=5)
					executed_summary.append(f"Triggered webhook: {action.webhook_url}")

		except Exception as e:
			failed = True
			tb = traceback.format_exc()
			executed_summary.append(f"Failed action ({atype}): {str(e)}")

	# Record Execution Log
	try:
		log = frappe.get_doc(
			{
				"doctype": "CRM Workflow Execution Log",
				"workflow_rule": rule_doc.name,
				"reference_doctype": doc.doctype,
				"reference_name": doc.name,
				"status": "Failed" if failed else "Success",
				"executed_actions": "\n".join(executed_summary),
				"traceback": tb if failed else "",
			}
		)
		log.insert(ignore_permissions=True)
	except Exception:
		pass
