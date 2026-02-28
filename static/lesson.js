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

  function setLinglongMad(mad) {
    if (linglongCard) linglongCard.classList.toggle("linglong--mad", mad);
    if (linglongText) linglongText.textContent = mad ? "Linglong is mad!" : "Linglong is watching...";
  }

  function showWrongPopup() {
    setLinglongMad(true);
    if (popupWrong) {
      popupWrong.hidden = false;
      popupWrongClose.focus();
    }
  }

  function hideWrongPopup() {
    if (popupWrong) popupWrong.hidden = true;
    setTimeout(function () {
      setLinglongMad(false);
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
    if (currentStep >= totalSteps) {
      try {
        localStorage.setItem("linglong_level1_complete", "true");
      } catch (e) {}
      showCompletePopup();
      return;
    }
    goToStep(currentStep + 1);
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

  function speakPromptText(speakerBtn) {
    var promptEl = speakerBtn && speakerBtn.closest(".lesson-prompt");
    if (!promptEl) return;
    var textEl = speakerBtn.nextElementSibling;
    var text = textEl ? textEl.textContent.trim() : "";
    if (!text) return;
    if (typeof speechSynthesis === "undefined") return;

    var u = new SpeechSynthesisUtterance(text);
    u.lang = "id-ID";
    var voices = speechSynthesis.getVoices();
    var idVoice = voices.filter(function (v) { return v.lang === "id-ID" || v.lang.startsWith("id"); })[0];
    if (idVoice) u.voice = idVoice;

    function doSpeak() {
      var v = speechSynthesis.getVoices();
      u.lang = "id-ID";
      var id = v.filter(function (x) { return x.lang === "id-ID" || x.lang.startsWith("id"); })[0];
      if (id) u.voice = id;
      speechSynthesis.speak(u);
    }
    if (voices.length === 0) {
      setTimeout(doSpeak, 50);
    } else {
      doSpeak();
    }
  }

  document.querySelector(".lesson-main").addEventListener("click", function (e) {
    var speaker = e.target.closest(".lesson-prompt__speaker");
    if (speaker) {
      e.preventDefault();
      var textEl = speaker.nextElementSibling;
      var promptText = textEl ? textEl.textContent.trim() : "";
      if (!promptText) return;
      var api = typeof LinglongAPI !== "undefined" ? LinglongAPI : null;
      if (api && api.getToken && api.getToken()) {
        api.tts({ text: promptText }).then(function (data) {
          if (data && data.audioUrl) {
            var audio = new Audio(data.audioUrl);
            audio.play();
          } else {
            speakPromptText(speaker);
          }
        }).catch(function () {
          speakPromptText(speaker);
        });
      } else {
        speakPromptText(speaker);
      }
    }
  });

  var recordingState = { active: false, stream: null, recorder: null, chunks: [], stepNum: null };
  var STT_LANGUAGE = "id"; // Indonesian (used when sending recorded audio to speech-to-text)
  function normalizeForMatch(s) {
    return (s || "").trim().toLowerCase().replace(/\s+/g, " ");
  }
  function selectOptionByTranscript(stepNum, transcript) {
    var stepEl = document.querySelector(".lesson-step[data-step=\"" + stepNum + "\"]");
    if (!stepEl) return;
    var options = stepEl.querySelectorAll(".lesson-option");
    var t = normalizeForMatch(transcript);
    if (!t) return;
    for (var i = 0; i < options.length; i++) {
      var opt = options[i];
      var val = (opt.getAttribute("data-value") || "").trim();
      var vNorm = normalizeForMatch(val);
      if (vNorm && (t === vNorm || t.indexOf(vNorm) !== -1 || vNorm.indexOf(t) !== -1)) {
        options.forEach(function (b) { b.classList.remove("is-selected"); });
        opt.classList.add("is-selected");
        selectedByStep[stepNum] = val;
        return;
      }
    }
  }
  function setVerbalLabel(mic, text) {
    var verbal = mic && mic.closest(".lesson-verbal");
    var label = verbal && verbal.querySelector(".lesson-verbal__label");
    if (label) label.textContent = text;
  }
  function setMicAriaLabel(mic, label) {
    if (mic) mic.setAttribute("aria-label", label);
  }
  document.querySelector(".lesson-main").addEventListener("click", function (e) {
    var mic = e.target.closest(".lesson-verbal__btn");
    if (!mic) return;
    e.preventDefault();
    var api = typeof LinglongAPI !== "undefined" ? LinglongAPI : null;

    if (recordingState.active) {
      var stepNum = recordingState.stepNum;
      var recorder = recordingState.recorder;
      if (!api || !api.stt) {
        recordingState.active = false;
        if (recordingState.stream) {
          recordingState.stream.getTracks().forEach(function (t) { t.stop(); });
          recordingState.stream = null;
        }
        recordingState.recorder = null;
        mic.classList.remove("is-recording");
        setMicAriaLabel(mic, "Answer verbally");
        setVerbalLabel(mic, "Voice answer unavailable");
        return;
      }
      recorder.onstop = function () {
        if (!recordingState.chunks.length) {
          setVerbalLabel(mic, "Recording too short — try again");
          return;
        }
        setVerbalLabel(mic, "Converting…");
        var convertingStarted = Date.now();
        var minConvertingMs = 1200;
        function setLabelAfterConverting(msg) {
          var elapsed = Date.now() - convertingStarted;
          var wait = Math.max(0, minConvertingMs - elapsed);
          if (wait > 0) {
            setTimeout(function () { setVerbalLabel(mic, msg); }, wait);
          } else {
            setVerbalLabel(mic, msg);
          }
        }
        var blob = new Blob(recordingState.chunks, { type: "audio/webm" });
        recordingState.chunks = [];
        var reader = new FileReader();
        reader.onload = function () {
          var dataUrl = reader.result;
          api.stt({ audioUrlOrBase64: dataUrl, language: STT_LANGUAGE }).then(function (data) {
            setLabelAfterConverting("Or answer verbally");
            var transcript = data && data.text != null ? data.text : "";
            selectOptionByTranscript(stepNum, transcript);
          }).catch(function (err) {
            var msg = (err && (err.message || (err.data && err.data.error))) || "Conversion failed — try again";
            if (msg.length > 45) msg = msg.slice(0, 42) + "...";
            setLabelAfterConverting(msg);
            setTimeout(function () {
              setVerbalLabel(mic, "Or answer verbally");
            }, 4000);
          });
        };
        reader.readAsDataURL(blob);
      };
      try {
        if (typeof recorder.requestData === "function") recorder.requestData();
      } catch (err) {}
      recorder.stop();
      recordingState.active = false;
      if (recordingState.stream) {
        recordingState.stream.getTracks().forEach(function (t) { t.stop(); });
        recordingState.stream = null;
      }
      recordingState.recorder = null;
      mic.classList.remove("is-recording");
      setMicAriaLabel(mic, "Answer verbally");
      return;
    }

    var hasMediaDevices = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    if (!hasMediaDevices) {
      var origin = typeof window !== "undefined" && window.location && window.location.origin ? window.location.origin : "";
      var hint = origin && origin.indexOf("localhost") === -1 && origin.indexOf("127.0.0.1") === -1 && origin.indexOf("https") !== 0
        ? " Open http://localhost" + (window.location.port ? ":" + window.location.port : "") + " instead."
        : "";
      setVerbalLabel(mic, "Use HTTPS or localhost to record." + hint);
      return;
    }
    if (typeof MediaRecorder === "undefined") {
      setVerbalLabel(mic, "Recording not supported in this browser");
      return;
    }
    setVerbalLabel(mic, "Starting…");
    navigator.mediaDevices.getUserMedia({ audio: true }).then(function (stream) {
      try {
        var recorder = new MediaRecorder(stream);
        recordingState.stepNum = currentStep;
        recordingState.chunks = [];
        recordingState.stream = stream;
        recordingState.recorder = recorder;
        recorder.ondataavailable = function (ev) {
          if (ev.data && ev.data.size) recordingState.chunks.push(ev.data);
        };
        recorder.start(100);
        recordingState.active = true;
        mic.classList.add("is-recording");
        setMicAriaLabel(mic, "Stop recording");
        setVerbalLabel(mic, "Tap again to stop");
      } catch (recErr) {
        if (stream) stream.getTracks().forEach(function (t) { t.stop(); });
        setVerbalLabel(mic, "Recording not supported");
      }
    }).catch(function (err) {
      var msg = "Or answer verbally";
      if (err && err.name === "NotAllowedError") {
        msg = "Microphone access denied";
      } else if (err && err.name === "NotFoundError") {
        msg = "No microphone found";
      } else if (err && err.name === "NotSupportedError" || (err && err.message && err.message.indexOf("secure") !== -1)) {
        msg = "Use HTTPS or localhost to record";
      } else if (err) {
        msg = "Microphone error";
      }
      setVerbalLabel(mic, msg);
    });
  });

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
