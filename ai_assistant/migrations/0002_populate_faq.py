# Populate initial FAQ entries
from django.db import migrations


def populate_faq_entries(apps, schema_editor):
    FAQEntry = apps.get_model('ai_assistant', 'FAQEntry')
    
    faq_data = [
        # General
        {
            'question': 'What is Student Resource Exchange?',
            'answer': 'Student Resource Exchange (SRE) is a platform that connects students to buy, sell, and lend educational resources like books, notes, electronics, and lab equipment. It helps students save money and promote sustainability by reusing academic materials.',
            'category': 'general',
            'keywords': 'what, sre, about, platform, student resource exchange',
        },
        {
            'question': 'Is this platform free to use?',
            'answer': 'Yes! SRE is completely free to use. There are no listing fees, no transaction fees, and no hidden charges. We believe in making education more accessible for all students.',
            'category': 'general',
            'keywords': 'free, cost, fees, charges, price',
        },
        # Products & Listings
        {
            'question': 'How do I create a product listing?',
            'answer': 'To list a product:\n1. Log in to your account\n2. Click "Upload Product" in the navigation\n3. Fill in the product details (title, description, category, condition)\n4. Set your price or mark it for lending\n5. Upload clear photos\n6. Submit your listing!\n\nTip: Good descriptions and photos help your items sell faster!',
            'category': 'products',
            'keywords': 'list, create, upload, sell, product, listing, post',
        },
        {
            'question': 'What can I sell on SRE?',
            'answer': 'You can sell various educational resources including:\n📚 Textbooks and reference books\n📝 Notes and study materials\n💻 Electronics (calculators, laptops, tablets)\n✏️ Stationery and supplies\n🔬 Lab equipment\n📦 Other academic materials\n\nAll items should be related to student/educational use.',
            'category': 'products',
            'keywords': 'sell, what, items, categories, books, electronics',
        },
        {
            'question': 'How do I search for products?',
            'answer': 'To find products:\n1. Use the search bar at the top of the Products page\n2. Browse by category (Books, Notes, Electronics, etc.)\n3. Apply filters for price range, condition, and location\n4. Sort by newest, price, or relevance\n\nYou can combine multiple filters to find exactly what you need!',
            'category': 'products',
            'keywords': 'search, find, browse, look, filter, products',
        },
        # Borrowing & Lending
        {
            'question': 'How does borrowing work?',
            'answer': 'Borrowing on SRE is simple:\n1. Find an item marked "For Lending"\n2. Click "Request to Borrow"\n3. The owner reviews your request\n4. Once approved, coordinate pickup details via chat\n5. Return the item by the agreed date\n\nRemember to take care of borrowed items and return them on time!',
            'category': 'borrowing',
            'keywords': 'borrow, how, request, lending, lend, rent',
        },
        {
            'question': 'How do I lend my items?',
            'answer': 'To lend items:\n1. Create a new listing\n2. Select "For Lending" as the listing type\n3. Set your lending terms (duration, any deposit required)\n4. Wait for borrow requests\n5. Review requesters and approve or decline\n6. Coordinate with approved borrowers via chat\n\nYou maintain control over who can borrow your items.',
            'category': 'borrowing',
            'keywords': 'lend, lending, my items, how to lend',
        },
        # Account & Profile
        {
            'question': 'How do I create an account?',
            'answer': 'Creating an account is easy:\n1. Click "Sign Up" on the homepage\n2. Enter your details (name, email, password)\n3. Verify your email address\n4. Complete your profile\n\nYou can also sign up using your Google account for faster registration!',
            'category': 'account',
            'keywords': 'create, account, sign up, register, registration',
        },
        {
            'question': 'I forgot my password. What do I do?',
            'answer': 'No worries! To reset your password:\n1. Go to the login page\n2. Click "Forgot Password"\n3. Enter your registered email\n4. Check your inbox for a reset link\n5. Follow the link to create a new password\n\nIf you don\'t receive the email, check your spam folder.',
            'category': 'account',
            'keywords': 'forgot, password, reset, recover, login problem',
        },
        {
            'question': 'How do I edit my profile?',
            'answer': 'To update your profile:\n1. Click on your profile picture/name in the navigation\n2. Select "Edit Profile"\n3. Update your information (name, photo, bio, etc.)\n4. Save your changes\n\nKeeping your profile updated helps build trust with other users!',
            'category': 'account',
            'keywords': 'edit, profile, update, change, information',
        },
        # Safety
        {
            'question': 'Is it safe to buy/sell on SRE?',
            'answer': 'We prioritize your safety! Here are our recommendations:\n✅ Verify user profiles before transactions\n📍 Meet in public places on campus\n💬 Use our built-in chat for communication\n📸 Document items before/after lending\n⚠️ Report suspicious activity immediately\n\nTrust your instincts - if something feels wrong, don\'t proceed with the transaction.',
            'category': 'safety',
            'keywords': 'safe, safety, secure, trust, scam, fraud',
        },
        {
            'question': 'How do I report a problem?',
            'answer': 'If you encounter any issues:\n1. Use the "Report" button on the user\'s profile or listing\n2. Describe the problem in detail\n3. Our team will review and take action\n\nYou can also contact us directly through the chat support. We take all reports seriously and aim to maintain a safe community.',
            'category': 'safety',
            'keywords': 'report, problem, issue, complaint, help',
        },
        # Technical
        {
            'question': 'How do I contact other users?',
            'answer': 'To message another user:\n1. Go to their profile or product listing\n2. Click "Message" or "Chat"\n3. Type your message and send\n\nYou can view all your conversations in the Messages section. We recommend keeping all communications on the platform for safety.',
            'category': 'technical',
            'keywords': 'contact, message, chat, communicate, user',
        },
    ]
    
    for faq in faq_data:
        FAQEntry.objects.create(**faq)


def remove_faq_entries(apps, schema_editor):
    FAQEntry = apps.get_model('ai_assistant', 'FAQEntry')
    FAQEntry.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('ai_assistant', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_faq_entries, remove_faq_entries),
    ]
