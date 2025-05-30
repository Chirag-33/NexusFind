import re
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Contact, Product, Comment

# Home View
class HomeView(View):
    def get(self, request):
        products = Product.objects.all()
        return render(request, 'home.html', context={'title': 'Home', 'products': products})

# About View
class AboutView(View):
    def get(self, request):
        return render(request, 'about.html', context={'title': 'About'})

# Contact View
class ContactView(View):
    def get(self, request):
        if request.user.is_authenticated:
            user_profile = getattr(request.user, 'profile', None)
            user_email = user_profile.email if user_profile and user_profile.email else request.user.email
            return render(request, 'contact.html', {'title': 'Contact', 'user_name': request.user.get_full_name() or request.user.username, 'user_email': user_email, 'show_login_prompt': False})
        else:
            return render(request, 'contact.html', {'title': 'Contact', 'show_login_prompt': True})

    def post(self, request):
        if not request.user.is_authenticated:
            messages.info(request, "Please sign in to send a message.")
            return redirect('/contact/?next=' + request.path)
        user_name = request.user.get_full_name() or request.user.username
        user_profile = getattr(request.user, 'profile', None)
        user_email = user_profile.email if user_profile and user_profile.email else request.user.email
        user_message = request.POST.get('message')
        attachment = request.FILES.get('file_path')
        if len(user_message.strip()) < 4:
            messages.error(request, 'Message too short. Please enter a more detailed message.')
            return redirect('contact')
        contact = Contact(name=user_name, email=user_email, message=user_message, file_path=attachment)
        contact.save()
        messages.success(request, 'Your message has been sent successfully!')
        return redirect('contact')

# Search View
class SearchView(View):
    def get(self, request):
        query = request.GET.get('query', '').strip()
        product_list = []
        if query and len(query) <= 78:
            product_list = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query) | Q(price__icontains=query)).order_by('-created_at')
        else:
            if len(query) > 78:
                messages.warning(request, "Search query too long. Please shorten it.")
        if not product_list:
            messages.warning(request, f'No search results found for "{query}". Please refine your query.')
        paginator = Paginator(product_list, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'search.html', {'title': 'Search', 'query': query, 'allProducts': page_obj})

# SignUp View
class SignUpView(View):
    def get(self, request):
        return render(request, "home.html")

    def post(self, request):
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirmPassword']
        if len(username) < 4 or len(password) < 4 or not username.isalnum():
            messages.error(request, 'Username/Password must be at least 4 characters long. And Username should only contain alphanumeric characters.')
            return render(request, "home.html")
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, "home.html")
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, "home.html")
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        login(request, user)
        messages.success(request, f'Welcome, {user.username}! You have successfully signed up.')
        next_url = request.POST.get('next', '/')
        return redirect(next_url)

# SignIn View
class SignInView(View):
    def get(self, request):
        return render(request, "home.html")

    def post(self, request):
        username_or_email = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            try:
                user = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user.username, password=password)
            except User.DoesNotExist:
                user = None
        if user is not None:
            login(request, user)
            next_url = request.POST.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username/email or password.')
            return render(request, "home.html")

# SignOut View
class SignOutView(View):
    def post(self, request):
        username = request.user.username
        logout(request)
        messages.success(request, f'{username} you have successfully logged out')
        next_url = request.POST.get('next', request.GET.get('next', '/'))
        return redirect(next_url if next_url.strip() else '/')

# Product Detail View
class ProductDetailView(View):
    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            comments = Comment.objects.filter(product=product, parent=None).order_by('-created_at')
            similar_products = Product.objects.filter(category=product.category).exclude(id=product_id)[:5]
        except Product.DoesNotExist:
            return redirect('home')
        return render(request, 'product_detail.html', {'product': product, 'comments': comments, 'similar_products': similar_products})

    def post(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist: return redirect('home')
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        if content:
            comment = Comment(product=product, user=request.user, content=content)
            if parent_id:
                try:
                    parent_comment = Comment.objects.get(id=parent_id)
                    comment.parent = parent_comment
                except Comment.DoesNotExist:
                    messages.error(request, "Parent comment does not exist.")
                    return redirect('product_detail', product_id=product_id)
            comment.save()
            messages.success(request, 'Your comment has been posted!')
        return redirect('product_detail', product_id=product_id)

# Information Page View
def info_page_view(request, page_type):
    allowed_pages = ['faq', 'returns', 'term', 'shipping']
    page_type = page_type.lower()
    if page_type not in allowed_pages:
        return render(request, '404.html', status=400)
    return render(request, 'info_page_view.html', {"page_type": page_type})