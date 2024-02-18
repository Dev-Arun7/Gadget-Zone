$(document).ready(function(){

    $('.payWithRazorpay').click(function (e){
        e.preventDefault();

        var selects = document.querySelector("[name='addressId").value;
        var token = $(" [ name='csrfmiddlewaretoken']").val();
        if (selects === "") {
            swal("Alert", "Select your address", "warning");
            return false;
        }
        else
        {
            console.log('else'); 
            $.ajax({
                method: "GET",
                url: "/razorpay",
                success: function (response) {
                     var amount=response.total_offer_price
                     var options = {
                         "key": "rzp_test_oR7x1WyMRe9zxr", // Enter the Key ID generated from the Dashboard
                         "amount": 1 * 100,
                        //  amount*100, 
                         "currency": "INR",
                         "name": "Gadgetzone", //your business name
                         "description": "Thank you for your purchase",
                         "image": "https://www.picng.com/upload/letter_g/png_letter_g_50866.png",
                         // "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                         "handler": function (responseb){
                            //  alert(responseb.razorpay_payment_id);
                             data = {
                                "payment_mode": "razorpay",
                                "payment_id": responseb.razorpay_payment_id,
                                csrfmiddlewaretoken: token,   
                             }
                             $.ajax({
                                method:"POST",
                                url: "/place_order",
                                data: data,
                                success: function (responsec){
                                    swal("Razorpay is working...!", responsec.status, "success").then((value) => {
                                        // window.location.href = '/home' 
                                       
                                    });
                                    
                                }

                            });
                            $("#order-form").submit();
                         },
                         "prefill": { //We recommend using the prefill parameter to auto-fill customer's contact information, especially their phone number
                             "name": "Gadgetzone", //your customer's name
                             "email": "gaurav.kumar@example.com", 
                             "contact": "9000090000"  //Provide the customer's phone number for better conversion rates 
                         },
                         "theme": {
                             "color": "#3399cc"
                         }
                     };

                    var rzp1 = new Razorpay(options);
                    rzp1.on('payment.failed', function (response){
                            alert(response.error.code);
                            alert(response.error.description);
                            alert(response.error.source);
                            alert(response.error.step);
                            alert(response.error.reason);
                            alert(response.error.metadata.order_id);
                            alert(response.error.metadata.payment_id);
                    });
                    rzp1.open();
                   
                }
            });
           
        }
    });
});



