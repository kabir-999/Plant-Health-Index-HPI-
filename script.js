document.getElementById('uploadButton').addEventListener('click', async function() {
    const fileInput = document.getElementById('imageInput');
    if (fileInput.files.length === 0) {
        alert("Please upload an image.");
        return;
    }

    const formData = new FormData();
    formData.append("image", fileInput.files[0]);

    // Convert image to URL
    const imageUrl = await uploadImage(fileInput.files[0]);

    // Call the Flask API to get HPI data
    const response = await fetch("https://your-render-app-url/process_image_url", { // Update with your Render app URL
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            image_url: imageUrl
        })
    });

    if (!response.ok) {
        alert("Error processing image.");
        return;
    }

    const data = await response.json();
    
    // Display HPI values and health status
    document.getElementById('healthStatus').textContent = data.health_status;
    document.getElementById('averageHpi').textContent = data.average_hpi;
    document.getElementById('hpiValues').textContent = JSON.stringify(data.hpi_percentage, null, 2);
    document.getElementById('hpiImage').src = `data:image/png;base64,${data.hpi_image}`;
});

async function uploadImage(file) {
    const formData = new FormData();
    formData.append("file", file);

    const response = await fetch("/upload", {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        throw new Error('Failed to upload image');
    }

    const data = await response.json();
    return data.image_url;
}
