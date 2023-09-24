
function make_card(Name,Number,Exp,no){
    var c1=document.createElement('div');
    c1.className = `text-white card card${no} rounded-5 border p-3 mx-auto mb-3`;
    var cardtype = detectCardType(parseInt(Number));
    var type=cardtype.type;
    var removeButton = document.createElement('button');
    removeButton.type = 'button';
    removeButton.className = 'btn btn-danger d-flex flex-column';
    removeButton.textContent = 'Remove';
    var proceBtn=document.createElement('button');
    proceBtn.className = "btn btn-primary";
    proceBtn.textContent="Proceed";
    proceBtn.addEventListener('click',function(){
        var cardToProcess = this.parentElement.parentElement;
        if(cardToProcess){
            Process_Payment(cardToProcess);
        }
    });
    removeButton.addEventListener('click', function () {
        var cardToRemove = this.parentElement.parentElement; // Get the parent of the parent
        if (cardToRemove) {
            removeCard(cardToRemove); // Call the removeCard function with the card element
        }
    });

    c1.innerHTML =`
        <div class="d-flex justify-content-between ">
            <div>
                <p class="m-0 fw-light">Card Holder</p>
                <p class="m-0" style="font-weight:bold; font-family:open-sans;color:black;">${Name}</p>
            </div>
            <div>
                <img src="${get_card_url(type)}" style="width:45px;height:35px;" alt="card-logo">
            </div>
        </div>
        <div class="d-flex justify-content-between pt-1">
            <p class="m-0">${Number}</p>
            <p class="m-0">${Exp}</p>
        </div>`;
    var c2=document.createElement('div');
    c2.className ="row card-buttons d-flex flex-col-auto"
    c2.appendChild(proceBtn);
    c2.appendChild(removeButton);
    c1.appendChild(c2);
    return c1;
}

function load_cards() {
    var target=document.getElementById("Cards");
    target.append(make_card('Pinaki Banerjee',"6759649826438453",'09/25',1));
    //target.append(make_card('Pinaki Banerjee', "6759649826438453", '09/25', 1));
}


function get_card_url(cardtype){
    return "/static/assets/icons/"+cardtype+".png";
}

function detectCardType(number) {
    var cardTypes = {
        electron: { pattern: /^(4026|417500|4405|4508|4844|4913|4917)/, length: [16], luhn: true },
        maestro: { pattern: /^(5018|5020|5038|5612|5893|6304|6759|6761|6762|6763|0604|6390)/, length: [12, 13, 14, 15, 16, 17, 18, 19], luhn: true },
        dankort: { pattern: /^(5019)/, length: [16], luhn: true },
        interpayment: { pattern: /^(636)/, length: [16], luhn: true },
        unionpay: { pattern: /^(62|88)/, length: [16, 17, 18, 19], luhn: false }, // UnionPay doesn't use Luhn
        visa: { pattern: /^4/, length: [13, 16, 19], luhn: true },
        mastercard: { pattern: /^5[1-5]/, length: [16], luhn: true },
        amex: { pattern: /^3[47]/, length: [15], luhn: true },
        diners: { pattern: /^3(?:0[0-5]|[68][0-9])/, length: [14], luhn: true },
        discover: { pattern: /^6(?:011|5[0-9]{2})/, length: [16, 19], luhn: true },
        jcb: { pattern: /^(?:2131|1800|35\d{3})/, length: [16], luhn: true },
        rupay: { pattern: /^6(?!011)(?:0|52[12])/, length: [16], luhn: true }
    };

    for (var key in cardTypes) {
        var cardType = cardTypes[key];
        if (cardType.pattern.test(number)) {
            // Check if the card number's length matches the expected length
            var isValidLength = cardType.length.includes(number.length);

            return { type: key, usesLuhn: cardType.luhn,len:cardType.length, isValidLength: isValidLength };
        }
    }
    return { type: "unknown", usesLuhn: false, isValidLength: false };
}


function isLuhnValid(number) {
    var sum = 0;
    var alt = false;
    var i = number.length - 1;

    while (i >= 0) {
        var num = parseInt(number.charAt(i));
        if (alt) {
            num *= 2;
            if (num > 9) {
                num = (num % 10) + 1;
            }
        }
        sum += num;
        alt = !alt;
        i--;
    }

    return sum % 10 === 0;
}

function add_card(){
    var target = document.getElementById("Cards");
    const Name=document.getElementById("Username").value;
    const Number = document.getElementById("cardNumber").value.replace(/\s/g, '');
    const ExpM = document.getElementById("expirationMonth").value;
    const ExpY = document.getElementById("expirationYear").value;
    if(!target||!Name||!Number||!ExpM||!ExpY)
        return;
    if(!isLuhnValid(Number)){
        alert("Card invalid!");
        return;
    }
    target.appendChild(make_card(Name, Number, String(ExpM)+'/'+String(ExpY), Math.floor(Math.random()*15)+1));;
}

function removeCard(cardElement) {
    cardElement.remove();
}

