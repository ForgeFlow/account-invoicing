# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    can_send_to_ai = fields.Boolean(compute="_compute_can_send_to_ai")

    @api.depends("state", "move_type", "company_id")
    def _compute_can_send_to_ai(self):
        for move in self:
            move.can_send_to_ai = move._get_can_send_to_ai()

    def _get_can_send_to_ai(self):
        return self.is_purchase_document() and self.state == "draft"

    def ai_process(self):
        self.ensure_one()
        attachments = self.message_main_attachment_id
        if attachments and attachments.exists() and self.can_send_to_ai:
            self.env["account.move.ai.predict"]._update_invoice_from_attachment(
                attachments[0], self
            )

    def ai_train_process(self):
        self.ensure_one()
        attachments = self.message_main_attachment_id
        if attachments and attachments.exists() and self.can_send_to_ai:
            self.env["account.move.ai.train"].add_record_to_database(
                attachments[0], self
            )

    def get_odoo_words(self):
        # manual classiffying fields and relevant value getters
        odoo_words = {}
        model = 'account.move'
        fields_data = models.execute_kw(
            models.get_model('ir.model.fields')._name,
            'search_read',
            [[['model', '=', model]]],
            {'fields': ['name', 'ttype']}
        )
        for field_data in fields_data:
            field_name = field_data['name']
            field_type = field_data['ttype']
            if field_type in ['char', 'many2one']:
                field_value = getattr(account_move_instance, field_name)  # Assuming account_move_instance is an instance of the model
                odoo_words[field_name] = field_value
        return odoo_words
