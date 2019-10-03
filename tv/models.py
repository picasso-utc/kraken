from django.db import models

class WebTV(models.Model):
    name = models.CharField(max_length=30)
    location = models.CharField(max_length=30)

    def __str__(self):
        return self.name

    def getUrl(self):
        if TVConfiguration.objects.filter(tv=self).count() > 0:
            tv_configuration = TVConfiguration.objects.filter(tv=self).last()
            if tv_configuration.url:
                url = tv_configuration.url
            else:
                url = None
            if tv_configuration.photo:
                image = tv_configuration.photo
            else:
                image = None
        else:
            url = None
        return {'name': self.name, 'location': self.location, 'url': url, 'image': image}


class TVConfiguration(models.Model):
    tv = models.ForeignKey(WebTV, on_delete=models.CASCADE)
    url = models.CharField(max_length=500, null=True, blank=True, default=None)

    def __str__(self):
        return self.tv.name

class TVMedia(models.Model):
	name = models.CharField(max_length=50)
	media = models.FileField(upload_to="tv", null=True, blank=True, default=None)