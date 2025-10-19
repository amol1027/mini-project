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

