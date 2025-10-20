# Chat System Documentation

## Overview
The chat system allows buyers and sellers to communicate directly about products listed on the Student Resource Exchange platform.

## Features

### For Buyers
- **Contact Seller**: Click the "Contact Seller" button on any product detail page to start a conversation
- **View All Conversations**: Access all your conversations from the "Messages" menu in the navigation bar
- **Real-time Messaging**: Send and receive messages instantly
- **Conversation History**: See complete message history for each conversation

### For Sellers
- **Receive Messages**: Get contacted by interested buyers through your product listings
- **Respond to Inquiries**: Reply to buyer questions directly in the chat interface
- **Multiple Conversations**: Handle multiple conversations about different products

## How It Works

### Starting a Conversation
1. Browse to a product you're interested in
2. Click the "Contact Seller" button (visible only if you're logged in and not the product owner)
3. You'll be redirected to a chat interface specific to that product and seller
4. If a conversation already exists, you'll be taken to the existing conversation

### Messaging Interface
- **Chat Window**: Displays all messages in chronological order
- **Product Context**: Shows the product being discussed at the top
- **Real-time Updates**: Messages appear immediately after sending
- **Message Status**: See timestamps for all messages
- **Read Receipts**: Messages are marked as read when viewed

### Conversation List
- Access from the "Messages" link in the navigation menu
- Shows all your active conversations
- Displays:
  - Other party's name and avatar
  - Product being discussed
  - Last message preview
  - Time since last message
  - Unread message count (badge)

## Technical Details

### Models

#### Conversation
- Links a buyer, seller, and product
- Ensures unique conversations per buyer-seller-product combination
- Tracks creation and update timestamps
- Automatically updates when new messages are sent

#### Message
- Belongs to a conversation
- Stores sender, content, and timestamp
- Tracks read status
- Ordered chronologically within conversations

### URLs
- `/chat/` - Conversation list
- `/chat/conversation/<id>/` - Chat detail/messaging interface
- `/chat/start/<product_id>/` - Start new conversation
- `/chat/send/<conversation_id>/` - Send message (AJAX endpoint)

### Views

#### `conversation_list`
- Displays all conversations for the current user
- Shows conversations where user is either buyer or seller
- Calculates unread message counts
- Sorted by most recent activity

#### `chat_detail`
- Shows full conversation with messaging interface
- Marks messages as read when viewed
- Verifies user access to conversation
- Displays product context

#### `start_conversation`
- Creates new conversation or redirects to existing one
- Prevents users from messaging themselves
- Requires login

#### `send_message`
- AJAX endpoint for sending messages
- Returns JSON response for real-time UI updates
- Updates conversation timestamp
- Validates user access and message content

## Security Features

1. **Authentication Required**: Users must be logged in to access chat
2. **Access Control**: Users can only view their own conversations
3. **Self-Messaging Prevention**: Cannot start conversation with yourself
4. **CSRF Protection**: All POST requests are CSRF-protected
5. **Input Validation**: Message content is validated and sanitized

## Database Schema

### chat_conversation
- `id`: Primary key
- `buyer_id`: Foreign key to User
- `seller_id`: Foreign key to User  
- `product_id`: Foreign key to Product
- `created_at`: Timestamp
- `updated_at`: Timestamp
- Unique constraint on (buyer, seller, product)

### chat_message
- `id`: Primary key
- `conversation_id`: Foreign key to Conversation
- `sender_id`: Foreign key to User
- `content`: Text field
- `is_read`: Boolean
- `created_at`: Timestamp

## Integration Points

### Product Detail Page
- "Contact Seller" button links to `chat:start_conversation`
- Only shown for available products
- Only shown to non-owners
- Requires login

### Navigation Menu
- "Messages" link added to user dropdown menu
- Shows all conversations in one place
- Easy access from any page

## Future Enhancements

Potential improvements for the chat system:

1. **Notifications**: Email or push notifications for new messages
2. **Image Sharing**: Allow users to share images in chat
3. **Typing Indicators**: Show when the other person is typing
4. **Online Status**: Display when users are online
5. **Message Search**: Search within conversations
6. **Archive/Delete**: Archive or delete old conversations
7. **Block Users**: Ability to block unwanted conversations
8. **Message Reactions**: React to messages with emojis
9. **File Attachments**: Share documents or files
10. **WebSocket Support**: True real-time messaging with Django Channels

## Usage Statistics

Track these metrics in Django admin:
- Total conversations
- Total messages sent
- Average response time
- Most active users
- Popular products (by conversation count)

## Admin Interface

Django admin integration allows administrators to:
- View all conversations
- Read all messages
- Monitor chat activity
- Moderate content if needed
- Delete spam or inappropriate messages

Access at: `/admin/chat/`

## Troubleshooting

### Messages Not Appearing
- Check if JavaScript is enabled
- Verify CSRF token is present
- Check browser console for errors

### Can't Start Conversation
- Ensure you're logged in
- Verify you're not the product owner
- Check if product is still available

### Access Denied
- Only conversation participants can view/send messages
- Login session may have expired
