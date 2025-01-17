import os
import matplotlib
matplotlib.use('Agg')  # Use Agg backend for matplotlib (no GUI)

from flask import Flask, render_template, request
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm

app = Flask(__name__)

# Set the upload folder and spectral image folder
UPLOAD_FOLDER = 'uploads/'
SPECTRAL_FOLDER = 'static/spectral_images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SPECTRAL_FOLDER'] = SPECTRAL_FOLDER

# Ensure the directories exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(app.config['SPECTRAL_FOLDER']):
    os.makedirs(app.config['SPECTRAL_FOLDER'])

# Function to process the image and calculate a Health Plant Index (HPI)
def calculate_hpi_from_image(image):
    grayscale_image = image.convert('L')
    image_array = np.array(grayscale_image)
    hpi_min = np.min(image_array)
    hpi_max = np.max(image_array)
    hpi_normalized = (image_array - hpi_min) / (hpi_max - hpi_min)
    hpi_percentage = hpi_normalized * 100
    return hpi_normalized, hpi_percentage

# Main route to handle image upload and HPI calculation
@app.route('/', methods=['GET', 'POST'])
def index():
    predicted_hpi = None
    health_status = None
    error_message = None
    spectral_image_path = None

    if request.method == 'POST':
        if 'image' not in request.files:
            error_message = 'No file part'
            return render_template('index.html', error_message=error_message)

        image_file = request.files['image']

        if image_file.filename == '':
            error_message = 'No selected file'
            return render_template('index.html', error_message=error_message)

        try:
            # Save the image
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
            image_file.save(image_path)

            # Process the image to calculate HPI
            image = Image.open(image_path)
            hpi_normalized, hpi_percentage = calculate_hpi_from_image(image)
            avg_hpi = np.mean(hpi_percentage)

            # Determine health status
            if avg_hpi < 25:
                health_status = "Poor"
            elif 25 <= avg_hpi < 50:
                health_status = "Moderate"
            elif 50 <= avg_hpi < 75:
                health_status = "Good"
            else:
                health_status = "Excellent"

            predicted_hpi = avg_hpi

            # Generate the spectral image
            spectral_image = os.path.join(app.config['SPECTRAL_FOLDER'], f"spectral_{image_file.filename}")
            plt.imshow(hpi_percentage, cmap=cm.jet)
            plt.colorbar()
            plt.axis('off')
            plt.savefig(spectral_image, bbox_inches='tight', pad_inches=0, transparent=True)
            plt.close()

            spectral_image_path = f"spectral_images/spectral_{image_file.filename}"

        except Exception as e:
            error_message = str(e)

    return render_template('index.html', predicted_hpi=predicted_hpi, health_status=health_status, error_message=error_message, spectral_image_path=spectral_image_path)

if __name__ == '__main__':
    app.run(debug=True)
