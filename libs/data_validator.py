"""
Data Validation Module

Ensures data quality before feeding into ML models.
Garbage in = garbage out - this module prevents that.

Author: Trading System ML Team
Created: 2026-01-07
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidator:
    """
    Validates OHLCV and feature data quality.
    
    Performs:
    - Outlier detection (Z-score, IQR)
    - Missing value analysis
    - OHLCV logic validation
    - Data quality reporting
    
    Example:
        >>> from libs.data_validator import DataValidator
        >>> validator = DataValidator(z_threshold=3.0)
        >>> report = validator.generate_quality_report(df)
        >>> print(f"Data quality score: {report['quality_score']}/100")
    """
    
    def __init__(self, z_threshold: float = 3.0):
        """
        Initialize data validator.
        
        Args:
            z_threshold: Z-score threshold for outlier detection (default: 3.0)
        """
        self.z_threshold = z_threshold
        self.validation_report = {}
        logger.info(f"Initialized DataValidator with z_threshold={z_threshold}")
    
    def detect_outliers_zscore(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Detect outliers using Z-score method.
        
        Z-score = (x - mean) / std
        Values with |Z-score| > threshold are outliers.
        
        Args:
            df: Input dataframe
            columns: Columns to check for outliers
            
        Returns:
            DataFrame with outlier flags (True = outlier)
        """
        outlier_flags = pd.DataFrame(index=df.index)
        
        for col in columns:
            if col not in df.columns:
                logger.warning(f"Column {col} not found in dataframe")
                continue
            
            # Calculate Z-scores
            z_scores = np.abs(stats.zscore(df[col].dropna()))
            
            # Create boolean mask (aligned with original index)
            mask = pd.Series(False, index=df.index)
            mask.loc[df[col].notna()] = z_scores > self.z_threshold
            
            outlier_flags[f'{col}_outlier'] = mask
            
            outlier_count = mask.sum()
            if outlier_count > 0:
                logger.info(f"Found {outlier_count} outliers in {col} (Z-score method)")
        
        return outlier_flags
    
    def detect_outliers_iqr(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """
        Detect outliers using Interquartile Range (IQR) method.
        
        More robust to extreme values than Z-score.
        Outliers: values < Q1 - 1.5*IQR or > Q3 + 1.5*IQR
        
        Args:
            df: Input dataframe
            columns: Columns to check for outliers
            
        Returns:
            DataFrame with outlier flags
        """
        outlier_flags = pd.DataFrame(index=df.index)
        
        for col in columns:
            if col not in df.columns:
                logger.warning(f"Column {col} not found in dataframe")
                continue
            
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outlier_flags[f'{col}_outlier_iqr'] = (
                (df[col] < lower_bound) | (df[col] > upper_bound)
            )
            
            outlier_count = outlier_flags[f'{col}_outlier_iqr'].sum()
            if outlier_count > 0:
                logger.info(f"Found {outlier_count} outliers in {col} (IQR method)")
        
        return outlier_flags
    
    def check_missing_values(self, df: pd.DataFrame) -> Dict:
        """
        Analyze missing values in dataset.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary with missing value statistics
        """
        missing_stats = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'columns_with_missing': {},
            'rows_with_any_missing': df.isnull().any(axis=1).sum(),
            'total_missing_values': df.isnull().sum().sum()
        }
        
        for col in df.columns:
            missing_count = df[col].isnull().sum()
            if missing_count > 0:
                missing_stats['columns_with_missing'][col] = {
                    'count': missing_count,
                    'percentage': (missing_count / len(df)) * 100
                }
        
        missing_stats['missing_percentage'] = (
            missing_stats['total_missing_values'] / 
            (len(df) * len(df.columns)) * 100
        )
        
        return missing_stats
    
    def validate_ohlcv_logic(self, df: pd.DataFrame) -> Dict:
        """
        Check OHLCV data logic.
        
        Rules:
        - High >= Low
        - High >= Open, Close
        - Low <= Open, Close
        - Volume >= 0
        - All values > 0 (prices can't be negative)
        
        Args:
            df: DataFrame with OHLCV columns
            
        Returns:
            Dictionary with validation results
        """
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            logger.error(f"Missing required columns: {missing_cols}")
            return {'valid': False, 'error': f'Missing columns: {missing_cols}'}
        
        validation_results = {
            'valid': True,
            'violations': {},
            'total_violations': 0
        }
        
        # Check High >= Low
        violations = (df['High'] < df['Low']).sum()
        if violations > 0:
            validation_results['violations']['high_low'] = violations
            validation_results['total_violations'] += violations
            logger.warning(f"Found {violations} rows where High < Low")
        
        # Check High >= Open
        violations = (df['High'] < df['Open']).sum()
        if violations > 0:
            validation_results['violations']['high_open'] = violations
            validation_results['total_violations'] += violations
            logger.warning(f"Found {violations} rows where High < Open")
        
        # Check High >= Close
        violations = (df['High'] < df['Close']).sum()
        if violations > 0:
            validation_results['violations']['high_close'] = violations
            validation_results['total_violations'] += violations
            logger.warning(f"Found {violations} rows where High < Close")
        
        # Check Low <= Open
        violations = (df['Low'] > df['Open']).sum()
        if violations > 0:
            validation_results['violations']['low_open'] = violations
            validation_results['total_violations'] += violations
            logger.warning(f"Found {violations} rows where Low > Open")
        
        # Check Low <= Close
        violations = (df['Low'] > df['Close']).sum()
        if violations > 0:
            validation_results['violations']['low_close'] = violations
            validation_results['total_violations'] += violations
            logger.warning(f"Found {violations} rows where Low > Close")
        
        # Check Volume >= 0
        violations = (df['Volume'] < 0).sum()
        if violations > 0:
            validation_results['violations']['negative_volume'] = violations
            validation_results['total_violations'] += violations
            logger.warning(f"Found {violations} rows with negative volume")
        
        # Check for negative prices
        for col in ['Open', 'High', 'Low', 'Close']:
            violations = (df[col] <= 0).sum()
            if violations > 0:
                validation_results['violations'][f'negative_{col.lower()}'] = violations
                validation_results['total_violations'] += violations
                logger.warning(f"Found {violations} rows with non-positive {col}")
        
        validation_results['valid'] = validation_results['total_violations'] == 0
        
        return validation_results
    
    def calculate_quality_score(self, df: pd.DataFrame) -> float:
        """
        Calculate overall data quality score (0-100).
        
        Factors:
        - Missing values (40 points)
        - OHLCV logic violations (40 points)
        - Outliers (20 points)
        
        Args:
            df: Input dataframe
            
        Returns:
            Quality score (0-100)
        """
        score = 100.0
        
        # Missing values penalty (max 40 points)
        missing_stats = self.check_missing_values(df)
        missing_penalty = min(40, missing_stats['missing_percentage'] * 2)
        score -= missing_penalty
        
        # OHLCV logic violations (max 40 points)
        ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if all(col in df.columns for col in ohlcv_cols):
            validation = self.validate_ohlcv_logic(df)
            violation_rate = (validation['total_violations'] / len(df)) * 100
            violation_penalty = min(40, violation_rate * 4)
            score -= violation_penalty
        
        # Outliers penalty (max 20 points)
        outlier_cols = [col for col in ['Close', 'Volume'] if col in df.columns]
        if outlier_cols:
            outliers = self.detect_outliers_iqr(df, outlier_cols)
            outlier_rate = (outliers.sum().sum() / (len(df) * len(outlier_cols))) * 100
            outlier_penalty = min(20, outlier_rate * 2)
            score -= outlier_penalty
        
        return max(0, score)
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict:
        """
        Generate comprehensive data quality report.
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary with complete quality report
        """
        logger.info("Generating data quality report...")
        
        report = {
            'dataset_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'date_range': (str(df.index.min()), str(df.index.max())) if isinstance(df.index, pd.DatetimeIndex) else ('N/A', 'N/A'),
                'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
            },
            'missing_values': self.check_missing_values(df),
            'quality_score': self.calculate_quality_score(df)
        }
        
        # OHLCV validation if applicable
        ohlcv_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if all(col in df.columns for col in ohlcv_cols):
            report['ohlcv_validation'] = self.validate_ohlcv_logic(df)
            
            # Outlier detection on OHLCV
            report['outliers_zscore'] = self.detect_outliers_zscore(
                df, ['Open', 'High', 'Low', 'Close', 'Volume']
            )
            report['outliers_iqr'] = self.detect_outliers_iqr(
                df, ['Open', 'High', 'Low', 'Close', 'Volume']
            )
        
        logger.info(f"✅ Quality report complete. Score: {report['quality_score']:.2f}/100")
        
        return report
    
    def print_quality_report(self, report: Dict) -> None:
        """
        Print quality report in human-readable format.
        
        Args:
            report: Quality report dictionary
        """
        print("\n" + "="*60)
        print("DATA QUALITY REPORT")
        print("="*60)
        
        # Dataset info
        info = report['dataset_info']
        print(f"\nDataset Info:")
        print(f"  Rows: {info['rows']:,}")
        print(f"  Columns: {info['columns']}")
        print(f"  Date Range: {info['date_range'][0]} to {info['date_range'][1]}")
        print(f"  Memory Usage: {info['memory_usage_mb']:.2f} MB")
        
        # Quality score
        score = report['quality_score']
        print(f"\n📊 Overall Quality Score: {score:.2f}/100")
        if score >= 90:
            print("   ✅ Excellent quality")
        elif score >= 75:
            print("   ⚠️  Good quality, minor issues")
        elif score >= 60:
            print("   ⚠️  Fair quality, needs attention")
        else:
            print("   ❌ Poor quality, requires cleanup")
        
        # Missing values
        missing = report['missing_values']
        print(f"\nMissing Values:")
        print(f"  Total: {missing['total_missing_values']:,} ({missing['missing_percentage']:.2f}%)")
        print(f"  Rows affected: {missing['rows_with_any_missing']:,}")
        if missing['columns_with_missing']:
            print(f"  Columns with missing data:")
            for col, stats in list(missing['columns_with_missing'].items())[:5]:
                print(f"    - {col}: {stats['count']:,} ({stats['percentage']:.2f}%)")
            if len(missing['columns_with_missing']) > 5:
                print(f"    ... and {len(missing['columns_with_missing']) - 5} more")
        
        # OHLCV validation
        if 'ohlcv_validation' in report:
            validation = report['ohlcv_validation']
            print(f"\nOHLCV Logic Validation:")
            if validation['valid']:
                print("  ✅ All OHLCV logic checks passed")
            else:
                print(f"  ❌ Found {validation['total_violations']} violations:")
                for violation_type, count in validation['violations'].items():
                    print(f"    - {violation_type}: {count}")
        
        # Outliers
        if 'outliers_iqr' in report:
            outliers = report['outliers_iqr']
            outlier_count = outliers.sum().sum()
            print(f"\nOutliers (IQR method):")
            print(f"  Total: {outlier_count}")
            if outlier_count > 0:
                for col in outliers.columns:
                    count = outliers[col].sum()
                    if count > 0:
                        print(f"    - {col}: {count}")
        
        print("\n" + "="*60 + "\n")


def validate_dataframe(df: pd.DataFrame, z_threshold: float = 3.0) -> Dict:
    """
    Convenience function to validate a dataframe.
    
    Args:
        df: DataFrame to validate
        z_threshold: Z-score threshold for outliers
        
    Returns:
        Quality report dictionary
    
    Example:
        >>> report = validate_dataframe(df)
        >>> print(f"Quality score: {report['quality_score']}")
    """
    validator = DataValidator(z_threshold=z_threshold)
    report = validator.generate_quality_report(df)
    validator.print_quality_report(report)
    
    return report
