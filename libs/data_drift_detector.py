import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

class DataDriftDetector:
    """
    Detects data drift between reference (training) data and current (production) data.
    Uses Kolmogorov-Smirnov (KS) Test and Population Stability Index (PSI).
    """
    
    def __init__(self, reference_data: pd.DataFrame):
        """
        Initialize with reference data (e.g., training set).
        
        Args:
            reference_data: DataFrame containing the baseline data.
        """
        self.reference_data = reference_data
        
    def calculate_psi(self, expected: np.ndarray, actual: np.ndarray, buckets: int = 10) -> float:
        """
        Calculate Population Stability Index (PSI) for a single feature.
        
        Args:
            expected: Reference data array
            actual: Current data array
            buckets: Number of quantiles/bins
            
        Returns:
            PSI value
            < 0.1: No significant drift
            0.1 - 0.2: Moderate drift
            > 0.2: Significant drift
        """
        def scale_range(input, min_v, max_v):
            input += -(np.min(input))
            input /= np.max(input) / (max_v - min_v)
            input += min_v
            return input

        breakpoints = np.arange(0, buckets + 1) / (buckets) * 100
        
        try:
            # Create breakpoints based on reference data (expected)
            breakpoints_values = np.percentile(expected, breakpoints)
            
            # Add small noise to avoid duplicate bin edges if many values are same
            if len(np.unique(breakpoints_values)) != len(breakpoints_values):
                breakpoints_values = np.unique(breakpoints_values)
                # Fallback to linear spacing if percentiles collapse
                if len(breakpoints_values) < 2:
                     breakpoints_values = np.linspace(np.min(expected), np.max(expected), buckets+1)

            # Calculate frequencies
            expected_percents = np.histogram(expected, breakpoints_values)[0] / len(expected)
            actual_percents = np.histogram(actual, breakpoints_values)[0] / len(actual)

            # Avoid division by zero
            expected_percents = np.where(expected_percents == 0, 0.0001, expected_percents)
            actual_percents = np.where(actual_percents == 0, 0.0001, actual_percents)

            # PSI formula
            psi_values = (expected_percents - actual_percents) * np.log(expected_percents / actual_percents)
            psi = np.sum(psi_values)
            
            return psi
            
        except Exception as e:
            logger.warning(f"PSI calculation failed: {e}")
            return 0.0

    def calculate_ks(self, data1: np.ndarray, data2: np.ndarray) -> Tuple[float, float]:
        """
        Perform Kolmogorov-Smirnov test.
        
        Returns:
            Tuple of (KS statistic, p-value).
            p-value < 0.05 implies distributions are different.
        """
        return stats.ks_2samp(data1, data2)
    
    def detect_drift(self, current_data: pd.DataFrame, 
                     features: List[str] = None,
                     psi_threshold: float = 0.2,
                     ks_p_value_threshold: float = 0.05) -> Dict:
        """
        Run drift detection on specified features (or all numeric features).
        
        Args:
            current_data: New data to check against reference.
            features: List of feature names to check.
            psi_threshold: Threshold for flagging PSI drift.
            ks_p_value_threshold: Threshold for flagging KS drift (significance level).
            
        Returns:
            Dictionary containing drift report.
        """
        if features is None:
            features = self.reference_data.select_dtypes(include=[np.number]).columns.tolist()
            
        # Intersect features
        features = [f for f in features if f in current_data.columns and f in self.reference_data.columns]
        
        report = {
            "drift_detected": False,
            "drifted_features": [],
            "details": {}
        }
        
        for feature in features:
            ref_vals = self.reference_data[feature].dropna().values
            curr_vals = current_data[feature].dropna().values
            
            if len(ref_vals) == 0 or len(curr_vals) == 0:
                continue
                
            # PSI
            psi = self.calculate_psi(ref_vals, curr_vals)
            
            # KS Test
            ks_stat, ks_p = self.calculate_ks(ref_vals, curr_vals)
            
            is_drifted = (psi > psi_threshold) or (ks_p < ks_p_value_threshold)
            
            report["details"][feature] = {
                "psi": float(psi),
                "ks_stat": float(ks_stat),
                "ks_p_value": float(ks_p),
                "drift_detected": bool(is_drifted)
            }
            
            if is_drifted:
                report["drifted_features"].append(feature)
                
        if report["drifted_features"]:
            report["drift_detected"] = True
            
        return report

if __name__ == "__main__":
    # Test
    print("Testing DataDriftDetector...")
    
    # Generate synthetic data
    np.random.seed(42)
    ref = pd.DataFrame({'feature1': np.random.normal(0, 1, 1000)})
    
    # 1. No Drift
    curr_no_drift = pd.DataFrame({'feature1': np.random.normal(0, 1, 1000)})
    
    # 2. Significant Drift (Shifted mean)
    curr_drift = pd.DataFrame({'feature1': np.random.normal(2, 1, 1000)})
    
    detector = DataDriftDetector(ref)
    
    print("\nCheck 1: No Drift")
    report1 = detector.detect_drift(curr_no_drift)
    print(f"Drift Detected: {report1['drift_detected']}")
    print(f"PSI: {report1['details']['feature1']['psi']:.4f}")
    
    print("\nCheck 2: Significant Drift")
    report2 = detector.detect_drift(curr_drift)
    print(f"Drift Detected: {report2['drift_detected']}")
    print(f"PSI: {report2['details']['feature1']['psi']:.4f}")
