# Copyright 2023 CreuBlanca
# Copyright 2023 ForgeFlow
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    can_send_to_ocr = fields.Boolean(compute="_compute_can_send_to_ocr")

    @api.depends("state", "type", "company_id")
    def _compute_can_send_to_ocr(self):
        for move in self:
            move.can_send_to_ocr = move._get_can_send_to_ocr()

    def _get_can_send_to_ocr(self):
        return (
            self.is_purchase_document()
            and self.state == "draft"
            and self.company_id.ocr_google_enabled != "no_send"
        )

    def ocr_process(self):
        self.ensure_one()
        attachments = self.message_main_attachment_id
        if attachments and attachments.exists() and self.can_send_to_ocr:
            self.env["account.move.google.document.ai"]._update_invoice_from_attachment(
                attachments[0], self
            )

    # The attachment decoders hooks were introduced in 14.0. They are defined
    # here, falling back to any other backport of them, so the rest of the
    # module keeps the 14.0 logic.
    def _get_create_invoice_from_attachment_decoders(self):
        res = getattr(
            super(), "_get_create_invoice_from_attachment_decoders", lambda: []
        )()
        if self.env.company.ocr_google_enabled == "send_automatically":
            res.append(
                (
                    90,
                    self.env[
                        "account.move.google.document.ai"
                    ]._create_invoice_from_attachment,
                )
            )
        return res

    def _get_update_invoice_from_attachment_decoders(self, invoice):
        res = getattr(
            super(), "_get_update_invoice_from_attachment_decoders", lambda invoice: [],
        )(invoice)
        if self.env.company.ocr_google_enabled == "send_automatically":
            res.append(
                (
                    90,
                    self.env[
                        "account.move.google.document.ai"
                    ]._update_invoice_from_attachment,
                )
            )
        return res

    def _message_post_after_hook(self, message, msg_vals):
        # Backport of the 14.0 behaviour: when posting a message, check the
        # attachments to see if they are an invoice and update the move with
        # the imported data.
        res = super()._message_post_after_hook(message, msg_vals)
        attachments = message.attachment_ids
        if (
            len(self) != 1
            or not attachments
            or self.env.context.get("no_new_invoice")
            or not self.is_invoice(include_receipts=True)
        ):
            return res
        decoders = self.env[
            "account.move"
        ]._get_update_invoice_from_attachment_decoders(self)
        if not decoders:
            return res
        odoobot = self.env.ref("base.partner_root")
        if self.state != "draft":
            self.message_post(
                body=_(
                    "The invoice is not a draft, it was not updated from the "
                    "attachment."
                ),
                message_type="comment",
                subtype="mail.mt_note",
                author_id=odoobot.id,
            )
            return res
        if self.line_ids:
            self.message_post(
                body=_(
                    "The invoice already contains lines, it was not updated from "
                    "the attachment."
                ),
                message_type="comment",
                subtype="mail.mt_note",
                author_id=odoobot.id,
            )
            return res
        for decoder in sorted(decoders, key=lambda d: d[0]):
            # Start with message_main_attachment_id, so only that one is parsed
            for attachment in attachments.sorted(
                lambda x: x != self.message_main_attachment_id
            ):
                if decoder[1](attachment, self):
                    return res
        return res
