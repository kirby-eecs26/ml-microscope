1. Camera → AI Inputs
We pull image data from the OpenFlexure microscope over its HTTP API. The AI pipeline
does not talk to the camera hardware directly; instead, it uses a snapshot endpoint exposed
by the OpenFlexure server running on the Raspberry Pi.
Input Source (API Layer)
• GET /api/v2/camera/snapshot → returns a single still-frame image as JPEG or PNG bytes.
• (Optional, later) A streaming or repeated snapshot mechanism may be used for motion
tracking.
Required Image Specifications
Based on the Raspberry Pi Camera v2 (Sony IMX219 sensor):
• Supported resolutions include 3280×2464 (8 MP), 1920×1080, 1280×720, and 640×480.
• For AI, we will standardize to a fixed resolution (e.g., 1280×720) and optionally downsample
to 640×480 for speed.
Color & Bit Depth
• Camera output is RGB (via Bayer + ISP) or YUV, and we will accept RGB or convert to
grayscale in preprocessing.
• 8-bit per channel (uint8) is assumed.
File Format
• JPEG will be the default format from the OpenFlexure snapshot endpoint.
• PNG may be used when lossless images are desired for certain tests.
Metadata Needed
To support density and motion metrics, the AI side will also use optional metadata such as:
• Magnification level (e.g., 40× objective).
• Pixel size in µm/pixel from calibration.
• Timestamp for each frame (for motion analysis).
2. Preprocessing RequirementsBefore an image is passed into the AI model, the pipeline will perform several preprocessing
steps to ensure consistent input across different samples and lighting conditions.
Core preprocessing steps:
• Decode JPEG/PNG bytes into a NumPy array (via PIL or OpenCV).
• Convert RGB to grayscale if needed for segmentation-focused models.
• Normalize intensity (e.g., 0–255 or 0–1) and optionally apply contrast enhancement.
• Denoise using Gaussian or median filtering to reduce sensor noise.
• Resize to a fixed model input size (e.g., 512×512 or 640×480).
3. AI → Output Requirements
After processing each frame, the AI module will generate structured outputs that the
dashboard can use for visualization, logging, and possible feedback to the user.
Detection Outputs
• Total count of detected cells or organisms in the frame.
• Centroid (x, y) positions for each detected object.
• A segmentation mask or a list of bounding boxes for detected regions.
• Optional confidence scores if a learned model is used.
Density and Calibration Outputs
Using pixel size and magnification metadata, the AI side can compute:
• Estimated density (objects per mm²) for a given field of view.
• Basic size statistics (e.g., area in µm² for each object).
Motion / Tracking Outputs (Optional, Later Phase)
For time-series or video-like use cases, the pipeline may also output:
• A persistent ID for each tracked organism across frames.
• Position history or trajectory for each ID.
• Velocity estimates or classification into moving vs. static objects.

