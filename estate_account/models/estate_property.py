import logging
from odoo import models, fields

_logger = logging.getLogger(__name__)

class EstateProperty(models.Model):
    _inherit = "real.estate.properties"

    def action_sold(self):
        _logger.info("=== action_sold in estate_account is being executed ===")

        selling_price = self.selling_price
        admin_fee = 100.00
        commission = selling_price * 0.06

        invoice_vals = {
            'partner_id': self.buyer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [
                (0, 0, {
                    'name': 'Commission Fee (6%)',
                    'quantity': 1,
                    'price_unit': commission,
                }),
                (0, 0, {
                    'name': 'Administrative Fee',
                    'quantity': 1,
                    'price_unit': admin_fee,
                }),
            ],
        }

        invoice = self.env['account.move'].create(invoice_vals)

        _logger.info(f"=== Invoice Created: {invoice.id} ===")

        return super().action_sold()
