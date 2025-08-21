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
