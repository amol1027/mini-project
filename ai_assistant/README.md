# AI Assistant for Student Resource Exchange

The AI Assistant is an intelligent chatbot that helps users navigate the Student Resource Exchange platform. It provides instant answers to common questions about buying, selling, borrowing, and using the platform.

## Features

- 🤖 **Smart Intent Detection** - Understands what users are asking about
- 📚 **FAQ Matching** - Provides accurate answers from a knowledge base
- 💬 **Conversation Memory** - Remembers chat history within sessions
- 🎯 **Context-Aware** - Provides personalized responses for logged-in users
- 📱 **Floating Widget** - Available on every page for quick help
- 🖥️ **Full Chat Page** - Dedicated chat interface for longer conversations

## How It Works

### Intent Detection
The assistant uses pattern matching to detect user intents:
- Greetings and farewells
- Product search queries
- Selling/listing questions
- Borrowing and lending inquiries
- Account-related questions
- Safety and trust concerns

### FAQ Matching
When a user asks a question, the assistant:
1. Searches the FAQ database for relevant entries
2. Uses keyword matching and text similarity
3. Returns the best matching answer with confidence score

### Response Priority
1. Quick responses (greetings, farewells, help)
2. FAQ matches (if confidence > 30%)
3. Intent-based fallback responses
4. Default helpful response

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/assistant/chat/` | GET | Full chat interface page |
| `/assistant/api/send-message/` | POST | Send message and get AI response |
| `/assistant/api/get-history/` | GET | Get chat history |
| `/assistant/api/clear-history/` | POST | Clear chat history |
| `/assistant/api/suggestions/` | GET | Get suggested questions |

## Models

### ChatSession
Stores chat sessions for users (logged in or anonymous).

### ChatMessage
Individual messages in a chat session with role, content, and metadata.

### FAQEntry
Pre-defined FAQ entries with questions, answers, categories, and keywords.

## Customization

### Adding FAQ Entries
1. Go to Django Admin → AI Assistant → FAQ Entries
2. Add new entries with questions, answers, and keywords
3. Entries are immediately available to the assistant

### Modifying Responses
Edit `ai_assistant/assistant.py` to:
- Add new intent patterns
- Modify quick responses
- Update fallback responses

## Usage

### Floating Widget
The chat widget appears in the bottom-right corner of every page. Users can:
- Click to open/close
- Type questions
- Use quick suggestion buttons
- Open full chat in new page

### Full Chat Page
Access at `/assistant/chat/` for a full-screen chat experience with:
- Complete chat history
- More suggested questions
- Clear chat option

## Testing

Run tests with:
```bash
python manage.py test ai_assistant
```

## Future Enhancements

- [ ] Integration with external AI APIs (OpenAI, etc.)
- [ ] Learning from user interactions
- [ ] Multi-language support
- [ ] Voice input/output
- [ ] Product recommendations based on chat context
