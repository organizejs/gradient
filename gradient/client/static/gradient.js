const PROD_URL = 'https://www.gradient.care';
const STAGING_URL = 'https://staging.gradient.care';
const DEVENV_URL = 'https://devenv.gradient.care'
const LOCALHOST = 'http://localhost:5001';

// Start a Gradient checkout flow.
// This submits the cart info to Gradient
// and then redirects the customer to
// the Gradient checkout page.
function gradientCheckout(
        vendor_id, cart, gradient_url) {

    if (gradient_url === undefined) {
        gradient_url = PROD_URL;
    }
    const INITIALIZE_URL = gradient_url + '/checkout/initialize';

    // TODO write a cart validator 

    fetch(`${INITIALIZE_URL}`, {
        mode: 'cors',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            'vendor_id': vendor_id,
            'products': cart
        })
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.success) {
            // Set the transaction's secret key as a cookie
            // for later validation.
            document.cookie = `${vendor_id}_txkey=${data.key}`;

            // Redirect to the Gradient checkout page.
            window.location.replace(data.url);
        } else {
            alert('was not successful');
        }
    })
    .catch(err => {
        alert(err);
    });
}

// Completes a Gradient checkout.
// This should be called on the vendor's specified redirect URL.
// It validates the transaction's completion against Gradient,
// and if valid, runs the `onSuccess` callback.
// Otherwise, the `onFailure` callback is called.
function completeGradientCheckout(
        onSuccess, onFailure, gradient_url) {

    if (gradient_url === undefined) {
        gradient_url = PROD_URL;
    }
    const VALIDATE_URL = gradient_url + '/checkout/validate';

    // by default, `onFailure` does nothing
    onFailure = onFailure || Function.prototype;

    // get vendor id and transaction id from URL params
    var vendor_id = getParameterByName('vid');
    var txid = getParameterByName('txid');

    // get the transaction key from the cookies
    var cookie = `${vendor_id}_txkey`;
    var txkey = getCookie(cookie);

    // send the transaction key to Gradient
    // to validate
    fetch(`${VALIDATE_URL}`, {
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        method: 'POST',
        body: JSON.stringify({
            'txkey': txkey,
            'txid': txid
        })
    })
    .then(resp => resp.json())
    .then(data => {
        if (data.success) {
            // delete cookie
            document.cookie = `${cookie}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
            onSuccess();
        } else {
            onFailure(data.message);
        }
    })
    .catch(err => {
        alert(err);
    });
}


function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for(var i = 0; i < ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}
