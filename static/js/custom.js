function step2() {
    next_button = document.getElementById('next');
    step1_div = document.getElementById('step1');
    osm_name = document.getElementById('osmDisplayName').value;

    document.getElementById('userid').value = "";
    document.getElementById('username').value = "";
    document.getElementById('error').textContent = "";

    if (osm_name.length !== 0) {

        next_button.disabled = true;
        next_button.value = "Wait";

        step2_div = document.getElementById('step2');
        error_label = document.getElementById('error');

        function reqListener(){
            // if status 200 check content-type is xml and set username
            if (this.status === 200){
                if (this.getResponseHeader("Content-Type") === "application/xml; charset=utf-8"){
                    step1_div.style.display = "none";
                    step2_div.style.display = "block";
                    document.getElementById('username').value = osm_name;
                }
            }
            // else if status 404 & content-type is plaintext check username
            else if (this.status === 404) {
                if (this.getResponseHeader("Content-Type") === "text/plain; charset=utf-8") {
                    error_label.innerHTML = "<small>Are you sure, you have account in OSM?<br/>Display names are case-sensitive</small>"
                }
                else {
                    error_label.textContent = "Something went wrong. Try after sometime."
                }
            }

            next_button.disabled = false;
            next_button.value = "Next";
        }

        url = "http://api.openstreetmap.org/api/0.6/changesets?display_name="+osm_name
        xhr = new XMLHttpRequest();
        xhr.addEventListener("load", reqListener);
        xhr.open("HEAD", url);
        xhr.send();
    } else {
        alert("Your OSM Username can't be empty");
    }
}


function validateForm(){
    email_value = document.getElementById('email').value;
    user_id = document.getElementById('userid').value;
    user_name = document.getElementById('username').value;
    if (user_id.length === 0 || user_name.length ===0 || email_value.lentgh === 0) {
        return false;
    }
    else {
        return true;
    }
}
