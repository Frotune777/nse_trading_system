"""
ML Predictions Page for Dashboard

Provides comprehensive interface for ML model predictions including:
- Symbol and model selection
- Real-time predictions with confidence
- Feature importance visualization
- Historical accuracy tracking
- Prediction explanations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def page_ml_predictions():
    """
    ML Predictions page with comprehensive features.
    """
    st.header("🤖 ML Stock Predictions")
    st.caption("Machine Learning powered stock direction predictions")
    
    from libs.ml_pipeline import MLPipeline
    from libs.historical_data_manager import HistoricalDataManager
    from libs.feature_engineering import FeatureEngineer
    
    # Check if models directory exists
    models_dir = Path('models')
    if not models_dir.exists():
        st.warning("⚠️ No trained models found. Please train a model first.")
        st.info("💡 Use the ML Pipeline to train models: `python -c \"from libs.ml_pipeline import train_model_for_symbol; train_model_for_symbol('TCS', '1d', '3class', 'xgboost')\"`")
        return
    
    # Get available models
    model_files = list(models_dir.glob("*_v1.joblib"))
    if not model_files:
        st.warning("⚠️ No trained models found.")
        return
    
    # Extract symbol-timeframe combinations
    available_models = []
    for model_file in model_files:
        parts = model_file.stem.split('_')
        if len(parts) >= 3:
            symbol = parts[0]
            timeframe = parts[1]
            available_models.append(f"{symbol}_{timeframe}")
    
    available_models = list(set(available_models))
    
    # Sidebar controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("🎯 Model Selection")
    
    if available_models:
        selected_model = st.sidebar.selectbox(
            "Choose Model",
            available_models,
            format_func=lambda x: f"{x.split('_')[0]} - {x.split('_')[1]}"
        )
        
        symbol, timeframe = selected_model.split('_')
        
        # Model version
        version = st.sidebar.selectbox("Model Version", ["v1"], index=0)
        
        # Prediction horizon
        horizon = st.sidebar.slider("Prediction Horizon (days)", 1, 5, 1)
        
    else:
        st.error("No models available")
        return
    
    # Main content
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Predictions", 
        "📈 Feature Importance", 
        "🎯 Model Performance",
        "📜 Prediction History"
    ])
    
    # Load model
    try:
        pipeline = MLPipeline(symbol, timeframe)
        pipeline.load_model(version=version)
        
        # Load latest data
        manager = HistoricalDataManager()
        df = manager.get_symbol_data(symbol, timeframe)
        
        if df.empty:
            st.error(f"No data found for {symbol} {timeframe}")
            return
        
        # Engineer features
        engineer = FeatureEngineer(df)
        features = engineer.build_all()
        
        # Combine with OHLCV
        ml_data = pd.concat([df, features], axis=1).dropna()
        
        if len(ml_data) == 0:
            st.error("No valid data after feature engineering")
            return
        
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return
    
    # Tab 1: Predictions
    with tab1:
        st.subheader(f"📊 Predictions for {symbol}")
        
        # Get latest data point
        latest_date = ml_data.index[-1]
        latest_features = ml_data[features.columns].iloc[[-1]]
        
        # Make prediction
        try:
            predictions, probabilities = pipeline.predict(latest_features)
            pred_class = predictions[0]
            pred_proba = probabilities[0]
            
            # Class labels
            class_labels = {0: "📉 Down", 1: "➡️ Neutral", 2: "📈 Up"}
            class_colors = {0: "#ef5350", 1: "#ffa726", 2: "#26a69a"}
            
            # Display prediction
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 2, 3])
            
            with col1:
                st.metric(
                    "Latest Close",
                    f"₹{ml_data['Close'].iloc[-1]:.2f}",
                    f"{ml_data['Close'].pct_change().iloc[-1]:.2%}"
                )
            
            with col2:
                st.metric(
                    "Prediction",
                    class_labels[pred_class],
                    f"{pred_proba[pred_class]:.1%} confidence"
                )
            
            with col3:
                st.metric(
                    "Date",
                    latest_date.strftime('%Y-%m-%d'),
                    f"Next {horizon} day(s)"
                )
            
            # Confidence gauge
            st.markdown("---")
            st.subheader("Confidence Breakdown")
            
            col1, col2, col3 = st.columns(3)
            
            for idx, (col, (class_id, label)) in enumerate(zip([col1, col2, col3], class_labels.items())):
                with col:
                    confidence = pred_proba[class_id] * 100
                    
                    # Create gauge chart
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=confidence,
                        title={'text': label},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'bar': {'color': class_colors[class_id]},
                            'steps': [
                                {'range': [0, 33], 'color': "lightgray"},
                                {'range': [33, 66], 'color': "gray"},
                                {'range': [66, 100], 'color': "darkgray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 50
                            }
                        }
                    ))
                    
                    fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig, use_container_width=True)
            
            # Recent price action
            st.markdown("---")
            st.subheader("Recent Price Action (Last 30 Days)")
            
            recent_data = ml_data.tail(30)
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=recent_data.index,
                open=recent_data['Open'],
                high=recent_data['High'],
                low=recent_data['Low'],
                close=recent_data['Close'],
                name=symbol
            ))
            
            # Add prediction marker
            fig.add_trace(go.Scatter(
                x=[latest_date],
                y=[ml_data['Close'].iloc[-1]],
                mode='markers+text',
                marker=dict(size=15, color=class_colors[pred_class], symbol='star'),
                text=[class_labels[pred_class]],
                textposition="top center",
                name="Prediction"
            ))
            
            fig.update_layout(
                title=f"{symbol} - Last 30 Days with Prediction",
                yaxis_title="Price (₹)",
                xaxis_title="Date",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Key statistics
            st.markdown("---")
            st.subheader("Key Statistics")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                volatility = ml_data['volatility_20d'].iloc[-1]
                st.metric("Volatility (20d)", f"{volatility:.4f}")
            
            with col2:
                volume_momentum = ml_data['volume_momentum_10d'].iloc[-1]
                st.metric("Volume Momentum", f"{volume_momentum:.2f}x")
            
            with col3:
                rsi = ml_data['RSI_14'].iloc[-1] if 'RSI_14' in ml_data.columns else None
                if rsi:
                    st.metric("RSI (14)", f"{rsi:.1f}")
            
            with col4:
                macd = ml_data['MACD'].iloc[-1] if 'MACD' in ml_data.columns else None
                if macd:
                    st.metric("MACD", f"{macd:.2f}")
            
        except Exception as e:
            st.error(f"Error making prediction: {e}")
            import traceback
            with st.expander("Error Details"):
                st.code(traceback.format_exc())
    
    # Tab 2: Feature Importance
    with tab2:
        st.subheader("📈 Feature Importance Analysis")
        
        try:
            # Get feature importance
            importance_df = pipeline.get_feature_importance(top_n=20)
            
            # Bar chart
            fig = px.bar(
                importance_df,
                x='importance',
                y='feature',
                orientation='h',
                title="Top 20 Most Important Features",
                labels={'importance': 'Importance Score', 'feature': 'Feature'},
                color='importance',
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(height=600, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
            
            # Feature importance table
            st.subheader("Feature Importance Table")
            st.dataframe(
                importance_df.style.format({'importance': '{:.4f}'}),
                use_container_width=True,
                height=400
            )
            
            # Feature categories breakdown
            st.markdown("---")
            st.subheader("Feature Categories")
            
            categories = {
                'Returns': [f for f in importance_df['feature'] if 'return' in f.lower()],
                'Volatility': [f for f in importance_df['feature'] if 'vol' in f.lower()],
                'Momentum': [f for f in importance_df['feature'] if any(x in f.lower() for x in ['momentum', 'roc'])],
                'Volume': [f for f in importance_df['feature'] if 'volume' in f.lower() or 'vwap' in f.lower()],
                'Patterns': [f for f in importance_df['feature'] if any(x in f.lower() for x in ['range', 'gap', 'shadow', 'body'])]
            }
            
            category_importance = {}
            for cat, features in categories.items():
                total_imp = importance_df[importance_df['feature'].isin(features)]['importance'].sum()
                category_importance[cat] = total_imp
            
            # Pie chart
            fig = px.pie(
                values=list(category_importance.values()),
                names=list(category_importance.keys()),
                title="Importance by Feature Category"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error displaying feature importance: {e}")
    
    # Tab 3: Model Performance
    with tab3:
        st.subheader("🎯 Model Performance Metrics")
        
        st.info("📝 **Note:** Performance metrics are from the test set during training.")
        
        # Load model metadata
        try:
            import joblib
            metadata_path = models_dir / f"{symbol}_{timeframe}_{version}_metadata.joblib"
            metadata = joblib.load(metadata_path)
            
            st.markdown("### Model Information")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Symbol", metadata['symbol'])
            with col2:
                st.metric("Timeframe", metadata['timeframe'])
            with col3:
                st.metric("Model Type", metadata['model_type'])
            
            st.markdown("---")
            st.markdown("### Training Configuration")
            st.write(f"**Classification Type:** {metadata['classification_type']}")
            st.write(f"**Features Used:** {len(metadata['feature_names'])}")
            st.write(f"**Target Variable:** {metadata['target_name']}")
            
            # Performance metrics (would need to be saved during training)
            st.markdown("---")
            st.markdown("### Performance Metrics")
            st.warning("⚠️ To display performance metrics, re-train the model with metric saving enabled.")
            
        except Exception as e:
            st.error(f"Error loading model metadata: {e}")
    
    # Tab 4: Prediction History
    with tab4:
        st.subheader("📜 Prediction History")
        
        st.info("🚧 **Coming Soon:** Historical predictions tracking will be implemented in the next update.")
        
        st.markdown("""
        **Planned Features:**
        - Track all predictions made over time
        - Compare predictions vs actual outcomes
        - Calculate accuracy metrics
        - Visualize prediction performance trends
        - Export prediction history to CSV
        """)


# Add this function to dashboard.py
