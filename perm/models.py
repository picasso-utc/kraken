from django.db import models
from core import models as core_models
from core.settings import PAYUTC_ARTICLES_CATEGORY
from django.utils import timezone
from core.services.current_semester import get_current_semester



class Perm(models.Model):

    nom = models.CharField(max_length=255)
    asso = models.BooleanField(default=True)  # true if asso
    semestre = models.ForeignKey(core_models.Semestre, on_delete=models.SET_NULL, null=True, default=get_current_semester)
    nom_resp = models.CharField(null=True, default=None, max_length=255)
    mail_resp = models.CharField(null=True, default=None, max_length=255)
    nom_resp_2 = models.CharField(null=True, default=None, max_length=255)
    mail_resp_2 = models.CharField(null=True, default=None, max_length=255)
    mail_asso = models.CharField(null=True, default=None, max_length=255, blank=True)

    def __str__(self):
        return f"{self.nom}"

    
class RequestedPerm(models.Model):

    nom = models.CharField(max_length=255)
    asso = models.BooleanField(default=True)  # true if asso
    mail_asso = models.CharField(null=True, default=None, max_length=255, blank=True)
    nom_resp = models.CharField(null=True, default=None, max_length=255)
    mail_resp = models.CharField(null=True, default=None, max_length=255)
    nom_resp_2 = models.CharField(null=True, default=None, max_length=255)
    mail_resp_2 = models.CharField(null=True, default=None, max_length=255)
    theme = models.CharField(null=True, default=None, max_length=255)
    description = models.TextField(null=True, default=None)
    membres = models.CharField(null=True, default=None, max_length=255)
    periode = models.TextField(null=True, default=None)
    added = models.BooleanField(default=False)
    founder_login = models.CharField(max_length=8, default=None)
    ambiance = models.IntegerField(default=0)
    semestre = models.ForeignKey(core_models.Semestre, on_delete=models.SET_NULL, null=True, default=get_current_semester)


class Creneau(models.Model):

    PERM_TRAITEE = 'T'
    PERM_NON_TRAITEE = 'N'

    PERM_STATE_VALUES = (
        (PERM_TRAITEE, 'Traitée'),
        (PERM_NON_TRAITEE, 'Non traitée'),
    )

    CRENEAU_CHOICES = (
        ('M', 'Matin'),
        ('D', 'Déjeuner'),
        ('S', 'Soir'),
    )

    perm = models.ForeignKey(Perm, related_name="creneaux", on_delete=models.CASCADE)
    date = models.DateField()
    creneau = models.CharField(max_length = 2, choices = CRENEAU_CHOICES)
    state = models.CharField(choices=PERM_STATE_VALUES, max_length=1, default='N')
    montantTTCMaxAutorise = models.FloatField(null=True, default=None)

    def __str__(self):
        return f"{self.date}:{self.creneau}:{self.id}"


    def get_montant_deco_max(self):
        if self.montantTTCMaxAutorise:
            return self.montantTTCMaxAutorise
        if self.date.weekday() in [3, 4]:
            return 30
        else:
            return 20

    def get_convention_information(self):
        period = "Matin"
        if self.creneau == "D":
            period = "Midi"
        elif self.creneau == "S":
            period = "Soir"

        date_info = str(self.date).split("-")
        date = date_info[2] + "/" + date_info[1] + "/" + date_info[0]

        articles = self.article_set.all()
        creneau_articles = list()

        for article in articles:
            creneau_articles.append({
                'nom': article.nom, 
                'stock': article.stock,
                'prixTTC': article.prix,
                'prixHT': article.get_price_without_taxes(),
                'TVA': article.tva   
            })
        return {
            'creneau': self,
            'period': period,
            'date': date,
            'articles': articles,
            'creneau_articles': creneau_articles,
        }

    def get_justificatif_information(self):
        articles = self.article_set.all()
        perm_articles = list()
        tva = set()
        for article in articles:
            article_info = {
                'nom': article.nom, 
                'prix': article.prix,
                'ventes': article.ventes, 
                'tva': article.tva
            }
            tva.add(article.tva)
            article_info['total'] = article_info['prix'] * article_info['ventes']
            perm_articles.append(article_info)
        tva_amounts = list()
        total_ht = round(sum([article.get_price_without_taxes()*article.ventes for article in articles]), 2)
        for tva_type in tva:
            tva_amounts.append({
                'tva': tva_type,
                'amount': round(sum([article.get_total_taxes() * article.ventes for article in articles if article.tva == tva_type]), 2)})
        total_ttc = round(sum([article.prix*article.ventes for article in articles]), 2)
        return {
            'perm_articles': perm_articles,
            'total_ht': total_ht,
            'total_ttc': total_ttc,
            'tva_amounts': tva_amounts,
        }


class Article(core_models.PricedModel):
    id_payutc = models.IntegerField(null=True, default=None)
    stock = models.IntegerField(default=0)
    ventes = models.IntegerField(default=0)
    ventes_last_update = models.DateTimeField(null=True, default=None)
    nom = models.CharField(max_length=255)
    creneau = models.ForeignKey(Creneau, on_delete=models.CASCADE)

    def create_payutc_article(self):
        if self.id_payutc:
            return self.id_payutc
        from core.services.payutc import PayutcClient
        p = PayutcClient()
        p.login_admin()
        data = {
            'active': True,
            'alcool': False,
            'cotisant': True,
            'name': self.nom + ' - ' + self.creneau.perm.nom,
            'parent': PAYUTC_ARTICLES_CATEGORY,
            'prix': round(self.prix*100),
            'stock': self.stock,
            'tva': self.tva,
            'variable_price': False
        }
        res = p.set_product(data)
        self.id_payutc = int(res['success'])
        self.ventes_last_update = timezone.now()
        self.save()
        Menu.objects.create(article=self)
        return self.id_payutc

    def update_sales(self):
        from core.services.payutc import PayutcClient
        p = PayutcClient()
        p.login_admin()
        rep = p.get_nb_sell(obj_id=self.id_payutc)
        self.ventes = rep
        self.ventes_last_update = timezone.now()
        self.save()
        return self.ventes

    def set_article_disabled(self):
        from core.services.payutc import PayutcClient
        p = PayutcClient()
        p.login_admin()
        rep = p.patch_api_rest('resources', 'products', self.id_payutc, active=False)
        return rep


class Menu(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="menu")
    is_closed = models.BooleanField(default=False)
    last_update = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self):
        return str(self.id)

    def update_orders(self):
        from core.services.payutc import PayutcClient
        p = PayutcClient()
        p.login_admin()
        rep = p.get_sales(product_id__in=[self.article.id_payutc])
        for line in rep['transactions']:
            if line['status'] == 'V':
                orderline, created = OrderLine.objects.get_or_create(id_transaction_payutc=line['id'], defaults={"menu": self})
                if created:
                    for payments in line['rows']:
                        orderline.id_rows_payutc = payments['id']
                        for menu in payments['payments']:
                            orderline.id_buyer = menu['buyer']['id']
                            orderline.quantity = menu['quantity']
                            orderline.buyer_first_name = menu['buyer']['first_name']
                            orderline.buyer_name = menu['buyer']['last_name']
                            orderline.save()
            for line1 in line['rows']:
                if line1['cancels']:
                    o = OrderLine.objects.filter(id_rows_payutc=line1['cancels']).first()
                    if o:
                        o.is_canceled = True
                        o.save()
        buyers_list = list()
        orders = OrderLine.objects.filter(menu_id=self.id, quantity__gt=0, is_canceled=False).order_by('served', 'is_staff', 'id_transaction_payutc')
        for order in orders:
            buyers_list.append({'last_name': order.buyer_name, 'first_name': order.buyer_first_name, 'quantity': order.quantity, 'served': order.served, 'is_staff': order.is_staff, 'id_transaction': order.id_transaction_payutc})
        return buyers_list


class OrderLine(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    buyer_name = models.CharField(max_length=255)
    buyer_first_name = models.CharField(max_length=255)
    quantity = models.IntegerField(default=0)
    served = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    id_transaction_payutc = models.IntegerField(default=0, unique=True)
    id_rows_payutc = models.IntegerField(default=0)
    id_buyer = models.IntegerField(default=0)
    is_canceled = models.BooleanField(default=False)

    def __str__(self):
        return '#' + str(self.id_rows_payutc) + ' - ' + self.buyer_name


class Signature(models.Model):
    nom = models.CharField(blank=True, max_length=100)
    creneau = models.ForeignKey(Creneau, on_delete=models.CASCADE, default=None)
    date = models.DateField(blank=True)
    login = models.CharField(blank=True, max_length=100)

    def _str_(self):
        return self.login


class Astreinte(models.Model):
    ASTREINTE_TYPE_CHOICES = (
        ('M1', 'Matin 1'),
        ('M2', 'Matin 2'),
        ('D1', 'Déjeuner 1'),
        ('D2', 'Déjeuner 2'),
        ('S', 'Soir'),
    )
    member = models.ForeignKey(core_models.Member, on_delete=models.CASCADE)
    creneau = models.ForeignKey(Creneau, related_name="astreintes", on_delete=models.CASCADE)
    astreinte_type = models.CharField(choices=ASTREINTE_TYPE_CHOICES, max_length=2)
    note_deco = models.IntegerField(default=0)
    note_orga = models.IntegerField(default=0)
    note_anim = models.IntegerField(default=0)
    note_menu = models.IntegerField(default=0)
    commentaire = models.CharField(null=True, default=None, blank=True, max_length=255)

    def __str__(self):
        return f"{self.astreinte_type} - {self.member.userright.name} - {self.id}"


class PermHalloween(models.Model):

    article_id = models.IntegerField(default=0)
    login = models.CharField(null=True, default=None, max_length=10)


class Etudiant(models.Model):

    login = models.CharField(null=True, default=None, max_length=10)
    mail = models.CharField(null=True, default=None, max_length=255)
    nouvo = models.BooleanField(default=False)
    nb_resa = models.IntegerField(default=0)
    nb_resa_conf = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.login}"


class Groupe(models.Model):

    goupe_id = models.CharField(null=True, default=None, max_length=10)
    login_etu = models.ManyToManyField(Etudiant)

    def __str__(self):
        return f"{self.goupe_id}"


class Reservation(models.Model):

    TABLE_TYPE_CHOICE = (
        ('EXT', 'Table exterieur'),
        ('INT', 'Table interieur'),
    )
    table_type = models.CharField(choices=TABLE_TYPE_CHOICE, max_length=3)
    date_resa = models.CharField(null=True, default=None, max_length=10)
    date_venu = models.CharField(null=True, default=None, max_length=10)
    groupe = models.ForeignKey(Groupe, on_delete=models.CASCADE)
