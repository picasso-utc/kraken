from rest_framework.decorators import api_view
from core.services.payutc import PayutcClient
from rest_framework.response import Response

################################################################
#                          GESARTICLE
################################################################
@api_view(['POST'])
def login_badge(request, format=None):
    p = PayutcClient()



################################################################
#                           SELFPOS
################################################################

@api_view(['GET'])
def get_articles(request, format=None):
    p = PayutcClient()
    articles = p.get_articles()

    if(request.GET.get('sorted')):

        sorted_articles = {
            3: 	('softs', []),
            11: ('bieresPression', []),
            10: ('bieresBouteille', []),
            9: 	('snacksSucres', []),
            17: ('snacksSales', []),
            184:('glace', []),
            221:('petitDej', []),
            199:('pampryls', []),
        }

        for article in articles :

        # IDs des catégories
        # ==================
        # Softs : 3
        # Bières pression : 11
        # Bières bouteille : 10
        # Snacks sucrés : 9
        # Snacks salés : 17
        # Glacé : 184
        # Petit dej : 221
        # Pampryls : 199

            if (article["active"]) :
                bin = sorted_articles.get(article["categorie_id"])
                if bin is not None:
                    bin[1].append({
                        'name' : article["name"],
                        'price' : article["price"]
                    })

        return Response(dict(sorted_articles.values()))

    return Response(articles)