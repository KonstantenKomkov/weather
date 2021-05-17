from django.contrib import admin
from .models import *


admin.site.register(Country)
admin.site.register(City)
admin.site.register(WeatherStation)
admin.site.register(WindDirection)
admin.site.register(Cloudiness)
admin.site.register(CloudinessCl)
admin.site.register(Weather)
