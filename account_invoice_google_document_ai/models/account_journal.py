# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def create_invoice_from_attachment(self, attachment_ids=None):
        # Backport of the 14.0 behaviour: try the attachment decoders before
        # creating an empty invoice. Attachments that no decoder can handle
        # follow the standard 13.0 flow.
        attachments = self.env["ir.attachment"].browse(attachment_ids or [])
        decoders = self.env[
            "account.move"
        ]._get_create_invoice_from_attachment_decoders()
        if not attachments or not decoders:
            return super().create_invoice_from_attachment(attachment_ids=attachment_ids)
        invoices = self.env["account.move"]
        pending = self.env["ir.attachment"]
        for attachment in attachments:
            invoice = False
            for decoder in sorted(decoders, key=lambda d: d[0]):
                invoice = decoder[1](attachment)
                if invoice:
                    break
            if not invoice:
                pending |= attachment
                continue
            attachment.write({"res_model": "mail.compose.message"})
            invoice.with_context(no_new_invoice=True).message_post(
                attachment_ids=[attachment.id]
            )
            invoices |= invoice
        if pending:
            action = super().create_invoice_from_attachment(attachment_ids=pending.ids)
            invoices |= self._get_invoices_from_action(action)
        action_vals = {
            "name": _("Generated Documents"),
            "domain": [("id", "in", invoices.ids)],
            "res_model": "account.move",
            "views": [[False, "tree"], [False, "form"]],
            "type": "ir.actions.act_window",
            "context": self._context,
        }
        if len(invoices) == 1:
            action_vals.update({"res_id": invoices.id, "view_mode": "form"})
        else:
            action_vals["view_mode"] = "tree,form"
        return action_vals

    def _get_invoices_from_action(self, action):
        if action.get("res_id"):
            return self.env["account.move"].browse(action["res_id"])
        for leaf in action.get("domain", []):
            if isinstance(leaf, (list, tuple)) and leaf[:2] in (
                ("id", "in"),
                ["id", "in"],
            ):
                return self.env["account.move"].browse(leaf[2])
        return self.env["account.move"]
