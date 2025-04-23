from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile, ProfileForm, CustomerAddressForm
from checkout.models import Order
from django.http import JsonResponse


@login_required
def profile_view(request):
    user = request.user
    profile, _ = Profile.objects.get_or_create(user=user)
    address_instance = profile.address if hasattr(profile, 'address') else None
    editing = request.GET.get('edit') == '1' or request.method == 'POST'

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        address_form = CustomerAddressForm(request.POST, instance=address_instance)
        if form.is_valid() and address_form.is_valid():
            profile = form.save()
            address = address_form.save(commit=False)
            address.user = user
            address.save()
            profile.address = address
            profile.save()
            return redirect('profile')  # back to view mode
    else:
        form = ProfileForm(instance=profile)
        address_form = CustomerAddressForm(instance=address_instance)

    history = Order.objects.filter(user=user).prefetch_related('items__product').order_by('-created_at')
    return render(request, 'profile.html', {
        'profile': profile,
        'form': form,
        'address_form': address_form,
        'history': history,
        'editing': editing
    })
