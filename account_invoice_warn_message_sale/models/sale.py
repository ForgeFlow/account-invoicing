# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_view_invoice(self, invoices=False):
        """Override to modify the action so if there is a warning message
        it is shown in the invoice form view."""
        action = super().action_view_invoice(invoices=invoices)
        if not action:
            return action
        # If the invoice has a warning message for the created from sale, show it
        if self.invoice_ids and self.invoice_ids[0].invoice_warn_msg:
            action["context"] = {
                "default_warning_message": self.invoice_ids[0].invoice_warn_msg,
            }
        return action
