var updateBtns = document.getElementsByClassName('update-cart');

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function() {
        var productId = this.dataset.product;
        var action = this.dataset.action;

        // Check if user is available
        if (user == 'AnonymousUser') {
            console.log('User is not authenticated');
        } else {
            updateUserOrder(productId, action)
        }
    });
}

function updateUserOrder(productId, action){
    console.log('User is logged in, sending data..')

    var url = '/update_item/'

    fetch(url,{
        method:'POST',
        headers:{
            'Content-type': 'application/json'
        },
        body:JSON.stringify({'productID': productId, 'action':action})
    })
    .then((response) =>{
        return response.json()
    })
    .then((data) =>{
        console.log('data:',data)
    })
}

 