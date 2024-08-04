from odoo import models, fields, api


class HospitalMedecin(models.Model):
    _name = 'hospital.medecin'
    _description = 'Médicament'

    denomination_commune_internationale = fields.Char(string='DCI')
    name = fields.Char(string='Nom')
    forme = fields.Char(string='Forme')
    dosage = fields.Char(string='Dosage')
    laboratoire = fields.Char(string='Laboratoire')
    paye_id = fields.Many2one('res.country', string='Pays')

    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    @api.depends('denomination_commune_internationale', 'name', 'forme', 'dosage')
    def _compute_display_name(self):
        for record in self:
            record.display_name = f"{record.denomination_commune_internationale} / {record.name} / {record.forme} / {record.dosage}"

    # Surcharger la méthode de recherche
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Rechercher par nom ou par denomination_commune_internationale
        custom_args = ['|', ('name', 'ilike', args[0]), ('denomination_commune_internationale', 'ilike', args[0])]
        return super(HospitalMedecin, self).search(custom_args, offset=offset, limit=limit, order=order, count=count)