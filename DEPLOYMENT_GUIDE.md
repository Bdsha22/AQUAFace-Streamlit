# 🚀 AQUAFace-Lite: Complete Deployment Guide

## 📋 File Checklist

Your complete Streamlit application includes:

```
✅ app.py                    - Main Streamlit frontend
✅ models/face_verifier.py  - ArcFace backend logic  
✅ utils/quality_metrics.py - Quality scoring
✅ utils/visualization.py   - Result charts
✅ requirements.txt         - Dependencies
✅ README.md               - Documentation
✅ config.toml             - Streamlit config
✅ .gitignore              - Git ignore rules
```

---

## 🎯 Setup Steps

### Step 1: Directory Structure

Create this folder structure:

```
AQUAFace_Streamlit_App/
├── app.py
├── models/
│   └── face_verifier.py
├── utils/
│   ├── quality_metrics.py
│   └── visualization.py
├── .streamlit/
│   └── config.toml
├── requirements.txt
├── README.md
└── .gitignore
```

### Step 2: Create __init__.py Files

Create empty `__init__.py` in each directory:

```bash
touch models/__init__.py
touch utils/__init__.py
```

### Step 3: Test Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run app
streamlit run app.py
```

Visit: `http://localhost:8501`

---

## ☁️ Deploy to Streamlit Cloud (Recommended)

### Option A: New Repository

1. **Create GitHub repository**
   - Go to github.com/new
   - Name: `AQUAFace_Streamlit_App`
   - Public repository
   - Initialize with README

2. **Push your code**
```bash
git clone https://github.com/YOUR_USERNAME/AQUAFace_Streamlit_App.git
cd AQUAFace_Streamlit_App

# Copy all files into this directory
cp app.py .
cp requirements.txt .
# ... etc

git add .
git commit -m "Add AQUAFace-Lite Streamlit app"
git push origin main
```

3. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Click "New app"
   - Connect GitHub account
   - Select repository: `AQUAFace_Streamlit_App`
   - Main file path: `app.py`
   - Click "Deploy"

**Your app is now live!** 🎉

URL will be: `https://aquaface-lite.streamlit.app`

---

## 🔧 Configuration

### Streamlit Cloud Secrets (Optional)

Create `.streamlit/secrets.toml` for sensitive settings:

```toml
# Example if you need API keys
api_key = "your_key_here"
```

### Environment Variables

Streamlit Cloud automatically uses `requirements.txt` for dependencies.

---

## 📊 Testing the App

### Test Images

1. **Same Person**: Use two photos of the same person
2. **Different People**: Use photos of different people
3. **Quality Test**: Use blurry vs. clear images

### Expected Behavior

| Scenario | Result |
|----------|--------|
| Same person, high quality | ✅ SAME (high confidence) |
| Same person, low quality | ✅ SAME (medium confidence) |
| Different people, high quality | ❌ DIFFERENT (high confidence) |
| Different people, low quality | ❌ DIFFERENT (low confidence) |
| No face detected | ⚠️ Error message |

---

## 🐛 Troubleshooting

### Issue: "No module named 'insightface'"
**Solution**: Make sure requirements.txt is in root directory
```bash
pip install -r requirements.txt
```

### Issue: "CUDA not available, falling back to CPU"
**Normal behavior** - App will run on CPU, just slower

### Issue: "Module import error" on Streamlit Cloud
**Solution**: Add missing `__init__.py` files:
```bash
touch models/__init__.py
touch utils/__init__.py
git add .
git commit -m "Add __init__.py files"
git push
```

### Issue: App takes long to load first time
**Normal** - First run downloads ~250MB ArcFace model
(Only happens once, then cached)

---

## 📈 Performance Tips

1. **Use GPU**: If available, models will auto-detect
2. **Image Size**: Works best with 112x112 or larger
3. **Lighting**: Good lighting improves quality scores
4. **Face Position**: Frontal faces work best

---

## 🔒 Security Checklist

- ✅ Images NOT stored anywhere
- ✅ No API calls made with images
- ✅ All computation local
- ✅ No login required
- ✅ No data collection

---

## 📝 Customization

### Change App Title
In `app.py`, line 18:
```python
st.set_page_config(
    page_title="Your Custom Title",  # Change this
    ...
)
```

### Change Threshold Default
In `app.py`, sidebar section:
```python
threshold = st.slider(
    "Similarity Threshold",
    value=0.75,  # Change this
    ...
)
```

### Change Colors
In `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#YOUR_COLOR"  # Change hex code
```

---

## 🚀 Advanced: Custom Deployment

### Deploy on Heroku (Free tier ended, use Railway instead)

### Deploy on Railway.app
1. Connect GitHub repo
2. Set environment: `Python`
3. Add `PORT` variable: `8501`
4. Railway auto-deploys on push

### Deploy on Fly.io
1. Install `flyctl`
2. Run: `flyctl launch`
3. Select Python region
4. Run: `flyctl deploy`

---

## 📞 Support

- **Issues**: Open GitHub issue
- **Questions**: Check README.md FAQ
- **Bugs**: Provide test images + error message

---

## ✅ Final Checklist Before Submission

- [ ] All files present (app.py, models/, utils/, requirements.txt)
- [ ] `__init__.py` files in models/ and utils/
- [ ] requirements.txt has all dependencies
- [ ] README.md is complete
- [ ] App runs locally without errors
- [ ] Deployed to Streamlit Cloud successfully
- [ ] Public URL is shareable
- [ ] Tested with sample images
- [ ] Download/export functionality works

---

## 🎓 For Your Project Report

Include these in your submission:

1. **Public URL**: `https://aquaface-lite.streamlit.app`
2. **GitHub Repo**: Link to your code
3. **Screenshot**: App interface screenshot
4. **Test Results**: Results from verification
5. **Deployment Notes**: Any customizations made

---

**You're ready to deploy! 🚀**

Questions? Check the README.md or GitHub discussions.
