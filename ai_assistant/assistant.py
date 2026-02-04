"""
AI Assistant Logic for Student Resource Exchange
Supports OpenAI (ChatGPT) and Google Gemini APIs
"""

import json
import requests
from django.conf import settings


class AIAssistant:
    """
    AI Assistant that uses real AI APIs (OpenAI or Google Gemini)
    """
    
    def __init__(self, user=None):
        self.user = user
        self.provider = getattr(settings, 'AI_PROVIDER', 'gemini')
        self.base_system_prompt = getattr(settings, 'AI_SYSTEM_PROMPT', self._get_default_system_prompt())
        # Dynamic system prompt includes product information
        self.system_prompt = self._build_system_prompt_with_products()
        
    def _get_default_system_prompt(self):
        return """You are a helpful AI assistant for Student Resource Exchange (SRE), 
        a platform where students can buy, sell, and lend educational resources. 
        Be helpful, friendly, and concise."""
    
    def _get_products_info(self):
        """Fetch current products from database"""
        try:
            from products.models import Product
            
            # Get available products
            products = Product.objects.filter(is_available=True).select_related('seller')[:50]
            
            if not products:
                return "\n\n📦 **Currently Listed Products**: No products are currently available."
            
            # Build product listing
            product_info = "\n\n📦 **CURRENTLY LISTED PRODUCTS ON SRE**:\n"
            product_info += "=" * 50 + "\n"
            
            # Group by category
            categories = {}
            for product in products:
                cat = product.get_category_display()
                if cat not in categories:
                    categories[cat] = []
                categories[cat].append(product)
            
            for category, items in categories.items():
                product_info += f"\n📂 **{category}** ({len(items)} items):\n"
                for p in items:
                    # Listing type
                    if p.listing_type == 'sell':
                        type_badge = "🏷️ For Sale"
                        price_info = f"₹{p.price}" if p.price else "Price not set"
                    elif p.listing_type == 'lend':
                        type_badge = "🤝 For Lending"
                        price_info = f"₹{p.borrow_price_per_day}/day" if p.borrow_price_per_day else "Free"
                    else:
                        type_badge = "🔄 Sale or Lend"
                        price_info = f"Buy: ₹{p.price}" if p.price else ""
                        if p.borrow_price_per_day:
                            price_info += f" | Rent: ₹{p.borrow_price_per_day}/day"
                    
                    # Condition
                    condition = p.get_condition_display()
                    
                    # Seller location
                    seller_location = ""
                    if hasattr(p.seller, 'city') and p.seller.city:
                        seller_location = f" | 📍 {p.seller.city}"
                    
                    product_info += f"  • **{p.title}** [{type_badge}]\n"
                    product_info += f"    - {price_info} | Condition: {condition}{seller_location}\n"
                    if p.description:
                        # Truncate description
                        desc = p.description[:100] + "..." if len(p.description) > 100 else p.description
                        product_info += f"    - {desc}\n"
            
            product_info += "\n" + "=" * 50
            product_info += "\nTotal Products Available: " + str(len(products))
            
            return product_info
            
        except Exception as e:
            print(f"Error fetching products: {e}")
            return "\n\n📦 **Products**: Unable to fetch current listings."
    
    def _build_system_prompt_with_products(self):
        """Build system prompt with dynamic product information"""
        products_info = self._get_products_info()
        return self.base_system_prompt + products_info
    
    def get_response(self, message, conversation_history=None):
        """
        Get AI response using the configured provider
        """
        try:
            if self.provider == 'openai':
                return self._get_openai_response(message, conversation_history)
            elif self.provider == 'gemini':
                return self._get_gemini_response(message, conversation_history)
            else:
                return self._get_fallback_response(message)
        except Exception as e:
            print(f"AI API Error: {str(e)}")
            return {
                'response': f"I'm having trouble connecting right now. Please try again in a moment.",
                'intent': 'error',
                'confidence': 0,
                'source': 'error'
            }
    
    def _get_openai_response(self, message, conversation_history=None):
        """Get response from OpenAI (ChatGPT)"""
        api_key = getattr(settings, 'OPENAI_API_KEY', '')
        model = getattr(settings, 'OPENAI_MODEL', 'gpt-3.5-turbo')
        
        if not api_key:
            return self._get_fallback_response(message)
        
        # Build messages array
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages for context
                messages.append({
                    "role": msg['role'],
                    "content": msg['content']
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': messages,
                    'max_tokens': 500,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content']
                return {
                    'response': ai_response,
                    'intent': 'ai_response',
                    'confidence': 1.0,
                    'source': 'openai'
                }
            else:
                print(f"OpenAI API Error: {response.status_code} - {response.text}")
                return self._get_fallback_response(message)
                
        except requests.exceptions.Timeout:
            return {
                'response': "I'm taking too long to respond. Please try again.",
                'intent': 'timeout',
                'confidence': 0,
                'source': 'error'
            }
        except Exception as e:
            print(f"OpenAI Error: {str(e)}")
            return self._get_fallback_response(message)
    
    def _get_gemini_response(self, message, conversation_history=None):
        """Get response from Google Gemini"""
        api_key = getattr(settings, 'GEMINI_API_KEY', '')
        model = getattr(settings, 'GEMINI_MODEL', 'gemini-2.5-flash')
        
        if not api_key:
            return self._get_fallback_response(message)
        
        # Build conversation context
        context = self.system_prompt + "\n\n"
        
        if conversation_history:
            for msg in conversation_history[-10:]:
                role = "User" if msg['role'] == 'user' else "Assistant"
                context += f"{role}: {msg['content']}\n"
        
        context += f"User: {message}\nAssistant:"
        
        try:
            response = requests.post(
                f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}',
                headers={'Content-Type': 'application/json'},
                json={
                    'contents': [{
                        'parts': [{'text': context}]
                    }],
                    'generationConfig': {
                        'temperature': 0.7,
                        'maxOutputTokens': 500,
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['candidates'][0]['content']['parts'][0]['text']
                return {
                    'response': ai_response,
                    'intent': 'ai_response',
                    'confidence': 1.0,
                    'source': 'gemini'
                }
            else:
                print(f"Gemini API Error: {response.status_code} - {response.text}")
                return self._get_fallback_response(message)
                
        except requests.exceptions.Timeout:
            return {
                'response': "I'm taking too long to respond. Please try again.",
                'intent': 'timeout',
                'confidence': 0,
                'source': 'error'
            }
        except Exception as e:
            print(f"Gemini Error: {str(e)}")
            return self._get_fallback_response(message)
    
    def _get_fallback_response(self, message):
        """Fallback response when API is not configured or fails"""
        message_lower = message.lower()
        
        # Simple keyword-based responses as fallback
        if any(word in message_lower for word in ['hi', 'hello', 'hey']):
            response = "Hello! 👋 Welcome to Student Resource Exchange! I'm here to help you find educational resources, list items, or answer any questions. How can I assist you today?"
        elif any(word in message_lower for word in ['sell', 'list', 'upload']):
            response = """To sell or list a product on SRE:

1. Click **"Upload Product"** in the navigation menu
2. Fill in the product details (title, description, category, condition)
3. Set your price or mark it for lending
4. Upload clear photos
5. Submit your listing!

💡 **Tip**: Good photos and detailed descriptions help items sell faster!"""
        elif any(word in message_lower for word in ['borrow', 'lend', 'lending']):
            response = """Here's how borrowing works on SRE:

**To Borrow:**
1. Find an item marked "For Lending"
2. Click "Request to Borrow"
3. The owner will review your request
4. Once approved, coordinate pickup/return

**To Lend:**
1. When creating a listing, select "For Lending"
2. Set your lending terms
3. Review borrow requests from students

🤝 Remember to communicate clearly and return items on time!"""
        elif any(word in message_lower for word in ['search', 'find', 'look']):
            response = """To search for products on SRE:

1. 🔍 Use the **search bar** at the top of the Products page
2. 📂 Filter by **category** (Books, Notes, Electronics, etc.)
3. 💰 Set **price range** if you have a budget
4. 📍 Filter by **location** to find items near you

Would you like me to help you find something specific?"""
        elif any(word in message_lower for word in ['help', 'what can you']):
            response = """I can help you with many things! Here's what I can do:

📚 **Finding Products** - Search for books, notes, electronics, and more
📝 **Listing Items** - Guide you through selling or lending your items
🤝 **Borrowing** - Explain how to borrow items from other students
👤 **Account Help** - Assist with profile and account questions
🔒 **Safety Tips** - Provide guidance on safe transactions

Just ask me anything!"""
        elif any(word in message_lower for word in ['bye', 'goodbye', 'thanks', 'thank you']):
            response = "You're welcome! 😊 Feel free to come back anytime you need help. Happy studying!"
        else:
            response = """I'm here to help! You can ask me about:

📚 **Browse Products** - Search for books, notes, and more
📝 **List Items** - Sell or lend your educational materials  
🤝 **Borrowing** - Learn about our lending system
👤 **Account Help** - Profile and registration assistance

What would you like to know?"""
        
        return {
            'response': response,
            'intent': 'fallback',
            'confidence': 0.5,
            'source': 'fallback'
        }

    def get_suggestions(self, context=None):
        """Get suggested questions based on context"""
        suggestions = [
            "How do I list a product?",
            "How does borrowing work?",
            "How do I search for books?",
            "Is my information safe?",
        ]
        
        if self.user:
            suggestions.insert(0, "Show me my active listings")
            suggestions.insert(1, "How do I edit my profile?")
        else:
            suggestions.insert(0, "How do I create an account?")
            
        return suggestions[:5]
