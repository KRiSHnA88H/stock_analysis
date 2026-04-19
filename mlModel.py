"""
mlModel.py

Simple linear regression baseline for next-day return prediction.

Usage:
  python mlModel.py train_lr
  python mlModel.py predict_lr

Saves model to `models/stock_lr.pkl` and metadata to `models/stock_lr_meta.json`.
"""

import os
import glob
import json
from typing import List

import pandas as pd
import numpy as np

try:
	from sklearn.linear_model import LinearRegression
	from sklearn.pipeline import Pipeline
	from sklearn.preprocessing import StandardScaler
	from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
except Exception:
	raise ImportError("scikit-learn is required. Install with: pip install scikit-learn")

import joblib


DEFAULT_FEATURES = [
	"Close",
	"Volume",
	"SMA20",
	"SMA50",
	"EMA12",
	"EMA26",
	"RSI",
	"Volatility",
	"Returns",
]


def gather_paths(indicator_root: str = "indicator_output", fallback: str = "data") -> List[str]:
	paths = glob.glob(os.path.join(indicator_root, "**", "*.csv"), recursive=True)
	if paths:
		return paths
	return glob.glob(os.path.join(fallback, "*.csv"))


def _load_csv(path: str) -> pd.DataFrame:
	try:
		df = pd.read_csv(path, parse_dates=["Date"])  # expecting a Date column
	except Exception:
		df = pd.read_csv(path, parse_dates=[0])
		df.rename(columns={df.columns[0]: "Date"}, inplace=True)

	df.sort_values("Date", inplace=True)
	if "Close" not in df.columns and "Adj Close" in df.columns:
		df["Close"] = df["Adj Close"]

	for col in ["Close", "Volume"]:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors="coerce")

	return df


def build_regression_dataset(paths: List[str], feature_cols: List[str] = None) -> pd.DataFrame:
	if feature_cols is None:
		feature_cols = DEFAULT_FEATURES

	rows = []
	for p in paths:
		try:
			df = _load_csv(p)
		except Exception:
			continue

		if "Close" not in df.columns:
			continue

		# basic features
		if "Returns" not in df.columns:
			df["Returns"] = df["Close"].pct_change()

		# target: next-day return
		df["NextReturn"] = df["Close"].shift(-1) / df["Close"] - 1

		available = [c for c in feature_cols if c in df.columns]
		if len(available) < 2:
			continue

		sub = df[available + ["NextReturn", "Date"]].dropna()
		if sub.empty:
			continue

		sub = sub.copy()
		sub["Ticker"] = os.path.splitext(os.path.basename(p))[0]
		rows.append(sub)

	if not rows:
		raise ValueError("No usable data found for regression.")

	data = pd.concat(rows, ignore_index=True)
	return data


def split_train_test_by_date(data: pd.DataFrame, test_size: float = 0.2):
	dates = np.sort(data["Date"].unique())
	cutoff_idx = int(len(dates) * (1 - test_size))
	cutoff_idx = max(1, min(cutoff_idx, len(dates) - 1))
	cutoff_date = dates[cutoff_idx]

	train = data[data["Date"] <= cutoff_date].copy()
	test = data[data["Date"] > cutoff_date].copy()
	return train, test


def train_linear_model(indicator_root: str = "indicator_output", model_out: str = "models/stock_lr.pkl", metrics_out: str = "models/metrics_lr.json") -> dict:
	paths = gather_paths(indicator_root=indicator_root)
	if not paths:
		raise FileNotFoundError("No CSV files found for training.")

	print(f"Building regression dataset from {len(paths)} files...")
	data = build_regression_dataset(paths)

	feature_cols = [c for c in DEFAULT_FEATURES if c in data.columns]
	X = data[feature_cols]
	y = data["NextReturn"]

	train, test = split_train_test_by_date(data)
	X_train = train[feature_cols]
	y_train = train["NextReturn"]
	X_test = test[feature_cols]
	y_test = test["NextReturn"]

	pipe = Pipeline([
		("scaler", StandardScaler()),
		("lr", LinearRegression()),
	])

	print("Training LinearRegression model...")
	pipe.fit(X_train, y_train)

	y_pred = pipe.predict(X_test)
	mse = mean_squared_error(y_test, y_pred)
	mae = mean_absolute_error(y_test, y_pred)
	r2 = r2_score(y_test, y_pred)

	metrics = {"mse": float(mse), "rmse": float(np.sqrt(mse)), "mae": float(mae), "r2": float(r2)}

	os.makedirs(os.path.dirname(model_out) or ".", exist_ok=True)
	joblib.dump(pipe, model_out)

	# save metadata (feature names)
	meta = {"features": feature_cols}
	meta_path = os.path.splitext(model_out)[0] + "_meta.json"
	with open(meta_path, "w") as f:
		json.dump(meta, f, indent=2)

	with open(metrics_out, "w") as f:
		json.dump(metrics, f, indent=2)

	print(f"Linear model saved to {model_out}")
	print(f"Metadata saved to {meta_path}")
	print(f"Metrics saved to {metrics_out}")
	return metrics


def predict_latest_lr(indicator_root: str = "indicator_output", model_path: str = "models/stock_lr.pkl") -> pd.DataFrame:
	if not os.path.exists(model_path):
		raise FileNotFoundError(f"Model file not found: {model_path}")

	pipe = joblib.load(model_path)
	meta_path = os.path.splitext(model_path)[0] + "_meta.json"
	if not os.path.exists(meta_path):
		raise FileNotFoundError(f"Model metadata not found: {meta_path}")

	with open(meta_path, "r") as f:
		meta = json.load(f)
	feature_cols = meta.get("features", [])

	paths = gather_paths(indicator_root=indicator_root)
	results = []
	for p in paths:
		try:
			df = _load_csv(p)
		except Exception:
			continue

		if "Close" not in df.columns:
			continue

		if "Returns" not in df.columns:
			df["Returns"] = df["Close"].pct_change()

		# pick last row that has all required features
		last = df.dropna(subset=feature_cols).iloc[-1:] if not df.dropna(subset=feature_cols).empty else None
		if last is None or last.empty:
			continue

		X = last[feature_cols]
		pred = float(pipe.predict(X)[0])
		ticker = os.path.splitext(os.path.basename(p))[0]
		results.append({"Ticker": ticker, "PredNextReturn": pred})

	return pd.DataFrame(results)


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Train or run simple linear regression model for next-day returns")
	parser.add_argument("action", choices=["train_lr", "predict_lr"], help="Action to run")
	parser.add_argument("--model-out", default="models/stock_lr.pkl")
	parser.add_argument("--metrics-out", default="models/metrics_lr.json")
	parser.add_argument("--indicator-root", default="indicator_output")
	args = parser.parse_args()

	if args.action == "train_lr":
		metrics = train_linear_model(indicator_root=args.indicator_root, model_out=args.model_out, metrics_out=args.metrics_out)
		print(json.dumps(metrics, indent=2))
	else:
		df_preds = predict_latest_lr(indicator_root=args.indicator_root, model_path=args.model_out)
		if df_preds.empty:
			print("No predictions available (missing features or data).")
		else:
			print(df_preds.sort_values("PredNextReturn", ascending=False).to_string(index=False))


