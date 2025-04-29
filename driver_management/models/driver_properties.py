from odoo import fields,models

class Driver(models.Model):
    _name = 'driver.management'

    name = fields.Char(string = 'Name')
    license_number = fields.Char(string = 'License Number')
    license_class = fields.Selection(
        string = 'License Class',
        selection=[('a', 'A'), ('b', 'B'), ('c', 'C')]
    )
    phone = fields.Char(string = 'Phone')
    email = fields.Char(string = 'Email')
    current_status = fields.Selection(
        string = 'Current Status',
        selection=[('active', 'Active'), ('inactive', 'Inactive'), ('suspended', 'Suspended')]
    )

