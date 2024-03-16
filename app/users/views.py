from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from django.contrib.auth import get_user_model
from .serializers import UserSerializer

from django.conf import settings

from app.users.models import TelegramUser

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from .models import Notification
from .tasks import send_notifications_task

User = get_user_model()


class UserViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = "username"

    def get_queryset(self, *args, **kwargs):
        # assert isinstance(self.request.user.id, int)
        return self.queryset.filter(id=self.request.user.id)

    @action(detail=False)
    def me(self, request):
        serializer = UserSerializer(request.user, context={"request": request})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


def send_telegram(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)
    media = []
    cache_path = settings.MEDIA_ROOT + "/"

    for i in notification.notificationshots_set.all():
        compressed_image = i.image_compress.url
        compressed_image_path = cache_path + compressed_image[len(settings.MEDIA_URL):]
        media.append(compressed_image_path)

    notification.status = notification.NotificationStatus.PROCEED
    notification.save()
    chunk_size = 10
    offset = 0
    all_chats_count = TelegramUser.objects.filter(is_active=True).count()

    first_task = None

    while True:
        limit = offset + chunk_size
        is_last = False
        if all_chats_count - limit <= chunk_size:
            is_last = True
        task = send_notifications_task.signature(
            (notification_id, notification.description, media, offset, chunk_size, is_last),
            immutable=True)

        if first_task:
            first_task |= task
        else:
            first_task = task

        offset += chunk_size
        if is_last is True:
            break

    first_task.apply_async()

    return redirect(reverse('admin:users_notification_changelist'))
