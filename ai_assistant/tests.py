from django.test import TestCase
from .assistant import AIAssistant
from .models import FAQEntry


class AIAssistantTestCase(TestCase):
    def setUp(self):
        # Create some test FAQ entries
        FAQEntry.objects.create(
            question="How do I create an account?",
            answer="To create an account, click on Sign Up and follow the instructions.",
            category="account",
            keywords="account, register, sign up, create",
            is_active=True
        )
        FAQEntry.objects.create(
            question="How do I list a product for sale?",
            answer="Go to Upload Product and fill in the details.",
            category="products",
            keywords="sell, list, product, upload",
            is_active=True
        )
    
    def test_greeting_response(self):
        assistant = AIAssistant()
        response = assistant.get_response("Hello!")
        self.assertEqual(response['intent'], 'greeting')
        self.assertIn('Hello', response['response'])
    
    def test_help_response(self):
        assistant = AIAssistant()
        response = assistant.get_response("help me")
        self.assertEqual(response['intent'], 'help')
    
    def test_faq_matching(self):
        assistant = AIAssistant()
        response = assistant.get_response("how do i create an account")
        self.assertEqual(response['source'], 'faq')
    
    def test_intent_detection(self):
        assistant = AIAssistant()
        
        # Test sell intent
        response = assistant.get_response("I want to sell my book")
        self.assertEqual(response['intent'], 'sell_product')
        
        # Test borrow intent
        response = assistant.get_response("Can I borrow a calculator?")
        self.assertEqual(response['intent'], 'borrow_lend')
