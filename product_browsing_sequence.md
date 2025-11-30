# Product Browsing Sequence Diagram

## Overview
This sequence diagram shows the product browsing workflow, including listing products with pagination, search/filter capabilities, and viewing product details with atomic view counter increments.

## Sequence Diagram

```mermaid
sequenceDiagram
    actor User as User (Browser)
    participant View as Product List View
    participant Model as Product Model
    participant DB as Database
    participant Paginator as Django Paginator
    participant DetailView as Product Detail View

    Note over User,DetailView: Product Browsing Flow

    rect rgb(240, 248, 255)
        Note right of User: PRODUCT LIST PAGE
        
        User->>View: GET /products/?category=&search=&page=
        
        View->>DB: Product.objects.filter(is_available=True)
        DB-->>View: QuerySet of products
        
        opt Category Filter Applied
            View->>View: Filter by category
            Note right of View: category__in=['Books', 'Notes', etc.]
        end
        
        opt Search Query Applied
            View->>View: Filter by search term
            Note right of View: title__icontains=search_query
        end
        
        View->>Paginator: Paginator(products, 12)
        Note right of Paginator: 12 products per page
        
        Paginator->>Paginator: Calculate total pages
        
        alt Valid Page Number
            Paginator-->>View: Page object with products
        else Invalid Page (Non-integer)
            Paginator-->>View: First page (page 1)
        else Empty Page (Out of range)
            Paginator-->>View: Last page
        end
        
        View->>User: Render product list with pagination
        Note over User: Displays:<br/>- Product cards (12)<br/>- Pagination controls<br/>- Category filters<br/>- Search bar
    end

    rect rgb(255, 248, 240)
        Note right of User: PRODUCT DETAIL PAGE
        
        User->>DetailView: Click product → GET /products/{id}/
        
        DetailView->>DB: get_object_or_404(Product, id=id)
        
        alt Product Not Found
            DB-->>DetailView: 404 Not Found
            DetailView->>User: Show 404 error page
        else Product Found
            DB-->>DetailView: Product object
            
            DetailView->>DB: Atomic increment view count
            Note right of DB: UPDATE products<br/>SET views = F('views') + 1<br/>WHERE id = {id}
            Note over DB: F() expression prevents<br/>race conditions
            
            DetailView->>DB: Get related products
            Note right of DB: Same category,<br/>is_available=True,<br/>exclude current product,<br/>limit 4
            
            DB-->>DetailView: Related products list
            
            opt User Logged In
                DetailView->>DetailView: Check if owner
                Note right of DetailView: product.seller.id ==<br/>session['user_id']
            end
            
            DetailView->>User: Render product detail page
            Note over User: Displays:<br/>- Product info<br/>- Images gallery<br/>- Seller details<br/>- Related products<br/>- Action buttons
        end
    end
```

## Flow Description

### Actors and Participants

1. **User (Browser)** - Student browsing the marketplace
2. **Product List View** - View handling product listing (`products/views.py`)
3. **Product Model** - Django model for products
4. **Database** - SQLite database with product data
5. **Django Paginator** - Built-in pagination utility
6. **Product Detail View** - View handling individual product display

### Product List Flow

1. **Request with Parameters**
   - User navigates to `/products/`
   - Optional URL parameters:
     - `category` - Filter by category
     - `search` - Search query
     - `page` - Page number

2. **Database Query**
   - Base query: `Product.objects.filter(is_available=True)`
   - Only shows available products
   - Ordered by `-created_at` (newest first)

3. **Filtering**
   - **Category Filter**: If category parameter present:
     - `products.filter(category=category)`
   - **Search Filter**: If search query present:
     - `products.filter(title__icontains=search_query)`
     - Case-insensitive partial matching

4. **Pagination**
   - Django Paginator splits results into pages of 12
   - Handles edge cases:
     - Non-integer page → Returns page 1
     - Out of range → Returns last page
   - Preserves filters across pagination

5. **Render List**
   - Shows product cards with:
     - Product image (or emoji fallback)
     - Title, price, condition
     - Category badge
     - Seller info (limited if not logged in)

### Product Detail Flow

1. **Product Request**
   - User clicks product card
   - Navigates to `/products/{id}/`

2. **Product Lookup**
   - `get_object_or_404()` queries database
   - Returns 404 if product not found
   - Returns product object if found

3. **View Counter (Atomic)**
   - Uses Django's **F() expression** for atomic increment
   - `Product.objects.filter(pk=pk).update(views=F('views') + 1)`
   - **Race condition safe**: Prevents count loss from concurrent views
   - Increments directly in database without loading object

4. **Related Products**
   - Queries products with:
     - Same category
     - `is_available=True`
     - Excludes current product
     - Limits to 4 results

5. **Ownership Check**
   - If user logged in:
     - Compares `product.seller.id` with `session['user_id']`
     - Sets `is_owner` flag
   - Determines which buttons to show:
     - **Owner**: Edit/Delete buttons
     - **Other user**: Contact Seller button
     - **Anonymous**: Login prompt

6. **Render Detail**
   - Product information
   - Image gallery (up to 5 images)
   - Seller details (full if logged in, limited if anonymous)
   - Pricing and condition
   - Related products section
   - Action buttons based on ownership

## Key Features

- **Pagination**: 12 products per page with smart navigation
- **Filter Preservation**: Category and search maintained across pages
- **Atomic View Counter**: Race condition-safe using F() expressions
- **Privacy Control**: Limited seller info for anonymous users
- **Related Products**: Intelligent recommendations based on category
- **Ownership Detection**: Different UI for product owners
- **Search Functionality**: Case-insensitive title search
- **Category Filtering**: 5 categories (Books, Notes, Electronics, Stationery, Lab Equipment)

## Related Files

- [products/views.py](file:///d:/projects/mini%20project/products/views.py#L15-L51) - Product list view
- [products/views.py](file:///d:/projects/mini%20project/products/views.py#L53-L79) - Product detail view
- [products/models.py](file:///d:/projects/mini%20project/products/models.py) - Product model
- [products/templates/products/product_list.html](file:///d:/projects/mini%20project/products/templates/products) - List template
- [products/templates/products/product_detail.html](file:///d:/projects/mini%20project/products/templates/products) - Detail template
