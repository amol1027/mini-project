from django.shortcuts import render, get_object_or_404
from django.contrib import messages
from django.db.models import F
from .models import Product

def product_list(request):
    """
    Display list of all available products
    """
    products = Product.objects.filter(is_available=True)
    
    # Filter by category if provided
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        products = products.filter(title__icontains=search_query)
    
    context = {
        'products': products,
        'selected_category': category,
        'search_query': search_query,
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
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'products/product_detail.html', context)

