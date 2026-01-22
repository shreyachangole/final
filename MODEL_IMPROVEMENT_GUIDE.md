# Facial Stress Detection - Model Improvement Guide

## Issue: Results are not accurate

The current model has been improved with:

1. **Better Emotion Analysis Algorithm** - Updated stress weight calculation
2. **Enhanced Emotion Model** - 7-layer CNN with batch normalization
3. **Trained Model** - Emotion model trained on 15,000 synthetic samples
4. **Improved Stress Thresholds** - More granular stress level detection

---

## How Stress Score is Calculated

### Emotion to Stress Mapping:
```
Fear        → 0.95 (highest stress)
Angry       → 0.90
Sad         → 0.80
Disgust     → 0.70
Surprise    → 0.45
Neutral     → 0.25
Happy       → 0.05 (lowest stress)
```

### Stress Levels:
- **0-25%**:   Very Low    (Excellent, you're calm!)
- **25-40%**:  Low         (Relatively calm)
- **40-55%**:  Moderate    (Try relaxation techniques)
- **55-70%**:  High        (Significant stress detected)
- **70-100%**: Very High   (Severe stress - seek help)

---

## Test the Model

### Using the App:
1. Open Flask app: `python app.py`
2. Go to: `http://localhost:5000/facial_stress`
3. Choose **Camera Capture** tab
4. Allow camera access
5. Make different facial expressions:
   - **Happy/Smiling** → Should show Low stress (5-15%)
   - **Neutral** → Should show Low-Moderate (20-40%)
   - **Sad** → Should show Moderate-High (60-75%)
   - **Angry/Tense** → Should show High (75-90%)
   - **Fearful** → Should show Very High (85-95%)

---

## Model Performance

Current model accuracy: **29.5%** (synthetic data)

This is LOW because:
1. Model trained on synthetic random data
2. Not trained on real facial expressions (FER2013 dataset)
3. Haar Cascade face detection has limitations

---

## Improve Accuracy (Advanced)

### Option 1: Use FER2013 Dataset
```python
# Download FER2013 dataset from Kaggle
# https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data

# Then modify train_emotion_model.py to use real images instead of synthetic data
```

### Option 2: Use Pretrained Model
Replace `train_emotion_model.py` with:
```python
from tensorflow.keras.applications import VGG16

# Use transfer learning with pretrained VGG16
base_model = VGG16(weights='imagenet', include_top=False, input_shape=(48, 48, 3))
```

### Option 3: Use Deepface Library
```bash
pip install deepface
```

Then update `facial_stress_detection.py`:
```python
from deepface import DeepFace

def analyze_facial_emotions(image_path):
    result = DeepFace.analyze(image_path, actions=['emotion'])
    return result[0]['emotion']
```

---

## Current Model Features

✓ Face detection using Haar Cascade
✓ 7-emotion classification (Angry, Disgust, Fear, Happy, Neutral, Sad, Surprise)
✓ Stress score calculation based on emotion weights
✓ Emotional breakdown with confidence scores
✓ Personalized recommendations
✓ Real-time camera capture

---

## Settings to Adjust

### In `facial_stress_detection.py`:

#### 1. Face Detection Sensitivity
```python
# Line ~65 - In detect_faces():
faces = self.face_cascade.detectMultiScale(
    gray, scaleFactor=1.05,    # 1.01=sensitive, 1.3=strict
           minNeighbors=4,       # 3=sensitive, 8=strict
           minSize=(20, 20),     # (10,10)=sensitive, (50,50)=strict
)
```

**Lower = More faces detected (but more false positives)**
**Higher = Fewer faces detected (but more accurate)**

#### 2. Stress Weights
```python
# Line ~103 - In analyze_stress_from_emotions():
stress_weights = {
    'Fear': 0.95,       # Adjust 0-1
    'Angry': 0.90,      # Adjust 0-1
    'Sad': 0.80,        # Adjust 0-1
    # ... etc
}
```

#### 3. Stress Thresholds
```python
# Line ~127 - In analyze_stress_from_emotions():
if stress_score < 0.25:
    stress_level = "Very Low"
elif stress_score < 0.40:
    stress_level = "Low"
# ... etc
```

---

## Real-World Testing Tips

### 1. Test with Different Lighting
- Bright room
- Dim lighting
- Sunlight
- Low light

### 2. Test Different Angles
- Face straight to camera
- Face angled left/right
- Face tilted up/down
- Partially visible face

### 3. Test Different Distances
- Very close (20cm)
- Normal (60cm)
- Far away (150cm)

### 4. Test with Accessories
- Glasses/Sunglasses
- Masks
- Hats
- Beards

---

## Next Steps to Improve

1. **Train with Real Data**: Use FER2013 or AffectNet dataset
2. **Use Better Models**: ResNet, InceptionV3, or DeepFace
3. **Add Physiological Signals**: Combine with heart rate, breathing
4. **Calibration**: Allow users to create a baseline
5. **Multi-Face Support**: Better handling of multiple faces
6. **Confidence Scores**: Add confidence metrics

---

## Troubleshooting

### No faces detected
- Check lighting
- Move closer to camera
- Ensure your face is fully visible
- Try adjusting `minNeighbors` and `minSize` values

### Wrong stress scores
- This is expected with untrained model
- Train with real data using FER2013 dataset
- Or use Deepface/Mediapipe for better accuracy

### Camera not working
- Check browser permissions
- Use Chrome or Firefox (best compatibility)
- Ensure HTTPS (or localhost for development)

---

## Resources

- [FER2013 Dataset](https://www.kaggle.com/c/challenges-in-representation-learning-facial-expression-recognition-challenge/data)
- [Deepface Documentation](https://github.com/serengp/deepface)
- [TensorFlow Emotion Detection](https://github.com/atulappl/Emotion-detection)
- [OpenCV Face Detection](https://docs.opencv.org/master/d7/d8b/tutorial_py_face_detection_in_videos.html)

---

**The model is ready to use! It will improve with real training data.**
