
import streamlit as st
import pandas as pd
import joblib


# -------------------------
# Load Saved Files
# -------------------------

model = joblib.load('food_wastage_model.pkl')
scaler = joblib.load('scaler.pkl')
encoders = joblib.load('encoders.pkl')


# -------------------------
# Page Configuration
# -------------------------

st.set_page_config(
    page_title="Smart Food Wastage Predictor",
    page_icon="🍽",
    layout="centered"
)


# -------------------------
# Title Section
# -------------------------

st.title("🍽 Smart Food Wastage Prediction System")

st.markdown("""
Estimate restaurant food wastage using Machine Learning.

This system predicts expected food wastage based on event,
guest count, food quantity, seasonality, and operational factors.
""")


# -------------------------
# Main Inputs
# -------------------------

st.subheader("📋 Event & Food Details")

col1, col2 = st.columns(2)

with col1:

    food_type = st.selectbox(
        "Type of Food",
        encoders['Type of Food'].classes_
    )

    guests = st.number_input(
        "Number of Guests",
        min_value=1,
        max_value=10000,
        step=1,
        value=100
    )

    event_type = st.selectbox(
        "Event Type",
        encoders['Event Type'].classes_
    )

with col2:

    quantity = st.number_input(
        "Quantity of Food Prepared",
        min_value=1,
        max_value=5000,
        step=10,
        value=200
    )

    seasonality = st.selectbox(
        "Seasonality",
        encoders['Seasonality'].classes_
    )


# -------------------------
# Advanced Settings
# -------------------------

with st.expander("⚙ Advanced Restaurant Settings"):

    storage_conditions = st.selectbox(
        "Storage Conditions",
        encoders['Storage Conditions'].classes_,
        index=0
    )

    purchase_history = st.selectbox(
        "Purchase History",
        encoders['Purchase History'].classes_,
        index=1
    )

    preparation_method = st.selectbox(
        "Preparation Method",
        encoders['Preparation Method'].classes_,
        index=0
    )

    location = st.selectbox(
        "Geographical Location",
        encoders['Geographical Location'].classes_,
        index=2
    )

    pricing = st.selectbox(
        "Pricing",
        encoders['Pricing'].classes_,
        index=2
    )


# -------------------------
# Predict Button
# -------------------------

if st.button("🔍 Predict Food Wastage"):

    # -------------------------
    # Business Logic Validation
    # -------------------------

    food_per_guest = quantity / guests

    reliability_warning = False

    if food_per_guest < 0.25:
        st.warning(
            "⚠ Food quantity seems unusually LOW for the number of guests. Prediction reliability may decrease."
        )
        reliability_warning = True

    elif food_per_guest > 5:
        st.warning(
            "⚠ Food quantity seems unusually HIGH for the number of guests. Prediction reliability may decrease."
        )
        reliability_warning = True


    # -------------------------
    # Encode Inputs
    # -------------------------

    food_type_encoded = encoders['Type of Food'].transform([food_type])[0]

    event_type_encoded = encoders['Event Type'].transform([event_type])[0]

    storage_encoded = encoders['Storage Conditions'].transform(
        [storage_conditions]
    )[0]

    purchase_encoded = encoders['Purchase History'].transform(
        [purchase_history]
    )[0]

    seasonality_encoded = encoders['Seasonality'].transform(
        [seasonality]
    )[0]

    preparation_encoded = encoders['Preparation Method'].transform(
        [preparation_method]
    )[0]

    location_encoded = encoders['Geographical Location'].transform(
        [location]
    )[0]

    pricing_encoded = encoders['Pricing'].transform(
        [pricing]
    )[0]


    # -------------------------
    # Create Input Data
    # -------------------------

    input_data = pd.DataFrame([{
        'Type of Food': food_type_encoded,
        'Number of Guests': guests,
        'Event Type': event_type_encoded,
        'Quantity of Food': quantity,
        'Storage Conditions': storage_encoded,
        'Purchase History': purchase_encoded,
        'Seasonality': seasonality_encoded,
        'Preparation Method': preparation_encoded,
        'Geographical Location': location_encoded,
        'Pricing': pricing_encoded
    }])


    # -------------------------
    # Scale & Predict
    # -------------------------

    input_scaled = scaler.transform(input_data)

    prediction = model.predict(input_scaled)[0]


    # Prevent impossible values
    prediction = max(0, prediction)

    max_possible_waste = quantity * 0.95
    prediction = min(prediction, max_possible_waste)


    # -------------------------
    # Prediction Output
    # -------------------------

    st.success(
        f"🍱 Estimated Food Wastage: {prediction:.2f} kg"
    )


    # -------------------------
    # Risk Assessment
    # -------------------------

    if prediction < quantity * 0.10:

        st.success(
            "✅ Low Wastage Risk: Food planning appears efficient."
        )

    elif prediction < quantity * 0.25:

        st.warning(
            "⚠ Moderate Wastage Risk: Consider improving food quantity planning."
        )

    else:

        st.error(
            "🚨 High Wastage Risk: Significant over-preparation detected."
        )


    # -------------------------
    # Smart Recommendation
    # -------------------------

    suggested_quantity = max(
        quantity - (prediction * 0.60),
        quantity * 0.60
    )

    st.info(
        f"💡 Suggested Optimization: Consider preparing around "
        f"{suggested_quantity:.0f} quantity of food to reduce wastage."
    )


    # -------------------------
    # Reliability Note
    # -------------------------

    if reliability_warning:

        st.caption(
            "Prediction generated with caution due to unusual guest-to-food ratio."
        )

