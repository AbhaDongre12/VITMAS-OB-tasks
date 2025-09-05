import numpy as np
import matplotlib.pyplot as plt

# Load Airline Passengers Dataset
def load_airline_data():
    # Monthly international airline passengers, 1949–1960
    return np.array([
        112,118,132,129,121,135,148,148,136,119,104,118,
        115,126,141,135,125,149,170,170,158,133,114,140,
        145,150,178,163,172,178,199,199,184,162,146,166,
        171,180,193,181,183,218,230,242,209,191,172,194,
        196,196,236,235,229,243,264,272,237,211,180,201,
        204,188,235,227,234,264,302,293,259,229,203,229,
        242,233,267,269,270,315,364,347,312,274,237,278,
        284,277,317,313,318,374,413,405,355,306,271,306,
        315,301,356,348,355,422,465,467,404,347,305,336,
        340,318,362,348,363,435,491,505,404,359,310,337,
        360,342,406,396,420,472,548,559,463,407,362,405,
        417,391,419,461,472,535,622,606,508,461,390,432
    ], dtype=np.float64)

# Differencing (Integration part - 'I')
def difference(series, d=1):
    diff = series.copy()
    for _ in range(d):
        diff = diff[1:] - diff[:-1]
    return diff

# Inverse differencing
def inverse_difference(original, diff_series, d=1):
    result = original[:d].tolist()
    for i in range(len(diff_series)):
        result.append(result[-1] + diff_series[i])
    return np.array(result)

# Autoregression model (AR part)
def predict_ar(train, lags, coefficients):
    yhat = 0
    for i in range(lags):
        yhat += coefficients[i] * train[-i-1]
    return yhat

# Moving Average model (MA part)
def predict_ma(errors, q, theta):
    yhat = 0
    for i in range(q):
        if i < len(errors):
            e = np.clip(errors[-i-1], -100.0, 100.0)
            yhat += theta[i] * e
    return yhat

# Train ARIMA(p,d,q) from scratch
def train_arima(series, p, d, q, n_forecast):
    diff_series = difference(series, d)

    train_size = len(diff_series) - n_forecast
    train, test = diff_series[:train_size], diff_series[train_size:]

    # Initialize AR and MA coefficients (use small random values)
    phi = np.random.randn(p) * 0.01
    theta = np.random.randn(q) * 0.01
    alpha = 0.0005  # learning rate

    history = train.tolist()
    errors = []

    # Simple Gradient Descent
    for epoch in range(50):  # number of training iterations
        for t in range(p, len(train)):
            ar_part = predict_ar(history[:t], p, phi)
            ma_part = predict_ma(errors, q, theta)
            yhat = ar_part + ma_part
            if not np.isfinite(ar_part) or not np.isfinite(ma_part) or not np.isfinite(yhat):
                print(f"Numerical instability detected at epoch {epoch}, t = {t}")
                return np.array([np.nan]*n_forecast)

            error = train[t] - yhat
            errors.append(error)
            error = np.clip(error, -100.0, 100.0)  # Prevent exploding errors

            # Update AR coefficients
            for i in range(p):
                phi[i] += alpha * error * history[t - i - 1]
                phi[i] = np.clip(phi[i], -10, 10)# Prevent phi from exploding

            # Update MA coefficients
            for i in range(q):
                if i < len(errors):
                    theta[i] += alpha * error * errors[-i-1]
                    theta[i] = np.clip(theta[i], -10, 10) # Prevent theta from exploding

    # Forecasting
    forecasts = []
    test_errors = []
    for t in range(len(test)):
        ar_part = predict_ar(history, p, phi)
        ma_part = predict_ma(errors, q, theta)
        yhat = ar_part + ma_part
        forecasts.append(yhat)

        error = test[t] - yhat
        errors.append(error)
        test_errors.append(error)
        history.append(test[t])  # use actual for next step

    # Inverse differencing to get actual forecast values
    forecasted_values = inverse_difference(series[-(n_forecast + d):], forecasts, d)

    # Evaluation
    actual = series[-n_forecast:]
    mse = np.mean((forecasted_values[-n_forecast:] - actual) ** 2)
    mae = np.mean(np.abs(forecasted_values[-n_forecast:] - actual))
    
    print(f'MSE: {mse:.3f}')
    print(f'MAE: {mae:.3f}')

    # Plot
    plt.figure(figsize=(12, 6))
    if not np.all(np.isfinite(forecasted_values[-n_forecast:])):
        print("Warning: NaNs in forecast. Skipping plot.")
        return forecasted_values[-n_forecast:]
    plt.plot(range(len(series)), series, label='Actual')
    plt.plot(range(len(series)-n_forecast, len(series)), forecasted_values[-n_forecast:], label='Forecast', color='red')
    plt.title(f'ARIMA({p},{d},{q}) Forecast')
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.grid(True)
    plt.show()

    return forecasted_values[-n_forecast:]

# Example usage
if __name__ == "__main__":
    data = load_airline_data()
    # Normalize the data
    mean, std = data.mean(), data.std()
    normalized_data = (data - mean) / std

    # Train ARIMA on normalized data
    forecast_normalized = train_arima(normalized_data, p=2, d=1, q=2, n_forecast=20)
    forecast = train_arima(data, p=2, d=1, q=2, n_forecast=20)
