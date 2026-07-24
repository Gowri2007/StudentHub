// ===============================
// Character Counter
// ===============================

const description = document.getElementById("description");
const count = document.getElementById("count");

if (description && count) {

    count.textContent = description.value.length;

    description.addEventListener("input", function () {

        count.textContent = this.value.length;

    });

}


// ===============================
// Date Validation
// ===============================

const eventDate = document.querySelector("input[name='event_date']");
const lastDate = document.querySelector("input[name='last_date']");

function validateDates() {

    if (!eventDate.value || !lastDate.value) return;

    if (lastDate.value > eventDate.value) {

        alert("Registration Last Date cannot be after Event Date.");

        lastDate.value = "";

    }

}

if(eventDate && lastDate){

    eventDate.addEventListener("change", validateDates);
    lastDate.addEventListener("change", validateDates);

}

// ===============================
// Submit Animation
// ===============================

const form = document.querySelector("form");

if(form){

form.addEventListener("submit", function(){

const button = document.querySelector(".publish-btn");

button.innerHTML =
'<i class="fa-solid fa-spinner fa-spin"></i> Publishing...';

button.disabled = true;

});

}