from rest_framework import viewsets

from app.middleware.dispatcher import Dispatcher
from app.middleware.messages import Messages
from app.models.models import Sensor
from app.serializers import SensorSerializer


# Create your views here.
class SensorView(viewsets.ModelViewSet):
    serializer_class = SensorSerializer
    queryset = Sensor.objects.all()

    # def create(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_create(serializer)
    #     headers = self.get_success_headers(serializer.data)
    #     token = create_token(serializer.data)
    #     return Response(data=token, status=status.HTTP_201_CREATED, headers=headers)

    # def list(self, request):
    #     pass

    # def create(self, request):
    #     pass

    # def retrieve(self, request, pk=None):
    #     pass

    # def update(self, request, pk=None, **kwargs):
    #     print("update")

    # def partial_update(self, request, pk=None):
    #     pass


    # def destroy(self, request, *args, **kwargs):
    #     sensor_id = self.get_object().id
    #     Dispatcher.send_msg(Messages.SENSOR_REMOVED_FROM_FRONT, {"id": sensor_id})
    #     return super(SensorView, self).destroy(request, *args, **kwargs)
