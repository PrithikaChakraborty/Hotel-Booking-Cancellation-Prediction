// Load background image
fetch("components/bgimg.html")
  .then(res => res.text())
  .then(data => {
    document.getElementById("bgimg").innerHTML = data;
  });

// Load navbar
fetch("components/navbar.html")
  .then(res => res.text())
  .then(data => {
    document.getElementById("navbar").innerHTML = data;

    // Navbar toggle
    const menuBtn = document.getElementById("menu-btn");
    const menu = document.getElementById("menu");
    if (menuBtn) {
      menuBtn.addEventListener("click", () => menu.classList.toggle("hidden"));
    }
  });

// Load Reviews
fetch("components/reviews.txt")
  .then(res => res.text())
  .then(text => {
    const reviews = text.trim().split("\n").slice(0, 5); // Top 5 reviews
    const slider = document.getElementById("slider");
    const dotsContainer = document.getElementById("dots");

    let index = 0;

    // Add slides & dots
    reviews.forEach((review, i) => {
      // Slide
      const slide = document.createElement("div");
      slide.className = "min-w-full flex items-center justify-center text-lg px-6";
      slide.textContent = review;
      slider.appendChild(slide);

      // Dot
      const dot = document.createElement("button");
      dot.className = "dot w-3 h-3 rounded-full bg-gray-400";
      dot.addEventListener("click", () => showSlide(i));
      dotsContainer.appendChild(dot);
    });

    const dots = dotsContainer.querySelectorAll(".dot");

    // Show slide function
    function showSlide(i) {
      index = i;
      slider.style.transform = `translateX(-${i * 100}%)`;
      dots.forEach((dot, idx) => {
        dot.classList.toggle("bg-red-500", idx === i);
        dot.classList.toggle("bg-gray-400", idx !== i);
      });
    }

    // Auto-slide
    setInterval(() => {
      index = (index + 1) % reviews.length;
      showSlide(index);
    }, 4000);

    // Init
    showSlide(0);
  });

