# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from datetime import timedelta
from odoo.exceptions import UserError
from odoo import api, fields, models
from datetime import date
from odoo.exceptions import ValidationError

GLOBAL_VAR = "test"


class Real_Estate(models.Model):
    _name = "real.estate.properties"
    _description = "Real Estate properties"
    _order = "id desc"

    name = fields.Char('Plan Name', required=True, translate=True, default="Untitled Plan")
    description = fields.Text()
    postcode = fields.Char()
    available_from = fields.Date(default=lambda self: self._default_availability_date(), copy=False)
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer(default=2)
    living_area = fields.Integer()
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer()
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[('north', 'North'), ('south', 'South'), ('east', 'East'), ('west', 'West')],
        help="Type is used to separate North, South, East, and West"
    )
    title = fields.Text()
    total_area = fields.Integer(
        string="Total Area",
        compute="_compute_total_area",
        store=True
    )

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    salesperson_id = fields.Many2one('res.users', string='Salesman', default=lambda self: self.env.user)
    buyer_id = fields.Many2one('res.partner', string='Buyer')
    property_tag_ids = fields.Many2many('estate.property.tag', string='Property Tags')
    offer_ids = fields.One2many('estate.property.offer', 'property_id', string='Offers')

    best_price = fields.Float(
        string="Best Offer",
        compute="_compute_best_offer"
    )

    @api.depends('offer_ids.price')
    def _compute_best_offer(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0.0

    @api.onchange('garden')
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = 'north'
        else:
            self.garden_area = 0
            self.garden_orientation = False

    def action_cancel(self):
        if self.state == 'sold':
            raise UserError("A sold property cannot be canceled.")
        self.state = 'canceled'

    def action_sold(self):
        if self.state == 'canceled':
            raise UserError("Cancelled properties cannot be sold.")
        self.state = 'sold'

    active = fields.Boolean(
        default=True

    )

    state = fields.Selection(
        selection=[('new', 'New'), ('offer received', 'Offer received'), ('offer accepted', 'Offer accepted'),
                   ('sold', 'Sold'), ('canceled', 'Cancelled')],
        required=True,
        default='new',
        string='Status',
        copy=False
    )

    @staticmethod
    def _default_availability_date():

        return date.today() + timedelta(days=90)

    _sql_constraints = [
        ('expected_price_positive', 'CHECK(expected_price > 0)', 'The expected price must be strictly positive.'),
        ('selling_price_positive', 'CHECK(selling_price > 0)', 'The selling price must be strictly positive')
    ]

    @api.constrains('expected_price')
    def _check_expected_price(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError("The expected price must be strictly positive.")

    @api.constrains('selling_price')
    def _check_selling_price_positive(self):
        for record in self:
            if record.selling_price <= 0:
                raise ValidationError("The selling price must be strictly positive.")

    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price_percentage(self):
        for record in self:
            if record.selling_price > 0:
                if record.selling_price < 0.9 * record.expected_price:
                    raise ValidationError(
                        "The selling price cannot be lower than 90% of the expected price."
                    )

    @api.ondelete(at_uninstall=False)
    def _prevent_deletion_if_not_new_or_canceled(self):
        for record in self:
            if record.state not in ['new', 'canceled']:
                raise UserError("Only new and cancelled properties can be deleted.")


class Real_Estate_Type(models.Model):
    _name = "estate.property.type"
    _order = "sequence, name"

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    property_ids = fields.One2many("real.estate.properties", "property_type_id", string="Properties")
    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id',
        string="Offers"
    )

    offer_count = fields.Integer(
        string="Offer Count",
        compute="_compute_offer_count",
        store=True
    )

    @api.depends('offer_ids')
    def _compute_offer_count(self):
        for record in self:
            record.offer_count = len(record.offer_ids)

    _sql_constraints = [
        ('unique_property_type_name', 'UNIQUE(name)', 'The property type name must be unique.')
    ]


class Real_Estate_Tag(models.Model):
    _name = "estate.property.tag"
    _order = "name"

    name = fields.Char(required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('unique_property_tag_name', 'UNIQUE(name)', 'The property tag name must be unique.')
    ]


class Real_Estate_Offer(models.Model):
    _name = "estate.property.offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[('accepted', 'Accepted'), ('refused', 'Refused')],
        string='Status',
        copy=False
    )
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(string="Deadline", compute="_compute_date_deadline", inverse="_inverse_date_deadline",
                                store=True)

    @api.depends('create_date', 'validity')
    def _compute_date_deadline(self):
        for record in self:
            create_date = record.create_date.date() if record.create_date else date.today()
            record.date_deadline = create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date:
                record.validity = (record.date_deadline - record.create_date.date()).days
            else:
                record.validity = (record.date_deadline - date.today()).days

    def action_accept(self):
        for offer in self:
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price
            offer.status = 'accepted'

    def action_refuse(self):
        self.status = 'refused'

    @api.constrains('price')
    def _check_price(self):
        self.self = self
        for record in self.self:
            if record.price <= 0:
                raise ValidationError("The offer price must be strictly positive.")

    @api.model
    def create(self, vals):
        property_id = self.env['real.estate.properties'].browse(vals.get('property_id'))

        if property_id.offer_ids and vals.get('price') <= max(property_id.offer_ids.mapped('price')):
            raise ValidationError("The offer amount must be higher than the existing highest offer.")

        if property_id.state == 'new':
            property_id.state = 'offer received'

        return super().create(vals)

    partner_id = fields.Many2one('res.partner', string='Partner')
    property_id = fields.Many2one('real.estate.properties', string='Property')
    property_type_id = fields.Many2one(
        'estate.property.type',
        string="Property Type",
        related="property_id.property_type_id",
        store=True
    )
