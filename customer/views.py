from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile, ProfileForm, CustomerAddressForm
from checkout.models import Order

@login_required
def profile_view(request):
    user = request.user
    # Use user's email as default to avoid empty email
    defaults = {'email': user.email or f'{user.username}@example.com'}
    profile, created = Profile.objects.get_or_create(user=user, defaults=defaults)
    address_instance = profile.address if hasattr(profile, 'address') else None
    editing = request.GET.get('edit') == '1' or request.method == 'POST'

    if request.method == 'POST':
        if request.GET.get('remove_picture') == '1':
            profile.profile_picture.delete()
            profile.profile_picture = None
            profile.save()
            messages.success(request, "Profile picture removed successfully.")
            return redirect('profile')
        else:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
            address_form = CustomerAddressForm(request.POST, instance=address_instance)
            new_username = request.POST.get('username')
            if new_username and new_username != user.username:
                if User.objects.filter(username=new_username).exclude(id=user.id).exists():
                    form.add_error(None, "This username is already taken.")
                else:
                    user.username = new_username
                    user.save()
                    messages.success(request, "Username updated successfully.")
            if form.is_valid() and address_form.is_valid():
                profile = form.save()
                if address_form.has_changed():  # Only save address if changed
                    address = address_form.save(commit=False)
                    address.user = user
                    address.save()
                    profile.address = address
                    profile.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('profile')
            else:
                messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile)
        address_form = CustomerAddressForm(instance=address_instance)

    history = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')
    recent_history = history[:3]  # Limit to 3 most recent orders for profile section
    total_orders = history.count()  # Total number of orders for numbering
    return render(request, 'profile.html', {
        'user': user,
        'profile': profile,
        'form': form,
        'address_form': address_form,
        'history': history,
        'recent_history': recent_history,
        'total_orders': total_orders,
        'editing': editing
    })