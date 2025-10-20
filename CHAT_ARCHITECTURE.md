# Chat System Architecture & Flow

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CHAT SYSTEM FLOW                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    BUYER     │         │   DATABASE   │         │    SELLER    │
│   (Amol)     │         │  (SQLite)    │         │   (Rahul)    │
└──────────────┘         └──────────────┘         └──────────────┘
      │                         │                         │
      │ 1. Click "Contact       │                         │
      │    Seller" on          │                         │
      │    product page         │                         │
      │─────────────────────────>                         │
      │                         │                         │
      │ 2. GET /chat/start/5/   │                         │
      │─────────────────────────>                         │
      │                         │                         │
      │                    3. Create/Get                  │
      │                    Conversation                   │
      │                    (buyer=Amol,                   │
      │                     seller=Rahul,                 │
      │                     product=5)                    │
      │                    ◄────────┐                     │
      │                         │   │                     │
      │ 4. Redirect to chat     │   │                     │
      │    interface            │   │                     │
      │◄────────────────────────┘   │                     │
      │                         │                         │
      │ 5. Load chat page       │                         │
      │    with messages        │                         │
      │◄────────────────────────────┘                     │
      │                         │                         │
      │ 6. Type message:        │                         │
      │    "Is this available?" │                         │
      │                         │                         │
      │ 7. POST /chat/send/1/   │                         │
      │─────────────────────────>                         │
      │                    8. Save message                │
      │                       to DB                       │
      │                    ◄────────┐                     │
      │                         │   │                     │
      │ 9. JSON response        │   │                     │
      │    {success: true}      │   │                     │
      │◄────────────────────────┘   │                     │
      │                         │                         │
      │ 10. Display message     │                         │
      │     in chat UI          │                         │
      │                         │                         │
      │                         │  11. Seller opens       │
      │                         │      Messages page      │
      │                         │◄────────────────────────│
      │                         │                         │
      │                         │  12. Load conversations │
      │                         │      with unread count  │
      │                         │─────────────────────────>
      │                         │                         │
      │                         │  13. Click conversation │
      │                         │◄────────────────────────│
      │                         │                         │
      │                         │  14. Load chat with     │
      │                         │      messages           │
      │                         │─────────────────────────>
      │                         │                         │
      │                         │  15. Mark messages as   │
      │                         │      read               │
      │                         │◄────────┐               │
      │                         │         │               │
      │                         │  16. Type reply         │
      │                         │      "Yes, it is!"      │
      │                         │                         │
      │                         │  17. POST /chat/send/1/ │
      │                         │◄────────────────────────│
      │                    18. Save message               │
      │                        to DB                      │
      │                    ◄────────┐                     │
      │                         │   │                     │
      │ 19. REAL-TIME POLLING   │   │  20. Display reply │
      │     (every 2 seconds)   │   │      in chat UI    │
      │                         │   └─────────────────────>
      │ GET /chat/get-messages/ │                         │
      │     ?last_message_id=42 │                         │
      │─────────────────────────>                         │
      │                    21. Query new                  │
      │                        messages                   │
      │                    ◄────────┐                     │
      │                         │   │                     │
      │ 22. JSON response       │   │                     │
      │     {messages: [...]}   │   │                     │
      │◄────────────────────────┘   │                     │
      │                         │                         │
      │ 23. NEW MESSAGE APPEARS!│                         │
      │     (Seller's reply)    │                         │
      │     Auto-displayed      │                         │
      │                         │                         │
      │ 24. Continue chatting...│  25. Continue chatting...│
      │                         │                         │
      └─────────────────────────┴─────────────────────────┘


═══════════════════════════════════════════════════════════════
                    DATABASE STRUCTURE
═══════════════════════════════════════════════════════════════

┌─────────────────────────┐
│   chat_conversation     │
├─────────────────────────┤
│ id (PK)                 │
│ buyer_id (FK → User)    │
│ seller_id (FK → User)   │
│ product_id (FK → Prod)  │
│ created_at              │
│ updated_at              │
└─────────────────────────┘
           │
           │ 1:N
           │
           ▼
┌─────────────────────────┐
│     chat_message        │
├─────────────────────────┤
│ id (PK)                 │
│ conversation_id (FK)    │
│ sender_id (FK → User)   │
│ content (TEXT)          │
│ is_read (BOOLEAN)       │
│ created_at              │
└─────────────────────────┘


═══════════════════════════════════════════════════════════════
                    REAL-TIME MECHANISM
═══════════════════════════════════════════════════════════════

TIME:  0s     2s     4s     6s     8s     10s
       │      │      │      │      │      │
BUYER: │ Send │ Poll │ Poll │ Poll │ Poll │ Poll
       │  Msg │  ✓   │  ✓   │  ✓   │  ✓   │  ✓
       │      │      │      │      │      │
       │      │      │      │  NEW MESSAGE RECEIVED!
       │      │      │      │      ▲
       │      │      │      │      │
SELLER:│      │ Send │      │      │
       │      │ Reply│      │      │
       │      │      │      │      │

Polling Interval: 2 seconds
Max Latency: 2 seconds
Network Requests: 30 per minute (minimal)


═══════════════════════════════════════════════════════════════
                    URL STRUCTURE
═══════════════════════════════════════════════════════════════

/chat/
  └─> conversation_list view
      └─> Shows all conversations
      └─> Unread counts
      └─> Last message previews

/chat/conversation/<id>/
  └─> chat_detail view
      └─> Full chat interface
      └─> Message history
      └─> Real-time updates

/chat/start/<product_id>/
  └─> start_conversation view
      └─> Creates/gets conversation
      └─> Redirects to chat_detail

/chat/send/<conversation_id>/
  └─> send_message view (AJAX)
      └─> POST only
      └─> Returns JSON
      └─> Saves message to DB

/chat/get-messages/<conversation_id>/
  └─> get_new_messages view (AJAX)
      └─> GET only
      └─> Returns new messages
      └─> Used for polling


═══════════════════════════════════════════════════════════════
                    NAVIGATION INTEGRATION
═══════════════════════════════════════════════════════════════

┌──────────────────────────────────────────────────────────┐
│  Student Resource Exchange              [👤 User Menu ▼] │
├──────────────────────────────────────────────────────────┤
│  Home | Upload Product | Dashboard                       │
└──────────────────────────────────────────────────────────┘
                                                    │
                                                    ▼
                        ┌───────────────────────────────┐
                        │  My Profile                   │
                        │  My Products                  │
                        │  Messages  ◄──── NEW!         │
                        │  Admin Dashboard              │
                        │  ─────────────────            │
                        │  Logout                       │
                        └───────────────────────────────┘
                                    │
                                    ▼
                        /chat/ (Conversation List)


═══════════════════════════════════════════════════════════════
              PRODUCT PAGE INTEGRATION
═══════════════════════════════════════════════════════════════

Product Detail Page
┌────────────────────────────────────────┐
│  Physics Textbook                      │
│  ₹500 • Like New • Books              │
│                                        │
│  [Image Gallery]                       │
│                                        │
│  Description: Great condition...       │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │   Seller Info                    │ │
│  │   Rahul • MIT • ⭐⭐⭐⭐⭐         │ │
│  │                                  │ │
│  │   ┌────────────────────────┐    │ │
│  │   │  Contact Seller        │    │ │◄── Leads to chat
│  │   └────────────────────────┘    │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════
                    SECURITY CHECKS
═══════════════════════════════════════════════════════════════

Every Request:
✓ User logged in? (session check)
✓ User part of conversation? (buyer or seller)
✓ CSRF token valid? (POST requests)
✓ Message not empty? (validation)
✓ Not messaging self? (business logic)

Access Control:
┌─────────────────────────────────────────┐
│  Conversation Participants Only         │
│  ┌───────────────────────────────────┐  │
│  │  Buyer (Amol) ✓ Can view/send    │  │
│  │  Seller (Rahul) ✓ Can view/send  │  │
│  │  Others (John) ✗ Access denied   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════
                    MESSAGE STATES
═══════════════════════════════════════════════════════════════

Message Lifecycle:

1. CREATED
   ├─> sender: User A
   ├─> is_read: False
   └─> created_at: Now

2. DISPLAYED (to sender)
   └─> Shows immediately in UI

3. POLLED (by receiver)
   └─> Fetched via get_new_messages

4. READ (by receiver)
   ├─> is_read: True
   └─> Updated automatically


═══════════════════════════════════════════════════════════════
                    PERFORMANCE METRICS
═══════════════════════════════════════════════════════════════

Polling Overhead:
- Request size: ~200 bytes
- Response (no new): ~50 bytes
- Response (1 message): ~300 bytes
- Frequency: 30 requests/min
- Total data: ~6 KB/min

Database Queries:
- Send message: 3 queries
- Poll (no new): 2 queries
- Poll (new): 3 queries
- Load chat: 5 queries

Optimizations:
✓ Select related (reduce N+1 queries)
✓ Incremental fetching (only new messages)
✓ Indexed fields (faster lookups)
✓ Smart scrolling (better UX)


═══════════════════════════════════════════════════════════════
              COMPARISON: EMAIL vs CHAT
═══════════════════════════════════════════════════════════════

┌────────────────────┬───────────────┬──────────────────┐
│      Feature       │     Email     │   This Chat      │
├────────────────────┼───────────────┼──────────────────┤
│  Latency           │  Minutes      │  2 seconds       │
│  Context           │  Manual       │  Automatic       │
│  User Experience   │  Complex      │  Simple          │
│  Real-time         │  No           │  Yes             │
│  Mobile-friendly   │  So-so        │  Excellent       │
│  Product link      │  Manual       │  Integrated      │
│  History           │  Threads      │  Clean           │
│  Accessibility     │  Email client │  In-app          │
└────────────────────┴───────────────┴──────────────────┘


═══════════════════════════════════════════════════════════════
                    SUCCESS INDICATORS
═══════════════════════════════════════════════════════════════

✅ Conversation created on first contact
✅ Messages appear in sender's chat immediately
✅ Messages appear in receiver's chat within 2s
✅ Unread count updates correctly
✅ Messages marked read when viewed
✅ Can't access others' conversations
✅ Product context always visible
✅ Mobile responsive
✅ No page refresh needed
✅ Works like WhatsApp!


═══════════════════════════════════════════════════════════════

                    🎉 SYSTEM READY! 🎉

═══════════════════════════════════════════════════════════════
