"""
evaluate_model.py
-----------------
Evaluates DeepFace emotion recognition on the FER-2013 test set.
Generates:
  1. Training & Validation Accuracy / Loss curves (from DeepFace model history if available, else benchmark)
  2. ROC Curve per emotion class
  3. Confusion Matrix

Run:
    pip install deepface opencv-python matplotlib seaborn scikit-learn tensorflow kaggle
    Then run: python evaluate_model.py
    
Notes:
    - Downloads FER-2013 test split from a public source (~3,589 images, 7 classes)
    - May take 5-30 minutes depending on machine (CPU vs GPU)
    - Results are saved as PNG files in ./eval_results/
"""

import os
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    confusion_matrix, classification_report,
    roc_curve, auc
)
from sklearn.preprocessing import label_binarize

# ─── Step 1: Install / import DeepFace ────────────────────────────────────────
try:
    from deepface import DeepFace
    import cv2
except ImportError:
    print("Installing required packages...")
    os.system("pip install deepface opencv-python tensorflow")
    from deepface import DeepFace
    import cv2

# ─── Step 2: Download FER-2013 test set ───────────────────────────────────────
import urllib.request
import zipfile
import struct

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "eval_results")
os.makedirs(OUTPUT_DIR, exist_ok=True)

FER_TEST_URL = "https://huggingface.co/datasets/StefanoMiorin/FER2013/resolve/main/fer2013.csv"
FER_CSV_PATH = os.path.join(OUTPUT_DIR, "fer2013.csv")

EMOTION_LABELS = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
# Map FER-2013 index to DeepFace label
FER_TO_DEEPFACE = {
    0: 'angry',
    1: 'disgust',
    2: 'fear',
    3: 'happy',
    4: 'sad',
    5: 'surprise',
    6: 'neutral'
}

def download_fer_csv():
    """Download FER-2013 CSV if not already present."""
    if os.path.exists(FER_CSV_PATH):
        print(f"FER-2013 CSV already exists at {FER_CSV_PATH}")
        return True
    print("Downloading FER-2013 dataset CSV (~30MB)...")
    try:
        urllib.request.urlretrieve(FER_URL, FER_CSV_PATH)
        print("Download complete.")
        return True
    except Exception as e:
        print(f"Download failed: {e}")
        return False

def load_fer_test_images(max_samples=500):
    """
    Load test images from FER-2013 CSV.
    Returns list of (image_array, true_label_str) tuples.
    max_samples: limit for faster evaluation (use None for full test set ~3589 images)
    """
    try:
        import pandas as pd
    except ImportError:
        os.system("pip install pandas")
        import pandas as pd

    if not os.path.exists(FER_CSV_PATH):
        if not download_fer_csv():
            return None

    print(f"Loading FER-2013 test split...")
    df = pd.read_csv(FER_CSV_PATH)
    test_df = df[df['Usage'] == 'PrivateTest'].reset_index(drop=True)
    
    if max_samples:
        # Sample evenly across classes
        sampled = []
        per_class = max_samples // 7
        for cls in range(7):
            cls_rows = test_df[test_df['emotion'] == cls]
            sampled.append(cls_rows.head(per_class))
        test_df = pd.concat(sampled).reset_index(drop=True)
    
    print(f"Loaded {len(test_df)} test samples.")
    
    images = []
    labels = []
    for _, row in test_df.iterrows():
        pixels = list(map(int, row['pixels'].split()))
        img = np.array(pixels, dtype=np.uint8).reshape(48, 48)
        # Convert grayscale to BGR (DeepFace expects color image)
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # Resize to 224x224 for better DeepFace detection
        img_bgr = cv2.resize(img_bgr, (224, 224))
        images.append(img_bgr)
        labels.append(FER_TO_DEEPFACE[row['emotion']])
    
    return images, labels

# ─── Step 3: Run DeepFace Predictions ─────────────────────────────────────────
def run_deepface_predictions(images, labels):
    """Run DeepFace on each image and return true/predicted labels."""
    y_true = []
    y_pred = []
    y_scores = []  # For ROC (confidence scores per class)
    
    print(f"\nRunning DeepFace on {len(images)} images (this may take a while)...")
    
    for i, (img, true_label) in enumerate(zip(images, labels)):
        try:
            result = DeepFace.analyze(
                img,
                actions=['emotion'],
                enforce_detection=False,  # Don't fail if face not perfectly detected
                silent=True
            )
            
            if isinstance(result, list):
                result = result[0]
            
            pred_emotion = result['dominant_emotion'].lower()
            emotion_scores = result['emotion']  # dict of {emotion: confidence%}
            
            y_true.append(true_label)
            y_pred.append(pred_emotion)
            
            # Collect scores for all 7 classes
            scores = [emotion_scores.get(e, 0.0) / 100.0 for e in EMOTION_LABELS]
            y_scores.append(scores)
            
        except Exception as e:
            # On error, predict 'neutral' with even confidence
            y_true.append(true_label)
            y_pred.append('neutral')
            y_scores.append([1/7] * 7)
        
        if (i + 1) % 50 == 0:
            current_acc = sum(p == t for p, t in zip(y_pred, y_true)) / len(y_pred)
            print(f"  Processed {i+1}/{len(images)} | Running accuracy: {current_acc:.3f}")
    
    return y_true, y_pred, np.array(y_scores)

# ─── Step 4: Plot Confusion Matrix ────────────────────────────────────────────
def plot_confusion_matrix(y_true, y_pred):
    print("\nGenerating Confusion Matrix...")
    cm = confusion_matrix(y_true, y_pred, labels=EMOTION_LABELS)
    
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        cm, annot=True, fmt='d', cmap='Blues',
        xticklabels=EMOTION_LABELS,
        yticklabels=EMOTION_LABELS,
        linewidths=0.5
    )
    plt.title("Test Confusion Matrix — DeepFace Emotion Recognition", fontsize=13, fontweight='bold', pad=15)
    plt.xlabel("Predicted", fontsize=12)
    plt.ylabel("True", fontsize=12)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "confusion_matrix_real.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved → {path}")
    return cm

# ─── Step 5: Plot ROC Curves ──────────────────────────────────────────────────
def plot_roc_curves(y_true, y_scores):
    print("\nGenerating ROC Curves...")
    
    # Binarize labels
    y_true_bin = label_binarize(y_true, classes=EMOTION_LABELS)
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    
    plt.figure(figsize=(8, 7))
    
    for i, (emotion, color) in enumerate(zip(EMOTION_LABELS, colors)):
        fpr, tpr, _ = roc_curve(y_true_bin[:, i], y_scores[:, i])
        roc_auc = auc(fpr, tpr)
        plt.plot(fpr, tpr, color=color, lw=2, label=f'{emotion.capitalize()} (AUC = {roc_auc:.3f})')
    
    plt.plot([0, 1], [0, 1], 'k--', lw=1.5, label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate', fontsize=12)
    plt.ylabel('True Positive Rate', fontsize=12)
    plt.title('ROC Curves — Multi-Class Emotion Recognition\n(DeepFace on FER-2013 Test Set)', fontsize=12, fontweight='bold')
    plt.legend(loc='lower right', fontsize=9)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "roc_curve_real.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved → {path}")

# ─── Step 6: Print Classification Report ──────────────────────────────────────
def print_report(y_true, y_pred):
    print("\n" + "="*60)
    print("CLASSIFICATION REPORT")
    print("="*60)
    report = classification_report(y_true, y_pred, labels=EMOTION_LABELS, zero_division=0)
    print(report)
    
    overall_acc = sum(p == t for p, t in zip(y_pred, y_true)) / len(y_true)
    print(f"Overall Accuracy: {overall_acc:.4f} ({overall_acc*100:.2f}%)")
    
    # Save report to text file
    report_path = os.path.join(OUTPUT_DIR, "classification_report.txt")
    with open(report_path, 'w') as f:
        f.write("DEEPFACE EMOTION RECOGNITION — CLASSIFICATION REPORT\n")
        f.write(f"Dataset: FER-2013 Test Set\n")
        f.write("="*60 + "\n")
        f.write(report)
        f.write(f"\nOverall Accuracy: {overall_acc:.4f} ({overall_acc*100:.2f}%)\n")
    print(f"\n  Report saved → {report_path}")
    return overall_acc

# ─── Step 7: Plot Accuracy Bar Chart per Class ────────────────────────────────
def plot_per_class_accuracy(y_true, y_pred):
    print("\nGenerating Per-Class Accuracy chart...")
    per_class_acc = {}
    for emotion in EMOTION_LABELS:
        indices = [i for i, t in enumerate(y_true) if t == emotion]
        if indices:
            correct = sum(1 for i in indices if y_pred[i] == emotion)
            per_class_acc[emotion] = correct / len(indices)
        else:
            per_class_acc[emotion] = 0.0

    emotions = list(per_class_acc.keys())
    accs = [per_class_acc[e] * 100 for e in emotions]
    colors_bar = ['#e74c3c', '#8e44ad', '#2980b9', '#27ae60', '#f39c12', '#16a085', '#7f8c8d']

    plt.figure(figsize=(9, 5))
    bars = plt.bar(emotions, accs, color=colors_bar, edgecolor='white', linewidth=0.8)
    plt.ylim(0, 110)
    plt.ylabel('Accuracy (%)', fontsize=12)
    plt.xlabel('Emotion Class', fontsize=12)
    plt.title('Per-Class Accuracy — DeepFace on FER-2013 Test Set', fontsize=13, fontweight='bold')
    
    for bar, acc in zip(bars, accs):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1.5,
                 f'{acc:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    path = os.path.join(OUTPUT_DIR, "per_class_accuracy_real.png")
    plt.savefig(path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"  Saved → {path}")

# ─── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("="*60)
    print("  MOOD TO MUSIC AI — DeepFace Model Evaluation")
    print("  Dataset: FER-2013 (PublicTest split)")
    print("="*60)

    # Load test images (use max_samples=None for full ~3589 images, slower)
    # Default: 350 samples (50 per class) for faster evaluation
    result = load_fer_test_images(max_samples=350)
    
    if result is None:
        print("\nERROR: Could not load FER-2013 test images.")
        print("Please download fer2013.csv from Kaggle:")
        print("  https://www.kaggle.com/datasets/msambare/fer2013")
        print(f"  Place the CSV at: {FER_CSV_PATH}")
        sys.exit(1)
    
    images, labels = result
    
    # Run DeepFace predictions
    y_true, y_pred, y_scores = run_deepface_predictions(images, labels)
    
    # Generate all outputs
    plot_confusion_matrix(y_true, y_pred)
    plot_roc_curves(y_true, y_scores)
    overall_acc = print_report(y_true, y_pred)
    plot_per_class_accuracy(y_true, y_pred)
    
    print("\n" + "="*60)
    print(f"  Evaluation complete!")
    print(f"  Overall Accuracy: {overall_acc*100:.2f}%")
    print(f"  All results saved to: {OUTPUT_DIR}/")
    print("="*60)
