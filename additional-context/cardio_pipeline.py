# CELL 1 - imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

try:
    from IPython.display import display  # works in notebooks
except ImportError:
    def display(obj):
        """Fallback display for non-notebook environments."""
        print(obj)

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score, roc_curve
)
import joblib
import json
import subprocess
import sys

print('imports ready')

# CELL 2 - load (sesuaikan path jika perlu)
import os
print('Current working dir:', os.getcwd())
csv_path = 'cardio_train.csv'  # ganti jika file ada di tempat lain
if os.path.exists(csv_path):
    df_preview = pd.read_csv(csv_path, sep=';')
    print('Loaded preview shape:', df_preview.shape)
    display(df_preview.head())
else:
    print(f"File '{csv_path}' tidak ditemukan di working directory. Upload file ke folder kerja atau ganti path pada variabel `csv_path`.")

# CELL 3 - quick inspection
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path, sep=';')
    display(df.info())
    display(df.describe(include='all').T)
    print('\nMissing values per column:')
    print(df.isnull().sum())
else:
    print('Skip inspection: file not found')

"""## 3) Data cleaning: convert age to years & filter outliers
Atur batas outlier sesuai kebutuhan domain. Contoh batas yang digunakan di notebook ini:
"""

# CELL 4 - age to years & filter outliers
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path, sep=';')
    df['age_years'] = (df['age'] / 365).astype(int)
    cond = (
        (df['ap_hi'] >= 60) & (df['ap_hi'] <= 250) &
        (df['ap_lo'] >= 40) & (df['ap_lo'] <= 180) &
        (df['height'] >= 130) & (df['height'] <= 220) &
        (df['weight'] >= 30) & (df['weight'] <= 250)
    )
    df = df[cond].copy()
    print('After filtering, shape =', df.shape)
    display(df.head())
else:
    print('Skip cleaning: file not found')

"""## 4) Feature engineering
Tambahkan BMI, selisih tekanan darah, dan kategori umur contoh.
"""

# CELL 6 - feature engineering
if 'df' in globals():
    df['bmi'] = df['weight'] / ((df['height'] / 100) ** 2)
    df['bp_diff'] = df['ap_hi'] - df['ap_lo']
    df['age_cat'] = pd.cut(df['age_years'], bins=[0,30,45,60,200], labels=['<30','30-45','45-60','60+'])
    display(df[['age_years','age_cat','height','weight','bmi','ap_hi','ap_lo']].head())
else:
    print('Skip feature engineering: df not available')

"""## 5) Encoding & dummies
Handle `gender`, `cholesterol`, `gluc`, dan `age_cat`.
"""

# CELL 7 - encoding
if 'df' in globals():
    df['gender'] = df['gender'].astype(int)
    # create gender_male (dataset Kaggle: 1 = female, 2 = male)
    df['gender_male'] = (df['gender'] == 2).astype(int)
    df = pd.get_dummies(df, columns=['cholesterol','gluc','age_cat'], drop_first=True)
    # drop original 'gender' if not needed
    df.drop(columns=['gender'], inplace=True)
    print('Columns after encoding/sample:')
    print(df.columns.tolist()[:40])
else:
    print('Skip encoding: df not available')

"""## 6) Quick EDA: target distribution & correlation heatmap"""

# CELL 8 - EDA plots
if 'df' in globals():
    plt.figure()
    sns.countplot(x='cardio', data=df)
    plt.title('Distribusi cardio')
    plt.show()

    plt.figure(figsize=(12,8))
    sns.heatmap(df.corr(), cmap='vlag', center=0, linewidths=.5)
    plt.title('Correlation matrix')
    plt.show()
else:
    print('Skip EDA plots: df not available')

"""## 7) Feature selection: prepare X, y
Drop kolom yang tidak perlu (`id`, `age` hari) dan siapkan X, y.
"""

# CELL 10 - prepare X, y
if 'df' in globals():
    drop_cols = []
    if 'id' in df.columns:
        drop_cols.append('id')
    if 'age' in df.columns:
        drop_cols.append('age')
    X = df.drop(columns=drop_cols + ['cardio'])
    y = df['cardio']
    print('X shape, y shape =', X.shape, y.shape)
    display(X.head())
    # save feature order for deployment/serving
    try:
        features_path = 'features.json'
        with open(features_path, 'w', encoding='utf-8') as fh:
            json.dump(X.columns.tolist(), fh, ensure_ascii=False, indent=2)
        print(f'Feature order saved to {features_path}')
    except Exception as e:
        print('Failed to save features.json:', e)
else:
    print('Skip prepare X,y: df not available')

"""## 8) Split data
Stratified split recommended untuk menjaga distribusi target.
"""

# CELL 11 - split
if 'X' in globals():
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    print('Train/Test sizes:', X_train.shape, X_test.shape)
else:
    print('Skip split: X not available')

"""## 9) Scaling numeric features
Scale numerics menggunakan `StandardScaler`. Simpan scaler untuk deployment.
"""

# CELL 12 - scaling
if 'X_train' in globals():
    num_cols = X.select_dtypes(include=['float64','int64']).columns.tolist()
    scaler = StandardScaler()
    # fit on train only
    X_train_scaled = X_train.copy()
    X_test_scaled = X_test.copy()
    X_train_scaled[num_cols] = scaler.fit_transform(X_train[num_cols])
    X_test_scaled[num_cols] = scaler.transform(X_test[num_cols])
    joblib.dump(scaler, 'scaler_cardio.joblib')
    print('Scaling done. Scaler saved to scaler_cardio.joblib')
else:
    print('Skip scaling: X_train not available')

"""## 10) Modeling - Logistic Regression baseline"""

# CELL 13 - Logistic Regression baseline
if 'X_train_scaled' in globals():
    lr = LogisticRegression(max_iter=1000)
    lr.fit(X_train_scaled, y_train)
    y_pred = lr.predict(X_test_scaled)
    print('LR Accuracy:', accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))
else:
    print('Skip LR: scaled data not available')

"""## 11) Modeling - Random Forest baseline"""

# CELL 14 - Random Forest
if 'X_train_scaled' in globals():
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    rf.fit(X_train_scaled, y_train)
    y_pred_rf = rf.predict(X_test_scaled)
    print('RF Accuracy:', accuracy_score(y_test, y_pred_rf))
    print(classification_report(y_test, y_pred_rf))
    y_proba_rf = rf.predict_proba(X_test_scaled)[:,1]
    print('RF ROC-AUC:', roc_auc_score(y_test, y_proba_rf))
    fpr, tpr, _ = roc_curve(y_test, y_proba_rf)
    plt.figure()
    plt.plot(fpr, tpr)
    plt.plot([0,1],[0,1], '--')
    plt.title('ROC')
    plt.show()
else:
    print('Skip RF: scaled data not available')

"""## 12) (Optional) Hyperparameter tuning contoh GridSearch untuk RandomForest
GridSearch bisa memakan waktu; ubah parameter jika perlu.
Set SKIP_GRIDSEARCH=1 environment variable to skip this step.
"""

# CELL 15 - GridSearch example (optional)
skip_grid = os.environ.get('SKIP_GRIDSEARCH', '0') == '1'
if skip_grid:
    print('SKIP_GRIDSEARCH=1, skipping GridSearch (saves time).')
elif 'X_train_scaled' in globals():
    print('Starting GridSearchCV... This may take 10-30 minutes.')
    print('Set environment variable SKIP_GRIDSEARCH=1 to skip this step in future runs.')
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5]
    }
    # verbose=2 shows progress for each fit
    gs = GridSearchCV(RandomForestClassifier(random_state=42, n_jobs=-1), param_grid, cv=3, scoring='f1', n_jobs=-1, verbose=2)
    gs.fit(X_train_scaled, y_train)
    print('Best params:', gs.best_params_)
    best_rf = gs.best_estimator_
    y_pred_best = best_rf.predict(X_test_scaled)
    print(classification_report(y_test, y_pred_best))
else:
    print('Skip GridSearch: scaled data not available')

"""## 13) Feature importance
Print & plot feature importance dari Random Forest.
"""

# CELL 16 - feature importance
if 'rf' in globals():
    importances = rf.feature_importances_
    feat_imp = pd.Series(importances, index=X.columns).sort_values(ascending=False)
    display(feat_imp.head(20))
    plt.figure()
    sns.barplot(x=feat_imp.values[:15], y=feat_imp.index[:15])
    plt.title('Feature importance (RandomForest)')
    plt.show()
else:
    print('Skip feature importance: rf not available')

"""## 14) SHAP (opsional)
Gunakan SHAP untuk explainability per-sample jika ingin.
Pastikan paket `shap` sudah terinstall.
Set SKIP_SHAP=1 environment variable to skip this step.
"""

# CELL 17 - SHAP (optional)
skip_shap = os.environ.get('SKIP_SHAP', '0') == '1'
if skip_shap:
    print('SKIP_SHAP=1, skipping SHAP analysis (saves time).')
else:
    try:
        if 'rf' in globals() and 'X_test_scaled' in globals():
            import shap
            print('Starting SHAP analysis... This may take 5-15 minutes.')
            print('Set environment variable SKIP_SHAP=1 to skip this step in future runs.')
            
            # Sample subset for faster SHAP calculation (1000 samples instead of all 13k+)
            max_samples = min(1000, len(X_test_scaled))
            print(f'Using {max_samples} samples for SHAP (out of {len(X_test_scaled)} test samples).')
            sample_indices = np.random.choice(len(X_test_scaled), max_samples, replace=False)
            X_shap = X_test_scaled.iloc[sample_indices] if hasattr(X_test_scaled, 'iloc') else X_test_scaled[sample_indices]
            
            print('Creating SHAP explainer...')
            explainer = shap.TreeExplainer(rf)
            print('Computing SHAP values...')
            shap_values = explainer.shap_values(X_shap)
            print('Generating SHAP summary plot...')
            # Summary plot
            shap.summary_plot(shap_values[1], X_shap)
            print('SHAP analysis complete.')
        else:
            print('Skip SHAP: rf or X_test_scaled not available')
    except Exception as e:
        print('SHAP error or not installed:', e)

"""## 15) Final evaluation & save model
Simpan model RandomForest yang sudah dilatih.
"""

# CELL 18 - final save
if 'rf' in globals():
    joblib.dump(rf, 'rf_cardio_model.joblib')
    print('Model saved to rf_cardio_model.joblib')
    # basic final metrics
    if 'y_pred_rf' in globals():
        print('Final RF Accuracy:', accuracy_score(y_test, y_pred_rf))
    # Optional: auto-register the model when environment indicates so.
    try:
        should_auto = os.environ.get('AUTO_REGISTER', '0') == '1' or bool(os.environ.get('MLFLOW_TRACKING_URI'))
        if should_auto:
            print('Auto-register condition met. Calling registration script...')
            python_exe = sys.executable or 'python'
            cmd = [python_exe, 'register_model_mlflow.py', '--model', 'rf_cardio_model.joblib', '--scaler', 'scaler_cardio.joblib', '--experiment', os.environ.get('MLFLOW_EXPERIMENT','cardio_experiment'), '--register-name', os.environ.get('REGISTER_MODEL_NAME','rf_cardio')]
            print('Running:', ' '.join(cmd))
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                print('Registration stdout:\n', res.stdout)
                print('Registration stderr:\n', res.stderr)
                print('Registration exit code:', res.returncode)
            except Exception as e:
                print('Failed to run registration subprocess:', e)
        else:
            print('Auto-register not enabled (set AUTO_REGISTER=1 or MLFLOW_TRACKING_URI).')
    except Exception as e:
        print('Error during auto-register attempt:', e)
else:
    print('Skip save: rf not available')

