from rest_framework import serializers
from main.models import Weather, WeatherStation, Country, Place


class CountrySerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = '__all__'


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = '__all__'


class WeatherSerializer(serializers.ModelSerializer):

    class Meta:
        model = Weather
        fields = '__all__'


class WeatherStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherStation
        fields = '__all__'

class PlaceFullSerializer(serializers.ModelSerializer):

    country = CountrySerializer()

    class Meta:
        model = Place
        fields = '__all__'


class WeatherStationListRetrieveSerializer(serializers.ModelSerializer):
    
    place = PlaceFullSerializer()

    class Meta:
        model = WeatherStation
        fields = ('id','place','number','latitude','longitude','rp5_link','last_date','data_type',)
