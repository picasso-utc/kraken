# coding: utf8

from treso import models as treso_models

def generate_checks_xls(worksheet):
    qs = list(treso_models.Cheque.objects.all().order_by('num').prefetch_related('facturerecue'))
    for n, val in enumerate(["Référence", "Destinataire", "Valeur", "Etat", "Numéro de facture",
                         "Destinataire de la facture"]):
        worksheet.write(0, n, val)
    for num, cheque in enumerate(qs):
        for n, val in enumerate([cheque.num, cheque.destinataire, cheque.valeur, cheque.get_state_display()]):
            worksheet.write(num+1, n, val)
        if cheque.facturerecue:
            worksheet.write(num+1, 4, cheque.facturerecue_id)
            worksheet.write(num+1, 5, cheque.facturerecue.nom_entreprise)
        else:
            worksheet.write(num+1, 4, "--")
            worksheet.write(num+1, 5, "--")
    return worksheet

def generate_receipts_xls(worksheet):
    qs = list(treso_models.FactureRecue.objects.all().order_by('id').prefetch_related('perm')
              .prefetch_related('categorie'))
    for n, val in enumerate(["Référence", "Entreprise", "Date", "Date de paiement", "Prix TTC", "TVA", "Etat",
                             "Personne à rembourser", "Date de remboursement", "Nom de la perm", "Date de la perm",
                             "Période de la perm", "Responsable de la perm"]):
        worksheet.write(0, n, val)
    for num, facture in enumerate(qs):
        for n, val in enumerate([facture.categorie.code + str(facture.id) if facture.categorie else facture.id,
                                 facture.nom_entreprise, unicode(facture.date or "--"),
                                 unicode(facture.date_paiement or "--"), facture.prix,
                                 facture.get_total_taxes(), facture.get_etat_display(),
                                 facture.personne_a_rembourser or "", facture.date_remboursement or ""]):
            worksheet.write(num+1, n, val)
        if facture.perm:
            worksheet.write(num+1, 9, facture.perm.nom)
            worksheet.write(num + 1, 10, unicode(facture.perm.date))
            worksheet.write(num + 1, 11, facture.perm.get_periode_display())
            worksheet.write(num + 1, 12, (facture.perm.nom_resp or "") + " - " + (facture.perm.mail_resp or "Pas d'email"))
        else:
            for i in range(9, 13):
                worksheet.write(num+1, i, "--")
    return worksheet
