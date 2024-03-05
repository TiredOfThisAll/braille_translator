function handleUpload() {
  fileInput.click();
}

function uploadFile(file, element) {
  const formData = new FormData();

  const csrf = document.querySelector("[name=csrfmiddlewaretoken]").value;
  const progressBar = element.querySelector(".progress-green");
  const downloadButton = element.querySelector(".download-button");
  const downloadLink = element.querySelector(".download-link");
  const imageCheckbox = document.querySelector("#image-checkbox");
  const translationCheckbox = document.querySelector("#translation-checkbox");
  const brailleCheckbox = document.querySelector("#braille-checkbox");
  const selectLanguage = document.querySelector("#language");
  
  formData.append("csrfmiddlewaretoken", csrf);
  formData.append("filename", file);
  formData.append("image_checkbox", imageCheckbox.checked);
  formData.append("translation_checkbox", translationCheckbox.checked);
  formData.append("braille_checkbox", brailleCheckbox.checked);
  formData.append("language", selectLanguage.value);

  fetch("upload/", {method:"POST", body:formData})
  .then(response => response.text())
  .then(uploadID => {
  let progress = 0;
  const getProgress = () => fetch("upload-status/?upload_id=" + uploadID)
  .then(response => response.text())
  .then(newProgress => {
    progress = parseInt(newProgress);
    progressBar.style.width = progress + "%";
    if (progress != 100) {
      setTimeout(getProgress, 1000);
    }
    if (progress == 100) {
      downloadButton.style.backgroundColor = "blue";
      downloadLink.href = "download/?upload_id=" + uploadID;
    }
  })
  getProgress();
  });
}

const fileInput = document.querySelector("[type=file]");
fileInput.addEventListener("change", function() {
  if (fileInput.files.length > 0) {
    const imageCheckbox = document.querySelector("#image-checkbox");
    const translationCheckbox = document.querySelector("#translation-checkbox");
    const brailleCheckbox = document.querySelector("#braille-checkbox");
    if (!imageCheckbox.checked & !translationCheckbox.checked & !brailleCheckbox.checked){
      return alert("Atleast one value should be choosen");
    } 

    let err = addElement();
    if (err === "Invalid datatype"){
      return alert(err);
    }
    let element = err;
    uploadFile(fileInput.files[0], element);
  }
});

function last(array) {
  return array[array.length-1];
}

function addElement() {
  const ext = last(fileInput.files[0].name.split("."))

  if (!["jpg", "jpeg", "png", "zip"].includes(ext)){
    return "Invalid datatype";
  }

  const newDiv = document.createElement("div");
  newDiv.classList.add("content");

  const fileReader = new FileReader()
  const newImage = document.createElement("img");
  fileReader.addEventListener("load", function() {
    if (ext === "zip") {
      newImage.src = "static/polls/images/zip_icon.png";
    }
    else {
      newImage.src = fileReader.result;
    }
    newImage.width = 120;
    newImage.height = 120;
  })
  fileReader.readAsDataURL(fileInput.files[0]);
  
  const nestedDivElement = document.createElement("div");

  const progressContainer = document.createElement("div");
  progressContainer.classList.add("progress-container");

  const progressGreen = document.createElement("div");
  progressGreen.classList.add("progress-green");
  progressGreen.id = "green";

  const progressWhite = document.createElement("div");
  progressWhite.classList.add("progress-white");
  progressWhite.id = "white";

  const textDiv = document.createElement("div");
  textDiv.textContent = fileInput.files[0].name;

  const downloadLink = document.createElement("a");
  downloadLink.classList.add("download-link");

  const downloadButton = document.createElement("button");
  downloadButton.textContent = "Download";
  downloadButton.classList.add("download-button");

  downloadLink.appendChild(downloadButton);

  progressContainer.appendChild(progressGreen);
  progressContainer.appendChild(progressWhite);

  nestedDivElement.appendChild(progressContainer);
  nestedDivElement.appendChild(textDiv);
  nestedDivElement.appendChild(downloadLink);

  newDiv.appendChild(newImage);
  newDiv.appendChild(nestedDivElement);

  const container = document.querySelector(".element-container");
  container.appendChild(newDiv);
  
  return newDiv;
}
