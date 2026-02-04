from django.shortcuts import render, redirect
from django.contrib import messages
from registration.models import User
from django.db.models import Count, Q, Sum, Avg, Max, Min, F
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta, datetime
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse, HttpResponse
import logging
import uuid
import json
import csv
from products.models import Product, BorrowRequest, PurchaseRequest
from products.history_models import ProductHistory
from chat.models import Conversation, Message

logger = logging.getLogger(__name__)

def dashboard_view(request):
    """
    Advanced Admin dashboard with comprehensive analytics
    """
    # Check if user is logged in and is admin
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access the dashboard.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    # Get current user
    try:
        current_user = User.objects.get(id=request.session['user_id'])
        if not current_user.is_admin:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('user_profile:profile')
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        request.session.flush()
        return redirect('login:login')
    
    # Time period filters - Get from request parameters
    now = timezone.now()
    today = now.date()
    
    # Get filter parameters
    period = request.GET.get('period', '30')  # default 30 days
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Determine date range based on parameters
    if start_date and end_date:
        try:
            start_datetime = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end_datetime = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
            filter_start = start_datetime
            filter_period_label = f"{start_date} to {end_date}"
        except ValueError:
            filter_start = now - timedelta(days=30)
            end_datetime = now
            filter_period_label = "Last 30 Days"
    elif period == 'all':
        filter_start = timezone.make_aware(datetime(2000, 1, 1))
        end_datetime = now
        filter_period_label = "All Time"
    else:
        try:
            days = int(period)
            filter_start = now - timedelta(days=days)
            end_datetime = now
            filter_period_label = f"Last {days} Days"
        except ValueError:
            filter_start = now - timedelta(days=30)
            end_datetime = now
            filter_period_label = "Last 30 Days"
    
    # Legacy time periods for compatibility
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    ninety_days_ago = now - timedelta(days=90)
    
    # ========== USER STATISTICS ==========
    total_users = User.objects.count()
    verified_users = User.objects.filter(email_verified=True).count()
    unverified_users = total_users - verified_users
    google_users = User.objects.filter(is_google_user=True).count()
    
    # User growth - filtered by date range
    new_users_today = User.objects.filter(created_at__date=today).count()
    new_users_7d = User.objects.filter(created_at__gte=seven_days_ago).count()
    new_users_30d = User.objects.filter(created_at__gte=thirty_days_ago).count()
    new_users_filtered = User.objects.filter(created_at__gte=filter_start, created_at__lte=end_datetime).count()
    
    # Calculate user growth rate (vs previous period)
    period_duration = (end_datetime - filter_start).days
    prev_period_start = filter_start - timedelta(days=period_duration)
    prev_period_users = User.objects.filter(
        created_at__gte=prev_period_start,
        created_at__lt=filter_start
    ).count()
    growth_rate = ((new_users_filtered - prev_period_users) / prev_period_users * 100) if prev_period_users > 0 else 0
    growth_rate_rounded = round(growth_rate, 1)
    growth_direction = 'up' if growth_rate_rounded >= 0 else 'down'
    growth_rate_abs = abs(growth_rate_rounded)
    
    # Users by rating
    high_rated = User.objects.filter(rating__gte=4).count()
    medium_rated = User.objects.filter(rating__gte=2, rating__lt=4).count()
    low_rated = User.objects.filter(rating__lt=2).count()
    avg_rating = User.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Address completion
    users_with_address = User.objects.filter(
        Q(address_line1__isnull=False) & ~Q(address_line1='')
    ).count()
    users_with_location = User.objects.filter(
        latitude__isnull=False, longitude__isnull=False
    ).count()
    
    # ========== PRODUCT STATISTICS ==========
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_available=True).count()
    inactive_products = total_products - active_products
    
    # Products by listing type
    for_sale = Product.objects.filter(listing_type__in=['sell', 'both']).count()
    for_lending = Product.objects.filter(listing_type__in=['lend', 'both']).count()
    currently_borrowed = Product.objects.filter(is_currently_borrowed=True).count()
    
    # Products by category
    products_by_category = Product.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Product growth
    new_products_today = Product.objects.filter(created_at__date=today).count()
    new_products_7d = Product.objects.filter(created_at__gte=seven_days_ago).count()
    new_products_30d = Product.objects.filter(created_at__gte=thirty_days_ago).count()
    new_products_filtered = Product.objects.filter(created_at__gte=filter_start, created_at__lte=end_datetime).count()
    
    # Total product value (estimated) - filtered
    total_product_value = Product.objects.filter(
        price__isnull=False,
        created_at__gte=filter_start,
        created_at__lte=end_datetime
    ).aggregate(Sum('price'))['price__sum'] or 0
    
    # Product rentals/borrows in period - using BorrowRequest model
    products_borrowed_in_period = BorrowRequest.objects.filter(
        start_date__gte=filter_start.date() if hasattr(filter_start, 'date') else filter_start,
        start_date__lte=end_datetime.date() if hasattr(end_datetime, 'date') else end_datetime,
        status__in=['active', 'returned']
    ).count()
    
    # ========== TRANSACTION STATISTICS ==========
    # Total Lend/Borrow transactions (all time)
    total_borrow_transactions = BorrowRequest.objects.filter(
        status__in=['active', 'returned', 'overdue']
    ).count()
    
    # Total Buy/Sell transactions (all time)
    total_purchase_transactions = PurchaseRequest.objects.filter(
        status__in=['approved', 'completed']
    ).count()
    
    # Transactions in filtered period
    borrow_transactions_filtered = BorrowRequest.objects.filter(
        request_date__gte=filter_start,
        request_date__lte=end_datetime,
        status__in=['active', 'returned', 'overdue']
    ).count()
    
    purchase_transactions_filtered = PurchaseRequest.objects.filter(
        request_date__gte=filter_start,
        request_date__lte=end_datetime,
        status__in=['approved', 'completed']
    ).count()
    
    # Total transaction value
    total_borrow_value = BorrowRequest.objects.filter(
        status__in=['active', 'returned', 'overdue']
    ).aggregate(Sum('total_cost'))['total_cost__sum'] or 0
    
    total_purchase_value = PurchaseRequest.objects.filter(
        status__in=['approved', 'completed']
    ).aggregate(Sum('purchase_price'))['purchase_price__sum'] or 0
    
    # Total product value (estimated)
    total_product_value = Product.objects.filter(
        price__isnull=False
    ).aggregate(Sum('price'))['price__sum'] or 0
    
    # Product views
    total_views = Product.objects.aggregate(Sum('views'))['views__sum'] or 0
    avg_views_per_product = Product.objects.aggregate(Avg('views'))['views__avg'] or 0
    
    # Top viewed products - filtered
    top_viewed_products = Product.objects.filter(
        created_at__gte=filter_start,
        created_at__lte=end_datetime
    ).order_by('-views')[:5]
    
    # ========== CHAT & ENGAGEMENT ==========
    total_conversations = Conversation.objects.count()
    total_messages = Message.objects.count()
    active_conversations_7d = Conversation.objects.filter(updated_at__gte=seven_days_ago).count()
    messages_today = Message.objects.filter(created_at__date=today).count()
    messages_7d = Message.objects.filter(created_at__gte=seven_days_ago).count()
    messages_filtered = Message.objects.filter(created_at__gte=filter_start, created_at__lte=end_datetime).count()
    
    # Average messages per conversation
    avg_messages_per_conv = total_messages / total_conversations if total_conversations > 0 else 0
    
    # ========== ACTIVITY LOG ==========
    recent_activities = []
    
    # Recent users - filtered
    recent_users_list = User.objects.filter(
        created_at__gte=filter_start,
        created_at__lte=end_datetime
    ).order_by('-created_at')[:5]
    for user in recent_users_list:
        recent_activities.append({
            'type': 'user_registered',
            'description': f"New user registered: {user.name or user.email}",
            'timestamp': user.created_at,
            'icon': 'user-plus',
            'color': 'blue'
        })
    
    # Recent products - filtered
    recent_products = Product.objects.filter(
        created_at__gte=filter_start,
        created_at__lte=end_datetime
    ).order_by('-created_at')[:5]
    for product in recent_products:
        recent_activities.append({
            'type': 'product_created',
            'description': f"New product listed: {product.title}",
            'timestamp': product.created_at,
            'icon': 'shopping-bag',
            'color': 'green'
        })
    
    # Recent messages - filtered
    recent_messages = Message.objects.filter(
        created_at__gte=filter_start,
        created_at__lte=end_datetime
    ).order_by('-created_at')[:5]
    for message in recent_messages:
        recent_activities.append({
            'type': 'message_sent',
            'description': f"Message in conversation about {message.conversation.product.title}",
            'timestamp': message.created_at,
            'icon': 'message-circle',
            'color': 'purple'
        })
    
    # Sort all activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]
    
    # ========== CHART DATA - Dynamic based on period ==========
    chart_days = min((end_datetime - filter_start).days, 90)  # Max 90 days for chart
    if chart_days < 1:
        chart_days = 1

    chart_start_date = (end_datetime - timedelta(days=chart_days)).date()
    chart_end_date = end_datetime.date()

    user_counts = {
        row['day']: row['count']
        for row in (
            User.objects.filter(
                created_at__date__gte=chart_start_date,
                created_at__date__lte=chart_end_date,
            )
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
        )
    }

    product_counts = {
        row['day']: row['count']
        for row in (
            Product.objects.filter(
                created_at__date__gte=chart_start_date,
                created_at__date__lte=chart_end_date,
            )
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
        )
    }

    user_growth_data = []
    product_growth_data = []
    for i in range(0, chart_days + 1):
        day = chart_start_date + timedelta(days=i)
        user_growth_data.append({
            'date': day.strftime('%b %d'),
            'count': user_counts.get(day, 0),
        })
        product_growth_data.append({
            'date': day.strftime('%b %d'),
            'count': product_counts.get(day, 0),
        })
    
    # Calculate percentages
    verified_percentage = (verified_users / total_users * 100) if total_users > 0 else 0
    address_percentage = (users_with_address / total_users * 100) if total_users > 0 else 0
    location_percentage = (users_with_location / total_users * 100) if total_users > 0 else 0
    active_product_percentage = (active_products / total_products * 100) if total_products > 0 else 0
    
    # Get latest users
    latest_users = User.objects.order_by('-created_at')[:10]

    # ========== CONVERSION FUNNEL (Signup cohort) ==========
    # Note: "Visitors" is not currently tracked in this app, so we show it as unavailable.
    signup_cohort_qs = User.objects.filter(created_at__gte=filter_start, created_at__lte=end_datetime)
    funnel_signups = signup_cohort_qs.count()
    funnel_verified = signup_cohort_qs.filter(email_verified=True).count()
    funnel_first_listing = signup_cohort_qs.filter(products__isnull=False).distinct().count()

    transaction_status_q = (
        Q(borrow_requests_made__status__in=['approved', 'active', 'returned', 'overdue']) |
        Q(borrow_requests_received__status__in=['approved', 'active', 'returned', 'overdue']) |
        Q(purchase_requests_made__status__in=['approved', 'completed']) |
        Q(purchase_requests_received__status__in=['approved', 'completed'])
    )
    funnel_first_transaction = signup_cohort_qs.filter(transaction_status_q).distinct().count()

    def _pct(numerator, denominator):
        return round((numerator / denominator * 100), 1) if denominator else 0

    conversion_funnel_steps = [
        {
            'label': 'Visitors',
            'value': None,
            'sub': 'Not tracked',
            'rate_from_prev': None,
            'rate_from_signups': None,
        },
        {
            'label': 'Signups',
            'value': funnel_signups,
            'sub': filter_period_label,
            'rate_from_prev': None,
            'rate_from_signups': 100.0 if funnel_signups else 0,
        },
        {
            'label': 'Verified',
            'value': funnel_verified,
            'sub': f"{_pct(funnel_verified, funnel_signups)}% of signups",
            'rate_from_prev': _pct(funnel_verified, funnel_signups),
            'rate_from_signups': _pct(funnel_verified, funnel_signups),
        },
        {
            'label': 'First Listing',
            'value': funnel_first_listing,
            'sub': f"{_pct(funnel_first_listing, funnel_signups)}% of signups",
            'rate_from_prev': _pct(funnel_first_listing, funnel_verified),
            'rate_from_signups': _pct(funnel_first_listing, funnel_signups),
        },
        {
            'label': 'First Transaction',
            'value': funnel_first_transaction,
            'sub': f"{_pct(funnel_first_transaction, funnel_signups)}% of signups",
            'rate_from_prev': _pct(funnel_first_transaction, funnel_first_listing),
            'rate_from_signups': _pct(funnel_first_transaction, funnel_signups),
        },
    ]

    # ========== COHORT RETENTION (Weekly) ==========
    # Definition:
    # - Cohort = users who signed up in a calendar week (Mon-Sun)
    # - Returned (W+1) = any activity in the next week after signup week
    # - Transacted (30d) = any approved/active/returned/overdue borrow OR approved/completed purchase within 30 days of cohort start
    cohort_retention_rows = []
    cohort_weeks = 8
    today_date = today
    current_week_start = today_date - timedelta(days=today_date.weekday())  # Monday

    for i in range(cohort_weeks - 1, -1, -1):
        week_start_date = current_week_start - timedelta(weeks=i)
        week_end_date = week_start_date + timedelta(days=7)
        week_start_dt = timezone.make_aware(datetime.combine(week_start_date, datetime.min.time()))
        week_end_dt = timezone.make_aware(datetime.combine(week_end_date, datetime.min.time()))

        cohort_user_ids = list(
            User.objects.filter(created_at__gte=week_start_dt, created_at__lt=week_end_dt)
            .values_list('id', flat=True)
        )
        cohort_size = len(cohort_user_ids)

        if cohort_size == 0:
            cohort_retention_rows.append({
                'week_label': f"{week_start_date.strftime('%b %d')}–{(week_end_date - timedelta(days=1)).strftime('%b %d')}",
                'cohort_size': 0,
                'returned_w1': 0,
                'returned_w1_pct': 0,
                'transacted_30d': 0,
                'transacted_30d_pct': 0,
            })
            continue

        # Week+1 return window
        return_start_dt = week_end_dt
        return_end_dt = week_end_dt + timedelta(days=7)

        returned_ids = set()
        returned_ids.update(
            Message.objects.filter(
                sender_id__in=cohort_user_ids,
                created_at__gte=return_start_dt,
                created_at__lt=return_end_dt,
            ).values_list('sender_id', flat=True)
        )
        returned_ids.update(
            Product.objects.filter(
                seller_id__in=cohort_user_ids,
                created_at__gte=return_start_dt,
                created_at__lt=return_end_dt,
            ).values_list('seller_id', flat=True)
        )
        returned_ids.update(
            BorrowRequest.objects.filter(
                borrower_id__in=cohort_user_ids,
                request_date__gte=return_start_dt,
                request_date__lt=return_end_dt,
            ).values_list('borrower_id', flat=True)
        )
        returned_ids.update(
            BorrowRequest.objects.filter(
                lender_id__in=cohort_user_ids,
                request_date__gte=return_start_dt,
                request_date__lt=return_end_dt,
            ).values_list('lender_id', flat=True)
        )
        returned_ids.update(
            PurchaseRequest.objects.filter(
                buyer_id__in=cohort_user_ids,
                request_date__gte=return_start_dt,
                request_date__lt=return_end_dt,
            ).values_list('buyer_id', flat=True)
        )
        returned_ids.update(
            PurchaseRequest.objects.filter(
                seller_id__in=cohort_user_ids,
                request_date__gte=return_start_dt,
                request_date__lt=return_end_dt,
            ).values_list('seller_id', flat=True)
        )

        returned_w1 = len(returned_ids)

        # 30-day transaction window from cohort start
        txn_end_dt = week_start_dt + timedelta(days=30)
        transacted_ids = set()
        transacted_ids.update(
            BorrowRequest.objects.filter(
                borrower_id__in=cohort_user_ids,
                request_date__gte=week_start_dt,
                request_date__lt=txn_end_dt,
                status__in=['approved', 'active', 'returned', 'overdue'],
            ).values_list('borrower_id', flat=True)
        )
        transacted_ids.update(
            BorrowRequest.objects.filter(
                lender_id__in=cohort_user_ids,
                request_date__gte=week_start_dt,
                request_date__lt=txn_end_dt,
                status__in=['approved', 'active', 'returned', 'overdue'],
            ).values_list('lender_id', flat=True)
        )
        transacted_ids.update(
            PurchaseRequest.objects.filter(
                buyer_id__in=cohort_user_ids,
                request_date__gte=week_start_dt,
                request_date__lt=txn_end_dt,
                status__in=['approved', 'completed'],
            ).values_list('buyer_id', flat=True)
        )
        transacted_ids.update(
            PurchaseRequest.objects.filter(
                seller_id__in=cohort_user_ids,
                request_date__gte=week_start_dt,
                request_date__lt=txn_end_dt,
                status__in=['approved', 'completed'],
            ).values_list('seller_id', flat=True)
        )

        transacted_30d = len(transacted_ids)

        cohort_retention_rows.append({
            'week_label': f"{week_start_date.strftime('%b %d')}–{(week_end_date - timedelta(days=1)).strftime('%b %d')}",
            'cohort_size': cohort_size,
            'returned_w1': returned_w1,
            'returned_w1_pct': _pct(returned_w1, cohort_size),
            'transacted_30d': transacted_30d,
            'transacted_30d_pct': _pct(transacted_30d, cohort_size),
        })

    # ========== TOP / BOTTOM PERFORMERS (Filtered period) ==========
    top_borrowed_products = Product.objects.annotate(
        borrow_count=Count(
            'borrow_requests',
            filter=Q(
                borrow_requests__request_date__gte=filter_start,
                borrow_requests__request_date__lte=end_datetime,
                borrow_requests__status__in=['active', 'returned', 'overdue'],
            ),
        )
    ).filter(borrow_count__gt=0).order_by('-borrow_count', '-views')[:5]

    active_users_qs = User.objects.annotate(
        messages_sent=Count(
            'sent_messages',
            filter=Q(sent_messages__created_at__gte=filter_start, sent_messages__created_at__lte=end_datetime),
            distinct=True,
        ),
        products_listed=Count(
            'products',
            filter=Q(products__created_at__gte=filter_start, products__created_at__lte=end_datetime),
            distinct=True,
        ),
        borrow_requests=Count(
            'borrow_requests_made',
            filter=Q(borrow_requests_made__request_date__gte=filter_start, borrow_requests_made__request_date__lte=end_datetime),
            distinct=True,
        ),
        purchase_requests=Count(
            'purchase_requests_made',
            filter=Q(purchase_requests_made__request_date__gte=filter_start, purchase_requests_made__request_date__lte=end_datetime),
            distinct=True,
        ),
    ).annotate(
        activity_score=(
            F('messages_sent') +
            F('products_listed') +
            F('borrow_requests') +
            F('purchase_requests')
        )
    ).filter(activity_score__gt=0).order_by('-activity_score', '-messages_sent')[:5]

    cancellation_users_qs = User.objects.annotate(
        borrow_cancellations=Count(
            'borrow_requests_made',
            filter=Q(
                borrow_requests_made__status='cancelled',
                borrow_requests_made__request_date__gte=filter_start,
                borrow_requests_made__request_date__lte=end_datetime,
            ),
            distinct=True,
        ),
        purchase_cancellations=Count(
            'purchase_requests_made',
            filter=Q(
                purchase_requests_made__status='cancelled',
                purchase_requests_made__request_date__gte=filter_start,
                purchase_requests_made__request_date__lte=end_datetime,
            ),
            distinct=True,
        ),
    ).annotate(
        cancellation_count=F('borrow_cancellations') + F('purchase_cancellations')
    ).filter(cancellation_count__gt=0).order_by('-cancellation_count')[:5]
    
    context = {
        'current_user': current_user,
        
        # Filter info
        'filter_period': period,
        'filter_period_label': filter_period_label,
        'filter_start_date': start_date,
        'filter_end_date': end_date,
        
        # User metrics
        'total_users': total_users,
        'verified_users': verified_users,
        'unverified_users': unverified_users,
        'google_users': google_users,
        'new_users_today': new_users_today,
        'new_users_7d': new_users_7d,
        'new_users_30d': new_users_30d,
        'new_users_filtered': new_users_filtered,
        'growth_rate': growth_rate_rounded,
        'growth_direction': growth_direction,
        'growth_rate_abs': growth_rate_abs,
        'high_rated': high_rated,
        'medium_rated': medium_rated,
        'low_rated': low_rated,
        'avg_rating': round(avg_rating, 2),
        'users_with_address': users_with_address,
        'users_with_location': users_with_location,
        'verified_percentage': round(verified_percentage, 1),
        'address_percentage': round(address_percentage, 1),
        'location_percentage': round(location_percentage, 1),
        
        # Product metrics
        'total_products': total_products,
        'active_products': active_products,
        'inactive_products': inactive_products,
        'for_sale': for_sale,
        'for_lending': for_lending,
        'currently_borrowed': currently_borrowed,
        'products_borrowed_in_period': products_borrowed_in_period,
        'products_by_category': products_by_category,
        'new_products_today': new_products_today,
        'new_products_7d': new_products_7d,
        'new_products_30d': new_products_30d,
        'new_products_filtered': new_products_filtered,
        'total_product_value': round(total_product_value, 2),
        'total_views': total_views,
        'avg_views_per_product': round(avg_views_per_product, 1),
        'top_viewed_products': top_viewed_products,
        'active_product_percentage': round(active_product_percentage, 1),
        
        # Transaction metrics
        'total_borrow_transactions': total_borrow_transactions,
        'total_purchase_transactions': total_purchase_transactions,
        'borrow_transactions_filtered': borrow_transactions_filtered,
        'purchase_transactions_filtered': purchase_transactions_filtered,
        'total_borrow_value': round(total_borrow_value, 2),
        'total_purchase_value': round(total_purchase_value, 2),
        
        # Chat & Engagement
        'total_conversations': total_conversations,
        'total_messages': total_messages,
        'active_conversations_7d': active_conversations_7d,
        'messages_today': messages_today,
        'messages_7d': messages_7d,
        'messages_filtered': messages_filtered,
        'avg_messages_per_conv': round(avg_messages_per_conv, 1),
        
        # Chart data
        'user_growth_data': json.dumps(user_growth_data),
        'product_growth_data': json.dumps(product_growth_data),
        
        # Lists
        'latest_users': latest_users,
        'recent_activities': recent_activities,

        # Funnel / retention / performers
        'conversion_funnel_steps': conversion_funnel_steps,
        'cohort_retention_rows': cohort_retention_rows,
        'top_borrowed_products': top_borrowed_products,
        'most_active_users': active_users_qs,
        'cancellation_users': cancellation_users_qs,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

def user_list_view(request):
    """
    Display all users in a table - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    # Get all users
    users = User.objects.order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(college_id__icontains=search_query)
        )
    
    context = {
        'users': users,
        'search_query': search_query,
        'total_count': users.count(),
    }
    
    return render(request, 'dashboard/user_list.html', context)

def user_detail_view(request, user_id):
    """
    Display detailed information about a specific user - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('dashboard:user_list')
    
    context = {
        'user': user,
    }
    
    return render(request, 'dashboard/user_detail.html', context)

def user_edit_view(request, user_id):
    """
    Edit user information - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('dashboard:user_list')
    
    if request.method == 'POST':
        # Update user fields
        user.name = request.POST.get('name', '').strip()
        new_email = request.POST.get('email', '').strip().lower()
        user.college_id = request.POST.get('college_id', '').strip()
        user.college_name = request.POST.get('college_name', '').strip()
        user.university_name = request.POST.get('university_name', '').strip()
        
        # Check email uniqueness before saving
        if new_email != user.email.lower():
            # Email is being changed, check if it's already taken
            if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                messages.error(request, f'Email "{new_email}" is already registered to another user. Please use a different email address.')
                context = {'user': user}
                return render(request, 'dashboard/user_edit.html', context)
        
        user.email = new_email
        
        # Handle rating
        try:
            rating = int(request.POST.get('rating', 0))
            user.rating = max(0, min(5, rating))  # Ensure between 0-5
        except ValueError:
            user.rating = 0
        
        # Update address fields
        user.address_line1 = request.POST.get('address_line1', '').strip()
        user.address_line2 = request.POST.get('address_line2', '').strip()
        user.city = request.POST.get('city', '').strip()
        user.state_province = request.POST.get('state_province', '').strip()
        user.zip_postal_code = request.POST.get('zip_postal_code', '').strip()
        user.country = request.POST.get('country', '').strip()
        
        # Update boolean fields
        user.email_verified = request.POST.get('email_verified') == 'on'
        
        # Handle is_admin field with strict authorization and audit logging
        current_user_id = request.session.get('user_id')
        current_user_email = request.session.get('user_email', 'Unknown')
        new_is_admin_value = request.POST.get('is_admin') == 'on'
        old_is_admin_value = user.is_admin
        
        # Double-check requester has admin privileges (defense in depth)
        if not request.session.get('is_admin', False):
            logger.error(
                f'Unauthorized is_admin change attempt: Non-admin user {current_user_id} '
                f'({current_user_email}) attempted to modify admin status for user {user_id}'
            )
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('user_profile:profile')
        
        # Check if admin is trying to edit their own account
        if current_user_id == user.id:
            # Prevent self-demotion from admin
            if user.is_admin and not new_is_admin_value:
                # Log the attempted self-demotion for auditing
                logger.warning(
                    f'Admin self-demotion attempt blocked: User ID {current_user_id} '
                    f'(email: {user.email}) attempted to remove their own admin privileges.'
                )
                messages.error(
                    request,
                    'You cannot remove your own admin privileges. '
                    'Please ask another administrator to make this change if needed.'
                )
                context = {'user': user}
                return render(request, 'dashboard/user_edit.html', context)
            # Keep existing is_admin value when editing own account
            # (no change allowed, even if trying to promote self)
            pass
        else:
            # Allow admins to change other users' is_admin status
            # Log admin status changes for audit trail
            if old_is_admin_value != new_is_admin_value:
                action = 'granted' if new_is_admin_value else 'revoked'
                logger.warning(
                    f'Admin privilege {action}: '
                    f'User {user.email} (ID: {user.id}) admin status changed to {new_is_admin_value} '
                    f'by admin {current_user_email} (ID: {current_user_id}) '
                    f'at {timezone.now().isoformat()}'
                )
                # Store the change for potential audit requirements
                messages.info(
                    request, 
                    f'Admin privileges {action} for user {user.email}. This action has been logged.'
                )
            
            user.is_admin = new_is_admin_value
        
        try:
            user.save()
            messages.success(request, f'User {user.email} updated successfully!')
            return redirect('dashboard:user_detail', user_id=user.id)
        except Exception as e:
            # Generate correlation ID for tracking
            correlation_id = str(uuid.uuid4())[:8]
            
            # Log full exception details server-side with correlation ID
            logger.exception(
                f'Error updating user (Correlation ID: {correlation_id}): '
                f'User ID: {user.id}, Email: {user.email}, '
                f'Updated by: {request.session.get("user_email", "Unknown")}'
            )
            
            # Show generic error message to user with correlation ID
            messages.error(
                request, 
                f'Error updating user. Please try again or contact support. '
                f'(Reference: {correlation_id})'
            )
    
    context = {
        'user': user,
    }
    
    return render(request, 'dashboard/user_edit.html', context)

@require_http_methods(["GET", "POST"])
def user_delete_view(request, user_id):
    """
    Delete a user - Admin only
    Requires POST method for actual deletion, GET for confirmation page
    """
    # Authentication check
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Authorization check - Admin only
    if not request.session.get('is_admin', False):
        logger.warning(
            f'Unauthorized delete attempt: User ID {request.session.get("user_id")} '
            f'attempted to access user deletion for user_id {user_id}'
        )
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    # Validate user_id exists
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        logger.warning(
            f'User deletion attempt for non-existent user: '
            f'Admin {request.session.get("user_id")} tried to delete user_id {user_id}'
        )
        messages.error(request, 'User not found.')
        return redirect('dashboard:user_list')
    
    # Prevent admin from deleting themselves
    if int(user_id) == request.session.get('user_id'):
        logger.warning(
            f'Self-deletion attempt blocked: Admin {request.session.get("user_id")} '
            f'attempted to delete their own account'
        )
        messages.error(request, 'You cannot delete your own account!')
        return redirect('dashboard:user_detail', user_id=user_id)
    
    # Handle POST request - perform actual deletion
    if request.method == 'POST':
        user_email = user.email
        
        # Get related data counts before deletion
        from products.models import Product, BorrowRequest, PurchaseRequest, BorrowOTP, PurchaseOTP
        from products.history_models import ProductHistory
        from chat.models import Conversation, Message, NotificationPreference
        
        products_count = Product.objects.filter(seller=user).count()
        borrow_requests_count = BorrowRequest.objects.filter(
            Q(borrower=user) | Q(lender=user)
        ).count()
        purchase_requests_count = PurchaseRequest.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).count()
        conversations_count = Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).count()
        messages_count = Message.objects.filter(sender=user).count()
        history_count = ProductHistory.objects.filter(user=user).count()
        
        try:
            with transaction.atomic():
                # First, nullify all SET_NULL foreign key references
                BorrowOTP.objects.filter(verified_by=user).update(verified_by=None)
                PurchaseOTP.objects.filter(verified_by=user).update(verified_by=None)
                Message.objects.filter(recipient=user).update(recipient=None)
                
                # Explicitly delete related records with CASCADE
                # (though CASCADE should handle this, being explicit helps with SQLite)
                ProductHistory.objects.filter(user=user).delete()
                NotificationPreference.objects.filter(user=user).delete()
                Product.objects.filter(seller=user).delete()
                BorrowRequest.objects.filter(Q(borrower=user) | Q(lender=user)).delete()
                PurchaseRequest.objects.filter(Q(buyer=user) | Q(seller=user)).delete()
                Conversation.objects.filter(Q(buyer=user) | Q(seller=user)).delete()
                Message.objects.filter(sender=user).delete()
                
                # Finally delete the user
                user.delete()
            
            # Success message with details
            deleted_info = []
            if products_count > 0:
                deleted_info.append(f"{products_count} product(s)")
            if borrow_requests_count > 0:
                deleted_info.append(f"{borrow_requests_count} borrow request(s)")
            if purchase_requests_count > 0:
                deleted_info.append(f"{purchase_requests_count} purchase request(s)")
            if conversations_count > 0:
                deleted_info.append(f"{conversations_count} conversation(s)")
            if messages_count > 0:
                deleted_info.append(f"{messages_count} message(s)")
            if history_count > 0:
                deleted_info.append(f"{history_count} history record(s)")
            
            if deleted_info:
                messages.success(request, 
                    f'User {user_email} and related data have been deleted successfully: {", ".join(deleted_info)}.')
            else:
                messages.success(request, f'User {user_email} has been deleted successfully.')
                
            return redirect('dashboard:user_list')
            
        except Exception as e:
            # Generate correlation ID for tracking
            correlation_id = str(uuid.uuid4())[:8]
            
            # Log full exception details server-side
            logger.exception(
                f'Error deleting user (Correlation ID: {correlation_id}): '
                f'User ID: {user_id}, Email: {user.email}, '
                f'Deleted by: {request.session.get("user_email", "Unknown")}'
            )
            
            # Show generic error to user with correlation ID
            messages.error(
                request,
                f'Error deleting user. Please try again or contact support. '
                f'(Reference: {correlation_id})'
            )
            return redirect('dashboard:user_detail', user_id=user_id)
    
    # Show confirmation page with counts
    from products.models import Product, BorrowRequest, PurchaseRequest
    from products.history_models import ProductHistory
    from chat.models import Conversation, Message
    
    context = {
        'user': user,
        'products_count': Product.objects.filter(seller=user).count(),
        'borrow_requests_count': BorrowRequest.objects.filter(
            Q(borrower=user) | Q(lender=user)
        ).count(),
        'purchase_requests_count': PurchaseRequest.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).count(),
        'conversations_count': Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).count(),
        'messages_count': Message.objects.filter(sender=user).count(),
        'history_count': ProductHistory.objects.filter(user=user).count(),
    }
    
    return render(request, 'dashboard/user_delete_confirm.html', context)


def transactions_view(request):
    """
    Display all transactions (buy/sell and lend/borrow) - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    # Get current user
    try:
        current_user = User.objects.get(id=request.session['user_id'])
        if not current_user.is_admin:
            messages.error(request, 'Access denied. Admin privileges required.')
            return redirect('user_profile:profile')
    except User.DoesNotExist:
        messages.error(request, 'User not found. Please log in again.')
        request.session.flush()
        return redirect('login:login')
    
    # Get filter parameters
    transaction_type = request.GET.get('type', 'all')  # all, purchase, borrow
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    date_filter_start = None
    date_filter_end = None
    if start_date or end_date:
        try:
            if start_date:
                date_filter_start = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                date_filter_end = timezone.make_aware(
                    datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                )
        except ValueError:
            messages.warning(request, 'Invalid date filter. Please use valid start/end dates.')
            start_date = ''
            end_date = ''
            date_filter_start = None
            date_filter_end = None
    
    # Get Purchase Requests
    purchase_requests = PurchaseRequest.objects.select_related(
        'product', 'buyer', 'seller'
    ).all()
    
    # Get Borrow Requests
    borrow_requests = BorrowRequest.objects.select_related(
        'product', 'borrower', 'lender'
    ).all()

    # Apply date filters (request_date)
    if date_filter_start:
        purchase_requests = purchase_requests.filter(request_date__gte=date_filter_start)
        borrow_requests = borrow_requests.filter(request_date__gte=date_filter_start)
    if date_filter_end:
        purchase_requests = purchase_requests.filter(request_date__lte=date_filter_end)
        borrow_requests = borrow_requests.filter(request_date__lte=date_filter_end)
    
    # Apply filters
    if status_filter != 'all':
        purchase_requests = purchase_requests.filter(status=status_filter)
        borrow_requests = borrow_requests.filter(status=status_filter)
    
    if search_query:
        purchase_requests = purchase_requests.filter(
            Q(product__title__icontains=search_query) |
            Q(buyer__name__icontains=search_query) |
            Q(buyer__email__icontains=search_query) |
            Q(seller__name__icontains=search_query) |
            Q(seller__email__icontains=search_query)
        )
        borrow_requests = borrow_requests.filter(
            Q(product__title__icontains=search_query) |
            Q(borrower__name__icontains=search_query) |
            Q(borrower__email__icontains=search_query) |
            Q(lender__name__icontains=search_query) |
            Q(lender__email__icontains=search_query)
        )
    
    # Determine which to show
    show_purchases = transaction_type in ['all', 'purchase']
    show_borrows = transaction_type in ['all', 'borrow']
    
    if not show_purchases:
        purchase_requests = PurchaseRequest.objects.none()
    if not show_borrows:
        borrow_requests = BorrowRequest.objects.none()
    
    # Order by most recent
    purchase_requests = purchase_requests.order_by('-request_date')
    borrow_requests = borrow_requests.order_by('-request_date')
    
    # Calculate statistics
    stats_purchase_qs = PurchaseRequest.objects.all()
    stats_borrow_qs = BorrowRequest.objects.all()
    if date_filter_start:
        stats_purchase_qs = stats_purchase_qs.filter(request_date__gte=date_filter_start)
        stats_borrow_qs = stats_borrow_qs.filter(request_date__gte=date_filter_start)
    if date_filter_end:
        stats_purchase_qs = stats_purchase_qs.filter(request_date__lte=date_filter_end)
        stats_borrow_qs = stats_borrow_qs.filter(request_date__lte=date_filter_end)

    total_purchases = stats_purchase_qs.count()
    total_borrows = stats_borrow_qs.count()

    purchase_stats = {
        'pending': stats_purchase_qs.filter(status='pending').count(),
        'approved': stats_purchase_qs.filter(status='approved').count(),
        'completed': stats_purchase_qs.filter(status='completed').count(),
        'rejected': stats_purchase_qs.filter(status='rejected').count(),
        'cancelled': stats_purchase_qs.filter(status='cancelled').count(),
    }

    borrow_stats = {
        'pending': stats_borrow_qs.filter(status='pending').count(),
        'approved': stats_borrow_qs.filter(status='approved').count(),
        'active': stats_borrow_qs.filter(status='active').count(),
        'returned': stats_borrow_qs.filter(status='returned').count(),
        'overdue': stats_borrow_qs.filter(status='overdue').count(),
        'rejected': stats_borrow_qs.filter(status='rejected').count(),
        'cancelled': stats_borrow_qs.filter(status='cancelled').count(),
    }
    
    context = {
        'current_user': current_user,
        'purchase_requests': purchase_requests[:50],  # Limit to 50 for performance
        'borrow_requests': borrow_requests[:50],
        'transaction_type': transaction_type,
        'status_filter': status_filter,
        'search_query': search_query,
        'start_date': start_date,
        'end_date': end_date,
        'show_purchases': show_purchases,
        'show_borrows': show_borrows,
        'total_purchases': total_purchases,
        'total_borrows': total_borrows,
        'purchase_stats': purchase_stats,
        'borrow_stats': borrow_stats,
    }
    
    return render(request, 'dashboard/transactions.html', context)


def export_transactions_csv(request):
    """
    Export transactions to CSV/Excel format - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    # Get filter parameters
    transaction_type = request.GET.get('type', 'all')
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('search', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')

    date_filter_start = None
    date_filter_end = None
    if start_date or end_date:
        try:
            if start_date:
                date_filter_start = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            if end_date:
                date_filter_end = timezone.make_aware(
                    datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
                )
        except ValueError:
            start_date = ''
            end_date = ''
            date_filter_start = None
            date_filter_end = None
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="transactions_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Determine which transactions to export
    show_purchases = transaction_type in ['all', 'purchase']
    show_borrows = transaction_type in ['all', 'borrow']
    
    # Export Purchase Requests
    if show_purchases:
        writer.writerow(['BUY/SELL TRANSACTIONS'])
        writer.writerow(['Product', 'Buyer Name', 'Buyer Email', 'Seller Name', 'Seller Email', 
                        'Price', 'Status', 'Request Date', 'Approved Date', 'Completed Date', 
                        'OTP Verified', 'Message'])
        
        purchase_requests = PurchaseRequest.objects.select_related('product', 'buyer', 'seller').all()

        if date_filter_start:
            purchase_requests = purchase_requests.filter(request_date__gte=date_filter_start)
        if date_filter_end:
            purchase_requests = purchase_requests.filter(request_date__lte=date_filter_end)
        
        if status_filter != 'all':
            purchase_requests = purchase_requests.filter(status=status_filter)
        
        if search_query:
            purchase_requests = purchase_requests.filter(
                Q(product__title__icontains=search_query) |
                Q(buyer__name__icontains=search_query) |
                Q(buyer__email__icontains=search_query) |
                Q(seller__name__icontains=search_query) |
                Q(seller__email__icontains=search_query)
            )
        
        purchase_requests = purchase_requests.order_by('-request_date')
        
        for req in purchase_requests:
            writer.writerow([
                req.product.title,
                req.buyer.name or '',
                req.buyer.email,
                req.seller.name or '',
                req.seller.email,
                float(req.purchase_price),
                req.get_status_display(),
                req.request_date.strftime('%Y-%m-%d %H:%M:%S'),
                req.approved_date.strftime('%Y-%m-%d %H:%M:%S') if req.approved_date else '',
                req.completed_date.strftime('%Y-%m-%d %H:%M:%S') if req.completed_date else '',
                'Yes' if req.handover_otp_verified else 'No',
                req.message or ''
            ])
        
        writer.writerow([])  # Empty row separator
    
    # Export Borrow Requests
    if show_borrows:
        writer.writerow(['LEND/BORROW TRANSACTIONS'])
        writer.writerow(['Product', 'Borrower Name', 'Borrower Email', 'Lender Name', 'Lender Email',
                        'Requested Days', 'Total Cost', 'Deposit', 'Status', 'Request Date', 
                        'Approved Date', 'Start Date', 'Expected Return', 'Actual Return', 
                        'Pickup OTP Verified', 'Return OTP Verified', 'Message'])
        
        borrow_requests = BorrowRequest.objects.select_related('product', 'borrower', 'lender').all()

        if date_filter_start:
            borrow_requests = borrow_requests.filter(request_date__gte=date_filter_start)
        if date_filter_end:
            borrow_requests = borrow_requests.filter(request_date__lte=date_filter_end)
        
        if status_filter != 'all':
            borrow_requests = borrow_requests.filter(status=status_filter)
        
        if search_query:
            borrow_requests = borrow_requests.filter(
                Q(product__title__icontains=search_query) |
                Q(borrower__name__icontains=search_query) |
                Q(borrower__email__icontains=search_query) |
                Q(lender__name__icontains=search_query) |
                Q(lender__email__icontains=search_query)
            )
        
        borrow_requests = borrow_requests.order_by('-request_date')
        
        for req in borrow_requests:
            writer.writerow([
                req.product.title,
                req.borrower.name or '',
                req.borrower.email,
                req.lender.name or '',
                req.lender.email,
                req.requested_days,
                float(req.total_cost),
                float(req.deposit_amount),
                req.get_status_display(),
                req.request_date.strftime('%Y-%m-%d %H:%M:%S'),
                req.approved_date.strftime('%Y-%m-%d %H:%M:%S') if req.approved_date else '',
                req.start_date.strftime('%Y-%m-%d') if req.start_date else '',
                req.expected_return_date.strftime('%Y-%m-%d') if req.expected_return_date else '',
                req.actual_return_date.strftime('%Y-%m-%d') if req.actual_return_date else '',
                'Yes' if req.pickup_otp_verified else 'No',
                'Yes' if req.return_otp_verified else 'No',
                req.message or ''
            ])
    
    return response


def export_users_csv(request):
    """
    Export users to CSV/Excel format - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    # Get search query if any
    search_query = request.GET.get('search', '')
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="users_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Name', 'Email', 'Phone', 'College', 'Course', 'Year', 'Email Verified', 
                    'Google User', 'Admin', 'Rating', 'Address', 'City', 'State', 'Pincode',
                    'Latitude', 'Longitude', 'Created At', 'Last Login'])
    
    users = User.objects.all().order_by('-created_at')
    
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    for user in users:
        writer.writerow([
            user.name or '',
            user.email,
            user.phone or '',
            user.college or '',
            user.course or '',
            user.year or '',
            'Yes' if user.email_verified else 'No',
            'Yes' if user.is_google_user else 'No',
            'Yes' if user.is_admin else 'No',
            float(user.rating) if user.rating else 0,
            user.address_line1 or '',
            user.city or '',
            user.state or '',
            user.pincode or '',
            float(user.latitude) if user.latitude else '',
            float(user.longitude) if user.longitude else '',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
        ])
    
    return response


def export_dashboard_summary_csv(request):
    """
    Export dashboard summary statistics to CSV - Admin only
    """
    if not request.session.get('user_id'):
        messages.error(request, 'Please log in to access this page.')
        return redirect('login:login')
    
    # Check if user is admin
    if not request.session.get('is_admin', False):
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('user_profile:profile')
    
    # Get filter parameters
    period = request.GET.get('period', '30')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    
    # Calculate statistics (simplified version of dashboard_view logic)
    now = timezone.now()
    
    if start_date and end_date:
        try:
            filter_start = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            filter_end = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d').replace(hour=23, minute=59, second=59))
            period_label = f"{start_date} to {end_date}"
        except ValueError:
            filter_start = now - timedelta(days=30)
            filter_end = now
            period_label = "Last 30 Days"
    elif period == 'all':
        filter_start = timezone.make_aware(datetime(2000, 1, 1))
        filter_end = now
        period_label = "All Time"
    else:
        try:
            days = int(period)
            filter_start = now - timedelta(days=days)
            filter_end = now
            period_label = f"Last {days} Days"
        except ValueError:
            filter_start = now - timedelta(days=30)
            filter_end = now
            period_label = "Last 30 Days"
    
    # Create the HttpResponse object with CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="dashboard_summary_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['DASHBOARD SUMMARY'])
    writer.writerow(['Period:', period_label])
    writer.writerow([])
    
    # User Statistics
    writer.writerow(['USER STATISTICS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Users', User.objects.count()])
    writer.writerow(['Verified Users', User.objects.filter(email_verified=True).count()])
    writer.writerow(['Google Users', User.objects.filter(is_google_user=True).count()])
    writer.writerow(['New Users in Period', User.objects.filter(created_at__gte=filter_start, created_at__lte=filter_end).count()])
    writer.writerow(['Average Rating', User.objects.aggregate(Avg('rating'))['rating__avg'] or 0])
    writer.writerow([])
    
    # Product Statistics
    writer.writerow(['PRODUCT STATISTICS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Products', Product.objects.count()])
    writer.writerow(['Active Products', Product.objects.filter(is_available=True).count()])
    writer.writerow(['For Sale', Product.objects.filter(listing_type__in=['sell', 'both']).count()])
    writer.writerow(['For Lending', Product.objects.filter(listing_type__in=['lend', 'both']).count()])
    writer.writerow(['Currently Borrowed', Product.objects.filter(is_currently_borrowed=True).count()])
    writer.writerow(['New Products in Period', Product.objects.filter(created_at__gte=filter_start, created_at__lte=filter_end).count()])
    writer.writerow(['Total Product Value', Product.objects.filter(price__isnull=False).aggregate(Sum('price'))['price__sum'] or 0])
    writer.writerow([])
    
    # Transaction Statistics
    writer.writerow(['TRANSACTION STATISTICS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Buy/Sell Transactions', PurchaseRequest.objects.filter(status__in=['approved', 'completed']).count()])
    writer.writerow(['Total Lend/Borrow Transactions', BorrowRequest.objects.filter(status__in=['active', 'returned', 'overdue']).count()])
    writer.writerow(['Buy/Sell in Period', PurchaseRequest.objects.filter(request_date__gte=filter_start, request_date__lte=filter_end, status__in=['approved', 'completed']).count()])
    writer.writerow(['Lend/Borrow in Period', BorrowRequest.objects.filter(request_date__gte=filter_start, request_date__lte=filter_end, status__in=['active', 'returned', 'overdue']).count()])
    writer.writerow(['Total Purchase Value', PurchaseRequest.objects.filter(status__in=['approved', 'completed']).aggregate(Sum('purchase_price'))['purchase_price__sum'] or 0])
    writer.writerow(['Total Borrow Value', BorrowRequest.objects.filter(status__in=['active', 'returned', 'overdue']).aggregate(Sum('total_cost'))['total_cost__sum'] or 0])
    writer.writerow([])
    
    # Chat Statistics
    writer.writerow(['CHAT & ENGAGEMENT STATISTICS'])
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Total Conversations', Conversation.objects.count()])
    writer.writerow(['Total Messages', Message.objects.count()])
    writer.writerow(['Messages in Period', Message.objects.filter(created_at__gte=filter_start, created_at__lte=filter_end).count()])
    
    return response
