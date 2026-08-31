/* Shared selfie + liveness-burst camera capture widget for the babysitter
   registration and family booking forms. Captures one selfie frame plus a
   short burst of extra frames (asking the user to slowly turn their head)
   so Smile ID's Biometric KYC product can run a facial-liveness check.
   No file upload involved - this reads directly from the device camera. */
window.ETLSelfieCapture = (function () {
  'use strict';

  var BURST_COUNT = 5;
  var BURST_INTERVAL_MS = 350;

  function attach(prefix) {
    var startBtn = document.getElementById(prefix + '-start-btn');
    var captureBtn = document.getElementById(prefix + '-capture-btn');
    var retakeBtn = document.getElementById(prefix + '-retake-btn');
    var video = document.getElementById(prefix + '-video');
    var preview = document.getElementById(prefix + '-preview');
    var placeholder = document.getElementById(prefix + '-placeholder');
    var canvas = document.getElementById(prefix + '-canvas');
    var status = document.getElementById(prefix + '-status');
    if (!startBtn || !video || !canvas) return null;

    var stream = null;
    var selfieData = null;
    var livenessFrames = [];

    function setStatus(msg, ok) {
      if (!status) return;
      status.textContent = msg;
      status.className = 'file-status' + (ok === true ? ' file-status--ok' : ok === false ? ' file-status--error' : '');
    }

    function stopStream() {
      if (stream) {
        stream.getTracks().forEach(function (t) { t.stop(); });
        stream = null;
      }
    }

    function frameToBase64() {
      var ctx = canvas.getContext('2d');
      canvas.width = video.videoWidth || 480;
      canvas.height = video.videoHeight || 360;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      var dataUrl = canvas.toDataURL('image/jpeg', 0.85);
      return dataUrl.slice(dataUrl.indexOf(',') + 1);
    }

    function wait(ms) {
      return new Promise(function (resolve) { setTimeout(resolve, ms); });
    }

    startBtn.addEventListener('click', async function () {
      setStatus('Requesting camera access, please allow it in your browser.', null);
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' }, audio: false });
        video.srcObject = stream;
        video.hidden = false;
        if (preview) preview.hidden = true;
        if (placeholder) placeholder.hidden = true;
        startBtn.hidden = true;
        captureBtn.hidden = false;
        retakeBtn.hidden = true;
        setStatus('Camera is on. Look straight at the camera and press Capture.', null);
      } catch (err) {
        setStatus('We could not access your camera. Please allow camera permission in your browser and try again.', false);
      }
    });

    captureBtn.addEventListener('click', async function () {
      captureBtn.disabled = true;
      setStatus('Capturing, please hold still and slowly turn your head slightly.', null);
      selfieData = frameToBase64();
      livenessFrames = [selfieData];
      for (var i = 1; i < BURST_COUNT; i++) {
        await wait(BURST_INTERVAL_MS);
        livenessFrames.push(frameToBase64());
      }
      if (preview) {
        preview.src = 'data:image/jpeg;base64,' + selfieData;
        preview.hidden = false;
      }
      video.hidden = true;
      stopStream();
      captureBtn.hidden = true;
      retakeBtn.hidden = false;
      captureBtn.disabled = false;
      setStatus('Selfie captured. You can retake it below if needed.', true);
    });

    retakeBtn.addEventListener('click', function () {
      selfieData = null;
      livenessFrames = [];
      if (preview) preview.hidden = true;
      if (placeholder) placeholder.hidden = false;
      retakeBtn.hidden = true;
      startBtn.hidden = false;
      setStatus('', null);
    });

    function reset() {
      selfieData = null;
      livenessFrames = [];
      stopStream();
      if (preview) preview.hidden = true;
      if (placeholder) placeholder.hidden = false;
      video.hidden = true;
      startBtn.hidden = false;
      captureBtn.hidden = true;
      retakeBtn.hidden = true;
      setStatus('', null);
    }

    function getData() {
      if (!selfieData || livenessFrames.length < 3) return null;
      return { selfie_data: selfieData, liveness_images: livenessFrames };
    }

    function buildFields() {
      var data = getData();
      if (!data) {
        throw new Error('Please capture a selfie using your camera (turn on your camera, then press Capture).');
      }
      return {
        selfie_data: data.selfie_data,
        selfie_filename: 'selfie.jpg',
        selfie_mimetype: 'image/jpeg',
        liveness_images: data.liveness_images,
      };
    }

    return { getData: getData, buildFields: buildFields, reset: reset };
  }

  return { attach: attach };
})();
