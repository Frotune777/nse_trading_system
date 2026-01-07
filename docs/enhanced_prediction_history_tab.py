# Enhanced ML Predictions Page - Prediction History Tab
# Add this to the page_ml_predictions() function in dashboard.py

"""
Enhanced prediction history tab code to add to dashboard.py

This should replace the Tab 4 section in page_ml_predictions()
"""

# In the tabs definition, change to 4 tabs:
# tab1, tab2, tab3, tab4 = st.tabs([
#     "📊 Predictions", 
#     "📈 Feature Importance", 
#     "🎯 Model Info",
#     "📜 Prediction History"
# ])

# Then add this as Tab 4 content:

def render_prediction_history_tab(symbol, timeframe, pipeline, ml_data, features):
    """
    Render prediction history tab with tracking and analytics.
    """
    from libs.prediction_tracker import PredictionTracker
    
    st.subheader("📜 Prediction History & Performance Tracking")
    
    tracker = PredictionTracker()
    
    # Auto-save current prediction
    st.markdown("### Current Prediction")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("💡 Predictions are automatically saved for tracking")
    
    with col2:
        if st.button("💾 Save Prediction", type="primary"):
            try:
                # Get latest prediction
                latest_features = ml_data[features.columns].iloc[[-1]]
                predictions, probabilities = pipeline.predict(latest_features)
                pred_class = predictions[0]
                pred_proba = probabilities[0]
                latest_date = ml_data.index[-1].strftime('%Y-%m-%d')
                
                # Save to tracker
                success = tracker.save_prediction(
                    symbol=symbol,
                    timeframe=timeframe,
                    predicted_class=int(pred_class),
                    probabilities=pred_proba.tolist(),
                    prediction_date=latest_date,
                    model_version='v1'
                )
                
                if success:
                    st.success(f"✅ Prediction saved for {latest_date}")
                else:
                    st.error("Failed to save prediction")
            
            except Exception as e:
                st.error(f"Error saving prediction: {e}")
    
    st.markdown("---")
    
    # Historical predictions
    st.markdown("### Historical Predictions")
    
    # Time range selector
    col1, col2 = st.columns([2, 1])
    
    with col1:
        days_back = st.slider("Days to show", 7, 90, 30, key="history_days")
    
    with col2:
        st.metric("Total Predictions", len(tracker.get_prediction_history(symbol, timeframe)))
    
    # Get prediction history
    history = tracker.get_prediction_history(symbol, timeframe, days=days_back)
    
    if len(history) == 0:
        st.warning("⚠️ No prediction history found. Make predictions to start tracking!")
        return
    
    # Display history table
    st.markdown("#### Prediction Log")
    
    # Format for display
    display_df = history.copy()
    display_df['prediction_date'] = pd.to_datetime(display_df['prediction_date'])
    
    # Add class labels
    class_labels = {0: "📉 Down", 1: "➡️ Neutral", 2: "📈 Up"}
    display_df['Predicted'] = display_df['predicted_class'].map(class_labels)
    
    if 'actual_class' in display_df.columns:
        display_df['Actual'] = display_df['actual_class'].map(lambda x: class_labels.get(x, "⏳ Pending") if pd.notna(x) else "⏳ Pending")
        display_df['Correct'] = display_df['is_correct'].map(lambda x: "✅" if x == 1 else ("❌" if x == 0 else "⏳"))
    
    # Select columns to display
    display_cols = ['prediction_date', 'Predicted', 'confidence_down', 'confidence_neutral', 'confidence_up']
    if 'Actual' in display_df.columns:
        display_cols.extend(['Actual', 'actual_return', 'Correct'])
    
    st.dataframe(
        display_df[display_cols].style.format({
            'confidence_down': '{:.1%}',
            'confidence_neutral': '{:.1%}',
            'confidence_up': '{:.1%}',
            'actual_return': '{:.2%}'
        }),
        use_container_width=True,
        height=400
    )
    
    # Performance metrics
    st.markdown("---")
    st.markdown("### Performance Metrics")
    
    metrics = tracker.calculate_accuracy(symbol, timeframe, days=days_back)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Predictions", metrics['total_predictions'])
    
    with col2:
        st.metric("With Outcomes", metrics['predictions_with_outcomes'])
    
    with col3:
        accuracy_pct = metrics['accuracy'] * 100
        st.metric("Accuracy", f"{accuracy_pct:.1f}%")
    
    with col4:
        correct = metrics['correct_predictions']
        st.metric("Correct", correct)
    
    # Precision by class
    if metrics['predictions_with_outcomes'] > 0:
        st.markdown("#### Precision by Class")
        
        col1, col2, col3 = st.columns(3)
        
        precision = metrics['precision_by_class']
        
        with col1:
            st.metric("📉 Down", f"{precision.get(0, 0):.1%}")
        
        with col2:
            st.metric("➡️ Neutral", f"{precision.get(1, 0):.1%}")
        
        with col3:
            st.metric("📈 Up", f"{precision.get(2, 0):.1%}")
        
        # Recall by class
        st.markdown("#### Recall by Class")
        
        col1, col2, col3 = st.columns(3)
        
        recall = metrics['recall_by_class']
        
        with col1:
            st.metric("📉 Down", f"{recall.get(0, 0):.1%}")
        
        with col2:
            st.metric("➡️ Neutral", f"{recall.get(1, 0):.1%}")
        
        with col3:
            st.metric("📈 Up", f"{recall.get(2, 0):.1%}")
    
    # Performance trend chart
    if len(history) > 5:
        st.markdown("---")
        st.markdown("### Performance Trend")
        
        # Calculate rolling accuracy
        history_sorted = history.sort_values('prediction_date')
        history_sorted['prediction_date'] = pd.to_datetime(history_sorted['prediction_date'])
        
        # Only include predictions with outcomes
        with_outcomes = history_sorted[history_sorted['is_correct'].notna()].copy()
        
        if len(with_outcomes) > 0:
            # Calculate cumulative accuracy
            with_outcomes['cumulative_correct'] = with_outcomes['is_correct'].cumsum()
            with_outcomes['cumulative_total'] = range(1, len(with_outcomes) + 1)
            with_outcomes['cumulative_accuracy'] = with_outcomes['cumulative_correct'] / with_outcomes['cumulative_total']
            
            # Plot
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=with_outcomes['prediction_date'],
                y=with_outcomes['cumulative_accuracy'] * 100,
                mode='lines+markers',
                name='Cumulative Accuracy',
                line=dict(color='#2196F3', width=2)
            ))
            
            # Add 50% baseline
            fig.add_hline(y=50, line_dash="dash", line_color="red", 
                         annotation_text="Random Baseline (50%)")
            
            fig.update_layout(
                title="Prediction Accuracy Over Time",
                xaxis_title="Date",
                yaxis_title="Accuracy (%)",
                height=400,
                yaxis=dict(range=[0, 100])
            )
            
            st.plotly_chart(fig, use_container_width=True)
