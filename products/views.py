from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import F
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Product
from .forms import ProductForm

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

def product_create(request):
    """
    Create a new product listing
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to upload a product.')
        return redirect('login:login')
    
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

def product_edit(request, product_id):
    """
    Edit an existing product
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to edit products.')
        return redirect('login:login')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user is the owner
    if product.seller.id != request.session['user_id']:
        messages.error(request, 'You can only edit your own products.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.title}" updated successfully!')
            return redirect('products:product_detail', product_id=product.id)
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

def product_delete(request, product_id):
    """
    Delete a product (soft delete by marking as unavailable)
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to delete products.')
        return redirect('login:login')
    
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user is the owner
    if product.seller.id != request.session['user_id']:
        messages.error(request, 'You can only delete your own products.')
        return redirect('products:product_detail', product_id=product_id)
    
    if request.method == 'POST':
        product_title = product.title
        product.delete()  # Hard delete
        messages.success(request, f'Product "{product_title}" has been deleted.')
        return redirect('products:product_list')
    
    context = {
        'product': product,
    }
    
    return render(request, 'products/product_confirm_delete.html', context)

def my_products(request):
    """
    Display user's own products
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to view your products.')
        return redirect('login:login')
    
    from registration.models import User
    user = User.objects.get(id=request.session['user_id'])
    
    products = Product.objects.filter(seller=user).order_by('-created_at')
    
    # Calculate statistics
    total_products = products.count()
    available_count = products.filter(is_available=True).count()
    total_views = sum(product.views for product in products)
    avg_price = sum(product.price for product in products) // total_products if total_products > 0 else 0
    
    context = {
        'products': products,
        'user': user,
        'total_products': total_products,
        'available_count': available_count,
        'total_views': total_views,
        'avg_price': avg_price,
    }
    
    return render(request, 'products/my_products.html', context)


# ========== Borrow/Lend Views ==========

def borrow_request_create(request, product_id):
    """
    Create a borrow request for a product
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to borrow items.')
        return redirect('login:login')
    
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


def borrow_request_detail(request, request_id):
    """
    View details of a borrow request
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to view borrow requests.')
        return redirect('login:login')
    
    from .models import BorrowRequest
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if user is involved in this request
    user_id = request.session['user_id']
    if borrow_request.borrower.id != user_id and borrow_request.lender.id != user_id:
        messages.error(request, 'You do not have permission to view this request.')
        return redirect('products:product_list')
    
    is_lender = borrow_request.lender.id == user_id
    is_borrower = borrow_request.borrower.id == user_id
    
    context = {
        'borrow_request': borrow_request,
        'is_lender': is_lender,
        'is_borrower': is_borrower,
    }
    
    return render(request, 'products/borrow_request_detail.html', context)


def borrow_request_approve(request, request_id):
    """
    Approve a borrow request (lender only)
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login:login')
    
    from .models import BorrowRequest
    from datetime import date, timedelta
    from django.utils import timezone
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if user is the lender
    if borrow_request.lender.id != request.session['user_id']:
        messages.error(request, 'Only the lender can approve this request.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
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


def borrow_request_reject(request, request_id):
    """
    Reject a borrow request (lender only)
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login:login')
    
    from .models import BorrowRequest
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if user is the lender
    if borrow_request.lender.id != request.session['user_id']:
        messages.error(request, 'Only the lender can reject this request.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
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


def borrow_request_return(request, request_id):
    """
    Mark an item as returned (lender confirms return)
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login:login')
    
    from .models import BorrowRequest
    from datetime import date
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if user is the lender
    if borrow_request.lender.id != request.session['user_id']:
        messages.error(request, 'Only the lender can mark items as returned.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
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


def borrow_request_cancel(request, request_id):
    """
    Cancel a borrow request (borrower only, for pending requests)
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login first.')
        return redirect('login:login')
    
    from .models import BorrowRequest
    
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)
    
    # Check if user is the borrower
    if borrow_request.borrower.id != request.session['user_id']:
        messages.error(request, 'Only the borrower can cancel this request.')
        return redirect('products:borrow_request_detail', request_id=request_id)
    
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


def my_borrow_requests(request):
    """
    View all borrow requests made by the user (as borrower)
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to view your borrow requests.')
        return redirect('login:login')
    
    from registration.models import User
    from .models import BorrowRequest
    
    user = User.objects.get(id=request.session['user_id'])
    
    borrow_requests = BorrowRequest.objects.filter(borrower=user).order_by('-created_at')
    
    context = {
        'borrow_requests': borrow_requests,
        'user': user,
    }
    
    return render(request, 'products/my_borrow_requests.html', context)


def my_lend_requests(request):
    """
    View all borrow requests received by the user (as lender)
    """
    # Check if user is logged in
    if 'user_id' not in request.session:
        messages.error(request, 'Please login to view lend requests.')
        return redirect('login:login')
    
    from registration.models import User
    from .models import BorrowRequest
    
    user = User.objects.get(id=request.session['user_id'])
    
    lend_requests = BorrowRequest.objects.filter(lender=user).order_by('-created_at')
    
    # Separate by status
    pending_requests = lend_requests.filter(status='pending')
    active_requests = lend_requests.filter(status='active')
    completed_requests = lend_requests.filter(status__in=['returned', 'rejected', 'cancelled'])
    
    context = {
        'lend_requests': lend_requests,
        'pending_requests': pending_requests,
        'active_requests': active_requests,
        'completed_requests': completed_requests,
        'user': user,
    }
    
    return render(request, 'products/my_lend_requests.html', context)

