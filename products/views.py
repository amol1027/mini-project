from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import F
from django.db import transaction
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse
import json
from django.core.cache import cache
from django.utils import timezone
from .models import Product, BorrowRequest, PurchaseRequest
from .history_models import ProductHistory
from .forms import ProductForm
from .decorators import login_required, owner_required, lender_required, borrower_required, request_participant_required, rate_limit

def product_list(request):
    """
    Display list of all available products with pagination
    """
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(title__icontains=search_query)
    
    # Pagination - 12 products per page
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        products_page = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page of results
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'products': products_page,
        'selected_category': category,
        'search_query': search_query,
        'paginator': paginator,
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, product_id):
    """
    Display detailed view of a single product
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Increment view count atomically to prevent race conditions
    Product.objects.filter(pk=product.pk).update(views=F('views') + 1)
    
    # Get related products (same category)
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(id=product.id)[:4]
    
    # Check if current user is the owner of this product
    is_owner = False
    if 'user_id' in request.session:
        is_owner = product.seller.id == request.session['user_id']
    
    context = {
        'product': product,
        'related_products': related_products,
        'is_owner': is_owner,
    }
    
    return render(request, 'products/product_detail.html', context)

@login_required
def product_create(request):
    """
    Create a new product listing
    """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        
        if form.is_valid():
            product = form.save(commit=False)
            
            # Get seller from session
            from registration.models import User
            product.seller = User.objects.get(id=request.session['user_id'])
            
            product.save()
            
            messages.success(request, f'Product "{product.title}" uploaded successfully!')
            return redirect('products:product_detail', product_id=product.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
        'page_title': 'Upload New Product',
    }
    
    return render(request, 'products/product_form.html', context)

@login_required
@owner_required
def product_edit(request, product_id):
    """
    Edit an existing product
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        import os
        
        # First, validate the form before making any changes
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            try:
                # Collect file paths to delete and image fields to update
                files_to_delete = []
                deleted_image_fields = []
                
                # Check which images are marked for deletion (image2-5 only, not primary image1)
                for i in range(2, 6):
                    delete_field = f'delete_image{i}'
                    if delete_field in request.POST and request.POST.get(delete_field):
                        image_field = f'image{i}'
                        image = getattr(product, image_field, None)
                        
                        if image:
                            # Collect the file path for later deletion
                            try:
                                if hasattr(image, 'path') and os.path.isfile(image.path):
                                    files_to_delete.append(image.path)
                            except Exception as e:
                                print(f"Error checking file path for {image_field}: {e}")
                            
                            # Mark field for clearing
                            setattr(product, image_field, None)
                            deleted_image_fields.append(image_field)
                
                # Use transaction to ensure atomicity
                with transaction.atomic():
                    # Save the form (updates all modified fields)
                    updated_product = form.save()
                    
                    # If images were deleted, save those fields explicitly
                    if deleted_image_fields:
                        product.save(update_fields=deleted_image_fields + ['updated_at'])
                    
                    # Schedule file deletion only after successful DB commit
                    if files_to_delete:
                        def delete_files():
                            for file_path in files_to_delete:
                                try:
                                    if os.path.isfile(file_path):
                                        os.remove(file_path)
                                        print(f"Deleted file: {file_path}")
                                except Exception as e:
                                    print(f"Error deleting file {file_path}: {e}")
                        
                        transaction.on_commit(delete_files)
                
                # Success message
                if deleted_image_fields:
                    messages.success(request, f'Product "{updated_product.title}" updated successfully! Deleted {len(deleted_image_fields)} image(s).')
                else:
                    messages.success(request, f'Product "{updated_product.title}" updated successfully!')
                
                return redirect('products:product_detail', product_id=updated_product.id)
                
            except Exception as e:
                messages.error(request, f'An error occurred while updating the product: {str(e)}')
                print(f"Error in product_edit transaction: {e}")
                import traceback
                traceback.print_exc()
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProductForm(instance=product)
    
    context = {
        'form': form,
        'product': product,
        'page_title': 'Edit Product',
        'is_edit': True,
    }
    
    return render(request, 'products/product_form.html', context)

@login_required
@owner_required
def product_delete(request, product_id):
    """
    Delete a product (soft delete by marking as unavailable)
    """
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()  # Hard delete
        messages.success(request, f'Product "{product_title}" has been deleted.')
        return redirect('products:product_list')
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/product_confirm_delete.html', context)

@login_required
def my_products(request):
    """
    Display user's own products
    """
    from registration.models import User
    user = User.objects.get(id=request.session['user_id'])
    
    products = Product.objects.filter(seller=user).order_by('-created_at')
    
    # Calculate statistics (before pagination)
    total_products = products.count()
    available_count = products.filter(is_available=True).count()
    total_views = sum(product.views for product in products)
    
    # Calculate average price (only for products with a price)
    prices = [product.price for product in products if product.price is not None]
    avg_price = sum(prices) // len(prices) if prices else 0
    
    # Pagination - 12 products per page
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    
    try:
        products_page = paginator.page(page)
    except PageNotAnInteger:
        products_page = paginator.page(1)
    except EmptyPage:
        products_page = paginator.page(paginator.num_pages)
    
    context = {
        'products': products_page,
        'user': user,
        'total_products': total_products,
        'available_count': available_count,
        'total_views': total_views,
        'avg_price': avg_price,
        'paginator': paginator,
    }
    
    return render(request, 'products/my_products.html', context)


# ========== Borrow/Lend Views ==========

@login_required
def borrow_request_create(request, product_id):
    """
    Create a borrow request for a product
    """
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is available for borrowing
    if not product.can_be_borrowed():
        messages.error(request, 'This item is not available for borrowing.')
        return redirect('products:product_detail', product_id=product_id)
    
    # Check if user is not the owner
    if product.seller.id == request.session['user_id']:
        messages.error(request, 'You cannot borrow your own item.')
        return redirect('products:product_detail', product_id=product_id)
    from registration.models import User
    from .models import BorrowRequest
    from .forms import BorrowRequestForm
    from datetime import date, timedelta
    
    borrower = User.objects.get(id=request.session['user_id'])
    
    # Check if user already has a pending/approved/active request for this product
    existing_request = BorrowRequest.objects.filter(
        product=product,
        borrower=borrower,
        status__in=['pending', 'approved', 'active']
    ).first()
    
    if existing_request:
        messages.warning(request, f'You already have a {existing_request.status} borrow request for this item.')
        return redirect('products:product_detail', product_id=product_id)
    
    # Safety check: Ensure product's is_currently_borrowed flag is accurate
    # Fix any inconsistency by checking actual active borrow requests
    active_borrows = BorrowRequest.objects.filter(
        product=product,
        status='active'
    ).exists()
    
    if product.is_currently_borrowed != active_borrows:
        # Fix the inconsistency
        product.is_currently_borrowed = active_borrows
        product.save(update_fields=['is_currently_borrowed'])
    
    if request.method == 'POST':
        form = BorrowRequestForm(request.POST, max_days=product.max_borrow_days)
        
        if form.is_valid():
            requested_days = form.cleaned_data['requested_days']
            message = form.cleaned_data.get('message', '')
            
            # Calculate costs
            total_cost = product.borrow_price_per_day * requested_days
            
            # Create borrow request
            borrow_request = BorrowRequest.objects.create(
                product=product,
                borrower=borrower,
                lender=product.seller,
                requested_days=requested_days,
                message=message,
                total_cost=total_cost,
                deposit_amount=product.borrow_deposit or 0,
                status='pending'
            )
            
            # Invalidate cache for lender's pending requests count
            cache_key = f'pending_borrow_requests_count_{product.seller.id}'
            cache.delete(cache_key)
            
            messages.success(request, f'Borrow request sent! Total cost: ₹{total_cost}')
            return redirect('products:borrow_request_detail', request_id=borrow_request.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = BorrowRequestForm(max_days=product.max_borrow_days)
    
    context = {
        'form': form,
        'product': product,
    }
    
    return render(request, 'products/borrow_request_create.html', context)


@login_required
@request_participant_required
def borrow_request_detail(request, request_id):
    """
    View details of a borrow request
    """
    from .models import BorrowRequest
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    user_id = request.session['user_id']
    is_lender = borrow_request.lender.id == user_id
    is_borrower = borrow_request.borrower.id == user_id
    
    context = {
        'borrow_request': borrow_request,
        'is_lender': is_lender,
        'is_borrower': is_borrower,
    }
    
    return render(request, 'products/borrow_request_detail.html', context)


@login_required
@lender_required
def borrow_request_approve(request, request_id):
    """
    Approve a borrow request (lender only)
    Now generates acceptance OTP automatically
    """
    from .models import BorrowRequest
    from datetime import date, timedelta
    from django.utils import timezone
    from .otp_utils import create_acceptance_otp, send_otp_notification
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if request is pending
    if borrow_request.status != 'pending':
        messages.warning(request, f'This request is already {borrow_request.status}.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        response_message = request.POST.get('response_message', '')
        
        # Update request status to approved (not active yet - waiting for OTP verification)
        borrow_request.status = 'approved'
        borrow_request.approved_date = timezone.now()
        borrow_request.lender_response = response_message
        borrow_request.save()
        
        # Generate acceptance OTP
        otp = create_acceptance_otp(borrow_request)
        
        # Send OTP notification to both borrower and lender via chat
        send_otp_notification(borrow_request, otp)
        
        # Invalidate cache for lender's pending requests count
        cache_key = f'pending_borrow_requests_count_{borrow_request.lender.id}'
        cache.delete(cache_key)
        
        messages.success(request, f'Request approved! Acceptance OTP ({otp.otp_code}) has been sent to the borrower via chat. They will show this OTP when picking up the item.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    context = {
        'borrow_request': borrow_request,
    }
    
    return render(request, 'products/borrow_request_approve.html', context)


@login_required
@lender_required
def borrow_request_reject(request, request_id):
    """
    Reject a borrow request (lender only)
    """
    from .models import BorrowRequest
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if request is pending
    if borrow_request.status != 'pending':
        messages.warning(request, f'This request is already {borrow_request.status}.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        response_message = request.POST.get('response_message', '')
        
        # Update request status
        borrow_request.status = 'rejected'
        borrow_request.lender_response = response_message
        borrow_request.save()
        
        # Invalidate cache for lender's pending requests count
        cache_key = f'pending_borrow_requests_count_{borrow_request.lender.id}'
        cache.delete(cache_key)
        
        messages.success(request, 'Borrow request rejected.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    context = {
        'borrow_request': borrow_request,
    }
    
    return render(request, 'products/borrow_request_reject.html', context)


@login_required
@lender_required
def borrow_request_return(request, request_id):
    """
    Mark an item as returned (lender confirms return)
    """
    from .models import BorrowRequest
    from datetime import date
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if request is active
    if borrow_request.status != 'active':
        messages.warning(request, 'This item is not currently borrowed.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        # Update request status
        borrow_request.status = 'returned'
        borrow_request.actual_return_date = date.today()
        borrow_request.save()
        
        # Mark product as available again
        product = borrow_request.product
        product.is_currently_borrowed = False
        product.save()
        
        messages.success(request, 'Item marked as returned. Transaction complete!')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    context = {
        'borrow_request': borrow_request,
    }
    
    return render(request, 'products/borrow_request_return.html', context)


@login_required
@borrower_required
def borrow_request_cancel(request, request_id):
    """
    Cancel a borrow request (borrower only, for pending requests)
    """
    from .models import BorrowRequest
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if request is pending
    if borrow_request.status != 'pending':
        messages.warning(request, 'Only pending requests can be cancelled.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        borrow_request.status = 'cancelled'
        borrow_request.save()
        
        # Invalidate cache for lender's pending requests count
        cache_key = f'pending_borrow_requests_count_{borrow_request.lender.id}'
        cache.delete(cache_key)
        
        messages.success(request, 'Borrow request cancelled.')
        return redirect('products:product_detail', product_id=borrow_request.product.id)
    
    context = {
        'borrow_request': borrow_request,
    }
    
    return render(request, 'products/borrow_request_cancel.html', context)


@login_required
def my_borrow_requests(request):
    """
    View all borrow requests made by the user (as borrower)
    """
    from registration.models import User
    from .models import BorrowRequest
    
    user = User.objects.get(id=request.session['user_id'])
    
    borrow_requests = BorrowRequest.objects.filter(borrower=user).order_by('-created_at')
    
    # Pagination - 12 requests per page
    paginator = Paginator(borrow_requests, 12)
    page = request.GET.get('page')
    
    try:
        requests_page = paginator.page(page)
    except PageNotAnInteger:
        requests_page = paginator.page(1)
    except EmptyPage:
        requests_page = paginator.page(paginator.num_pages)
    
    context = {
        'borrow_requests': requests_page,
        'user': user,
        'paginator': paginator,
    }
    
    return render(request, 'products/my_borrow_requests.html', context)


@login_required
def my_lend_requests(request):
    """
    View all borrow requests received by the user (as lender)
    """
    from registration.models import User
    from .models import BorrowRequest
    
    user = User.objects.get(id=request.session['user_id'])
    
    lend_requests = BorrowRequest.objects.filter(lender=user).order_by('-created_at')
    
    # Separate by status (before pagination for stats)
    pending_requests = lend_requests.filter(status='pending')
    active_requests = lend_requests.filter(status='active')
    completed_requests = lend_requests.filter(status__in=['returned', 'rejected', 'cancelled'])
    
    # Pagination - 12 requests per page
    paginator = Paginator(lend_requests, 12)
    page = request.GET.get('page')
    
    try:
        requests_page = paginator.page(page)
    except PageNotAnInteger:
        requests_page = paginator.page(1)
    except EmptyPage:
        requests_page = paginator.page(paginator.num_pages)
    
    context = {
        'lend_requests': requests_page,
        'pending_requests': pending_requests,
        'active_requests': active_requests,
        'completed_requests': completed_requests,
        'user': user,
        'paginator': paginator,
    }
    
    return render(request, 'products/my_lend_requests.html', context)


@login_required
def product_history(request):
    """
    View product listing and deletion history for the current user
    """
    from registration.models import User
    
    user = User.objects.get(id=request.session['user_id'])
    
    # Get all history for this user
    history = ProductHistory.objects.filter(user=user).order_by('-action_date')
    
    # Filter by action if provided
    action_filter = request.GET.get('action')
    if action_filter and action_filter in ['created', 'updated', 'deleted', 'sold']:
        history = history.filter(action=action_filter)
    
    # Pagination - 20 items per page
    paginator = Paginator(history, 20)
    page = request.GET.get('page')
    
    try:
        history_page = paginator.page(page)
    except PageNotAnInteger:
        history_page = paginator.page(1)
    except EmptyPage:
        history_page = paginator.page(paginator.num_pages)
    
    # Calculate statistics
    total_created = ProductHistory.objects.filter(user=user, action='created').count()
    total_deleted = ProductHistory.objects.filter(user=user, action='deleted').count()
    total_updated = ProductHistory.objects.filter(user=user, action='updated').count()
    
    context = {
        'history': history_page,
        'user': user,
        'total_created': total_created,
        'total_deleted': total_deleted,
        'total_updated': total_updated,
        'action_filter': action_filter,
        'paginator': paginator,
    }
    
    return render(request, 'products/product_history.html', context)


@login_required
def get_pending_requests_count(request):
    """
    AJAX endpoint to get pending borrow requests count
    Used by navbar polling script
    Uses Django's cache framework to reduce database queries
    """
    # Get user_id from session (login_required decorator ensures this exists)
    user_id = request.session.get('user_id')
    
    if not user_id:
        return JsonResponse({
            'success': False,
            'pending_count': 0,
            'error': 'User not authenticated'
        })
    
    # Generate cache key for this user's pending requests count
    cache_key = f'pending_borrow_requests_count_{user_id}'
    
    # Try to get the count from cache first
    count = cache.get(cache_key)
    
    if count is None:
        # Cache miss - query the database
        count = BorrowRequest.objects.filter(
            lender_id=user_id,
            status='pending'
        ).count()
        
        # Store in cache for 5 minutes (300 seconds)
        cache.set(cache_key, count, 300)
    
    return JsonResponse({
        'success': True,
        'pending_count': count
    })


# ========== OTP Views (Uber-style Verification) ==========

@login_required
@lender_required
def generate_acceptance_otp(request, request_id):
    """
    Generate acceptance OTP when lender approves the borrow request
    Borrower will show this OTP when picking up the item
    """
    from .models import BorrowRequest
    from .otp_utils import create_acceptance_otp, send_otp_notification
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if request is in approved status
    if borrow_request.status != 'approved':
        messages.error(request, 'OTP can only be generated for approved requests.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Check if acceptance OTP already verified
    if borrow_request.acceptance_otp_verified:
        messages.warning(request, 'Acceptance OTP already verified.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Generate OTP
    otp = create_acceptance_otp(borrow_request)
    
    # Send notification to borrower
    send_otp_notification(borrow_request, otp, recipient_type='borrower')
    
    messages.success(request, f'Acceptance OTP generated: {otp.otp_code}. Share with the borrower.')
    return redirect('products:borrow_request_detail', request_id=request_id)


@login_required
@lender_required
def verify_acceptance_otp(request, request_id):
    """
    Verify acceptance OTP entered by borrower when picking up item
    This confirms the handover - similar to Uber's pickup verification
    """
    from .models import BorrowRequest
    from .otp_utils import verify_otp
    from registration.models import User
    from datetime import date, timedelta
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    user = User.objects.get(id=request.session['user_id'])
    
    # Check if request is in approved status
    if borrow_request.status != 'approved':
        messages.error(request, 'This request is not in approved status.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Check if already verified
    if borrow_request.acceptance_otp_verified:
        messages.warning(request, 'Acceptance OTP already verified.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code', '').strip()
        
        # Verify OTP
        success, message, otp = verify_otp(borrow_request, 'acceptance', entered_otp, user)
        
        if success:
            # Update borrow request status to active
            borrow_request.status = 'active'
            borrow_request.acceptance_otp_verified = True
            borrow_request.acceptance_otp_verified_at = timezone.now()
            borrow_request.start_date = date.today()
            borrow_request.expected_return_date = date.today() + timedelta(days=borrow_request.requested_days)
            borrow_request.save()
            
            # Mark product as currently borrowed
            product = borrow_request.product
            product.is_currently_borrowed = True
            product.save()
            
            messages.success(request, 'Item handover confirmed! Borrowing period has started.')
            return redirect('products:borrow_request_detail', request_id=request_id)
        else:
            messages.error(request, message)
    
    context = {
        'borrow_request': borrow_request,
    }
    
    return render(request, 'products/verify_acceptance_otp.html', context)


@login_required
@borrower_required
def generate_return_otp(request, request_id):
    """
    Generate return OTP when borrower is ready to return the item
    Lender will verify this OTP when receiving the item back
    """
    from .models import BorrowRequest
    from .otp_utils import create_return_otp, send_otp_notification
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if request is in active status
    if borrow_request.status != 'active':
        messages.error(request, 'Return OTP can only be generated for active borrowings.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Check if return OTP already verified
    if borrow_request.return_otp_verified:
        messages.warning(request, 'Return OTP already verified.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Generate OTP
    otp = create_return_otp(borrow_request)
    
    # Send notification to both borrower and lender
    send_otp_notification(borrow_request, otp)
    
    messages.success(request, f'Return OTP generated: {otp.otp_code}. This has been sent to you via chat. Show this OTP to the lender when returning the item.')
    return redirect('products:borrow_request_detail', request_id=request_id)


@login_required
@lender_required
def verify_return_otp(request, request_id):
    """
    Verify return OTP when borrower returns the item
    This confirms the return - similar to Uber's drop-off verification
    """
    from .models import BorrowRequest
    from .otp_utils import verify_otp
    from registration.models import User
    from datetime import date
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    user = User.objects.get(id=request.session['user_id'])
    
    # Check if request is in active status
    if borrow_request.status != 'active':
        messages.error(request, 'This item is not currently borrowed.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Check if already verified
    if borrow_request.return_otp_verified:
        messages.warning(request, 'Return OTP already verified.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code', '').strip()
        
        # Verify OTP
        success, message, otp = verify_otp(borrow_request, 'return', entered_otp, user)
        
        if success:
            # Update borrow request status to returned
            borrow_request.status = 'returned'
            borrow_request.return_otp_verified = True
            borrow_request.return_otp_verified_at = timezone.now()
            borrow_request.actual_return_date = date.today()
            borrow_request.save()
            
            # Mark product as available again
            product = borrow_request.product
            product.is_currently_borrowed = False
            product.save()
            
            messages.success(request, 'Item return confirmed! Transaction complete.')
            return redirect('products:borrow_request_detail', request_id=request_id)
        else:
            messages.error(request, message)
    
    context = {
        'borrow_request': borrow_request,
    }
    
    return render(request, 'products/verify_return_otp.html', context)


@login_required
def resend_otp_view(request, request_id, otp_type):
    """
    Resend/Regenerate OTP (for both acceptance and return)
    """
    from .models import BorrowRequest
    from .otp_utils import resend_otp, send_otp_notification
    from registration.models import User
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    user_id = request.session['user_id']
    
    # Validate OTP type
    if otp_type not in ['acceptance', 'return']:
        messages.error(request, 'Invalid OTP type.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Check permissions and status
    if otp_type == 'acceptance':
        # Only lender can resend acceptance OTP
        if borrow_request.lender.id != user_id:
            messages.error(request, 'Only the lender can resend acceptance OTP.')
            return redirect('products:borrow_request_detail', request_id=request_id)
        
        if borrow_request.status != 'approved':
            messages.error(request, 'Request must be approved to resend acceptance OTP.')
            return redirect('products:borrow_request_detail', request_id=request_id)
    else:  # return
        # Only borrower can resend return OTP
        if borrow_request.borrower.id != user_id:
            messages.error(request, 'Only the borrower can resend return OTP.')
            return redirect('products:borrow_request_detail', request_id=request_id)
        
        if borrow_request.status != 'active':
            messages.error(request, 'Request must be active to resend return OTP.')
            return redirect('products:borrow_request_detail', request_id=request_id)
    
    # Resend OTP
    otp = resend_otp(borrow_request, otp_type)
    
    # Send notification to both parties
    send_otp_notification(borrow_request, otp)
    
    messages.success(request, f'{otp_type.title()} OTP resent: {otp.otp_code}. Check your chat messages.')
    return redirect('products:borrow_request_detail', request_id=request_id)


@login_required
def get_otp_status(request, request_id):
    """
    AJAX endpoint to get current OTP status for a borrow request
    """
    from .models import BorrowRequest
    from .otp_utils import get_active_otp, get_otp_expiry_minutes
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    user_id = request.session['user_id']
    
    # Check if user is participant
    if borrow_request.borrower.id != user_id and borrow_request.lender.id != user_id:
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    data = {
        'success': True,
        'status': borrow_request.status,
        'acceptance_verified': borrow_request.acceptance_otp_verified,
        'return_verified': borrow_request.return_otp_verified,
    }
    
    # Get active acceptance OTP if exists
    if borrow_request.status == 'approved' and not borrow_request.acceptance_otp_verified:
        acceptance_otp = get_active_otp(borrow_request, 'acceptance')
        if acceptance_otp:
            data['acceptance_otp'] = {
                'code': acceptance_otp.otp_code if borrow_request.lender.id == user_id else '******',
                'expires_in_minutes': get_otp_expiry_minutes(acceptance_otp),
                'attempts': acceptance_otp.attempts,
                'max_attempts': acceptance_otp.max_attempts,
            }
    
    # Get active return OTP if exists
    if borrow_request.status == 'active' and not borrow_request.return_otp_verified:
        return_otp = get_active_otp(borrow_request, 'return')
        if return_otp:
            data['return_otp'] = {
                'code': return_otp.otp_code if borrow_request.borrower.id == user_id else '******',
                'expires_in_minutes': get_otp_expiry_minutes(return_otp),
                'attempts': return_otp.attempts,
                'max_attempts': return_otp.max_attempts,
            }
    
    return JsonResponse(data)


# ========================================
# PURCHASE/BUY VIEWS
# ========================================

@login_required
def purchase_request_create(request, product_id):
    """
    Create a purchase request for a product
    """
    from .models import PurchaseRequest
    from registration.models import User
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check if product is available for purchase
    if not product.can_be_purchased():
        messages.error(request, 'This item is not available for purchase.')
        return redirect('products:product_detail', product_id=product_id)
    
    # Check if user is not the owner
    if product.seller.id == request.session['user_id']:
        messages.error(request, 'You cannot buy your own item.')
        return redirect('products:product_detail', product_id=product_id)
    
    buyer = User.objects.get(id=request.session['user_id'])
    
    # Check if user already has a pending/approved request for this product
    existing_request = PurchaseRequest.objects.filter(
        product=product,
        buyer=buyer,
        status__in=['pending', 'approved']
    ).first()
    
    if existing_request:
        messages.warning(request, f'You already have a {existing_request.status} purchase request for this item.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        
        # Create purchase request
        purchase_request = PurchaseRequest.objects.create(
            product=product,
            buyer=buyer,
            seller=product.seller,
            message=message,
            purchase_price=product.price,
            status='pending'
        )
        
        # Invalidate cache for seller's pending requests count
        cache_key = f'pending_purchase_requests_count_{product.seller.id}'
        cache.delete(cache_key)
        
        messages.success(request, f'Purchase request sent! Price: ₹{product.price}')
        return redirect('products:purchase_request_detail', request_id=purchase_request.id)
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/purchase_request_create.html', context)


@login_required
def purchase_request_detail(request, request_id):
    """
    View details of a purchase request
    """
    from .models import PurchaseRequest
    from .otp_utils import get_active_purchase_otp
    
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    user_id = request.session['user_id']
    
    # Check if user is participant
    if purchase_request.buyer.id != user_id and purchase_request.seller.id != user_id:
        messages.error(request, 'You are not authorized to view this purchase request.')
        return redirect('products:product_list')
    
    # Get active OTP if exists
    active_otp = None
    if purchase_request.status == 'approved' and not purchase_request.handover_otp_verified:
        active_otp = get_active_purchase_otp(purchase_request)
    
    context = {
        'purchase_request': purchase_request,
        'is_buyer': purchase_request.buyer.id == user_id,
        'is_seller': purchase_request.seller.id == user_id,
        'active_otp': active_otp,
    }
    
    return render(request, 'products/purchase_request_detail.html', context)


@login_required
def purchase_request_approve(request, request_id):
    """
    Approve a purchase request (seller only) and generate OTP
    """
    from .models import PurchaseRequest
    from .otp_utils import send_purchase_otp_notification
    from django.db import transaction
    
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    
    # Check if user is the seller
    if purchase_request.seller.id != request.session['user_id']:
        messages.error(request, 'Only the seller can approve this request.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    # Check if already approved
    if purchase_request.status != 'pending':
        messages.warning(request, f'This request has already been {purchase_request.status}.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        seller_response = request.POST.get('seller_response', '')
        
        with transaction.atomic():
            # Update purchase request status
            purchase_request.status = 'approved'
            purchase_request.approved_date = timezone.now()
            purchase_request.seller_response = seller_response
            purchase_request.save()
            
            # Generate and send OTP notification
            success, message = send_purchase_otp_notification(purchase_request, 'handover')
            
            if success:
                messages.success(request, 'Purchase request approved! Handover OTP sent to buyer.')
            else:
                messages.warning(request, f'Request approved but failed to send OTP: {message}')
        
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    context = {
        'purchase_request': purchase_request,
    }
    
    return render(request, 'products/purchase_request_approve.html', context)


@login_required
def purchase_request_reject(request, request_id):
    """
    Reject a purchase request (seller only)
    """
    from .models import PurchaseRequest
    
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    
    # Check if user is the seller
    if purchase_request.seller.id != request.session['user_id']:
        messages.error(request, 'Only the seller can reject this request.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    # Check if can be rejected
    if purchase_request.status not in ['pending', 'approved']:
        messages.error(request, f'Cannot reject a {purchase_request.status} request.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        seller_response = request.POST.get('seller_response', '')
        
        purchase_request.status = 'rejected'
        purchase_request.seller_response = seller_response
        purchase_request.save()
        
        messages.success(request, 'Purchase request rejected.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    context = {
        'purchase_request': purchase_request,
    }
    
    return render(request, 'products/purchase_request_reject.html', context)


@login_required
def purchase_request_cancel(request, request_id):
    """
    Cancel a purchase request (buyer or seller)
    - Buyer can cancel pending or approved requests
    - Seller can cancel approved requests if handover hasn't happened
    """
    from .models import PurchaseRequest
    
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    user_id = request.session['user_id']
    
    is_buyer = purchase_request.buyer.id == user_id
    is_seller = purchase_request.seller.id == user_id
    
    # Check if user is participant
    if not (is_buyer or is_seller):
        messages.error(request, 'You are not authorized to cancel this request.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    # Check cancellation permissions
    can_cancel = False
    cancellation_reason = ""
    
    if is_buyer and purchase_request.can_be_cancelled_by_buyer():
        can_cancel = True
        cancellation_reason = "Cancelled by buyer"
    elif is_seller and purchase_request.can_be_cancelled_by_seller():
        can_cancel = True
        cancellation_reason = "Cancelled by seller (handover not completed)"
    
    if not can_cancel:
        messages.error(request, f'Cannot cancel a {purchase_request.status} request at this stage.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        user_reason = request.POST.get('cancellation_reason', '').strip()
        
        # Build cancellation message
        full_reason = cancellation_reason
        if user_reason:
            full_reason += f": {user_reason}"
        
        purchase_request.status = 'cancelled'
        purchase_request.seller_response = (
            f"{purchase_request.seller_response}\n\n{full_reason}"
            if purchase_request.seller_response
            else full_reason
        ).strip()
        purchase_request.save()
        
        messages.success(request, 'Purchase request cancelled successfully.')
        
        # Redirect based on user role
        if is_buyer:
            return redirect('products:my_purchase_requests')
        else:
            return redirect('products:my_sale_requests')
    
    context = {
        'purchase_request': purchase_request,
        'is_buyer': is_buyer,
        'is_seller': is_seller,
    }
    
    return render(request, 'products/purchase_request_cancel.html', context)


@login_required
def my_purchase_requests(request):
    """
    View all purchase requests made by the current user (as buyer)
    """
    from .models import PurchaseRequest
    from registration.models import User
    
    user = User.objects.get(id=request.session['user_id'])
    purchase_requests = PurchaseRequest.objects.filter(
        buyer=user
    ).select_related('product', 'seller').order_by('-created_at')
    
    context = {
        'purchase_requests': purchase_requests,
        'is_buyer_view': True,
    }
    
    return render(request, 'products/my_purchase_requests.html', context)


@login_required
def my_sale_requests(request):
    """
    View all purchase requests received by the current user (as seller)
    """
    from .models import PurchaseRequest
    from registration.models import User
    
    user = User.objects.get(id=request.session['user_id'])
    purchase_requests = PurchaseRequest.objects.filter(
        seller=user
    ).select_related('product', 'buyer').order_by('-created_at')
    
    # Get counts by status
    pending_count = purchase_requests.filter(status='pending').count()
    approved_count = purchase_requests.filter(status='approved').count()
    completed_count = purchase_requests.filter(status='completed').count()
    
    context = {
        'purchase_requests': purchase_requests,
        'is_seller_view': True,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'completed_count': completed_count,
    }
    
    return render(request, 'products/my_sale_requests.html', context)


@login_required
def verify_purchase_handover_otp(request, request_id):
    """
    Verify handover OTP for purchase (seller verifies)
    """
    from .models import PurchaseRequest
    from .otp_utils import verify_purchase_otp
    from registration.models import User
    
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    user = User.objects.get(id=request.session['user_id'])
    
    # Check if user is the seller
    if purchase_request.seller.id != user.id:
        messages.error(request, 'Only the seller can verify handover OTP.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    # Check if request is approved
    if purchase_request.status != 'approved':
        messages.error(request, 'Request must be approved to verify OTP.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    # Check if already verified
    if purchase_request.handover_otp_verified:
        messages.info(request, 'Handover OTP already verified.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        entered_otp = request.POST.get('otp_code', '').strip()
        
        if not entered_otp:
            messages.error(request, 'Please enter the OTP code.')
            context = {
                'purchase_request': purchase_request,
            }
            return render(request, 'products/verify_purchase_handover_otp.html', context)
        
        # Verify OTP (includes product availability update in transaction)
        try:
            success, message, otp = verify_purchase_otp(purchase_request, user, entered_otp)
            
            if success:
                # Double-check that product state was updated
                purchase_request.refresh_from_db()
                product = purchase_request.product
                product.refresh_from_db()
                
                # Verify the transaction completed successfully
                if (purchase_request.status == 'completed' and 
                    purchase_request.handover_otp_verified and 
                    not product.is_available):
                    messages.success(
                        request, 
                        'Handover OTP verified! Purchase completed successfully. '
                        'The product has been marked as sold.'
                    )
                    return redirect('products:purchase_request_detail', request_id=request_id)
                else:
                    # Transaction might have partially failed
                    messages.error(
                        request,
                        'OTP verification succeeded but there was an issue updating the product state. '
                        'Please contact support.'
                    )
                    context = {
                        'purchase_request': purchase_request,
                    }
                    return render(request, 'products/verify_purchase_handover_otp.html', context)
            else:
                messages.error(request, f'Verification failed: {message}')
                context = {
                    'purchase_request': purchase_request,
                }
                return render(request, 'products/verify_purchase_handover_otp.html', context)
                
        except Exception as e:
            # Handle any database or unexpected errors
            messages.error(
                request,
                f'An error occurred during verification: {str(e)}. Please try again.'
            )
            context = {
                'purchase_request': purchase_request,
            }
            return render(request, 'products/verify_purchase_handover_otp.html', context)
    
    context = {
        'purchase_request': purchase_request,
    }
    return render(request, 'products/verify_purchase_handover_otp.html', context)


@login_required
def resend_purchase_otp(request, request_id):
    """
    Resend/Regenerate handover OTP for purchase
    """
    from .models import PurchaseRequest
    from .otp_utils import create_purchase_handover_otp, send_purchase_otp_notification
    
    purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
    user_id = request.session['user_id']
    
    # Only seller can resend OTP
    if purchase_request.seller.id != user_id:
        messages.error(request, 'Only the seller can resend handover OTP.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    if purchase_request.status != 'approved':
        messages.error(request, 'Request must be approved to resend OTP.')
        return redirect('products:purchase_request_detail', request_id=request_id)
    
    # Resend OTP
    success, message = send_purchase_otp_notification(purchase_request, 'handover')
    
    if success:
        messages.success(request, 'Handover OTP resent. Check chat messages.')
    else:
        messages.error(request, f'Failed to resend OTP: {message}')
    
    return redirect('products:purchase_request_detail', request_id=request_id)


# ============================================================================
# MAP AND LOCATION VIEWS
# ============================================================================

@login_required
def product_map(request):
    """Display all available products on an interactive map"""
    from registration.models import User
    from registration.geocoding_utils import (
        get_distance_between_users,
        approximate_coordinates
    )
    from django.db.models import Q
    import json
    
    current_user = request.session.get('user_id')
    user = get_object_or_404(User, id=current_user)
    
    # Get filter parameters
    category = request.GET.get('category', '')
    max_distance = request.GET.get('distance', '')  # in km
    listing_type = request.GET.get('type', '')  # sell, lend, both
    
    # Base query - available products with location
    products = Product.objects.filter(
        is_available=True,
        seller__latitude__isnull=False,
        seller__longitude__isnull=False
    ).select_related('seller')
    
    # Apply filters
    if category:
        products = products.filter(category=category)
    
    if listing_type:
        if listing_type in ['sell', 'lend']:
            products = products.filter(Q(listing_type=listing_type) | Q(listing_type='both'))
        else:
            products = products.filter(listing_type=listing_type)
    
    # Calculate distances and filter by max_distance
    products_with_distance = []
    for product in products:
        distance = get_distance_between_users(user, product.seller)
        
        if max_distance and distance:
            try:
                if distance > float(max_distance):
                    continue
            except ValueError:
                pass
        
        # Use approximate location for privacy
        if product.seller.share_precise_location:
            lat, lng = product.seller.latitude, product.seller.longitude
        else:
            lat, lng = approximate_coordinates(
                product.seller.latitude,
                product.seller.longitude
            )
        
        products_with_distance.append({
            'id': product.id,
            'title': product.title,
            'category': product.get_category_display(),
            'price': float(product.price) if product.price else None,
            'borrow_price': float(product.borrow_price_per_day) if product.borrow_price_per_day else None,
            'listing_type': product.listing_type,
            'image_url': product.image1.url if product.image1 else None,
            'latitude': float(lat) if lat else None,
            'longitude': float(lng) if lng else None,
            'distance': distance,
            'seller_name': product.seller.name or 'Anonymous',
            'seller_city': product.seller.city,
        })
    
    # User's location
    user_location = None
    if user.has_location():
        user_location = {
            'latitude': float(user.latitude),
            'longitude': float(user.longitude),
            'name': user.name or 'You'
        }
    
    context = {
        'products_json': json.dumps(products_with_distance),
        'user_location_json': json.dumps(user_location),
        'categories': Product.CATEGORY_CHOICES,
        'selected_category': category,
        'selected_distance': max_distance,
        'selected_type': listing_type,
        'user': user,
    }
    
    return render(request, 'products/product_map.html', context)


@login_required
@rate_limit(max_requests=30, window_seconds=60)
def product_distance_api(request, product_id):
    """
    API endpoint to get distance to a product.
    
    Security features:
    - Rate limited to 30 requests per minute per user
    - Verifies product availability
    - Respects seller privacy settings
    - Only returns distance when both parties have location data
    - Returns appropriate HTTP status codes
    """
    from registration.models import User
    from registration.geocoding_utils import get_distance_between_users
    
    current_user = request.session.get('user_id')
    user = get_object_or_404(User, id=current_user)
    
    # Get product and verify it exists
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Check if product is available
    if not product.is_available:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Check if requester has location data
    if not user.has_location():
        return JsonResponse({
            'error': 'Please set your location in your profile to see distances',
            'has_location': False
        }, status=400)
    
    # Check if seller has location data
    if not product.seller.has_location():
        return JsonResponse({
            'error': 'Distance information not available for this product',
            'has_location': False
        }, status=404)
    
    # Privacy check: Seller must allow location sharing (at least approximate)
    # We only show distance if seller has enabled some form of location visibility
    # Note: For public product browsing, we check if seller has any location set up
    # For precise location, users need to use per-request sharing in approved transactions
    if not product.seller.latitude or not product.seller.longitude:
        return JsonResponse({
            'error': 'Location information not available',
            'has_location': False
        }, status=403)
    
    # Calculate distance
    try:
        distance = get_distance_between_users(user, product.seller)
        
        if distance is None:
            return JsonResponse({
                'error': 'Unable to calculate distance',
                'has_location': False
            }, status=400)
        
        return JsonResponse({
            'distance': distance,
            'distance_formatted': f"{distance:.1f} km",
            'has_location': True
        })
    except Exception as e:
        # Log error but don't expose details to user
        return JsonResponse({
            'error': 'Error calculating distance',
            'has_location': False
        }, status=500)


@login_required
def meeting_point_api(request, request_id, request_type):
    """
    API endpoint to get suggested meeting point for a request
    request_type: 'borrow' or 'purchase'
    """
    from registration.models import User
    from registration.geocoding_utils import get_meeting_point
    from .models import PurchaseRequest
    
    current_user = request.session.get('user_id')
    user = get_object_or_404(User, id=current_user)
    
    # Get the request
    if request_type == 'borrow':
        req = get_object_or_404(BorrowRequest, id=request_id)
        other_user = req.lender if req.borrower.id == user.id else req.borrower
        
        # Only show for approved/active requests
        if req.status not in ['approved', 'active']:
            return JsonResponse({'error': 'Request not approved yet'}, status=403)
        
        # Check location sharing permissions - ONLY use per-request flag
        # This ensures explicit consent for each transaction
        if req.borrower.id == user.id:
            can_see_location = req.lender_shares_location
        else:
            can_see_location = req.borrower_shares_location
    else:
        req = get_object_or_404(PurchaseRequest, id=request_id)
        other_user = req.seller if req.buyer.id == user.id else req.buyer
        
        # Only show for approved/completed requests
        if req.status not in ['approved', 'completed']:
            return JsonResponse({'error': 'Request not approved yet'}, status=403)
        
        # Check location sharing permissions - ONLY use per-request flag
        # This ensures explicit consent for each transaction
        if req.buyer.id == user.id:
            can_see_location = req.seller_shares_location
        else:
            can_see_location = req.buyer_shares_location
    
    # Get meeting point
    meeting = get_meeting_point(user, other_user)
    
    if not meeting:
        # Check which user is missing location
        if not user.has_location():
            return JsonResponse({'error': 'Please set your location in your profile before using this feature'}, status=400)
        elif not other_user.has_location():
            return JsonResponse({'error': 'The other party has not set their location yet'}, status=400)
        else:
            return JsonResponse({'error': 'Cannot calculate meeting point. Please ensure both users have valid addresses.'}, status=400)
    
    # Add user locations
    result = {
        'meeting_point': meeting,
        'user1': {
            'name': user.name or 'You',
            'latitude': float(user.latitude),
            'longitude': float(user.longitude),
        },
        'user2': {
            'name': other_user.name or 'Other user',
            'latitude': float(other_user.latitude) if can_see_location else None,
            'longitude': float(other_user.longitude) if can_see_location else None,
            'approximate_location': other_user.get_approximate_location(),
            'shares_location': can_see_location
        }
    }
    
    return JsonResponse(result)


@login_required
def toggle_location_sharing(request, request_id, request_type):
    """Toggle location sharing for a specific request"""
    from registration.models import User
    from .models import PurchaseRequest
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)
    
    current_user = request.session.get('user_id')
    user = get_object_or_404(User, id=current_user)
    
    # Get the request
    if request_type == 'borrow':
        req = get_object_or_404(BorrowRequest, id=request_id)
        
        # Check if user is part of this request
        if req.borrower.id != user.id and req.lender.id != user.id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Only allow for approved/active requests
        if req.status not in ['approved', 'active']:
            return JsonResponse({'error': 'Request must be approved'}, status=400)
        
        # Toggle appropriate field
        if req.borrower.id == user.id:
            req.borrower_shares_location = not req.borrower_shares_location
            shares_location = req.borrower_shares_location
        else:
            req.lender_shares_location = not req.lender_shares_location
            shares_location = req.lender_shares_location
        
        req.save()
        
    else:  # purchase
        req = get_object_or_404(PurchaseRequest, id=request_id)
        
        # Check if user is part of this request
        if req.buyer.id != user.id and req.seller.id != user.id:
            return JsonResponse({'error': 'Unauthorized'}, status=403)
        
        # Only allow for approved/completed requests
        if req.status not in ['approved', 'completed']:
            return JsonResponse({'error': 'Request must be approved'}, status=400)
        
        # Toggle appropriate field
        if req.buyer.id == user.id:
            req.buyer_shares_location = not req.buyer_shares_location
            shares_location = req.buyer_shares_location
        else:
            req.seller_shares_location = not req.seller_shares_location
            shares_location = req.seller_shares_location
        
        req.save()
    
    return JsonResponse({
        'success': True,
        'shares_location': shares_location,
        'message': 'Location sharing enabled' if shares_location else 'Location sharing disabled'
    })


@login_required
@rate_limit(max_requests=60, window_seconds=60)
def live_location_api(request, request_id, request_type):
    '''Handle live location updates from seller/lender and polling by the other party.'''
    from registration.models import User

    current_user = request.session.get('user_id')
    get_object_or_404(User, id=current_user)
    request_type = (request_type or '').lower()

    if request_type == 'borrow':
        req = get_object_or_404(BorrowRequest, id=request_id)
        owner_user = req.lender
        viewer_user = req.borrower
        allowed_status = ['approved', 'active']
        share_enabled = req.lender_shares_location
        live_prefix = 'lender'
    elif request_type == 'purchase':
        req = get_object_or_404(PurchaseRequest, id=request_id)
        owner_user = req.seller
        viewer_user = req.buyer
        allowed_status = ['approved', 'completed']
        share_enabled = req.seller_shares_location
        live_prefix = 'seller'
    else:
        return JsonResponse({'error': 'Invalid request type'}, status=400)

    if owner_user is None or viewer_user is None:
        return JsonResponse({'error': 'Participants not found'}, status=400)

    if current_user not in [owner_user.id, viewer_user.id]:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    if req.status not in allowed_status:
        return JsonResponse({'error': 'Not authorized'}, status=403)

    live_enabled_attr = f'{live_prefix}_live_tracking_enabled'
    live_lat_attr = f'{live_prefix}_live_latitude'
    live_lng_attr = f'{live_prefix}_live_longitude'
    live_updated_attr = f'{live_prefix}_live_updated_at'

    if request.method == 'POST':
        if owner_user.id != current_user:
            return JsonResponse({'error': 'Only the seller or lender can send live location'}, status=403)
        if not share_enabled:
            return JsonResponse({'error': 'Enable precise location sharing before live tracking'}, status=400)

        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)

        is_active = payload.get('is_active', True)
        update_fields = [live_enabled_attr, live_lat_attr, live_lng_attr, live_updated_attr, 'updated_at']

        if not is_active:
            setattr(req, live_enabled_attr, False)
            setattr(req, live_lat_attr, None)
            setattr(req, live_lng_attr, None)
            setattr(req, live_updated_attr, None)
            req.save(update_fields=update_fields)
            return JsonResponse({'success': True, 'is_active': False})

        latitude = payload.get('latitude')
        longitude = payload.get('longitude')

        if latitude is None or longitude is None:
            return JsonResponse({'error': 'Latitude and longitude are required'}, status=400)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Invalid coordinates supplied'}, status=400)

        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            return JsonResponse({'error': 'Coordinates out of bounds'}, status=400)

        setattr(req, live_enabled_attr, True)
        setattr(req, live_lat_attr, latitude)
        setattr(req, live_lng_attr, longitude)
        setattr(req, live_updated_attr, timezone.now())
        req.save(update_fields=update_fields)

        return JsonResponse({'success': True, 'is_active': True})

    if request.method == 'GET':
        live_enabled = getattr(req, live_enabled_attr)
        latitude = getattr(req, live_lat_attr)
        longitude = getattr(req, live_lng_attr)
        updated_at = getattr(req, live_updated_attr)

        is_active = bool(share_enabled and live_enabled and latitude is not None and longitude is not None)

        return JsonResponse({
            'is_active': is_active,
            'latitude': float(latitude) if is_active else None,
            'longitude': float(longitude) if is_active else None,
            'updated_at': updated_at.isoformat() if updated_at else None,
        })

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
@rate_limit(max_requests=30, window_seconds=60)
def route_to_meeting_point(request, request_id, request_type):
    """
    API endpoint to get route from OSRM for meeting point.
    
    Security features:
    - Rate limited to 30 requests per minute per user
    - Verifies user is participant in the request
    - Respects location sharing settings
    - Returns GeoJSON route geometry
    """
    from registration.models import User
    from django.conf import settings
    import requests as http_requests
    
    current_user = request.session.get('user_id')
    user = get_object_or_404(User, id=current_user)
    
    # Get the request based on type
    if request_type == 'borrow':
        borrow_request = get_object_or_404(BorrowRequest, id=request_id)
        
        # Only show for approved/active requests
        if borrow_request.status not in ['approved', 'active']:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        is_lender = borrow_request.product.seller.id == current_user
        is_borrower = borrow_request.borrower.id == current_user
        
        if not (is_lender or is_borrower):
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        user1 = borrow_request.product.seller
        user2 = borrow_request.borrower
        user1_shares = borrow_request.lender_shares_location
        user2_shares = borrow_request.borrower_shares_location
    else:  # purchase
        purchase_request = get_object_or_404(PurchaseRequest, id=request_id)
        
        # Only show for approved/completed requests
        if purchase_request.status not in ['approved', 'completed']:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        is_seller = purchase_request.product.seller.id == current_user
        is_buyer = purchase_request.buyer.id == current_user
        
        if not (is_seller or is_buyer):
            return JsonResponse({'error': 'Not authorized'}, status=403)
        
        user1 = purchase_request.product.seller
        user2 = purchase_request.buyer
        user1_shares = purchase_request.seller_shares_location
        user2_shares = purchase_request.buyer_shares_location
    
    # Check if both users have location data
    if not user1.has_location() or not user2.has_location():
        return JsonResponse({'error': 'Both parties need location data'}, status=400)
    
    # Get coordinates (use precise if shared, otherwise approximate)
    from registration.geocoding_utils import approximate_coordinates
    
    # Seller/lender location (destination)
    if user1_shares:
        seller_lat, seller_lng = user1.latitude, user1.longitude
    else:
        seller_lat, seller_lng = approximate_coordinates(user1.latitude, user1.longitude)
    
    # Buyer/borrower location (start point)
    if user2_shares:
        buyer_lat, buyer_lng = user2.latitude, user2.longitude
    else:
        buyer_lat, buyer_lng = approximate_coordinates(user2.latitude, user2.longitude)
    
    # Route: buyer/borrower goes to seller/lender
    # If current user is seller/lender, show reverse route (from seller to buyer)
    if current_user == user1.id:
        start_lat, start_lng = seller_lat, seller_lng
        end_lat, end_lng = buyer_lat, buyer_lng
    else:
        start_lat, start_lng = buyer_lat, buyer_lng
        end_lat, end_lng = seller_lat, seller_lng
    
    # Query OSRM for route (from start to end location)
    osrm_url = getattr(settings, 'OSRM_BASE_URL', 'http://localhost:5000')
    route_url = f"{osrm_url}/route/v1/driving/{start_lng},{start_lat};{end_lng},{end_lat}?overview=full&geometries=geojson"
    
    try:
        response = http_requests.get(route_url, timeout=10)
        response.raise_for_status()
        route_data = response.json()
        
        if route_data.get('code') != 'Ok':
            return JsonResponse({'error': 'Route calculation failed'}, status=500)
        
        # Check if routes exist
        if not route_data.get('routes') or len(route_data['routes']) == 0:
            return JsonResponse({'error': 'No route found between these locations'}, status=404)
            
        # Extract route geometry and summary
        route = route_data['routes'][0]
        geometry = route['geometry']
        distance = route['distance'] / 1000  # Convert to km
        duration = route['duration'] / 60  # Convert to minutes
        
        return JsonResponse({
            'geometry': geometry,
            'distance_km': distance,
            'duration_minutes': duration
        })
    except http_requests.RequestException as e:
        return JsonResponse({'error': 'Routing service unavailable'}, status=503)
    except Exception as e:
        return JsonResponse({'error': 'Error calculating route'}, status=500)

