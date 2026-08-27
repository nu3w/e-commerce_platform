from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        
        # Users can only see their own Notifications
        return Notification.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
        
    def create(self, request, *args, **kwargs):
        
        # Notifications are created by the system, not mannually by users.
        return Response(
            {
                "detail": "Notifications are created automatically by the system."
            },
            status=status.HTTP_403_FORBIDDEN
        )
        
    def update(self, request, *args, **kwargs):
        notification = self.get_object()
        
        # Users can only update their own notifications
        if notification.user != request.user:
            return Response(
                {
                    "detail": "You can only modify your own notifications."
                },
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Only allow changing read status
        if "is_read" not in request.data:
            return Response(
                {
                    "detail": "Only is_read can be updated."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        notification.is_read = request.data["is_read"]
        notification.save(update_fields=["is_read"])
        
        return Response(
            self.get_serializer(notification).data
        )
        
    def partial_update(self, request, *args, **kwargs):
        notification = self.get_object()
        
        # Only the owner can modify the notification
        if notification.user != request.user:
            return Response(
                {
                    "detail": "You can only modify your own notifications."
                },
                status=status.HTTP_403_FORBIDDEN
            )
            
        # Only allow changing read status
        if "is_read" not in request.data:
            return Response(
                {
                    "detail": "Only is_read can be updated."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
            
        notification.is_read = request.data["is_read"]
        notification.save(update_fields=["is_read"])
        
        return Response(
            self.get_serializer(notification).data
        )
        
    def destroy(self, request, *args, **kwargs):
        
        # User can delete their own notifications
        notification = self.get_object()
        notification.delete()
        
        return Response(
            {
                "detail": "Notification deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )