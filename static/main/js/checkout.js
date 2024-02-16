$(document).ready(function(){

    $('.payWithRazorpay').click(function (e){
        e.preventDefault();

        var selects = document.querySelector("[name='addressId").value;
        if (selects === "") {
            swal("Alert", "Select your address", "warning");
            return false;
        }
        else
        {
            $.ajax({
                method: "GET",
                url: "/razorpay",
                success: function (response) {
                    // console.log(response);
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

            var options = {
                "key": "rzp_test_NVkSrkfRfkhnIQ", // Enter the Key ID generated from the Dashboard
                "amount": response.total_offer_price, 
                "currency": "INR",
                "name": "Acme Corp", //your business name
                "description": "Thank you for your purchase",
                "image": "https://www.picng.com/upload/letter_g/png_letter_g_50866.png",
                // "order_id": "order_9A33XWu170gUtm", //This is a sample Order ID. Pass the `id` obtained in the response of Step 1
                "handler": function (response){
                    alert(response.razorpay_payment_id);

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
           
        }
    });
});