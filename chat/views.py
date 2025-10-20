from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Max, Count, Prefetch
from django.utils import timezone
from .models import Conversation, Message, NotificationPreference
from registration.models import User
from products.models import Product


def conversation_list(request):
    """
    Display all conversations for the current user
    """
    if 'user_id' not in request.session:
        return redirect('login:login')
    
    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    
    # Get all conversations where user is either buyer or seller
    conversations = Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    ).select_related('buyer', 'seller', 'product').prefetch_related(
        Prefetch('messages', queryset=Message.objects.order_by('-created_at'))
    ).annotate(
        last_message_time=Max('messages__created_at')
    ).order_by('-last_message_time')
    
    # Add context for each conversation
    conversation_data = []
    for conv in conversations:
        # Determine the other party in the conversation
        other_user = conv.seller if conv.buyer.id == user.id else conv.buyer
        last_message = conv.get_last_message()
        unread_count = conv.messages.exclude(sender=user).filter(is_read=False).count()
        
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': unread_count
        })
    
    context = {
        'conversations': conversation_data,
        'user': user
    }
    return render(request, 'chat/conversation_list.html', context)


def chat_detail(request, conversation_id):
    """
    Display a specific conversation with messaging interface
    """
    if 'user_id' not in request.session:
        return redirect('login:login')
    
    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    
    # Get conversation and verify user has access
    conversation = get_object_or_404(
        Conversation.objects.select_related('buyer', 'seller', 'product'),
        id=conversation_id
    )
    
    # Verify user is part of this conversation
    if conversation.buyer.id != user.id and conversation.seller.id != user.id:
        return redirect('chat:conversation_list')
    
    # Mark all messages from the other party as read
    Message.objects.filter(
        conversation=conversation
    ).exclude(sender=user).filter(is_read=False).update(is_read=True)
    
    # Get all messages in the conversation
    messages = conversation.messages.select_related('sender').order_by('created_at')
    # Compute last message id safely for template logic
    last_message_id = messages.last().id if messages.exists() else 0
    
    # Determine the other party
    other_user = conversation.seller if conversation.buyer.id == user.id else conversation.buyer
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'user': user,
        'other_user': other_user,
        'product': conversation.product,
        'last_message_id': last_message_id,
    }
    return render(request, 'chat/chat_detail.html', context)


def start_conversation(request, product_id):
    """
    Start a new conversation with a seller about a product
    """
    if 'user_id' not in request.session:
        return redirect('login:login')
    
    user_id = request.session['user_id']
    buyer = get_object_or_404(User, id=user_id)
    product = get_object_or_404(Product.objects.select_related('seller'), id=product_id)
    
    # Can't start conversation with yourself
    if product.seller.id == buyer.id:
        return redirect('products:product_detail', pk=product_id)
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        buyer=buyer,
        seller=product.seller,
        product=product
    )
    
    # Redirect to the chat detail page
    return redirect('chat:chat_detail', conversation_id=conversation.id)


@require_http_methods(["POST"])
def send_message(request, conversation_id):
    """
    Send a message in a conversation (AJAX endpoint)
    """
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    
    # Get conversation and verify access
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if conversation.buyer.id != user.id and conversation.seller.id != user.id:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get message content
    content = request.POST.get('content', '').strip()
    
    if not content:
        return JsonResponse({'error': 'Message cannot be empty'}, status=400)
    
    # Create the message
    message = Message.objects.create(
        conversation=conversation,
        sender=user,
        content=content
    )
    
    # Update conversation timestamp
    conversation.updated_at = timezone.now()
    conversation.save(update_fields=['updated_at'])
    
    return JsonResponse({
        'success': True,
        'message': {
            'id': message.id,
            'content': message.content,
            'sender_name': user.name or user.email,
            'created_at': message.created_at.strftime('%b %d, %Y %I:%M %p'),
            'is_current_user': True
        }
    })


@require_http_methods(["GET"])
def get_new_messages(request, conversation_id):
    """
    Get new messages since last check (AJAX endpoint for real-time updates)
    """
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    
    # Get conversation and verify access
    conversation = get_object_or_404(Conversation, id=conversation_id)
    
    if conversation.buyer.id != user.id and conversation.seller.id != user.id:
        return JsonResponse({'error': 'Access denied'}, status=403)
    
    # Get last message ID from request
    last_message_id = request.GET.get('last_message_id', 0)
    
    # Get messages newer than the last known message
    new_messages = Message.objects.filter(
        conversation=conversation,
        id__gt=last_message_id
    ).select_related('sender').order_by('created_at')
    
    # Mark messages from other user as read
    new_messages.exclude(sender=user).filter(is_read=False).update(is_read=True)
    
    # Format messages for JSON response
    messages_data = []
    for msg in new_messages:
        messages_data.append({
            'id': msg.id,
            'content': msg.content,
            'sender_id': msg.sender.id,
            'sender_name': msg.sender.name or msg.sender.email,
            'sender_initial': (msg.sender.name or msg.sender.email)[0].upper(),
            'created_at': msg.created_at.strftime('%b %d, %Y %I:%M %p'),
            'is_current_user': msg.sender.id == user.id
        })
    
    return JsonResponse({
        'success': True,
        'messages': messages_data,
        'count': len(messages_data)
    })


@require_http_methods(["GET"])
def get_unread_count(request):
    """
    Get total unread message count for current user (AJAX endpoint)
    """
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    
    # Get total unread count
    unread_count = Conversation.get_total_unread_count(user)
    
    return JsonResponse({
        'success': True,
        'unread_count': unread_count
    })


@require_http_methods(["GET", "POST"])
def notification_settings(request):
    """
    View and update notification preferences
    """
    if 'user_id' not in request.session:
        return redirect('login:login')
    
    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    
    # Get or create notification preferences
    preferences, created = NotificationPreference.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        # Update preferences
        preferences.enable_sound = request.POST.get('enable_sound') == 'on'
        preferences.enable_desktop = request.POST.get('enable_desktop') == 'on'
        preferences.enable_email = request.POST.get('enable_email') == 'on'
        preferences.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Notification preferences updated successfully'
            })
        
        return redirect('chat:notification_settings')
    
    context = {
        'user': user,
        'preferences': preferences
    }
    return render(request, 'chat/notification_settings.html', context)


@require_http_methods(["GET"])
def get_notification_preferences(request):
    """
    Get user's notification preferences (AJAX endpoint)
    """
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    user_id = request.session['user_id']
    user = get_object_or_404(User, id=user_id)
    
    preferences, created = NotificationPreference.objects.get_or_create(user=user)
    
    return JsonResponse({
        'success': True,
        'preferences': {
            'enable_sound': preferences.enable_sound,
            'enable_desktop': preferences.enable_desktop,
            'enable_email': preferences.enable_email
        }
    })
