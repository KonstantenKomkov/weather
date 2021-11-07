from rest_framework import viewsets, permissions
from .serializers import WeatherSerializer, WeatherStationSerializer, WeatherStationListRetrieveSerializer
from ..models import Weather, WeatherStation
from django_filters.rest_framework import DjangoFilterBackend


class WeatherViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer


class WeatherStationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = WeatherStation.objects.all()
    serializer_class = WeatherStationSerializer
    # filter_backends = (DjangoFilterBackend, )

    action_to_serializer = {
        "list": WeatherStationListRetrieveSerializer,
        "retrieve": WeatherStationListRetrieveSerializer,
    }

    def get_serializer_class(self):
        return self.action_to_serializer.get(
            self.action,
            self.serializer_class
        )