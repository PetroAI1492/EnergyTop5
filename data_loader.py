# data_loader.py
from storehouse import daily_change, latest_value

def load_market_data():
    data = {
        "brent": daily_change("DCOILBRENTEU"),
        "wti": daily_change("DCOILWTICO"),
        "crack": daily_change("WPU3011"),

        "stocks_total": latest_value("PET.WGTSTUS1.W"),
    }

    data["_missing"] = {k: v for k, v in data.items() if v is None}
    return data
