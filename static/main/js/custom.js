$(document).ready(function(){

    $('.increment-btn').click(function (e) {
        e.preventDefault();
        var inc_value = $(this).closest('.product_data').find('.qty-input').val();
        var value = parseInt(inc_value, 10);
        value = isNaN(value) ? 0 : value;
        if (value < 10) {
            value++;
            $(this).closest('.product_data').find('.qty-input').val(value);
        }
    });

    $('.decrement-btn').click(function (e) {
        e.preventDefault();
        var dec_value = $(this).closest('.product_data').find('.qty-input').val();
        var value = parseInt(dec_value, 10);
        value = isNaN(value) ? 0 : value;
        if (value > 1) {
            value--;
            $(this).closest('.product_data').find('.qty-input').val(value);
        }
    });

    $('.addToCartBtn').click(function (e) {
        e.preventDefault();
    
        var product_id = $(this).closest('.single-add-to-cart').find('.prod_id').val();
        var variant_id = $(this).closest('.single-add-to-cart').find('.variant_id').val(); 
        var product_qty = $(this).closest('.single-add-to-cart').find('.qty-input').val(); 
        var token = $('input[name=csrfmiddlewaretoken]').val(); 
        $.ajax({
            method: "POST",
            url: "/add_to_cart/" + product_id  + "/" + variant_id + "/",
            data: {
                'product_id': product_id,
                'variant_id': variant_id, 
                'product_qty': product_qty,
                'csrfmiddlewaretoken': token  
            },
            success: function (response) {
                console.log(response);
                if (response.added) {
                    // Show success message using SweetAlert
                    Swal.fire({
                        title: "Success!",
                        text: response.status,
                        icon: "success"
                    });
                } else {
                    // Handle other responses or errors
                    // For example, if the product is already in the cart
                    // You can show a warning message
                    Swal.fire({
                        title: "Warning!",
                        text: response.status,
                        icon: "warning"
                    });
                }
            },
            error: function(xhr, errmsg, err) {
                // Handle errors if any
                console.log(xhr.status + ": " + xhr.responseText); // Log the error for debugging
            }
        });
    });
    
    $('.changeQuantity').click(function (e) {
        console.log("---------------")
        e.preventDefault();
    
        var product_id = $(this).closest('.tr').find('.prod_id').val();
        var variant_id = $(this).closest('.tr').find('.variant_id').val(); 
        var product_qty = $(this).closest('.tr').find('.qty-input').val();
        var token = $('input[name=csrfmiddlewaretoken]').val();
        
    
        $.ajax({
            method: "POST",
            url: "/update_cart/",
            data: {
                'product_id': product_id,
                'variant_id': variant_id,
                'product_qty': product_qty,
                'csrfmiddlewaretoken': token
            },
            success: function (response) {
                console.log("response",response)
                // alert(response.status);
                // Redirect to the cart page after successful update
                // window.location.href = response.redirect_url;
                window.location.href = "/cart/"
            }
        });
    });

    $('.delete_cart_item').click(function (e) {
        e.preventDefault();
    
        // Use closest() to find the closest tr element
        var productRow = $(this).closest('tr');
    
        // Find the hidden input with class 'prod_id' within the tr element
        var product_id = productRow.find('.prod_id').val();
    
        // Ensure product_id is not undefined or null before sending the request
        if (product_id !== undefined && product_id !== null) {
            var token = $('input[name=csrfmiddlewaretoken]').val();
    
            $.ajax({
                method: "POST",
                url: "/delete_cart/",
                data: {
                    'product_id': product_id,
                    'csrfmiddlewaretoken': token
                },
                success: function (response) {
                alertify.success(response.status);
                $('.cart_data').load(location.href + " .cart_data");

                }
            });
        } else {
            console.error("Product ID is undefined or null.");
        }
    });

});
