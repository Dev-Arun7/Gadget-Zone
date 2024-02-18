    
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@never_cache
def dashboard(request):
    orders = Order.objects.order_by("-id")
    labels = []
    data = []
    for order in orders:
        labels.append(str(order.id))
        data.append(float(order.amount))  # Convert Decimal to float

    total_customers = Customer.objects.count()

    # Calculate the count of new users in the last one week
    one_week_ago = timezone.now() - timezone.timedelta(weeks=1)
    new_users_last_week = Customer.objects.filter(date_joined__gte=one_week_ago).count()

    # Get the total number of orders
    total_orders = Order.objects.count()

    # Calculate the count of orders in the last one week
    orders_last_week = Order.objects.filter(date__gte=one_week_ago).count()

    # Calculate the total amount received
    total_amount_received = Order.objects.aggregate(
        total_amount_received=Cast(Sum(F('amount')), FloatField())
    )['total_amount_received'] or 0

    # Calculate the total amount received in the last week
    total_amount_received_last_week = Order.objects.filter(date__gte=one_week_ago).aggregate(
        total_amount_received=Cast(Sum(F('amount')), FloatField())
    )['total_amount_received'] or 0
    print(total_amount_received_last_week)


    categories = Category.objects.annotate(num_products=Count('product'))
    category_labels = [category.category_name for category in categories]
    category_data = [category.num_products for category in categories]

    total_products = Product.objects.count()

    time_interval = request.GET.get('time_interval', 'all')  # Default to 'all' if not provided
    if time_interval == 'yearly':
        orders = Order.objects.annotate(date_truncated=TruncYear('date', output_field=DateField()))
        orders = orders.values('date_truncated').annotate(total_amount=Sum('amount'))
    elif time_interval == 'monthly':
        orders = Order.objects.annotate(date_truncated=TruncMonth('date', output_field=DateField()))
        orders = orders.values('date_truncated').annotate(total_amount=Sum('amount'))
    else:
        # Default to 'all' or handle other time intervals as needed
        orders = Order.objects.annotate(date_truncated=F('date'))
        orders = orders.values('date_truncated').annotate(total_amount=Sum('amount'))

    # Calculate monthly sales
    monthly_sales = Order.objects.annotate(
        month=TruncMonth('date')
    ).values('month').annotate(total_amount=Sum('amount')).order_by('month')

    # Extract data for the monthly sales chart
    monthly_labels = [entry['month'].strftime('%B %Y') for entry in monthly_sales]
    monthly_data = [float(entry['total_amount']) for entry in monthly_sales]

    # Add this block to handle AJAX request for filtered data
    headers = HttpHeaders(request.headers)
    is_ajax_request = headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax_request and request.method == 'GET':
        time_interval = request.GET.get('time_interval', 'all')
        filtered_labels = []
        filtered_data = []

        if time_interval == 'yearly':
            filtered_orders = Order.objects.annotate(
                date_truncated=TruncYear('date', output_field=DateField())
            )
        elif time_interval == 'monthly':
            filtered_orders = Order.objects.annotate(
                date_truncated=TruncMonth('date', output_field=DateField())
            )
        else:
            # Default to 'all' or handle other time intervals as needed
            filtered_orders = Order.objects.annotate(date_truncated=F('date'))

        filtered_orders = filtered_orders.values('date_truncated').annotate(total_amount=Sum('amount')).order_by('date_truncated')

        filtered_labels = [entry['date_truncated'].strftime('%B %Y') for entry in filtered_orders]
        filtered_data = [float(entry['total_amount']) for entry in filtered_orders]

        return JsonResponse({"labels": filtered_labels, "data": filtered_data})
    context = {
        "labels": json.dumps(labels),
        "data": json.dumps(data),
        "total_customers": total_customers,
        "new_users_last_week": new_users_last_week,
        "total_orders": total_orders,
        "orders_last_week": orders_last_week,
        "total_amount_received": total_amount_received,
        "total_amount_received": total_amount_received_last_week,
        "total_products": total_products,
        "category_labels": json.dumps(category_labels),
        "category_data": json.dumps(category_data),
    }
    context.update({
        "monthly_labels": json.dumps(monthly_labels),
        "monthly_data": json.dumps(monthly_data),
    })

    if "admin" in request.session:
        return render(request, "dashboard/home.html", context)
    else:
        return redirect("admin")