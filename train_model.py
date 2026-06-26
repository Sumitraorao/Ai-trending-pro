"""Model training script"""
import os
import sys
import argparse
import pickle
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from sklearn.model_selection import cross_val_score
import numpy as np

from ml_training.dataset import TradingDataset
from config import settings

def train_model(symbol: str, model_type: str = "random_forest", save: bool = True):
    """Train a trading model for a specific symbol"""
    print(f"🚀 Training {model_type} model for {symbol}...")

    # Prepare dataset
    dataset = TradingDataset(symbol, period="3y", interval="1d")
    X_train, X_test, y_train, y_test = dataset.prepare_dataset(test_size=0.2)

    print(f"📊 Dataset prepared: {len(X_train)} training samples, {len(X_test)} test samples")
    print(f"📈 Features: {len(dataset.feature_columns)}")

    # Select model
    if model_type == "random_forest":
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
            class_weight='balanced'
        )
    elif model_type == "gradient_boosting":
        model = GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}")

    # Train model
    print("🏋️  Training model...")
    model.fit(X_train, y_train)

    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_accuracy = accuracy_score(y_train, train_pred)
    test_accuracy = accuracy_score(y_test, test_pred)

    # Cross-validation
    cv_scores = cross_val_score(model, X_train, y_train, cv=5)

    # Feature importance
    feature_importance = dataset.get_feature_importance(model)

    # Classification report
    y_test_labels = dataset.inverse_transform_labels(y_test)
    test_pred_labels = dataset.inverse_transform_labels(test_pred)
    report = classification_report(y_test_labels, test_pred_labels, output_dict=True)

    # Confusion matrix
    cm = confusion_matrix(y_test, test_pred)

    results = {
        "symbol": symbol,
        "model_type": model_type,
        "train_accuracy": round(train_accuracy * 100, 2),
        "test_accuracy": round(test_accuracy * 100, 2),
        "cv_mean": round(cv_scores.mean() * 100, 2),
        "cv_std": round(cv_scores.std() * 100, 2),
        "feature_importance": {k: round(v, 4) for k, v in list(feature_importance.items())[:10]},
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
        "training_date": datetime.now().isoformat(),
        "samples": {
            "train": len(X_train),
            "test": len(X_test)
        }
    }

    print(f"✅ Training complete!")
    print(f"   Train Accuracy: {results['train_accuracy']}%")
    print(f"   Test Accuracy: {results['test_accuracy']}%")
    print(f"   CV Score: {results['cv_mean']}% (+/- {results['cv_std']}%)")

    # Save model
    if save:
        model_dir = settings.MODEL_PATH
        os.makedirs(model_dir, exist_ok=True)

        model_filename = f"{model_dir}/{symbol.replace('.', '_')}_{model_type}.pkl"
        scaler_filename = f"{model_dir}/{symbol.replace('.', '_')}_scaler.pkl"
        encoder_filename = f"{model_dir}/{symbol.replace('.', '_')}_encoder.pkl"

        with open(model_filename, 'wb') as f:
            pickle.dump(model, f)
        with open(scaler_filename, 'wb') as f:
            pickle.dump(dataset.scaler, f)
        with open(encoder_filename, 'wb') as f:
            pickle.dump(dataset.label_encoder, f)

        # Save results
        results_filename = f"{model_dir}/{symbol.replace('.', '_')}_results.json"
        with open(results_filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"💾 Model saved to: {model_filename}")
        print(f"💾 Results saved to: {results_filename}")

    return results

def main():
    parser = argparse.ArgumentParser(description='Train AI Trading Model')
    parser.add_argument('--symbol', type=str, default='RELIANCE.NS', help='Stock symbol')
    parser.add_argument('--model', type=str, default='random_forest', choices=['random_forest', 'gradient_boosting'])
    parser.add_argument('--no-save', action='store_true', help='Do not save the model')

    args = parser.parse_args()

    results = train_model(args.symbol, args.model, save=not args.no_save)

    print("\n📊 Final Results:")
    print(json.dumps(results, indent=2, default=str))

if __name__ == "__main__":
    main()
