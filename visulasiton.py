import os
import glob
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


warnings.filterwarnings("ignore")


def sma(series, n):
	return series.rolling(n).mean()


def ema(series, n):
	return series.ewm(span=n, adjust=False).mean()


def rsi(series, days=14):
	change = series.diff()
	gain = change.where(change > 0, 0)
	loss = -change.where(change < 0, 0)
	avg_gain = gain.rolling(days).mean()
	avg_loss = loss.rolling(days).mean()
	rs = avg_gain / avg_loss
	return 100 - (100 / (1 + rs))


def volatility(series, days=20):
	returns = series.pct_change()
	return returns.rolling(days).std()


def compute_avg_volume(path, lookback=252):
	try:
		df = pd.read_csv(path, usecols=["Date", "Volume"], parse_dates=["Date"]) 
		df = df.sort_values("Date").tail(lookback)
		return pd.to_numeric(df["Volume"], errors="coerce").dropna().mean()
	except Exception:
		try:
			df = pd.read_csv(path, usecols=["Volume"]) 
			return pd.to_numeric(df["Volume"], errors="coerce").dropna().tail(lookback).mean()
		except Exception:
			return 0


def load_price_frame(path):
	try:
		df = pd.read_csv(path, parse_dates=["Date"]) 
	except Exception:
		df = pd.read_csv(path, parse_dates=[0])
		df.rename(columns={df.columns[0]: "Date"}, inplace=True)

	df.sort_values("Date", inplace=True)
	df.set_index("Date", inplace=True)

	if "Close" not in df.columns and "Adj Close" in df.columns:
		df["Close"] = df["Adj Close"]

	for col in ["Close", "Volume"]:
		if col in df.columns:
			df[col] = pd.to_numeric(df[col], errors="coerce")

	return df


def plot_for_ticker(df, ticker, out_folder):
	close = df.get("Close")
	if close is None or close.dropna().empty:
		print(f"Skipping {ticker}: no close price")
		return

	# compute indicators only if missing (won't overwrite CSVs)
	if "SMA20" not in df.columns:
		df["SMA20"] = sma(close, 20)
	if "SMA50" not in df.columns:
		df["SMA50"] = sma(close, 50)
	if "EMA12" not in df.columns:
		df["EMA12"] = ema(close, 12)
	if "EMA26" not in df.columns:
		df["EMA26"] = ema(close, 26)
	if "RSI" not in df.columns:
		df["RSI"] = rsi(close)
	if "Volatility" not in df.columns:
		df["Volatility"] = volatility(close)

	df["Returns"] = close.pct_change()

	sns.set_style("darkgrid")

	fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 10), gridspec_kw={"height_ratios": [3, 1, 1]}, sharex=True)

	ax1.plot(df.index, close, label="Close", color="black")
	ax1.plot(df.index, df.get("SMA20"), label="SMA20", color="blue", linewidth=0.8)
	ax1.plot(df.index, df.get("SMA50"), label="SMA50", color="red", linewidth=0.8)
	ax1.plot(df.index, df.get("EMA12"), label="EMA12", color="green", linewidth=0.7)
	ax1.plot(df.index, df.get("EMA26"), label="EMA26", color="orange", linewidth=0.7)

	ax1.set_title(f"{ticker} — Price and Moving Averages")
	ax1.legend(loc="upper left")

	if "Volume" in df.columns:
		ax1b = ax1.twinx()
		ax1b.bar(df.index, df["Volume"], color="grey", alpha=0.25, width=1)
		ax1b.set_ylabel("Volume")

	if "RSI" in df.columns:
		ax2.plot(df.index, df["RSI"], color="purple")
		ax2.axhline(70, color="red", linestyle="--", linewidth=0.7)
		ax2.axhline(30, color="green", linestyle="--", linewidth=0.7)
		ax2.set_ylabel("RSI")

	if "Volatility" in df.columns:
		ax3.plot(df.index, df["Volatility"], color="brown")
		ax3.set_ylabel("Volatility")

	ax3.set_xlabel("Date")
	fig.tight_layout()

	os.makedirs(out_folder, exist_ok=True)
	out_path = os.path.join(out_folder, f"{ticker}.png")
	fig.savefig(out_path, dpi=150)
	plt.close(fig)

	try:
		fig2 = plt.figure(figsize=(6, 4))
		sns.histplot(df["Returns"].dropna(), bins=50, kde=True, color="steelblue")
		plt.title(f"{ticker} — Daily Returns Histogram")
		plt.xlabel("Daily Return")
		plt.tight_layout()
		fig2_path = os.path.join(out_folder, f"{ticker}_returns.png")
		fig2.savefig(fig2_path, dpi=150)
		plt.close(fig2)

		# Per-ticker boxplot for returns (horizontal)
		try:
			returns_clean = df["Returns"].dropna()
			if not returns_clean.empty:
				fig3 = plt.figure(figsize=(6, 3))
				sns.boxplot(x=returns_clean, color="lightseagreen", orient="h")
				plt.title(f"{ticker} — Daily Returns Boxplot")
				plt.xlabel("Daily Return")
				plt.tight_layout()
				fig3_path = os.path.join(out_folder, f"{ticker}_boxplot.png")
				fig3.savefig(fig3_path, dpi=150)
				plt.close(fig3)
		except Exception:
			pass
	except Exception:
		pass


def main(indicator_root="indicator_output", fallback_data="data", out_folder="visualizations/top20", top_n=20):
	# Prefer indicator_output files (already contain indicators). Fallback to raw data.
	indicator_paths = glob.glob(os.path.join(indicator_root, "**", "*.csv"), recursive=True)
	if indicator_paths:
		paths = indicator_paths
		print(f"Using indicator CSVs from '{indicator_root}' ({len(paths)} files)")
	else:
		print(f"No indicator CSVs found in '{indicator_root}', falling back to '{fallback_data}'")
		paths = glob.glob(os.path.join(fallback_data, "*.csv"))

	if not paths:
		print("No CSV files found to process.")
		return

	vols = []
	for p in paths:
		avgv = compute_avg_volume(p, lookback=252)
		ticker = os.path.splitext(os.path.basename(p))[0]
		vols.append((ticker, p, avgv))

	vols = sorted(vols, key=lambda x: x[2], reverse=True)
	top_list = vols[:top_n]

	os.makedirs(out_folder, exist_ok=True)
	pd.DataFrame([(t, v) for t, p, v in top_list], columns=["Ticker", "AvgVolume"]).to_csv(os.path.join(out_folder, "top20_list.csv"), index=False)

	print("Top tickers (by avg volume):")
	for t, p, v in top_list:
		print(t, int(v) if not np.isnan(v) else 0)

	for ticker, path, _ in top_list:
		try:
			df = load_price_frame(path)
			plot_for_ticker(df, ticker, out_folder)
			print("Saved visuals for", ticker)
		except Exception as e:
			print("Error processing", ticker, e)

	# correlation heatmap
	try:
		close_df = pd.DataFrame()
		for ticker, path, _ in top_list:
			df = load_price_frame(path)
			if "Close" in df.columns:
				close_df[ticker] = df["Close"]

		close_df.sort_index(inplace=True)
		returns_df = close_df.pct_change()
		corr = returns_df.corr()

		plt.figure(figsize=(12, 10))
		sns.heatmap(corr, cmap="RdBu_r", center=0, vmin=-1, vmax=1)
		plt.title("Correlation matrix (daily returns) - Top 20")
		plt.tight_layout()
		plt.savefig(os.path.join(out_folder, "correlation_heatmap.png"), dpi=150)
		plt.close()

		# Combined boxplot of daily returns for top tickers
		try:
			returns_melt = returns_df.stack().reset_index()
			returns_melt.columns = ["Date", "Ticker", "Return"]
			returns_melt = returns_melt.dropna()
			if not returns_melt.empty:
				plt.figure(figsize=(10, 8))
				sns.boxplot(x="Return", y="Ticker", data=returns_melt, orient="h", palette="vlag")
				plt.title("Daily Returns Distribution - Top 20")
				plt.tight_layout()
				plt.savefig(os.path.join(out_folder, "top20_returns_boxplot.png"), dpi=150)
				plt.close()
				print("Saved top20 returns boxplot")
		except Exception as e:
			print("Could not create top20 returns boxplot:", e)

		print("Saved correlation heatmap")
	except Exception as e:
		print("Could not create correlation heatmap:", e)


if __name__ == "__main__":
	main()

