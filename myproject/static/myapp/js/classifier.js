// Food class and nutrition mapping (should match backend)
const FOOD_CLASSES = [
  "burger",
  "chiya",
  "dalbhat",
  "friedrice",
  "jeri",
  "momo",
  "omelette",
  "pakoda",
  "panipuri",
  "pizza",
  "roti",
  "samosa",
  "selroti",
  "yomari",
  "chatamari",
  "chhoila",
  "dhindo",
  "gundruk",
  "kheer",
  "sekuwa",
];
const CALS = [
  500, 120, 450, 300, 160, 300, 150, 180, 100, 285, 120, 150, 200, 250, 180,
  280, 300, 65, 200, 250,
];

const FOOD_NUTRITION = [
  { calories: 500, protein: 25, fat: 22, carbs: 45, fiber: 3 }, // burger
  { calories: 120, protein: 2, fat: 4, carbs: 18, fiber: 0 }, // chiya
  { calories: 450, protein: 12, fat: 8, carbs: 80, fiber: 5 }, // dalbhat
  { calories: 300, protein: 7, fat: 6, carbs: 50, fiber: 2 }, // friedrice
  { calories: 160, protein: 2, fat: 5, carbs: 32, fiber: 1 }, // jeri
  { calories: 300, protein: 12, fat: 10, carbs: 38, fiber: 2 }, // momo
  { calories: 150, protein: 10, fat: 12, carbs: 2, fiber: 0 }, // omelette
  { calories: 180, protein: 5, fat: 10, carbs: 20, fiber: 2 }, // pakoda
  { calories: 100, protein: 3, fat: 2, carbs: 18, fiber: 1 }, // panipuri
  { calories: 285, protein: 12, fat: 10, carbs: 36, fiber: 2 }, // pizza
  { calories: 120, protein: 3, fat: 1, carbs: 25, fiber: 2 }, // roti
  { calories: 150, protein: 4, fat: 8, carbs: 18, fiber: 2 }, // samosa
  { calories: 200, protein: 3, fat: 6, carbs: 36, fiber: 1 }, // selroti
  { calories: 250, protein: 4, fat: 5, carbs: 48, fiber: 2 }, // yomari
  { calories: 180, protein: 5, fat: 4, carbs: 32, fiber: 1 }, // chatamari
  { calories: 280, protein: 20, fat: 18, carbs: 6, fiber: 1 }, // chhoila
  { calories: 300, protein: 6, fat: 2, carbs: 60, fiber: 4 }, // dhindo
  { calories: 65, protein: 3, fat: 0, carbs: 14, fiber: 5 }, // gundruk
  { calories: 200, protein: 5, fat: 6, carbs: 34, fiber: 0 }, // kheer
  { calories: 250, protein: 22, fat: 15, carbs: 4, fiber: 1 }, // sekuwa
];

function getCookie(name) {
  let value = null;
  document.cookie.split(";").forEach((cookie) => {
    const [k, v] = cookie.trim().split("=");
    if (k === name) value = decodeURIComponent(v);
  });
  return value;
}

async function postResult(cls, conf, imageData) {
  if (conf < 0.5) return; // only high-confidence
  try {
    await fetch("/api/track/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ class: cls, confidence: conf, image: imageData }),
    });
  } catch (e) {
    console.error("\u274c Post error:", e);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const videoEl = document.getElementById("webcam");
  const canvasEl = document.getElementById("capture-canvas");
  const captureBtn = document.getElementById("capture-btn");
  const retakeBtn = document.getElementById("retake-btn");
  const errorEl = document.getElementById("error-msg");
  const resultSection = document.getElementById("scan-result");
  const foodNameEl = document.getElementById("food-name");
  const foodNutritionEl = document.getElementById("food-nutrition");
  const foodImageEl = document.getElementById("food-image");
  const addMealBtn = document.getElementById("add-meal-btn");
  let model, stream;
  let detectorModel;
  let lastScan = null;
  let facingMode = "environment"; // still default, but no toggle UI

  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: facingMode },
        audio: false,
      });
      videoEl.srcObject = stream;
      await videoEl.play().catch(() => {});
      videoEl.classList.remove("hidden");
      canvasEl.classList.add("hidden");
      captureBtn.classList.remove("hidden");
      retakeBtn.classList.add("hidden");
      resultSection.classList.add("hidden");
      errorEl.textContent = "";
    } catch (e) {
      console.error("Camera error:", e);
      errorEl.textContent = "Camera error: " + (e.message || e.name);
    }
  }

  async function captureAndClassify() {
    console.log("captureAndClassify called");
    // Draw current frame to canvas
    canvasEl.width = videoEl.videoWidth;
    canvasEl.height = videoEl.videoHeight;
    const ctx = canvasEl.getContext("2d");
    ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
    // Hide video, show canvas
    videoEl.classList.add("hidden");
    canvasEl.classList.remove("hidden");
    captureBtn.classList.add("hidden");
    retakeBtn.classList.remove("hidden");

    // Get image data as base64
    const imageData = canvasEl.toDataURL("image/jpeg");

    // Load models if needed
    try {
      console.log("Checking classifier model...");
      if (!model) {
        try {
          model = await window.loadClassifierModel();
          console.log("Classifier model loaded in captureAndClassify");
        } catch (e) {
          errorEl.textContent = "Failed to load classifier model";
          console.error("Failed to load classifier model", e);
          return;
        }
      }
      console.log("Checking detector model...");
      if (!detectorModel) {
        try {
          detectorModel = await window.loadDetectorModel();
          console.log("Detector model loaded in captureAndClassify");
        } catch (e) {
          errorEl.textContent = "Failed to load detector model";
          console.error("Failed to load detector model", e);
          return;
        }
      }
      console.log("Models loaded, starting detection...");
    } catch (e) {
      console.error("Error during model loading:", e);
      errorEl.textContent = "Error during model loading.";
      return;
    }

    // Run detection first
    try {
      console.log("Preparing input tensor for detection...");
      const input = tf.image
        .resizeBilinear(tf.browser.fromPixels(canvasEl), [128, 128])
        .expandDims(0);
      console.log("Calling detectorModel.executeAsync...");
      const detResult = await detectorModel.executeAsync(input);
      console.log("Detector model output:", detResult);
      if (!detResult) {
        console.error("Detector model returned null/undefined");
        errorEl.textContent = "Detector model returned no output.";
        return;
      }
      // Handle single tensor output [1, 4]
      let boxesArr;
      if (
        detResult.shape &&
        detResult.shape.length === 2 &&
        detResult.shape[0] === 1 &&
        detResult.shape[1] === 4
      ) {
        boxesArr = detResult.arraySync(); // [[ymin, xmin, ymax, xmax]]
        console.log("Single box detected:", boxesArr[0]);
      } else {
        errorEl.textContent = "Detector model output shape not recognized.";
        console.error("Unexpected detector output shape:", detResult.shape);
        return;
      }
      // Clean up tensors
      input.dispose();
      detResult.dispose && detResult.dispose();
      // If all zeros, treat as no detection
      const box = boxesArr[0];
      if (!box || box.every((v) => v === 0)) {
        errorEl.textContent = "No food detected.";
        resultSection.classList.add("hidden");
        addMealBtn.classList.add("hidden");
        console.log("No detection found (all zeros).");
        return;
      }
      // For the detected box, crop and classify
      const [ymin, xmin, ymax, xmax] = box;
      // Calculate portion area as percent of image
      const boxW = (xmax - xmin) * canvasEl.width;
      const boxH = (ymax - ymin) * canvasEl.height;
      let portionPct =
        ((boxW * boxH) / (canvasEl.width * canvasEl.height)) * 100;
      // If box touches any image edge, halve the portion estimate
      let edgeCorrection = false;
      if (
        Math.abs(xmin) < 0.01 ||
        Math.abs(ymin) < 0.01 ||
        Math.abs(xmax - 1) < 0.01 ||
        Math.abs(ymax - 1) < 0.01
      ) {
        portionPct = portionPct / 2;
        edgeCorrection = true;
      }
      // Crop image data for classification
      const cropX = Math.round(xmin * canvasEl.width);
      const cropY = Math.round(ymin * canvasEl.height);
      const cropW = Math.round(boxW);
      const cropH = Math.round(boxH);
      // Create a temp canvas for the crop
      const cropCanvas = document.createElement("canvas");
      cropCanvas.width = cropW;
      cropCanvas.height = cropH;
      const cropCtx = cropCanvas.getContext("2d");
      cropCtx.drawImage(
        canvasEl,
        cropX,
        cropY,
        cropW,
        cropH,
        0,
        0,
        cropW,
        cropH,
      );
      // Preprocess for classifier
      let predClass = null,
        predConf = null;
      try {
        let imgTensor = tf.browser.fromPixels(cropCanvas);
        const inputCls = tf.image
          .resizeBilinear(imgTensor, [224, 224])
          .div(255)
          .expandDims(0);
        imgTensor.dispose();
        const pred = model.predict(inputCls);
        predClass = pred.argMax(-1).dataSync()[0];
        predConf = pred.max().dataSync()[0];
        pred.dispose();
        inputCls.dispose();
      } catch (err) {
        predClass = null;
        predConf = null;
        console.error("Classification error for detection:", err);
      }
      // Draw box
      ctx.strokeStyle = "#059669";
      ctx.lineWidth = 3;
      const x = xmin * canvasEl.width;
      const y = ymin * canvasEl.height;
      const w = (xmax - xmin) * canvasEl.width;
      const h = (ymax - ymin) * canvasEl.height;
      ctx.strokeRect(x, y, w, h);
      // Show result in UI
      let html = "";
      if (predClass !== null && predConf >= 0.7) {
        const nut = FOOD_NUTRITION[predClass];
        // Scale nutrition by portion percentage
        const scale = portionPct / 100;
        const estCalories = Math.round(nut.calories * scale);
        const estProtein = (nut.protein * scale).toFixed(1);
        const estFat = (nut.fat * scale).toFixed(1);
        const estCarbs = (nut.carbs * scale).toFixed(1);
        const estFiber = (nut.fiber * scale).toFixed(1);
        html += `<div class="bg-green-50 rounded-xl shadow p-4 mb-4 flex flex-col items-center border border-green-100">
          <img src="${cropCanvas.toDataURL("image/jpeg")}" alt="Food Crop" class="rounded-lg max-h-24 mb-2" />
          <div class="font-bold text-lg text-green-800 mb-1">${FOOD_CLASSES[predClass].charAt(0).toUpperCase() + FOOD_CLASSES[predClass].slice(1)}</div>
          <div class="text-gray-700 mb-1">Portion: ${portionPct.toFixed(1)}% of image</div>
          <div class="text-gray-600">Estimated Calories: <b>${estCalories}</b> kcal</div>
          <div class="text-gray-600">Estimated Protein: <b>${estProtein}</b> g</div>
          <div class="text-gray-600">Estimated Fat: <b>${estFat}</b> g</div>
          <div class="text-gray-600">Estimated Carbs: <b>${estCarbs}</b> g</div>
          <div class="text-gray-600">Estimated Fiber: <b>${estFiber}</b> g</div>
          <button id="add-meal-btn" class="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg shadow hover:bg-blue-700 text-lg font-semibold transition">Add</button>
        </div>`;
      } else {
        html += `<div class="text-red-600 font-bold">Could not confidently identify food.</div>`;
      }
      resultSection.innerHTML = `<h3 class="text-xl font-semibold text-green-700 mb-2">Result</h3>${html}`;
      resultSection.classList.remove("hidden");
      errorEl.textContent = "";
      // Add event listener for the new Add button
      const addBtn = document.getElementById("add-meal-btn");
      if (addBtn) {
        addBtn.onclick = async () => {
          // Use the last detected/estimated values for logging
          await postResult(
            predClass,
            predConf,
            cropCanvas.toDataURL("image/jpeg"),
          );
          addBtn.disabled = true;
          addBtn.textContent = "Added!";
        };
      }
    } catch (e) {
      console.error("Detection error (exception):", e);
      errorEl.textContent = "Detection error (exception).";
      return;
    }
  }

  captureBtn.addEventListener("click", captureAndClassify);
  retakeBtn.addEventListener("click", () => {
    startCamera();
  });

  addMealBtn.addEventListener("click", async () => {
    if (!lastScan) return;
    await postResult(lastScan.cls, lastScan.conf, lastScan.imageData);
    addMealBtn.classList.add("hidden");
    errorEl.textContent = "Meal added to history!";
  });

  // Start camera on load
  startCamera();
});
