(function () {
  var totalSteps = 5;
  var currentStep = 1;
  var selectedByStep = {};
  var progressBar = document.getElementById("progressBar");
  var progressCount = document.getElementById("progressCount");
  var linglongCard = document.getElementById("linglongCard");
  var linglongText = document.getElementById("linglongText");
  var popupWrong = document.getElementById("popupWrong");
  var popupWrongClose = document.getElementById("popupWrongClose");
  var popupWrongBackdrop = document.getElementById("popupWrongBackdrop");
  var popupComplete = document.getElementById("popupComplete");
  var popupCompleteClose = document.getElementById("popupCompleteClose");
  var popupCompleteBackdrop = document.getElementById("popupCompleteBackdrop");

  function getCurrentStepEl() {
    return document.querySelector(".lesson-step.is-active");
  }

  function setLinglongState(state) {
    if (!linglongCard || !linglongText) return;
    linglongCard.classList.remove("linglong--happy", "linglong--mad");
    if (state === "happy") {
      linglongCard.classList.add("linglong--happy");
      linglongText.textContent = "Linglong is happy!";
    } else if (state === "crying") {
      linglongCard.classList.add("linglong--mad");
      linglongText.textContent = "Linglong is sad...";
    } else {
      linglongText.textContent = "Linglong is watching...";
    }
  }

  function showWrongPopup() {
    setLinglongState("crying");
    if (popupWrong) {
      popupWrong.hidden = false;
      popupWrongClose.focus();
    }
  }

  function hideWrongPopup() {
    if (popupWrong) popupWrong.hidden = true;
    setTimeout(function () {
      setLinglongState("neutral");
    }, 400);
  }

  function showCompletePopup() {
    if (popupComplete) popupComplete.hidden = false;
  }

  function goToStep(step) {
    var steps = document.querySelectorAll(".lesson-step");
    steps.forEach(function (el) {
      el.classList.toggle("is-active", parseInt(el.getAttribute("data-step"), 10) === step);
    });
    currentStep = step;
    if (progressBar) progressBar.style.width = (step / totalSteps) * 100 + "%";
    if (progressCount) progressCount.textContent = step + "/" + totalSteps;
    if (progressBar) {
      progressBar.setAttribute("aria-valuenow", step);
    }
  }

  function getSubmitButtonForStep(step) {
    return document.getElementById("submitBtn" + (step === 1 ? "" : step));
  }

  function checkAnswer() {
    var stepEl = getCurrentStepEl();
    if (!stepEl) return;
    var optionsEl = stepEl.querySelector(".lesson-options");
    var correct = optionsEl ? optionsEl.getAttribute("data-correct") : null;
    var selected = selectedByStep[currentStep];
    if (selected === undefined || selected === null) return;
    if (selected !== correct) {
      showWrongPopup();
      return;
    }
    setLinglongState("happy");
    if (currentStep >= totalSteps) {
      try {
        localStorage.setItem("linglong_level1_complete", "true");
      } catch (e) {}
      showCompletePopup();
      return;
    }
    setTimeout(function () {
      setLinglongState("neutral");
      goToStep(currentStep + 1);
    }, 600);
  }

  function bindStep(stepNum) {
    var stepEl = document.querySelector(".lesson-step[data-step=\"" + stepNum + "\"]");
    if (!stepEl) return;
    var options = stepEl.querySelectorAll(".lesson-option");
    var submitBtn = getSubmitButtonForStep(stepNum);
    options.forEach(function (btn) {
      btn.addEventListener("click", function () {
        options.forEach(function (b) { b.classList.remove("is-selected"); });
        btn.classList.add("is-selected");
        selectedByStep[stepNum] = btn.getAttribute("data-value");
      });
    });
    if (submitBtn) {
      submitBtn.addEventListener("click", function () {
        checkAnswer();
      });
    }
  }

  for (var s = 1; s <= totalSteps; s++) {
    bindStep(s);
  }

  if (popupWrongClose) {
    popupWrongClose.addEventListener("click", hideWrongPopup);
  }
  if (popupWrongBackdrop) {
    popupWrongBackdrop.addEventListener("click", hideWrongPopup);
  }
  if (popupCompleteClose) {
    popupCompleteClose.addEventListener("click", function () {
      if (popupComplete) popupComplete.hidden = true;
    });
  }
  if (popupCompleteBackdrop) {
    popupCompleteBackdrop.addEventListener("click", function () {
      if (popupComplete) popupComplete.hidden = true;
    });
  }

  goToStep(1);
})();
