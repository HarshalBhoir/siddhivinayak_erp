# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class ResUsersInherit(models.Model):
    _inherit = 'res.users'

    chatter_position = fields.Selection([("normal", "Normal"), ("sided", "Sided")],
        string="Chatter Position", default="normal" )