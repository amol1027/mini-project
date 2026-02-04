from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Max, Count, Prefetch
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.cache import cache
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
    # Only show conversations that have at least one message
    conversations = Conversation.objects.filter(
        Q(buyer=user) | Q(seller=user)
    ).select_related('buyer', 'seller', 'product').prefetch_related(
        Prefetch('messages', queryset=Message.objects.order_by('-created_at'))
    ).annotate(
        last_message_time=Max('messages__created_at'),
        message_count=Count('messages'),
        unread_count=Count(
            'messages',
            filter=Q(messages__is_read=False) & ~Q(messages__sender=user),
            distinct=True,
        ),
    ).filter(message_count__gt=0).order_by('-last_message_time')
    
    # Add context for each conversation
    conversation_data = []
    for conv in conversations:
        # Determine the other party in the conversation
        other_user = conv.seller if conv.buyer.id == user.id else conv.buyer
        last_message = conv.get_last_message()
        
        conversation_data.append({
            'conversation': conv,
            'other_user': other_user,
            'last_message': last_message,
            'unread_count': conv.unread_count
        })
    
    # Pagination - 12 conversations per page
    paginator = Paginator(conversation_data, 12)
    page = request.GET.get('page')
    
    try:
        conversations_page = paginator.page(page)
    except PageNotAnInteger:
        conversations_page = paginator.page(1)
    except EmptyPage:
        conversations_page = paginator.page(paginator.num_pages)
    
    context = {
        'conversations': conversations_page,
        'user': user,
        'paginator': paginator,
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
    updated_count = Message.objects.filter(
        conversation=conversation
    ).exclude(sender=user).filter(is_read=False).update(is_read=True)
    
    # Invalidate cache for current user's unread count if messages were marked as read
    if updated_count > 0:
        cache_key = f'unread_message_count_{user.id}'
        cache.delete(cache_key)
    
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
        return redirect('products:product_detail', product_id=product_id)
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        buyer=buyer,
        seller=product.seller,
        product=product
    )
    
    # Redirect to the chat detail page
    return redirect('chat:chat_detail', conversation_id=conversation.id)


def start_conversation_with_user(request, product_id, other_user_id):
    """
    Start a conversation with a specific user about a product.
    This is useful for borrow/lend scenarios where the lender needs to chat with the borrower.
    """
    if 'user_id' not in request.session:
        return redirect('login:login')
    
    user_id = request.session['user_id']
    current_user = get_object_or_404(User, id=user_id)
    other_user = get_object_or_404(User, id=other_user_id)
    product = get_object_or_404(Product.objects.select_related('seller'), id=product_id)
    
    # Can't start conversation with yourself
    if current_user.id == other_user.id:
        return redirect('products:product_detail', product_id=product_id)
    
    # Determine who is buyer and who is seller based on product ownership
    # The product owner is always the seller
    if product.seller.id == current_user.id:
        # Current user is the product owner (seller)
        buyer = other_user
        seller = current_user
    elif product.seller.id == other_user.id:
        # Other user is the product owner (seller)
        buyer = current_user
        seller = other_user
    else:
        # Neither is the product owner, make current user the buyer
        buyer = current_user
        seller = other_user
    
    # Get or create conversation
    conversation, created = Conversation.objects.get_or_create(
        buyer=buyer,
        seller=seller,
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
    
    # Invalidate cache for the recipient's unread count
    recipient = conversation.seller if conversation.buyer.id == user.id else conversation.buyer
    cache_key = f'unread_message_count_{recipient.id}'
    cache.delete(cache_key)
    
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
    updated_count = new_messages.exclude(sender=user).filter(is_read=False).update(is_read=True)
    
    # Invalidate cache for current user's unread count if messages were marked as read
    if updated_count > 0:
        cache_key = f'unread_message_count_{user.id}'
        cache.delete(cache_key)
    
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
    Uses Django's cache framework to reduce database queries
    """
    if 'user_id' not in request.session:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    
    user_id = request.session['user_id']
    
    # Generate cache key for this user's unread message count
    cache_key = f'unread_message_count_{user_id}'
    
    # Try to get the count from cache first
    unread_count = cache.get(cache_key)
    
    if unread_count is None:
        # Cache miss - query the database
        user = get_object_or_404(User, id=user_id)
        unread_count = Conversation.get_total_unread_count(user)
        
        # Store in cache for 30 seconds (for faster updates)
        cache.set(cache_key, unread_count, 30)
    
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
        
        return redirect('products:product_list')
    
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
