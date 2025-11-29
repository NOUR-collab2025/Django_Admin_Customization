document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.querySelector("input[type='file']");
    const previewImg = document.getElementById("img-preview");

    if (!fileInput || !previewImg) return;

    fileInput.addEventListener("change", function (e) {
        const file = e.target.files[0];

        if (file) {
            const reader = new FileReader();
            reader.onload = function (event) {
                previewImg.src = event.target.result;
                previewImg.style.display = "block";
                previewImg.style.width = "150px";
                previewImg.style.height = "150px";
                previewImg.style.objectFit = "cover";
                previewImg.style.borderRadius = "10px";
            };
            reader.readAsDataURL(file);
        }
    });
});
