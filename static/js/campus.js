// ===============================
// StudentHub Campus Events
// ===============================

// Search Box
const search = document.getElementById("search");

// Sort Dropdown
const sortSelect = document.getElementById("sortSelect");

// Date Filter
const dateFilter = document.getElementById("dateFilter");

// Category Buttons
const categoryButtons = document.querySelectorAll(".category-btn");

// Event Container
const container = document.querySelector(".event-container");

// Event Cards
let events = Array.from(document.querySelectorAll(".event"));

// Current Selected Category
let currentCategory = "all";


// =====================================
// Category Button Click
// =====================================

categoryButtons.forEach(button => {

    button.addEventListener("click", function () {

        // Remove active class
        categoryButtons.forEach(btn =>
            btn.classList.remove("active")
        );

        // Highlight selected category
        this.classList.add("active");

        currentCategory = this.dataset.category;

        filterEvents();

    });

});


// =====================================
// Filter Function
// =====================================
function filterEvents() {

    const searchValue = search.value.toLowerCase();
    const selectedDate = dateFilter.value;

    let visibleCount = 0;

    events.forEach(event => {

        const eventName = event.dataset.name.toLowerCase();
        const college = event.dataset.college.toLowerCase();
        const category = event.dataset.category;
        const eventDate = event.dataset.date;

        const matchesSearch =
            eventName.includes(searchValue) ||
            college.includes(searchValue);

        const matchesCategory =
            currentCategory === "all" ||
            category === currentCategory;

        const matchesDate =
            selectedDate === "" ||
            eventDate === selectedDate;

        if (matchesSearch && matchesCategory && matchesDate) {

            event.style.display = "block";
            visibleCount++;

        } else {

            event.style.display = "none";

        }

    });

    const noResults = document.getElementById("no-results");

    if (visibleCount === 0) {
        noResults.style.display = "block";
    } else {
        noResults.style.display = "none";
    }

}
// =====================================
// Sort Events
// =====================================

sortSelect.addEventListener("change", function () {

    events.sort((a, b) => {

        switch (this.value) {
            case "none":
        return 0;

            case "name":
                return a.dataset.name.localeCompare(b.dataset.name);

            case "college":
                return a.dataset.college.localeCompare(b.dataset.college);

            case "latest":
                return new Date(b.dataset.date) - new Date(a.dataset.date);

            case "earliest":
                return new Date(a.dataset.date) - new Date(b.dataset.date);

            default:
                return 0;

        }

    });

    // Re-append sorted cards
    events.forEach(event => {

        container.appendChild(event);

    });

    // Apply filters again
    filterEvents();

});


// =====================================
// Event Listeners
// =====================================

search.addEventListener("keyup", filterEvents);

dateFilter.addEventListener("change", filterEvents);


// =====================================
// Initial Load
// =====================================

filterEvents();