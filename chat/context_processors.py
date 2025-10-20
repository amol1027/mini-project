from .models import Conversation


def unread_messages(request):
    """
    Context processor to add unread message count to all templates
    """
    if 'user_id' in request.session:
        from registration.models import User
        try:
            user = User.objects.get(id=request.session['user_id'])
            unread_count = Conversation.get_total_unread_count(user)
            return {'unread_message_count': unread_count}
        except User.DoesNotExist:
            pass
    
    return {'unread_message_count': 0}
