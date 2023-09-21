async function check_login(){
  let response=await fetch('/Check_login');
  if(!response.ok){
    document.getElementById('Sign_up').innerHTML="Sign Up";
    document.getElementById('Login').innerHTML='Login';
  }
  
}

var nav=document.getElementsByClassName("navbar-nav");
for(let i=0;i<nav.length;i++){
  nav[i].style.color='white';
  console.log(nav[i]);
}

var dict = {
  messages: expandMessagesDropdown,
  notifications: expandMessagesDropdown,
  query: expandMessagesDropdown,
  ask: expandMessagesDropdown,
  askaquery: expandMessagesDropdown,
  'ask a query': expandMessagesDropdown,
  home:Go_home,
  profile:Go_profile,
  login:Go_Login,
  help: expandMessagesDropdown,
  logout:Logout,
  signup:Go_SignUp,
};

function search(){
  var searched = document.getElementById('Search_bar').value;
  
  if(searched.length>0){
    event.preventDefault();
    if (searched.length<=15 && dict.hasOwnProperty(searched.toLowerCase())){
      dict[searched.toLowerCase()]();
    }else{
      findString(searched);
      
    }
    setTimeout(function () {
      document.getElementById('Search_bar').value = '';
      document.head.click();
    }, 5000);
    
  }
}

function findString(str) {
  var found = false;

  if (window.find) {
    // Modern browsers that support window.find
    found = window.find(str);
  } else {
    // Fallback for older browsers
    var body = document.body;
    var textNode = document.createTextNode(str);
    var searchRange, range, span;

    // Create a temporary element to wrap the found text
    span = document.createElement('span');
    span.className = 'highlighted-text';
    span.appendChild(textNode);

    // Append the temporary element to the body
    body.appendChild(span);

    // Create a range to search for the text
    searchRange = document.createRange();
    searchRange.selectNodeContents(body);

    // Start the search from the beginning of the document
    range = searchRange.cloneRange();
    range.collapse(true);

    // Perform the search
    while (range.findText(str)) {
      range.surroundContents(span.cloneNode(true));
      found = true;
    }

    // Clean up temporary elements
    body.normalize();
    span.parentNode.replaceChild(textNode, span);
  }

  if (!found) {
    // Handle not found
    if (str.length > 10) {
      showPopup(str.substring(0,5) + '...');
    } else {
      showPopup(str);
    }
    document.getElementById('Search_bar').value = '';
  }
}


// Function to expand the "Messages" dropdown
function expandMessagesDropdown() {
  const messagesToggle = document.getElementById('MessagesToggle');
  if (messagesToggle) {
    // Trigger a click event on the "Messages" dropdown toggle button
    messagesToggle.click();
  }
}


function showPopup(data) {
  // Create a container element for the popup
  const container = document.createElement('div');
  container.setAttribute('class', 'popup-container');
  document.body.appendChild(container);

  const box = document.createElement('div');
  box.setAttribute('class', 'big_5_selected_text_analysis_box');

  box.innerHTML = `
    <h3 class="title">
      <span>${data} not found</span>
    </h3>
    <h6 style="color:green">You can make a Query instead.</h6>
  `;

  const buttonContainer = document.createElement('div');
  buttonContainer.style.display = 'flex';
  buttonContainer.style.justifyContent = 'flex-end';
  buttonContainer.style.marginTop = '10px';

  const okButton = document.createElement('button');
  okButton.style.width = '70px';
  okButton.style.height = '30px';
  okButton.style.borderRadius = '4px';
  okButton.style.backgroundColor = '#27f2b2';
  okButton.style.border = 'none';
  okButton.style.cursor = 'pointer';
  okButton.style.marginRight = '10px';
  okButton.style.marginTop = '10px';
  okButton.innerText = 'OK';

  const cancelButton = document.createElement('button');
  cancelButton.style.width = '70px';
  cancelButton.style.height = '30px';
  cancelButton.style.borderRadius = '4px';
  cancelButton.style.backgroundColor = '#27f2b2';
  cancelButton.style.marginTop = '10px';
  cancelButton.style.border = 'none';
  cancelButton.style.cursor = 'pointer';
  cancelButton.innerText = 'Cancel';

  okButton.addEventListener('click', () => {
    expandMessagesDropdown();
    box.remove();
    container.remove();
    
  });

  cancelButton.addEventListener('click', () => {
    box.remove();
    container.remove();
  });

  // Create a <span> element to style the inner HTML
  const closeBtn = document.createElement('button');
  closeBtn.style.width = '25px';
  closeBtn.style.height = '25px';
  closeBtn.style.borderRadius = '4px';
  closeBtn.style.backgroundColor = '#fff';
  closeBtn.style.border = 'none';
  closeBtn.style.cursor = 'pointer';
  closeBtn.style.margin = '15px 15px 5px 0px';

  // Create a <span> element to style the inner HTML
  const closeIcon = document.createElement('span');
  closeIcon.innerHTML = '&#10005;'; // Insert the cross sign (×)
  closeIcon.style.fontFamily = 'Arial, sans-serif'; // Set the font family
  closeIcon.style.fontSize = '18px'; // Set the font size
  closeIcon.style.fontWeight = 'bold';
  closeIcon.style.color = 'black'; // Set the color
  closeIcon.style.position = 'relative';
  closeIcon.style.bottom = '10px';
  closeBtn.appendChild(closeIcon);

  closeBtn.addEventListener('click', () => {
    box.remove();
    container.remove();
  });

  setTimeout(function () {
    closeBtn.click();
  }, 6000);

  box.querySelector('h3').appendChild(closeBtn);

  // Append buttons to button container
  buttonContainer.appendChild(okButton);
  buttonContainer.appendChild(cancelButton);

  // Append the button container to the box
  box.appendChild(buttonContainer);

  // Append the box to the container
  container.appendChild(box);

  // Apply CSS styles to control the position
  container.style.position = 'fixed'; // Fixed positioning to keep it in view
  container.style.top = '80px'; // Adjust top as needed
  container.style.right = '30px'; // Adjust right as needed
  container.style.background = '#ffe6c4'; // Background color
  container.style.color = 'black'; // Text color
  container.style.maxWidth = '80%'; // Maximum width for responsiveness
  container.style.padding = '10px'; // Padding for content
  container.style.zIndex = '9999'; // Ensure it's above other content
  container.style.borderRadius = '10px';
  box.style.borderRadius = '10px';
  container.style.alignContent = 'center';
  box.style.padding = '10px';
  container.style.border = '2px solid black';
}

function expandMessagesDropdown() {
setTimeout(function () {
  const messagesToggle = document.getElementById('MessagesToggle');
  if (messagesToggle) {
    // Trigger a click event on the "Messages" dropdown toggle button
    messagesToggle.click();
  }
}, 100); // Delay execution by 100 milliseconds
}


function Go_home(){
  location.href='/';
}


function Go_Login() {
  location.href = '/profile';
}
function Go_SignUp() {
  location.href = '/Sign_up';
}

function Go_profile() {
  Go_Login();
}
function Logout(){
  var btn=document.getElementById('Logout');
  if(btn){
    btn.click();
  }else{
    Go_Login();
  }
}

function getFirebaseErrorMessage (code) {
  var message = null;
  console.log(code);
  switch (code) {
    case "auth/user-not-found":
      message = 'USER NOT FOUND';
      break;
    case "auth/email-already-in-use":
      message = 'EMAIL ALREADY IN USE';
      break;
    case "auth/internal-error":
      message = 'INTERNAL ERROR';
      break;
    case "auth/invalid-login-credentials":
      message = 'INVALID LOGIN CREDENTIALS';
      break;
    case "auth/invalid-email":
      message = 'INVALID EMAIL FORMAT';
      break;
    case "auth/invalid-password":
      message = 'INVALID PASSWORD FORMAT';
      break;
    case "auth/weak-password":
      message = 'Password Too Weak! Use Atleast 6 characters';
      break;
    default:
      message = 'Something Went Wrong! Try Again';
      break;
  }
  return message;
}


function validateMobile() {
  var mobileInput = document.getElementById("mobile") || document.getElementById("editMobile");
  var mobileValue = mobileInput.value;
  if (mobileValue.length > 0 && mobileValue.length < 12 && mobileValue.length!=10) {
    alert("Provide a 10/12 digit mobile number!");
    mobileInput.value = "";
    return false;
  }
  // Regular expression to match valid mobile number format
  var mobileRegex = /^(\+\d{1,2}\s?)?\d{10}$/;


  if (mobileValue.length > 0 && !mobileRegex.test(mobileValue)) {
    alert("Invalid mobile number format.Use 10/12 digits Only");
    mobileInput.value = "";
    return false;
  }

  return true;
}


