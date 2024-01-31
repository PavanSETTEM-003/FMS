// current date
var currentDate = new Date();
var year = currentDate.getFullYear();
var month = currentDate.getMonth() + 1; 
var day = currentDate.getDate();

// Display the date
var formattedDate =(day < 10 ? "0" : "") +day + "-" + +(month < 10 ? "0" : "") + month + "-" + year;
document.getElementById("dateDisplay").innerHTML = formattedDate;

function addPixelStars(count) {
  var containerDiv = document.getElementById("pixelStarContainer");
  containerDiv.innerHTML = '';

  for (var i = 0; i < count; i++) {
    var img = document.createElement("img");

    img.src = "https://img.icons8.com/color/35/pixel-star.png";
    img.alt = "pixel-star";
    img.className = "pixel-star";

    containerDiv.appendChild(img);
  }
}


document.addEventListener("DOMContentLoaded", function () {
  var dropdownButton = document.getElementById("dropdownButton");
  var dropdown = document.querySelector(".dropdown");

  dropdownButton.addEventListener("click", function () {
    dropdown.classList.toggle("active");
  });

  // Close the dropdown when clicking outside of it
  document.addEventListener("click", function (event) {
    if (
      !dropdown.contains(event.target) &&
      dropdown.classList.contains("active")
    ) {
      dropdown.classList.remove("active");
    }
  });
});

