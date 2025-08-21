import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# Dummy-Daten erzeugen
def generate_data(n=200):
    df = pd.DataFrame({
        "Absatz": np.random.poisson(lam=20, size=n),
        "Lagerbestand": np.random.randint(50, 500, size=n),
        "Preisstufe": np.random.choice([1, 2, 3, 4], size=n),
        "Warengruppe": np.random.choice(["A", "B", "C"], size=n),
        "Saison": np.random.choice([0, 1], size=n),
        "Wochen_trend": np.random.normal(0, 1, size=n),
        "Abschriften_Empfehlung": np.random.choice([0, 10, 30], size=n)
    })
    return pd.get_dummies(df, columns=["Warengruppe"], drop_first=True)

# Modell trainieren
def train_model():
    df_encoded = generate_data()
    X = df_encoded.drop("Abschriften_Empfehlung", axis=1)
    y = df_encoded["Abschriften_Empfehlung"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = xgb.XGBClassifier(
        objective="multi:softmax",
        num_class=3,
        eval_metric="mlogloss",
        use_label_encoder=False,
        n_estimators=50,
        max_depth=3
    )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    
    joblib.dump(model, "abschriften_model.pkl")
    print(f"✅ Modell gespeichert als 'abschriften_model.pkl' | RMSE: {rmse:.2f}")

# Funktion ausführen
if __name__ == "__main__":
    train_model()

# Modell speichern
joblib.dump(model, "abschriften_model.pkl")
print("✅ Modell gespeichert als 'abschriften_model.pkl'")

def generate_ml_prediction(df):
    if model is None:
        return None

    try:
        # Nur benötigte Features verwenden
        df_input = df.copy()
        df_input = pd.get_dummies(df_input, columns=["Warengruppe"], drop_first=True)

        # Gleiche Features wie beim Training (ggf. anpassen!)
        used_cols = ["Absatz", "Lagerbestand", "Preisstufe", "Saison", "Wochen_trend"]
        used_cols += [col for col in df_input.columns if "Warengruppe_" in col]
        df_input = df_input[used_cols]

        return model.predict(df_input)
    except Exception as e:
        print(f"ML Prediction Error: {e}")
        return None

