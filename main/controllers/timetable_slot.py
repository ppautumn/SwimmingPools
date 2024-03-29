from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from main.serializers.timetable_slot import TimetableSlotSerializer
from main.models.timetable_slot import TimetableSlot as TimetableSlotModel
from main.services import get_count_of_available_tracks_by_datetime, get_max_capacity_of_tracks


class TimetableSlot(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, slot_id):
        """
        выдать подробности по слоту (здесь будут все related сущности)
        """
        slot_query = TimetableSlotModel.objects.select_related('user', 'track')
        slot = get_object_or_404(slot_query, pk=slot_id)
        serializer = TimetableSlotSerializer(slot)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, slot_id):
        """
        удалить слот по его id
        """
        try:
            slot = TimetableSlotModel.objects.get(id=slot_id, user_id=request.user.id)
            slot.delete()
            return Response(data="Удалено", status=status.HTTP_204_NO_CONTENT)
        except:
            return Response(data='У данного юзера нет такого слота', status=status.HTTP_400_BAD_REQUEST)

class SlotStatusDetail(APIView):
    def get_object(self, pk):
        try:
            return TimetableSlotModel.objects.get(id=pk)
        except TimetableSlotModel.DoesNotExist:
            raise Http404

    def post(self, request, pk):
        slot = self.get_object(pk)
        slot.status = 'paid'
        slot.save()
        serializer = TimetableSlotSerializer(slot)
        return Response(data=serializer.data, status=status.HTTP_200_OK)



class UpcomingTimetableSlot(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Получить предстоящие слоты юзера
        """
        upcoming_slot = request.user.get_upcoming_slot()
        if upcoming_slot:
            serializer = TimetableSlotSerializer(upcoming_slot)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={'message': 'Upcoming slots not found'}, status=status.HTTP_204_NO_CONTENT)


class TracksSchedule(APIView):
    permission_classes = []

    def get(self, request):
        """
        Возвращает слоты за определенный промежуток времени, берущийся из параметров запроса
        """
        start, end = request.GET.get('start'), request.GET.get('end')
        return Response(data={'available_tracks': get_count_of_available_tracks_by_datetime(start, end)},
                        status=status.HTTP_200_OK)


class TrackAvailable(APIView):
    def get(self, request):
        data = request.data
        res = get_max_capacity_of_tracks(data['date'], data['time_slot'])
        return Response(data={'max_users': res}, status=status.HTTP_200_OK)
