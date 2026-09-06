from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Room, Booking
from .forms import CustomerRegistrationForm, BookingForm,AvailabilitySearchForm
from datetime import datetime

def home(request):

    featured = Room.objects.filter(
        is_available=True
    )[:4]


    search_form = AvailabilitySearchForm()


    context = {

        'featured': featured,

        'search_form': search_form,

    }


    return render(
        request,
        'home.html',
        context
    )
def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'room_list.html', {'rooms': rooms})

def room_detail(request, pk):

    room = get_object_or_404(
        Room,
        pk=pk
    )


    check_in = request.GET.get(
        'check_in'
    )

    check_out = request.GET.get(
        'check_out'
    )

    num_guests = request.GET.get(
        'num_guests'
    )


    context = {

        'room': room,

        'check_in': check_in,

        'check_out': check_out,

        'num_guests': num_guests,

    }


    return render(
        request,
        'room_detail.html',
        context
    )

def register(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('dashboard')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        messages.error(request, "Invalid username or password")
    return render(request, 'login.html')

@login_required
def dashboard(request):
    bookings = Booking.objects.filter(customer=request.user).order_by('-check_in_date')
    return render(request, 'dashboard.html', {'bookings': bookings})

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, pk=room_id)

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.room = room

            days = (booking.check_out_date - booking.check_in_date).days
            if days <= 0:
                messages.error(request, "Check-out date must be after check-in date.")
                return render(request, 'book_room.html', {'form': form, 'room': room})

            booking.total_amount = room.price_per_night * days

            # Check for overlapping bookings
            overlap = Booking.objects.filter(
                room=room,
                check_in_date__lt=booking.check_out_date,
                check_out_date__gt=booking.check_in_date,
                status__in=['pending', 'confirmed', 'checked_in']
            ).exists()

            if overlap:
                messages.error(request, "Room is not available for the selected dates.")
            else:
                booking.save()
                messages.success(request, f"Booking successful for Room {room.room_number}!")
                return redirect('dashboard')
    else:

        initial_data = {}


        check_in = request.GET.get(
            'check_in'
        )

        check_out = request.GET.get(
            'check_out'
        )

        num_guests = request.GET.get(
            'num_guests'
        )


    if check_in:

        initial_data[
            'check_in_date'
        ] = check_in


    if check_out:

        initial_data[
            'check_out_date'
        ] = check_out


    if num_guests:

        initial_data[
            'num_guests'
        ] = num_guests


    form = BookingForm(
        initial=initial_data
    )

    return render(request, 'book_room.html', {'form': form, 'room': room})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

def search_rooms(request):

    form = AvailabilitySearchForm(
        request.GET or None
    )

    rooms = Room.objects.none()


    if form.is_valid():

        check_in = form.cleaned_data[
            'check_in'
        ]

        check_out = form.cleaned_data[
            'check_out'
        ]

        num_guests = form.cleaned_data[
            'num_guests'
        ]


        # Step 1:
        # Find bookings that overlap
        # with the requested dates.

        overlapping_bookings = Booking.objects.filter(

            check_in_date__lt=check_out,

            check_out_date__gt=check_in,

            status__in=[
                'pending',
                'confirmed',
                'checked_in',
            ]

        )


        # Step 2:
        # Get the IDs of rooms
        # already occupied.

        unavailable_room_ids = (
            overlapping_bookings
            .values_list(
                'room_id',
                flat=True
            )
        )


        # Step 3:
        # Find rooms that:
        #
        # - are active
        # - hold enough guests
        # - are not already booked

        rooms = (
            Room.objects
            .filter(
                is_available=True,
                capacity__gte=num_guests,
            )
            .exclude(
                id__in=unavailable_room_ids
            )
        )


        context = {

            'form': form,

            'rooms': rooms,

            'check_in': check_in,

            'check_out': check_out,

            'num_guests': num_guests,

        }


        return render(
            request,
            'search_results.html',
            context
        )


    context = {

        'form': form,

        'rooms': rooms,

    }


    return render(
        request,
        'search_results.html',
        context
    )