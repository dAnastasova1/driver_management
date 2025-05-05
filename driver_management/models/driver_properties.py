from odoo import fields,models
from odoo.fields import One2many


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
    current_carrier_id = fields.Many2one("res.partner", string="Carriers")
    employment_history_ids = fields.One2many("driver.employment.history","driver_id", string="Employment History")

class EmploymentHistory(models.Model):
    _name = 'driver.employment.history'

    driver_id = fields.Many2one("driver.management", string="Drivers List")
    carrier_id = fields.Many2one("res.partner",string="Carriers")
    start_date = fields.Date()
    end_date = fields.Date()
    position_title = fields.Char(string = 'Position Title')
    notes = fields.Text(string = 'Notes')
