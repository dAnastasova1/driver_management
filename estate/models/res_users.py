from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    property_ids = fields.One2many(
        'real.estate.properties',
        'salesperson_id',
        string="Properties",
        domain=[('state', '=', 'available')]
    )
