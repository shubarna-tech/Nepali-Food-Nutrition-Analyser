// MUST be loaded as a regular script, tf is global
// No import statements needed

window.loadClassifierModel = async function () {
  console.log(
    "\u25b6\ufe0f Loading model from /static/myapp/models/classifier/model.json",
  );
  const model = await tf.loadGraphModel(
    "/static/myapp/models/classifier/model.json",
  );
  console.log("\u2705 Model loaded");
  return model;
};

window.loadDetectorModel = async function () {
  console.log(
    "\u25b6\ufe0f Loading detector model from /static/myapp/models/detector/model.json",
  );
  const model = await tf.loadGraphModel(
    "/static/myapp/models/detector/model.json",
  );
  console.log("\u2705 Detector model loaded");
  return model;
};
