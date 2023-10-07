
function Add_template(Name, Desc, modal = "none") {
    var elem = document.createElement('div');
    elem.setAttribute('class', "col-sm-6 mb-3");
    var ch1 = document.createElement('div');
    ch1.setAttribute('class', "card h-100");
    var ch2 = document.createElement('div');
    ch2.setAttribute('class', "card-body");
    ch2.innerHTML = `<h6 class="d-flex align-items-center mb-3" style="font-size:20px;">${Name}</h6>
    <p>${Desc}</p><hr style="padding:0px;margin:0px;"><div style="margin-top:5px;padding:0px;text-align:right;">
    <a class="btn btn-info btn-md" style=" background-color:lightgreen;"${modal} >Go</a></div>`;
    ch1.appendChild(ch2);
    elem.appendChild(ch1);
    document.getElementById('Content-Div').appendChild(elem);
}


function show_super_admin_content() {
    Add_template('Create Admin', 'Add a new Admin for this system');
    Add_template('Delete Admin', 'Remove Admin account');
   
}

function show_admin_content() {

    var elem2 = document.createElement('h4');
    elem2.textContent = "ADMIN SECTION";
    elem2.style.color = 'blue';
    document.getElementById("Content-Div").appendChild(elem2);
    Add_template('Change Toll Rate', 'Modify the current Toll Rates');
    Add_template('Modify Discounts', 'Issue new or modify existing Discount offers.');
    
}

function show_user_content() {

    
    Add_template('All Transactions', 'Check your lifetime transactions', 'data-bs-toggle="modal" data-bs-target="#RecentModal"');

}
document.addEventListener('DOMContentLoaded', function () {
    // Make a query to the URL and save the data in a variable
    
    fetch('/load_recent_transactions')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.transactions.length > 0) {
                var recentTransactions = data.transactions.slice(0, 5); // Limit to 5 transactions
                const listGroup = document.querySelector('.list-group');
                var alltransactions = data.transactions;
                // Iterate over the recent transactions and create list items
                recentTransactions.forEach(transaction => {
                    const listItem = document.createElement('li');
                    listItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');

                    // Create a div to hold the transaction details
                    const transactionDiv = document.createElement('div');
                    transactionDiv.textContent = transaction.data.Type;

                    // Calculate the value (Amount - GlobalDiscount - Cupons + Gst)
                    const value = transaction.data.Amount - transaction.data.GlobalDiscount - transaction.data.Cupon + transaction.data.Gst;
                    const valueSpan = document.createElement('span');

                    // Add a plus sign and make it green for "Add Money," otherwise add a negative sign and make it red
                    if (transaction.data.Type === 'Add Money') {
                        valueSpan.innerHTML = `+ &#8377;${value.toFixed(2)}`; // Format to 2 decimal places
                        valueSpan.style.color = 'green';
                    } else {
                        valueSpan.innerHTML = `- &#8377;${Math.abs(value).toFixed(2)}`; // Format to 2 decimal places
                        valueSpan.style.color = 'red';
                    }

                    // Append the transaction details and value to the list item
                    listItem.appendChild(transactionDiv);
                    listItem.appendChild(valueSpan);

                    // Append the list item to the list group
                    listGroup.appendChild(listItem);
                });

                alltransactions.forEach(transaction => {
                    fillModalBody(transaction);
                });
            } else {
                // Handle the case where there are no recent transactions
                fillModalBodyDummy('No recent transactions !');
                console.log('No recent transactions available');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

function fillModalBodyDummy(text) {
    const listGroup = document.querySelector('.list-group');
    const listItem = document.createElement('li');
    listItem.classList.add('list-group-item', 'd-flex', 'justify-content-between', 'align-items-center');

    // Create a div to hold the transaction details
    const transactionDiv = document.createElement('div');
    transactionDiv.textContent =text;
    listItem.appendChild(transactionDiv);
    listGroup.appendChild(listItem);
    const modalBody = document.getElementById("RecentModalbody");
    const transactionType = document.createElement('p');
    transactionType.textContent = text;
    modalBody.appendChild(transactionType);
}

    // Function to fill the modal body with transaction details
    function fillModalBody(transactionData) {
        const modalBody = document.getElementById("RecentModalbody");

        // Create and append elements for transaction details
        const transactionType = document.createElement('p');
        transactionType.textContent = `Transaction Type: ${transactionData.data.Type}`;
        if (transactionData.data.Type==='Add Money'){
            transactionType.style.color ='#43e66e';
        }else{
            transactionType.style.color = '#de282b';
        }
        transactionType.style.textAlign='center';
        // Create a new Date object from the provided DateTime string
        const transactionDateTime = new Date(transactionData.DateTime);

        // Convert the date to IST (Indian Standard Time)
        transactionDateTime.setMinutes(transactionDateTime.getMinutes() -330); // IST is UTC+5:30

        // Format the date as a string in IST
        const formattedDate = transactionDateTime.toLocaleString('en-US', {
            timeZone: 'Asia/Kolkata', // IST timezone
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            second: 'numeric'
        });

        // Create and append the element for the formatted date
        const transactionDate = document.createElement('p');
        transactionDate.textContent = `Transaction Date: ${formattedDate}`;


        const priceBreakup = document.createElement('p');
        const price = transactionData.data.Amount - transactionData.data.GlobalDiscount - transactionData.data.Cupon + transactionData.data.Gst;
        priceBreakup.textContent = `Net Amount: ${price.toFixed(2)}`;

        const transactionId = document.createElement('p');
        transactionId.textContent = `Transaction ID: ${transactionData.ReferenceNumber}`;

        // Append the elements to the modal body
        var div = document.createElement('div');

        div.style.padding = '10px'; // Add padding to create some space around the content
        div.style.border ='1px solid #381c03';
        div.style.background="white";
        div.appendChild(transactionType);
        div.appendChild(transactionDate);
        div.appendChild(priceBreakup);
        div.appendChild(transactionId);
        
        modalBody.appendChild(div);
        
    }



function toggleAddMoneySection() {
    const addMoneySection = document.getElementById('AddMoneySection');
    const addMoneyButton = document.querySelector('[onclick="toggleAddMoneySection()"]');
    const proceedButton = document.getElementById('proceedButton');

    if (addMoneySection.style.display === 'none') {
        addMoneySection.style.display = 'block';
        addMoneyButton.style.display = 'none';
        proceedButton.style.display = 'block';
    } else {
        addMoneySection.style.display = 'none';
        addMoneyButton.style.display = 'block';
        proceedButton.style.display = 'none';
    }
}

function processAddMoney() {
    const amountInput = document.getElementById('amount');
    const amount = parseInt(amountInput.value);
    // Check if the entered amount is a valid integer within the specified range
    if (Number.isInteger(amount) && amount >= 100 && amount <= 5000) {
        process_add_money(amount) ;
       
    } else {
        
        amountInput.value = ''; // Clear the input field
    }
}




async function process_add_money(amount) {
    event.preventDefault();
    //$('#walletModal').hide();
    // Create an object with the data you want to send to the /pay endpoint
    //document.getElementById("WalletBody").innerHTML = ``

    var data = {
        Type: "Add Money",
        Amount: amount
    };

    try {
        // Send the POST request using await fetch
        const response = await fetch('/pay', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            // Response status is OK, check if it's a redirection
            if (response.redirected) {
                window.location.href = '/complete_payment';
            } else {
                // Handle other successful responses if needed
            }
        } else {
            // Handle other response statuses (e.g., 404, 500) if needed
            console.error('Response status:', response.status);
        }
    } catch (error) {
        console.error("Error:", error);
    }
}



function formatToTwoDecimalPlaces(number) {
    return parseFloat(number).toFixed(2);
}


function Reset() {
    // JavaScript for handling Reset PIN button click
    var resetPinButton = document.getElementById('ResetPinButton');
    var resetPinFields = document.getElementById('ResetPinFields');
   
    resetPinFields.style.display = 'block'; // Show the input fields
    resetPinButton.style.display = 'none'; // Hide the Reset PIN button
    document.getElementById('Gobutton').style.display='none';
    var cancel=document.getElementById('cancelButton');
    cancel.style.display = 'inline-block';
    cancel.addEventListener(
        'click', reset_style
    );
    // JavaScript for handling Confirm button click
    var confirmButton = document.getElementById('confirmButton');
    confirmButton.style.display ='inline-block';
    
    confirmButton.addEventListener('click', function () {
        try {
            var newPin = document.getElementById('NewPinInput').value;
            var confirmPin = document.getElementById('ConfirmPinInput').value;
        } catch (error) {
            return;
        }

        if (newPin.length !== 4 || confirmPin.length !== 4) {
            return;
        }

        console.log("Sending new PIN:", newPin);

        // Check if the entered PINs match and have 4 digits
        if (newPin.length === 4 && newPin === confirmPin) {
            // Prepare the data object to send as JSON
            var data = {
                New: newPin
            };

            console.log("Sending data to server:", JSON.stringify(data));

            fetch('/Forgot_wallet_pass', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            })
                .then(function (response) {
                    
                    if (response.ok) {
                        document.getElementById("Default_pin").textContent = "PIN reset Successful.";
                        document.getElementById("Default_pin").style.color = '#37fa64';
                        reset_style();
                    } else {
                        // Handle error response from the server
                        console.error('Failed to reset PIN. Server returned an error.');
                        alert('Failed to reset PIN. Please try again.');
                        reset_style();
                    }
                })
                .catch(function (error) {
                    console.error('Failed to reset PIN. Error:', error);
                    alert('Failed to reset PIN. Please try again.');
                    reset_style();
                });
        } else {
            reset_style();
        }
    });

    function reset_style(){
        $('#ConfirmPinInput').val('');
        $('#NewPinInput').val('');
        resetPinFields.style.display = 'none'; // Hide the input fields
        resetPinButton.style.display = 'inline-block'; // Show the Reset PIN button again
        cancel.style.display = 'none';
        confirmButton.style.display='none';
        document.getElementById('Gobutton').style.display = 'inline-block';
    }
}

$(document).ready(function () {
    // Add event listener to the New PIN input field
    $('#NewPinInput').on('input', function () {
        var value = $(this).val();

        // Remove non-numeric characters and ensure the value is a positive integer
        value = value.replace(/\D/g, ''); // Remove non-numeric characters

        value = parseInt(value, 10); // Convert to integer

        if (isNaN(value) || value <= 0) {
            value = ''; // Reset to empty if not a positive integer
        } else if (value > 9999) {
            value = $(this).val().slice(0, 4); // Limit to 4-digit positive integer
        }
        if (String(value).length == 4) {
            $('#ConfirmPinInput').focus();
        }
        $(this).val(value);
        
    });

    // Add event listener to the Confirm PIN input field
    $('#ConfirmPinInput').on('input', function () {
        var value = $(this).val();

        // Remove non-numeric characters and ensure the value is a positive integer
        value = value.replace(/\D/g, ''); // Remove non-numeric characters
        value = parseInt(value, 10); // Convert to integer

        if (isNaN(value) || value <= 0) {
            value = ''; // Reset to empty if not a positive integer
        } else if (value > 9999) {
            value = $(this).val().slice(0, 4); // Limit to 4-digit positive integer
        }

        $(this).val(value);
    });
});



