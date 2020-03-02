function check_city() {
    var source = document.getElementById('source').value
    var destination = document.getElementById('destination').value
    var geocoder = new google.maps.Geocoder()
    console.log(destination)

    if (source.toLowerCase() == destination.toLowerCase()) {
        document.getElementById("book").disabled = true;
        document.getElementById('errorSameCity').style.display = "block";

    } else {
        document.getElementById("book").disabled = false;
        document.getElementById('errorSameCity').style.display = "none";

    }
    if (destination != '' && source.toLowerCase() != destination.toLowerCase()) {
        geocoder.geocode({
            'address': destination,

            region: 'in'

        }, function(results, status) {
            console.log('a')
            console.log(destination)
            console.log(status, results)
            if (status === google.maps.GeocoderStatus.OK && results.length > 0) {
                document.getElementById('error').style.display = "none";
                document.getElementById("book").disabled = false;

            } else {
                document.getElementById('error').style.display = "block";
                document.getElementById("book").disabled = true;
            }

        });

    } else {
        document.getElementById('error').style.display = "none";
        document.getElementById("book").disabled = false;

    }
}


function check_password() {
    var password = document.getElementById('password').value

    var confirm = document.getElementById('confirm').value
    if (password != confirm) {
        document.getElementById("signUp_form").disabled = true;
        document.getElementById('error').style.display = "block";
    } else {
        document.getElementById("signUp_form").disabled = false;

        document.getElementById('error').style.display = "none";
    }

}

function journeyType(evt, typess) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName('tabcontent');
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }

    tablinks = document.getElementsByClassName("journeyTypeBtn");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace("active", "");
    }
    document.getElementById(typess).style.display = "block"
    evt.currentTarget.className += " active"


}

function auto_fill(firstName, lastName, email, mobile) {
    document.getElementById('name').value = firstName + ' ' + lastName
    document.getElementById('email').value = email
    document.getElementById('inputMobile').value = mobile

}