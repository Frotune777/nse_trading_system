import mlflow
import mlflow.sklearn
import mlflow.pytorch
import mlflow.xgboost
import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime

class MLflowManager:
    """
    Manages MLflow experiment tracking and logging.
    """
    
    def __init__(self, experiment_name="nse_trading_system", tracking_uri=None):
        """
        Initialize MLflow manager.
        
        Args:
            experiment_name (str): Name of the experiment to log to.
            tracking_uri (str): MLflow tracking URI (default: local ./mlruns)
        """
        if tracking_uri is None:
            # Default to local mlruns folder in project root
            project_root = Path(__file__).resolve().parent.parent
            tracking_uri = f"file://{project_root}/mlruns"
            
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        self.experiment = mlflow.get_experiment_by_name(experiment_name)
        self.run_id = None
        
    def start_run(self, run_name=None, nested=False):
        """Start a new MLflow run."""
        if run_name is None:
            run_name = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
        run = mlflow.start_run(run_name=run_name, nested=nested)
        self.run_id = run.info.run_id
        return run
        
    def end_run(self):
        """End the current MLflow run."""
        if mlflow.active_run():
            mlflow.end_run()
            self.run_id = None
            
    def log_params(self, params):
        """Log a dictionary of parameters."""
        mlflow.log_params(params)
        
    def log_metrics(self, metrics, step=None):
        """Log a dictionary of metrics."""
        mlflow.log_metrics(metrics, step=step)
        
    def log_model(self, model, artifact_path, model_type="sklearn"):
        """
        Log a model to MLflow.
        model_type: 'sklearn', 'xgboost', 'pytorch'
        """
        if model_type == "sklearn":
            mlflow.sklearn.log_model(model, artifact_path)
        elif model_type == "xgboost":
            mlflow.xgboost.log_model(model, artifact_path)
        elif model_type == "pytorch":
            mlflow.pytorch.log_model(model, artifact_path)
        else:
            print(f"Warning: Unknown model type '{model_type}', skipping log_model.")
            
    def log_artifact(self, local_path, artifact_path=None):
        """Log a local file or directory as an artifact."""
        if os.path.exists(local_path):
            mlflow.log_artifact(local_path, artifact_path)
        else:
            print(f"Warning: Artifact not found at {local_path}")
            
    def register_model(self, model_name, model_uri=None):
        """Register the current run's model to the Model Registry."""
        if model_uri is None and self.run_id:
            model_uri = f"runs:/{self.run_id}/model"
            
        if model_uri:
            mlflow.register_model(model_uri, model_name)
            
    def get_best_run(self, metric_name="accuracy", ascending=False):
        """Get the best run from the experiment based on a metric."""
        runs = mlflow.search_runs(experiment_ids=[self.experiment.experiment_id])
        if runs.empty:
            return None
            
        runs = runs.sort_values(f"metrics.{metric_name}", ascending=ascending)
        return runs.iloc[0]

if __name__ == "__main__":
    # Test
    manager = MLflowManager()
    with manager.start_run(run_name="test_run"):
        manager.log_params({"param1": 5})
        manager.log_metrics({"accuracy": 0.95})
        print("Test run logged successfully.")
