(function () {
  const slidesEl = document.getElementById("slides");
  if (slidesEl) {
    const slides = Array.from(slidesEl.querySelectorAll(".slide"));
    const dots = Array.from(document.querySelectorAll(".dot"));
    const frame = document.querySelector(".slideshow__frame");
    const videos = Array.from(slidesEl.querySelectorAll(".slide__video"));
    var reel4MaxTime = 0;
    var reel4WatchedToEnd = false;
    var reel5Watched3s = false;

    if (slides.length > 0 && dots.length > 0) {
      let index = 0;

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
        videos.forEach(function (v, i) {
          v.pause();
          if (i === index) v.play().catch(function () {});
        });
      }

      if (videos[3]) {
        videos[3].addEventListener("timeupdate", function () {
          if (videos[3].currentTime > reel4MaxTime) reel4MaxTime = videos[3].currentTime;
        });
        videos[3].addEventListener("ended", function () {
          reel4WatchedToEnd = true;
        });
      }
      if (videos[4]) {
        videos[4].addEventListener("timeupdate", function () {
          if (videos[4].currentTime >= 3) reel5Watched3s = true;
        });
      }

      videos.forEach(function (video, i) {
        video.addEventListener("ended", function () {
          if (i === 4) {
            var popup = document.getElementById("reelQuizPopup");
            var q1 = document.getElementById("reelQuizQ1");
            var q2 = document.getElementById("reelQuizQ2");
            var q3 = document.getElementById("reelQuizQ3");
            if (q1) q1.style.display = reel4MaxTime >= 35 ? "" : "none";
            if (q2) q2.style.display = reel4WatchedToEnd ? "" : "none";
            if (q3) q3.style.display = reel5Watched3s ? "" : "none";
            if (popup) {
              popup.hidden = false;
              popup.querySelector(".reel-quiz-q__input") && popup.querySelector(".reel-quiz-q__input").focus();
            }
          } else {
            setActive(index + 1);
          }
        });
      });

      var quizForm = document.getElementById("reelQuizForm");
      var quizFeedback = document.getElementById("reelQuizFeedback");
      if (quizForm) {
        quizForm.addEventListener("submit", function (e) {
          e.preventDefault();
          var correct = 0;
          var total = 0;
          [1, 2, 3].forEach(function (n) {
            var el = document.getElementById("reelQuizQ" + n);
            if (!el || el.style.display === "none") return;
            total++;
            var answer = el.getAttribute("data-answer");
            if (n === 3) {
              var input = quizForm.querySelector('input[name="q3"]');
              if (input && input.value.trim().toLowerCase() === answer.toLowerCase()) correct++;
            } else {
              var radio = quizForm.querySelector('input[name="q' + n + '"]:checked');
              if (radio && radio.value === answer) correct++;
            }
          });
          if (quizFeedback) {
            quizFeedback.hidden = false;
            quizFeedback.textContent = "You got " + correct + " out of " + total + " correct.";
            quizFeedback.className = "reel-quiz-popup__feedback " + (correct === total ? "reel-quiz-popup__feedback--ok" : "reel-quiz-popup__feedback--warn");
          }
        });
      }
      var quizClose = document.getElementById("reelQuizClose");
      var quizBackdrop = document.getElementById("reelQuizBackdrop");
      function closeQuiz() {
        var popup = document.getElementById("reelQuizPopup");
        if (popup) popup.hidden = true;
        setActive(0);
      }
      if (quizClose) quizClose.addEventListener("click", closeQuiz);
      if (quizBackdrop) quizBackdrop.addEventListener("click", closeQuiz);

      dots.forEach(function (dot) {
        dot.addEventListener("click", function () {
          var raw = dot.getAttribute("data-dot");
          var next = raw ? parseInt(raw, 10) : 0;
          setActive(next);
        });
      });

      if (frame) {
        frame.addEventListener("keydown", function (e) {
          if (e.key === "ArrowRight") {
            setActive(index + 1);
            e.preventDefault();
          } else if (e.key === "ArrowLeft") {
            setActive(index - 1);
            e.preventDefault();
          }
        });
      }

      setActive(0);
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
