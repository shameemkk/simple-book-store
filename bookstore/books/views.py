from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from .forms import BookForm
from .models import Book
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .models import Cart, CartItem, Book
from django.db.models import Q
import stripe


# Create your views here.
@login_required
def home(request):
    user=request.user
    if user.is_staff:
        return redirect('dashboard')
    else:
        return redirect('booklist_main')
    

@login_required 
@staff_member_required(login_url='dashboard')   
def dashboard(request):
    from django.db.models import Q

@login_required
@staff_member_required(login_url='dashboard')
def dashboard(request):
    search_query = request.GET.get('q','')
    if search_query:
        # Use Q objects to filter books based on multiple fields  title or author)
        books = Book.objects.filter(Q(title__icontains=search_query) | Q(author__icontains=search_query))
    else:
        books = Book.objects.all()
    
    paginator = Paginator(books, 5)  
    page_number = request.GET.get('page')
    try:
        books_page = paginator.page(page_number)
    except PageNotAnInteger:
        books_page = paginator.page(1)
    except EmptyPage:
        books_page = paginator.page(paginator.num_pages)
    
    context = {
        'book': books_page,
        'search_query': search_query
    }
    return render(request, 'dashboard.html', context)

@login_required
@staff_member_required(login_url='dashboard')
def upload_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'Book "{book.title}" has been successfully added.')
            return redirect('dashboard')  
    else:
        form = BookForm()
    
    return render(request, 'upload_book.html', {'form': form})

 

    

@login_required
@staff_member_required(login_url='dashboard')
def delete_book(request,id):
    book=Book.objects.get(id=id)
    book.delete()
    return redirect('dashboard')


@login_required
@staff_member_required(login_url='dashboard')
def update_book(request, id):
    book = Book.objects.get(id=id)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            # Delete old image if a new one is uploaded
            if 'image' in request.FILES:
                if book.image:
                    book.image.delete()
            updated_book = form.save()
            messages.success(request, f'Book "{updated_book.title}" has been successfully updated.')
            return redirect('dashboard')  
    else:
        form = BookForm(instance=book)
    
    return render(request, 'update_book.html', {'form': form, 'book': book})


@login_required
@staff_member_required(login_url='dashboard')
def book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    context = {
        'book': book,
        'title': f"{book.title} - Book Details",
    }
    return render(request, 'book_detail.html', context)


@login_required
def view_book_main(request):
    search_query = request.GET.get('q','')
    if search_query:
        # Use Q objects to filter books based on multiple fields  title or author)
        books = Book.objects.filter(Q(title__icontains=search_query) | Q(author__icontains=search_query))
    else:
        books = Book.objects.all()
    
    paginator = Paginator(books, 8)  
    page_number = request.GET.get('page')
    try:
        books_page = paginator.page(page_number)
    except PageNotAnInteger:
        books_page = paginator.page(1)
    except EmptyPage:
        books_page = paginator.page(paginator.num_pages)
    
    context = {
        'books': books_page,
        'search_query': search_query
    }
    return render(request,'book_main_list.html',context)  

@login_required
def book_detail_main(request, pk):
    book = Book.objects.get(pk=pk)
    context = {
        'book': book,
        'title': f"{book.title} - Book Details",
    }
    return render(request,'bookAddcart.html', context)





@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart) 
    total_price = 0
    for item in cart_items:  
        total_price += item.quantity * item.book.price
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})

@login_required
def increase_quantity(request, item_id):
    item = CartItem.objects.get(id=item_id)
    if item.quantity < item.book.quantity:
        item.book.quantity -= 1
        item.book.save()
        item.quantity += 1
        item.save()
        messages.success(request, f"Quantity of '{item.book.title}' increased.")
    else:
        messages.warning(request, f"Sorry, we don't have more '{item.book.title}' in stock.")
    return redirect('view_cart')

@login_required
def decrease_quantity(request, item_id):
    item = CartItem.objects.get(id=item_id)
    if item.quantity > 1:
        item.book.quantity += 1
        item.book.save()
        item.quantity -= 1
        item.save()
        messages.success(request, f"Quantity of '{item.book.title}' decreased.")
    else:
        item.delete()
        messages.success(request, f"'{item.book.title}' removed from your cart.")
    return redirect('view_cart')

@login_required
def remove_from_cart(request, item_id):
    item = CartItem.objects.get(id=item_id)
    item.book.quantity += item.quantity
    item.book.save()
    item.delete()
    messages.success(request, f"'{item.book.title}' removed from your cart.")
    return redirect('view_cart')

@login_required
def add_to_cart(request, book_id):
    book = Book.objects.get(id=book_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, book=book)
    if not created:
        if cart_item.quantity < book.quantity:
            cart_item.quantity += 1
            cart_item.save()
            book.quantity -= 1  
            book.save()
            messages.success(request, f"'{book.title}' quantity increased in your cart.")
        else:
            messages.warning(request, f"Sorry, we don't have more '{book.title}' in stock.")
    else:
        messages.success(request, f"'{book.title}' added to your cart.")
    return redirect('view_cart')



@login_required
def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    cart= Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        messages.warning(request, "Your cart is empty.")
        return redirect('view_cart')

    # Create a list of items to send to Stripe
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': item.book.title,
                },
                'unit_amount': int(item.book.price * 100), 
            },
            'quantity': item.quantity,
        })

    # Create a checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/home/'),
        cancel_url=request.build_absolute_uri('/home/'),
    )

    return redirect(session.url, code=303)