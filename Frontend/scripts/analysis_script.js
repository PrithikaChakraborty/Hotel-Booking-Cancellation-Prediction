 // Load background image section
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

      // Reattach navbar JS after loading
      const menuBtn = document.getElementById("menu-btn");
      const menu = document.getElementById("menu");
      if (menuBtn) {
        menuBtn.addEventListener("click", () => menu.classList.toggle("hidden"));
      }
    });

    // Navbar toggle
    const menuBtn = document.getElementById("menu-btn");
    const menu = document.getElementById("menu");
    menuBtn.addEventListener("click", () => menu.classList.toggle("hidden"));

    // Form handling
    const form = document.getElementById("analysisForm");
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      alert("Form submitted successfully!");
    });