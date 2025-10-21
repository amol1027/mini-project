from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product
from .history_models import ProductHistory
from .forms import ProductForm
from .decorators import login_required, owner_required, lender_required, borrower_required, request_participant_required

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
        try:
            # Handle image deletions first (but NOT image1 - primary image cannot be deleted)
            import os
            deleted_images = []
            
            # Start from image2 (i=2) since image1 is the primary and cannot be deleted
            for i in range(2, 6):
                delete_field = f'delete_image{i}'
                # Check if delete checkbox was checked
                if delete_field in request.POST and request.POST.get(delete_field):
                    image_field = f'image{i}'
                    image = getattr(product, image_field, None)
                    
                    if image:
                        # Delete the physical file
                        try:
                            if hasattr(image, 'path'):
                                file_path = image.path
                                if os.path.isfile(file_path):
                                    os.remove(file_path)
                                    print(f"Deleted file: {file_path}")
                        except Exception as e:
                            print(f"Error deleting image file for {image_field}: {e}")
                        
                        # Clear the field in the database
                        setattr(product, image_field, None)
                        deleted_images.append(image_field)
            
            # Save the product if any images were deleted
            if deleted_images:
                product.save(update_fields=[f'image{i}' for i in range(2, 6)] + ['updated_at'])
                messages.info(request, f'Deleted {len(deleted_images)} image(s)')
            
            # Now process the form with updated product instance
            form = ProductForm(request.POST, request.FILES, instance=product)
            
            if form.is_valid():
                updated_product = form.save()
                messages.success(request, f'Product "{updated_product.title}" updated successfully!')
                return redirect('products:product_detail', product_id=updated_product.id)
            else:
                messages.error(request, 'Please correct the errors below.')
                
        except Exception as e:
            messages.error(request, f'An error occurred: {str(e)}')
            print(f"Error in product_edit: {e}")
            import traceback
            traceback.print_exc()
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
    
    # Check if user already has a pending/active request for this product
    existing_request = BorrowRequest.objects.filter(
        product=product,
        borrower=borrower,
        status__in=['pending', 'approved', 'active']
    ).first()
    
    if existing_request:
        messages.warning(request, f'You already have a {existing_request.status} borrow request for this item.')
        return redirect('products:product_detail', product_id=product_id)
    
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
    """
    from .models import BorrowRequest
    from datetime import date, timedelta
    from django.utils import timezone
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if request is pending
    if borrow_request.status != 'pending':
        messages.warning(request, f'This request is already {borrow_request.status}.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
    if request.method == 'POST':
        response_message = request.POST.get('response_message', '')
        
        # Update request status
        borrow_request.status = 'active'
        borrow_request.approved_date = timezone.now()
        borrow_request.start_date = date.today()
        borrow_request.expected_return_date = date.today() + timedelta(days=borrow_request.requested_days)
        borrow_request.lender_response = response_message
        borrow_request.save()
        
        # Mark product as currently borrowed
        product = borrow_request.product
        product.is_currently_borrowed = True
        product.save()
        
        messages.success(request, 'Borrow request approved! The borrower can now collect the item.')
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

