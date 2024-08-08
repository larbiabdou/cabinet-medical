from odoo import api, fields, models


class MedicalCare(models.Model):
    _name = 'medical.care'
    _description = 'Soins médicaux'

    outpatient_id = fields.Many2one(
        comodel_name='hospital.outpatient',
        string='outpatient_id',
        required=False)
    type_id = fields.Many2one(
        comodel_name='visit.type',
        string='Type_id',
        required=False)
    product_id = fields.Many2one(
        comodel_name='product.product',
        string='Article',
        required=False)

    quantity = fields.Float(
        string='Quantité',
        required=False)

    uom_id = fields.Many2one(
        comodel_name='uom.uom',
        string='Udm',
        domain="[('category_id', '=', product_uom_category_id)]",
        required=False)

    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')

