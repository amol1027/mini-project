import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from registration.models import User
from .models import ChatSession, ChatMessage
from .assistant import AIAssistant


def get_or_create_session(request):
    """Get or create a chat session for the current user/visitor"""
    user_id = request.session.get('user_id')
    user = None
    
    if user_id:
        try:
            user = User.objects.get(id=user_id)
            # Get or create session for authenticated user
            session, created = ChatSession.objects.get_or_create(
                user=user,
                is_active=True,
                defaults={'session_key': request.session.session_key}
            )
        except User.DoesNotExist:
            session = None
    else:
        # For anonymous users, use session key
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
            
        session, created = ChatSession.objects.get_or_create(
            session_key=session_key,
            user=None,
            is_active=True
        )
    
    return session, user


def chat_view(request):
    """Render the chat interface page"""
    session, user = get_or_create_session(request)
    
    # Get chat history
    messages = []
    if session:
        messages = session.messages.all().order_by('created_at')[:50]
    
    context = {
        'messages': messages,
        'user': user,
    }
    return render(request, 'ai_assistant/chat.html', context)


@require_http_methods(["POST"])
def send_message(request):
    """API endpoint to send a message and get AI response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message cannot be empty'
            }, status=400)
        
        # Get or create session
        session, user = get_or_create_session(request)
        
        if not session:
            return JsonResponse({
                'success': False,
                'error': 'Could not create chat session'
            }, status=500)
        
        # Save user message
        user_msg = ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        # Get conversation history for context
        history = session.messages.all().order_by('created_at')[:20]
        conversation_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in history
        ]
        
        # Get AI response with conversation history
        assistant = AIAssistant(user=user)
        response_data = assistant.get_response(user_message, conversation_history)
        
        # Save assistant response
        assistant_msg = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=response_data['response'],
            metadata={
                'intent': response_data.get('intent'),
                'confidence': response_data.get('confidence'),
                'source': response_data.get('source'),
            }
        )
        
        # Update session
        session.save()  # Updates the updated_at timestamp
        
        return JsonResponse({
            'success': True,
            'response': response_data['response'],
            'message_id': assistant_msg.id,
            'intent': response_data.get('intent'),
            'timestamp': assistant_msg.created_at.isoformat(),
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_chat_history(request):
    """Get chat history for the current session"""
    session, user = get_or_create_session(request)
    
    if not session:
        return JsonResponse({
            'success': True,
            'messages': []
        })
    
    messages = session.messages.all().order_by('created_at')[:100]
    
    message_list = [{
        'id': msg.id,
        'role': msg.role,
        'content': msg.content,
        'timestamp': msg.created_at.isoformat(),
    } for msg in messages]
    
    return JsonResponse({
        'success': True,
        'messages': message_list
    })


@require_http_methods(["POST"])
def clear_chat_history(request):
    """Clear chat history for the current session"""
    session, user = get_or_create_session(request)
    
    if session:
        session.messages.all().delete()
        
    return JsonResponse({
        'success': True,
        'message': 'Chat history cleared'
    })


@require_http_methods(["GET"])
def get_suggestions(request):
    """Get suggested questions"""
    session, user = get_or_create_session(request)
    
    assistant = AIAssistant(user=user)
    suggestions = assistant.get_suggestions()
    
    return JsonResponse({
        'success': True,
        'suggestions': suggestions
    })
