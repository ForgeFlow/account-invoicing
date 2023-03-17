from odoo import fields, models


class AccountMoveAiTag(models.Model):
    _name = "account.move.ai.tag"
    _description = "DB of training data"

    name = fields.Char(string="Tag")
    pattern_ids = fields.One2many("account.move.ai.tag", "tag_id")

class AccountMoveAiPattern(models.Model):
    _name = "account.move.ai.pattern"
    _description = "account move AI Patterns"

    name = fields.Char()
    tag_id = fields.Many2one("account.move.ai.tag")
