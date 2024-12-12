from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import BookCatalog

@receiver(post_save, sender=BookCatalog)
def book_added_or_updated(sender, instance, created, **kwargs):
    print(f"Signal triggered for book: {instance.book_title}") 
    channel_layer = get_channel_layer()
    message = {
        'type': 'send_notification',  
        'action': 'added' if created else 'updated',
        'book_title': instance.book_title,
        'message': f"A book titled '{instance.book_title}' has been added!"
    }

    async_to_sync(channel_layer.group_send)(
        'book_notifications',  
        message
    )

@receiver(post_delete, sender=BookCatalog)
def book_deleted(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    message = {
        'type': 'send_notification',
        'action': 'deleted',
        'book_title': instance.book_title
    }
    async_to_sync(channel_layer.group_send)(
        'book_notifications',
        message
    )
