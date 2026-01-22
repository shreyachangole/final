# 📖 API Reference - DeepFace Stress Detection

## Overview

Your stress detection system provides multiple endpoints and functions for facial emotion recognition and stress analysis.

---

## 🐍 Python API

### 1. Initialize Detector

```python
from facial_stress_detection import initialize_facial_detector

detector = initialize_facial_detector()
# Returns: FacialStressDetector instance
# Status: Ready for analysis
```

---

### 2. Analyze Image File

```python
from facial_stress_detection import get_facial_stress_analysis

result = get_facial_stress_analysis('path/to/image.jpg')

# Returns:
{
    'success': bool,                    # True if analysis succeeded
    'faces_detected': int,              # Number of faces found
    'average_stress_score': float,      # 0.0-1.0 overall stress
    'overall_stress_level': str,        # 'Very Low', 'Low', 'Moderate', 'High', 'Very High'
    'face_data': [                      # List of face analyses
        {
            'face_id': int,
            'stress_score': float,      # 0.0-1.0 individual stress
            'stress_level': str,
            'dominant_emotion': str,    # Primary detected emotion
            'emotion_confidence': float,# 0.0-1.0 confidence
            'all_emotions': dict,       # All emotions with scores
            'recommendations': list     # Wellness suggestions
        },
        # ... more faces
    ]
}
```

**Parameters:**
- `image_path` (str): Path to image file (JPG, PNG, BMP, GIF)

**Returns:** Dict with stress analysis

**Example:**
```python
result = get_facial_stress_analysis('photo.jpg')

if result['success']:
    print(f"Stress: {result['average_stress_score']}")
    print(f"Level: {result['overall_stress_level']}")
    print(f"Faces: {result['faces_detected']}")
else:
    print(f"Error: {result['error']}")
```

---

### 3. Analyze Base64 Image

```python
from facial_stress_detection import get_facial_stress_from_base64

result = get_facial_stress_from_base64(base64_string)

# Returns: Same as get_facial_stress_analysis()
```

**Parameters:**
- `base64_string` (str): Base64 encoded image (with or without prefix)

**Supports:**
- `data:image/jpeg;base64,...` format
- Raw base64 string

**Example:**
```python
# From camera capture
canvas = request.form.get('image')
result = get_facial_stress_from_base64(canvas)

# From fetch API
base64_data = "data:image/jpeg;base64,/9j/4AAQSkZJR..."
result = get_facial_stress_from_base64(base64_data)
```

---

### 4. Combine Multimodal Predictions

```python
from facial_stress_detection import combine_multimodal_predictions

result = combine_multimodal_predictions(
    facial_stress=0.52,           # 0.0-1.0 from DeepFace
    physiological_stress=0.45,    # 0.0-1.0 from HR, BP, etc
    text_stress=0.38              # 0.0-1.0 from NLP analysis
)

# Returns:
{
    'combined_score': float,                    # 0.0-1.0 weighted average
    'stress_level': str,                        # Stress classification
    'facial_contribution': str,                 # "35%"
    'physiological_contribution': str,          # "35%"
    'text_contribution': str                    # "30%"
}
```

**Parameters:**
- `facial_stress` (float): 0.0-1.0 stress score
- `physiological_stress` (float): 0.0-1.0 stress score
- `text_stress` (float): 0.0-1.0 stress score

**Weights:**
- Facial: 35%
- Physiological: 35%
- Text: 30%

**Example:**
```python
combined = combine_multimodal_predictions(
    facial_stress=0.52,
    physiological_stress=0.45,
    text_stress=0.38
)

print(combined['combined_score'])      # 0.4535
print(combined['stress_level'])        # "Moderate"
```

---

## 🌐 REST API (Flask)

### 1. Analyze Uploaded Image

**Endpoint:**
```
POST /analyze_facial_stress
Content-Type: multipart/form-data
```

**Parameters:**
- `image` (file): Image file (JPG, PNG, GIF, BMP)

**Response:**
```json
{
  "success": true,
  "faces_detected": 1,
  "average_stress_score": 0.52,
  "overall_stress_level": "Moderate",
  "face_data": [...]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/analyze_facial_stress \
  -F "image=@photo.jpg"
```

**Python Requests:**
```python
import requests

with open('photo.jpg', 'rb') as f:
    files = {'image': f}
    response = requests.post(
        'http://localhost:5000/analyze_facial_stress',
        files=files
    )
    result = response.json()
```

---

### 2. Analyze Camera Image

**Endpoint:**
```
POST /analyze_facial_stress_camera
Content-Type: application/json
```

**Body:**
```json
{
  "image": "data:image/jpeg;base64,..."
}
```

**Response:**
```json
{
  "success": true,
  "faces_detected": 1,
  "average_stress_score": 0.52,
  "overall_stress_level": "Moderate",
  "face_data": [...]
}
```

**JavaScript Example:**
```javascript
const canvas = document.getElementById('camera');
const image = canvas.toDataURL('image/jpeg');

fetch('/analyze_facial_stress_camera', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({image: image})
})
.then(r => r.json())
.then(data => {
    console.log('Stress:', data.average_stress_score);
    console.log('Emotions:', data.face_data[0].all_emotions);
});
```

---

### 3. Get Facial Stress Page

**Endpoint:**
```
GET /facial_stress
```

**Returns:** HTML page with UI for camera and upload

**Access:** http://localhost:5000/facial_stress

---

## 📊 Data Structures

### Emotion Dictionary
```python
{
    'happy': 0.08,      # 0.0-1.0 confidence
    'sad': 0.62,
    'angry': 0.12,
    'fear': 0.08,
    'disgust': 0.06,
    'surprise': 0.02,
    'neutral': 0.02
}
```

### Face Data Object
```python
{
    'face_id': 1,
    'stress_score': 0.68,
    'stress_level': 'High',
    'dominant_emotion': 'sad',
    'emotion_confidence': 0.62,
    'all_emotions': {...},
    'recommendations': [
        '⚠️ High stress detected',
        '🧘 Try meditation',
        '...'
    ]
}
```

### Recommendation Types
```
Very Low (0.00-0.20):
- ✅ Excellent! Your stress level is very low
- 🧘 Maintain current healthy habits
- 📚 Continue with regular mindfulness practice

Low (0.20-0.35):
- ✅ Good! Your stress level is low
- 🎯 Keep up with healthy stress management
- 💪 Regular exercise helps maintain low stress

Moderate (0.35-0.50):
- ⚠️ Moderate stress detected
- 🧘 Try meditation or mindfulness exercises
- 🚶 Take a short break from current activities
- 🎵 Listen to calming music

High (0.50-0.70):
- ⚠️⚠️ High stress detected
- 🧘 Practice progressive muscle relaxation
- 💨 Try deep breathing exercises
- 📞 Consider talking to someone
- 🏃 Physical exercise can reduce stress

Very High (0.70-1.00):
- 🚨 Very high stress detected
- 📞 Consider professional support
- 🧘 Immediate relaxation needed
- 💨 Practice the 4-7-8 breathing technique
- 😴 Ensure adequate rest and sleep
```

---

## 🎨 Error Handling

### Successful Response
```python
{
    'success': True,
    'faces_detected': 1,
    'average_stress_score': 0.52,
    'overall_stress_level': 'Moderate',
    'face_data': [...]
}
```

### Error Response
```python
{
    'success': False,
    'error': 'No faces detected in image',
    'faces_detected': 0
}
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `'No faces detected'` | Face not visible | Better lighting, center face |
| `'Faces detected but emotion analysis failed'` | Edge case | Try different angle |
| `'Could not read image'` | Invalid file | Use JPG, PNG, GIF |
| `'Could not decode image'` | Corrupted file | Re-upload image |

---

## 🔌 Integration Examples

### Flask/Python App
```python
from flask import Flask, request, jsonify
from facial_stress_detection import get_facial_stress_analysis

@app.route('/stress', methods=['POST'])
def analyze_stress():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    
    file = request.files['image']
    file.save('temp.jpg')
    
    result = get_facial_stress_analysis('temp.jpg')
    return jsonify(result)
```

### JavaScript/React
```javascript
async function analyzeFacialStress(imageBase64) {
    const response = await fetch('/analyze_facial_stress_camera', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({image: imageBase64})
    });
    
    const data = await response.json();
    
    if (data.success) {
        console.log(`Stress: ${data.average_stress_score}`);
        data.face_data.forEach(face => {
            console.log(`Emotion: ${face.dominant_emotion}`);
            face.recommendations.forEach(rec => {
                console.log(`  • ${rec}`);
            });
        });
    } else {
        console.error(`Error: ${data.error}`);
    }
}
```

### Multimodal Analysis
```python
def get_total_stress(image_path, heart_rate, text_input):
    # Get facial stress
    facial_result = get_facial_stress_analysis(image_path)
    facial_score = facial_result['average_stress_score']
    
    # Calculate physiological stress
    # (HR = 100 → stress = 0.5)
    physio_score = min((heart_rate - 60) / 80, 1.0)
    
    # Get text stress from NLP model
    # (assuming text_model exists)
    text_score = analyze_text_stress(text_input)
    
    # Combine all three
    combined = combine_multimodal_predictions(
        facial_stress=facial_score,
        physiological_stress=physio_score,
        text_stress=text_score
    )
    
    return combined
```

---

## 📈 Response Codes

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | `{'success': True, ...}` |
| 400 | Bad Request | Missing image file |
| 500 | Server Error | DeepFace failure |

### Success/Failure Flag

```python
# Always check success flag
if result['success']:
    # Process results
    stress = result['average_stress_score']
else:
    # Handle error
    error = result['error']
```

---

## 🚀 Performance Notes

### Processing Time
- Face Detection: ~100-200ms
- Emotion Recognition: ~50-100ms
- Stress Calculation: ~10ms
- **Total: ~200-300ms per face**

### Optimization Tips
1. Resize large images before uploading
2. Use GPU if available (auto-detected)
3. Process multiple faces in parallel
4. Cache results for same image

### Batch Processing
```python
from facial_stress_detection import get_facial_stress_analysis
import os
from pathlib import Path

# Analyze all images in directory
image_dir = Path('images/')
results = []

for image_file in image_dir.glob('*.jpg'):
    result = get_facial_stress_analysis(str(image_file))
    results.append({
        'file': image_file.name,
        'stress': result['average_stress_score'],
        'level': result['overall_stress_level']
    })

# Print summary
for r in results:
    print(f"{r['file']}: {r['stress']:.2f} ({r['level']})")
```

---

## 🔐 Security Considerations

### Input Validation
```python
# Validate file type
ALLOWED = {'jpg', 'jpeg', 'png', 'gif', 'bmp'}
extension = filename.rsplit('.', 1)[1].lower()
if extension not in ALLOWED:
    return error('Invalid file type')

# Validate file size
MAX_SIZE = 16 * 1024 * 1024  # 16MB
if len(file) > MAX_SIZE:
    return error('File too large')
```

### Privacy
- ✅ All processing is local
- ✅ No images sent to cloud
- ✅ No data stored
- ✅ No tracking

---

## 📚 Complete Examples

### Example 1: Simple Analysis
```python
from facial_stress_detection import get_facial_stress_analysis

result = get_facial_stress_analysis('photo.jpg')
print(f"Stress Level: {result['overall_stress_level']}")
```

### Example 2: Detailed Report
```python
result = get_facial_stress_analysis('photo.jpg')

if result['success']:
    print(f"Analyzed {result['faces_detected']} face(s)")
    print(f"Average Stress: {result['average_stress_score']:.2%}")
    
    for face in result['face_data']:
        print(f"\nFace #{face['face_id']}")
        print(f"  Emotion: {face['dominant_emotion']}")
        print(f"  Stress: {face['stress_score']:.2%}")
        print("  Recommendations:")
        for rec in face['recommendations']:
            print(f"    - {rec}")
```

### Example 3: Batch Processing
```python
import glob
from facial_stress_detection import get_facial_stress_analysis

for image in glob.glob('photos/*.jpg'):
    result = get_facial_stress_analysis(image)
    if result['success']:
        print(f"{image}: {result['overall_stress_level']}")
```

---

## 🎯 Quick Reference

| Task | Function | Returns |
|------|----------|---------|
| Initialize | `initialize_facial_detector()` | Detector |
| Analyze image | `get_facial_stress_analysis()` | Dict |
| Analyze base64 | `get_facial_stress_from_base64()` | Dict |
| Combine results | `combine_multimodal_predictions()` | Dict |

---

## 📞 Support

### Check Status
```python
from facial_stress_detection import initialize_facial_detector

detector = initialize_facial_detector()
print("Detector ready:", detector is not None)
```

### Debug Mode
```python
# Add debug output
import logging
logging.basicConfig(level=logging.DEBUG)

result = get_facial_stress_analysis('photo.jpg')
```

---

*API Reference Version: 2.0*
*Last Updated: 2026-01-22*
*Status: ✅ COMPLETE*
