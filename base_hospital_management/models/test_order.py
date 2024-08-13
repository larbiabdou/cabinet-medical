from odoo import api, fields, models


class laboratoryTest(models.Model):
    _name = 'laboratory.test'
    _description = 'laboratory Test'

    name = fields.Char(string="Nom")

    parent_id = fields.Many2one(
        comodel_name='laboratory.test',
        string='Parent_id',
        required=False)

    sub_test_ids = fields.One2many(
        comodel_name='laboratory.test',
        inverse_name='parent_id',
        string='Sous-tests',
        required=False)


class LaboratoryTestGroup(models.Model):
    _name = 'laboratory.test.group'
    _description = 'Laboratory Test Group'

    name = fields.Char(string="Nom")

    sub_tests = fields.Many2many(
        comodel_name='laboratory.test',
        string='Sous-tests',
        required=False)



