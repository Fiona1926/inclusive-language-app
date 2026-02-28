(function () {
  const slidesEl = document.getElementById("slides");
  if (slidesEl) {
    const slides = Array.from(slidesEl.querySelectorAll(".slide"));
    const dots = Array.from(document.querySelectorAll(".dot"));
    const frame = document.querySelector(".slideshow__frame");

    if (slides.length > 0 && dots.length > 0) {
      let index = 0;
      let timer = null;

      function setActive(next) {
        index = ((next % slides.length) + slides.length) % slides.length;
        slides.forEach(function (s, i) {
          s.classList.toggle("is-active", i === index);
        });
        dots.forEach(function (d, i) {
          var active = i === index;
          d.classList.toggle("is-active", active);
          if (active) d.setAttribute("aria-current", "true");
          else d.removeAttribute("aria-current");
        });
      }

      function start() {
        if (timer != null) clearInterval(timer);
        timer = setInterval(function () {
          setActive(index + 1);
        }, 5000);
      }

      function stop() {
        if (timer != null) {
          clearInterval(timer);
          timer = null;
        }
      }

      dots.forEach(function (dot) {
        dot.addEventListener("click", function () {
          var raw = dot.getAttribute("data-dot");
          var next = raw ? parseInt(raw, 10) : 0;
          setActive(next);
          start();
        });
      });

      if (frame) {
        frame.addEventListener("keydown", function (e) {
          if (e.key === "ArrowRight") {
            setActive(index + 1);
            start();
            e.preventDefault();
          } else if (e.key === "ArrowLeft") {
            setActive(index - 1);
            start();
            e.preventDefault();
          }
        });
        frame.addEventListener("pointerenter", stop);
        frame.addEventListener("pointerleave", start);
        frame.addEventListener("focusin", stop);
        frame.addEventListener("focusout", start);
      }

      setActive(0);
      start();
    }
  }

  // To-do: toggle done state and update counter
  var todoItems = document.querySelectorAll(".todoList__item");
  var countEl = document.getElementById("todoCount");
  var total = todoItems.length;

  function updateTodoCount() {
    if (!countEl) return;
    var done = document.querySelectorAll(".todoList__item--done").length;
    countEl.textContent = done + "/" + total;
  }

  todoItems.forEach(function (item) {
    item.addEventListener("click", function () {
      item.classList.toggle("todoList__item--done");
      var span = item.querySelector(".todoList__check, .todoList__circle");
      if (span) {
        if (item.classList.contains("todoList__item--done")) {
          span.className = "todoList__check";
          span.textContent = "\u2713";
        } else {
          span.className = "todoList__circle";
          span.textContent = "";
        }
      }
      updateTodoCount();
    });
  });
})();

document.addEventListener('DOMContentLoaded', function() {
  const sidebar = document.querySelector('.sidebar');
  const collapseBtn = document.querySelector('.sidebar__collapse');
  
  if (!sidebar || !collapseBtn) return;
  
  // Load saved state
  if (localStorage.getItem('sidebarCollapsed') === 'true') {
    sidebar.classList.add('collapsed');
  }
  
  collapseBtn.addEventListener('click', function() {
    sidebar.classList.toggle('collapsed');
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
  });
});
