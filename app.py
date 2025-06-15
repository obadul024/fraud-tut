from fastapi import FastAPI, Query
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score
)
import numpy as np
import joblib
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from typing import List
# Load data & models
X_test = joblib.load('data/X_test_pca.pkl')
y_test = joblib.load('data/y_test_pca.pkl')
rf_pca = joblib.load('data/rf_pca.pkl')
lr_pca = joblib.load('data/lr_pca.pkl')

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "MODEL"}

@app.get("/predict")
def predict(
    model: str,
    data: List[float] = Query(..., description="List of PCA-transformed features")
):
    input_data = np.array(data).reshape(1, -1)
    if model == "rf_pca":
        return rf_pca.predict(input_data).tolist()
    else:
        return lr_pca.predict(input_data).tolist()
@app.get("/score")
def score(
    model: str,
    acc_flag: bool = False,
    f1_flag: bool = False,
    recall_flag: bool = False,
    precision_flag: bool = False,
    conf_flag: bool = False,
    roc_flag: bool = False
):
    if model == "rf_pca":
        current_model = rf_pca
    else:
        current_model = lr_pca

    y_pred = current_model.predict(X_test)
    return_out = {}

    input_example = X_test[:5]
    signature = infer_signature(input_example, current_model.predict(input_example))
    
    mlflow.set_experiment("default")
    with mlflow.start_run(run_name=f"{model}_score_run", nested=True):
        mlflow.set_tag("model", model)

        if roc_flag:
            roc = roc_auc_score(y_test, y_pred)
            return_out["roc_auc"] = roc
            mlflow.log_metric("roc_auc", roc)

        if acc_flag:
            acc = accuracy_score(y_test, y_pred)
            return_out["accuracy"] = acc
            mlflow.log_metric("accuracy", acc)

        if f1_flag:
            f1 = f1_score(y_test, y_pred)
            return_out["f1"] = f1
            mlflow.log_metric("f1", f1)

        if recall_flag:
            recall = recall_score(y_test, y_pred)
            return_out["recall"] = recall
            mlflow.log_metric("recall", recall)

        if precision_flag:
            precision = precision_score(y_test, y_pred)
            return_out["precision"] = precision
            mlflow.log_metric("precision", precision)

        if conf_flag:
            conf = confusion_matrix(y_test, y_pred)
            return_out["confusion_matrix"] = conf.tolist()

        # ✅ Modern MLflow logging
        mlflow.sklearn.log_model(
            sk_model=current_model,
            name=f"{model}_model",
            input_example=input_example,
            signature=signature
        )

    return return_out
