# Copyright (c) 2026, TezCRM and contributors
# For license information, please see license.txt

import json
import frappe


@frappe.whitelist()
def get_workflow_rules():
	"""
	Get all workflow rules with child conditions and actions
	"""
	rules = frappe.get_all(
		"CRM Workflow Rule",
		fields=[
			"name",
			"rule_name",
			"document_type",
			"trigger_type",
			"trigger_field",
			"is_active",
			"description",
			"modified",
		],
		order_by="modified desc",
	)

	for r in rules:
		doc = frappe.get_doc("CRM Workflow Rule", r.name)
		r["conditions"] = [c.as_dict() for c in doc.conditions]
		r["actions"] = [a.as_dict() for a in doc.actions]

	return rules


@frappe.whitelist()
def save_workflow_rule(rule_data):
	"""
	Save or update a CRM Workflow Rule
	"""
	if isinstance(rule_data, str):
		rule_data = json.loads(rule_data)

	name = rule_data.get("name")
	if name and frappe.db.exists("CRM Workflow Rule", name):
		doc = frappe.get_doc("CRM Workflow Rule", name)
	else:
		doc = frappe.new_doc("CRM Workflow Rule")

	doc.rule_name = rule_data.get("rule_name")
	doc.document_type = rule_data.get("document_type")
	doc.trigger_type = rule_data.get("trigger_type")
	doc.trigger_field = rule_data.get("trigger_field")
	doc.is_active = 1 if rule_data.get("is_active") else 0
	doc.description = rule_data.get("description")

	# Set conditions
	doc.set("conditions", [])
	for cond in rule_data.get("conditions", []):
		doc.append(
			"conditions",
			{
				"field": cond.get("field"),
				"operator": cond.get("operator"),
				"value": cond.get("value"),
			},
		)

	# Set actions
	doc.set("actions", [])
	for act in rule_data.get("actions", []):
		doc.append(
			"actions",
			{
				"action_type": act.get("action_type"),
				"email_template": act.get("email_template"),
				"recipient_field": act.get("recipient_field"),
				"custom_recipient": act.get("custom_recipient"),
				"update_field_name": act.get("update_field_name"),
				"update_field_value": act.get("update_field_value"),
				"task_subject": act.get("task_subject"),
				"task_due_in_days": act.get("task_due_in_days", 1),
				"assign_to_user": act.get("assign_to_user"),
				"webhook_url": act.get("webhook_url"),
			},
		)

	doc.save(ignore_permissions=True)
	return doc.name


@frappe.whitelist()
def delete_workflow_rule(rule_name):
	"""
	Delete a workflow rule
	"""
	if frappe.db.exists("CRM Workflow Rule", rule_name):
		frappe.delete_doc("CRM Workflow Rule", rule_name, ignore_permissions=True)
		return True
	return False


@frappe.whitelist()
def toggle_workflow_rule(rule_name, is_active):
	"""
	Quick toggle active state
	"""
	if frappe.db.exists("CRM Workflow Rule", rule_name):
		frappe.db.set_value("CRM Workflow Rule", rule_name, "is_active", 1 if is_active else 0)
		return True
	return False


@frappe.whitelist()
def get_doctype_fields(doctype):
	"""
	Get list of field names and labels for a Target Doctype
	"""
	if not frappe.db.exists("DocType", doctype):
		return []

	meta = frappe.get_meta(doctype)
	fields = []
	for f in meta.fields:
		if f.fieldtype not in ("Section Break", "Column Break", "Tab Break", "HTML", "Table"):
			fields.append({"fieldname": f.fieldname, "label": f.label or f.fieldname, "type": f.fieldtype})
	return fields


@frappe.whitelist()
def get_execution_logs(workflow_rule=None, limit=50):
	"""
	Get workflow execution audit logs
	"""
	filters = {}
	if workflow_rule:
		filters["workflow_rule"] = workflow_rule

	logs = frappe.get_all(
		"CRM Workflow Execution Log",
		filters=filters,
		fields=[
			"name",
			"workflow_rule",
			"reference_doctype",
			"reference_name",
			"status",
			"executed_actions",
			"creation",
		],
		order_by="creation desc",
		limit=int(limit),
	)
	return logs
