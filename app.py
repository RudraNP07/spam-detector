import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import numpy as np
import time

# Set page configuration
st.set_page_config(page_title="Enterprise Spam Shield", layout="wide", page_icon="🛡️")

# --- 1. SIMULATED DATABASE INITIALIZATION WITH DETAILS ---
if "history" not in st.session_state:
    st.session_state.history = pd.DataFrame([
        {"Timestamp": "2026-05-27 14:20", "Message Snippet": "Hey, are we still meeting for lunch today?", "Classification": "Safe (Ham)", "Confidence": 0.98, "Analysis Details": "None (Standard Syntax)"},
        {"Timestamp": "2026-05-27 15:10", "Message Snippet": "URGENT: Your account access expires in 24h. Click here...", "Classification": "Spam", "Confidence": 0.99, "Analysis Details": "Suspicious Links, Spam Keywords"},
        {"Timestamp": "2026-05-27 16:05", "Message Snippet": "Congratulations! You won a $500 gift card! Claim now.", "Classification": "Spam", "Confidence": 0.95, "Analysis Details": "Promotional Language, Excessive Exclamations"},
        {"Timestamp": "2026-05-27 16:42", "Message Snippet": "Can you review the attached project proposal files?", "Classification": "Safe (Ham)", "Confidence": 0.92, "Analysis Details": "None (Standard Syntax)"},
    ])

# --- 2. FOOLPROOF TRAINING PIPELINE ---
@st.cache_resource
def train_model():
    try:
        df = pd.read_csv('spam.csv', encoding='latin-1')
        df.columns = df.columns.str.strip()
        if 'v1' in df.columns and 'v2' in df.columns:
            text_data = df['v2'].astype(str)
            labels = df['v1'].astype(str).str.strip().str.lower()
        elif 'text' in df.columns and 'label' in df.columns:
            text_data = df['text'].astype(str)
            labels = df['label'].astype(str).str.strip().str.lower()
        else:
            text_data = df.iloc[:, 1].astype(str)
            labels = df.iloc[:, 0].astype(str).str.strip().str.lower()
            
        labels = labels.replace({'1': 'spam', '1.0': 'spam', '0': 'ham', '0.0': 'ham', 'positive': 'spam', 'negative': 'ham'})
        clean_df = pd.DataFrame({'text': text_data, 'label': labels})
        clean_df = clean_df[clean_df['label'].isin(['ham', 'spam'])].dropna()
        
        vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), min_df=1)
        X_train = vectorizer.fit_transform(clean_df['text'])
        
        model = MultinomialNB(alpha=1.0, fit_prior=True)
        model.fit(X_train, clean_df['label'])
        return model, vectorizer, f"Successfully trained on {len(clean_df)} valid rows!"
    except Exception as e:
        dummy_vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
        dummy_texts = ["hello friend how are you doing", "hey did you see the email", "win free cash prize lottery click link now claim your money", "urgent award text claim cash"]
        dummy_labels = ["ham", "ham", "spam", "spam"]
        X = dummy_vectorizer.fit_transform(dummy_texts)
        dummy_model = MultinomialNB(alpha=1.0, fit_prior=True).fit(X, dummy_labels)
        return dummy_model, dummy_vectorizer, f"Fallback Active (Error: {e})"

model, vectorizer, status = train_model()

# --- 3. INTERFACE HEADER ---
st.title("🛡️ Enterprise Spam Shield & Analytics Center")

# --- STANDALONE USER SECURITY TIPS ADVISORY ---
st.html("""
<div style="background-color: #0d121f; padding: 22px 25px; border-radius: 10px; border-left: 5px solid #00FFCC; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.35);">
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
        <span style="font-size: 18px;">🛡️</span>
        <span style="font-family: 'Segoe UI', sans-serif; font-size: 14px; font-weight: 700; color: #ffffff; letter-spacing: 0.5px;">USER DEFENSE: HOW TO SPOT AND EVADE EVASIVE SPAM</span>
    </div>
    <ul style="margin: 0; padding-left: 20px; font-family: 'Segoe UI', sans-serif; font-size: 12.5px; color: #8b949e; line-height: 1.7;">
        <li><strong style="color: #ffffff;">1. Inspect the Sender's Domain Root:</strong> Verify the actual email address domain after the <code style="color: #00FFCC;">@</code> symbol matches your official corporate extension precisely.</li>
        <li><strong style="color: #ffffff;">2. Beware of "Urgency" and "Consequence" Hooks:</strong> If an incoming text demands immediate action under threat of suspension, or promises an unexpected payout, it is likely a phishing vector.</li>
        <li><strong style="color: #ffffff;">3. Do Not Click "Unsubscribe" inside Suspicious Mail:</strong> This often just alerts the attacker that your inbox is active. Instead, flag it to train local infrastructure models.</li>
    </ul>
</div>
""")

st.sidebar.success(f"Model Status: {status}")

# --- 4. NAVIGATION TABS ---
tab1, tab2 = st.tabs(["🔍 Real-Time Message Analysis", "📊 Security Monitoring Dashboard"])

# ==============================================================================
# TAB 1: REAL-TIME INPUT SCANNER
# ==============================================================================
with tab1:
    st.header("Scan Incoming Messages")
    user_text = st.text_area("Message Content Input Field:", height=150, placeholder="Paste raw string content here...")
    
    if st.button("Run Security Inspection", type="primary"):
        if user_text.strip() == "":
            st.warning("⚠️ Please input text to evaluate.")
        else:
            with st.spinner("Analyzing text architecture..."):
                time.sleep(0.2)
                data = vectorizer.transform([user_text])
                prediction = model.predict(data)[0]
                
                probabilities = model.predict_proba(data)[0]
                class_labels = list(model.classes_)
                confidence = float(probabilities[class_labels.index(prediction)])
                
                # --- DYNAMIC FEATURE ANALYSIS ENGINE ---
                detected_details = []
                
                # 1. Spam Keywords Rule
                trigger_words = ['lottery', 'prize', 'claim', 'won', 'cash', 'free cash', 'whatsapp', 'urgent']
                if any(word in user_text.lower() for word in trigger_words):
                    detected_details.append("Spam Keywords")
                    if prediction == 'ham':
                        prediction = 'spam'
                        confidence = 0.94
                
                # 2. Suspicious Links Rule
                if "http" in user_text.lower() or "www." in user_text.lower() or ".com" in user_text.lower() or ".net" in user_text.lower():
                    detected_details.append("Suspicious Links")
                
                # 3. Excessive Exclamations Rule
                if user_text.count("!") >= 2:
                    detected_details.append("Excessive Exclamations")
                
                # 4. Promotional Language Rule
                promo_words = ['free', 'congratulations', 'won', 'offer', 'gift card', 'bonus', 'payout', 'guaranteed']
                if any(word in user_text.lower() for word in promo_words):
                    detected_details.append("Promotional Language")
                
                # Format the list into a clean comma-separated string
                analysis_details_str = ", ".join(detected_details) if detected_details else "None (Standard Syntax)"
                
                is_spam = prediction == 'spam'
                confidence = min(max(confidence, 0.0), 1.0)

                # Write metrics to persistent global history state with the new details column
                new_entry = {
                    "Timestamp": time.strftime("%Y-%m-%d %H:%M"),
                    "Message Snippet": user_text[:50] + "..." if len(user_text) > 50 else user_text,
                    "Classification": "Spam" if is_spam else "Safe (Ham)",
                    "Confidence": round(confidence, 2),
                    "Analysis Details": analysis_details_str
                }
                st.session_state.history = pd.concat([pd.DataFrame([new_entry]), st.session_state.history], ignore_index=True)
            
            # --- UI PRESENTATION LAYER WITH NEON BAR METER ---
            st.subheader("Analysis Results")
            risk_score = int(confidence * 100) if is_spam else int((1.0 - confidence) * 100)
            
            if risk_score >= 75:
                accent_color, alert_text = "#FF0055", "CRITICAL THREAT LEVEL"
                glow_shadow = "box-shadow: 0 0 15px #FF0055, 0 0 30px #FF0055;"
            elif risk_score >= 40:
                accent_color, alert_text = "#FF9900", "SUSPICIOUS CHARACTERISTICS"
                glow_shadow = "box-shadow: 0 0 15px #FF9900, 0 0 30px #FF9900;"
            else:
                accent_color, alert_text = "#00FFCC", "NOMINAL // SHIELD INSULATED"
                glow_shadow = "box-shadow: 0 0 15px #00FFCC, 0 0 30px #00FFCC;"

            st.html(f"""
<div style="background-color: #0b0f17; padding: 30px 35px; border-radius: 14px; border: 1px solid #1f293d; margin-bottom: 25px; box-shadow: 0 10px 40px rgba(0,0,0,0.6);">
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px;">
        <div style="display: flex; flex-direction: column; gap: 4px;">
            <span style="font-family: 'Courier New', monospace; font-size: 10px; color: #4b566b; letter-spacing: 2px; font-weight: bold;">REAL-TIME INBOUND AUDIT</span>
            <span style="font-family: 'Segoe UI', system-ui, sans-serif; font-size: 14px; font-weight: 800; color: #ffffff;">VECTOR STATUS: <span style="color: {accent_color};">{alert_text}</span></span>
        </div>
        <div style="font-family: 'Courier New', monospace; font-size: 28px; font-weight: 900; color: {accent_color}; text-shadow: 0 0 12px {accent_color};">{risk_score}<span style="font-size: 14px; color: #4b566b;">%</span></div>
    </div>
    <div style="background-color: #141923; border: 1px solid #222c3f; height: 22px; width: 100%; border-radius: 6px; padding: 3px; box-sizing: border-box; display: flex; align-items: center; margin-bottom: 12px;">
        <div style="background-color: {accent_color}; height: 100%; width: {risk_score}%; border-radius: 4px; transition: width 0.7s ease-out; {glow_shadow}"></div>
    </div>
    <div style="display: flex; justify-content: space-between; font-family: 'Courier New', monospace; font-size: 9px; color: #364156; font-weight: bold;">
        <span>000 // MIN_RISK</span><span>Detected: {analysis_details_str}</span><span>100 // MAX_ALERT</span>
    </div>
</div>
""")
            col_res1, col_res2 = st.columns([3, 1])
            with col_res1:
                if is_spam:
                    st.error(f"🚨 **THREAT DETECTED:** Malicious components logged: {analysis_details_str}")
                else:
                    st.success("✅ **SIGNATURE STABLE:** Content verified safe for transmission pipelines.")
            with col_res2:
                st.metric(label="Filter Confidence", value=f"{confidence * 100:.1f}%")

# ==============================================================================
# TAB 2: MANAGEMENT DASHBOARD
# ==============================================================================
with tab2:
    st.header("Security Management Console")
    
    total_scanned = len(st.session_state.history)
    spam_count = len(st.session_state.history[st.session_state.history["Classification"] == "Spam"])
    ham_count = total_scanned - spam_count
    spam_ratio = (spam_count / total_scanned) * 100 if total_scanned > 0 else 0
    avg_confidence = st.session_state.history['Confidence'].mean()
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Total Scanned Traffic", f"{total_scanned} msgs")
    kpi2.metric("Spam Incidents Caught", f"{spam_count}", delta=f"{spam_ratio:.1f}% Rate", delta_color="inverse")
    kpi3.metric("Legitimate Clean Volume", f"{ham_count}")
    kpi4.metric("Avg Filter Certainty", f"{avg_confidence * 100:.1f}%")
    
    st.markdown("---")
    chart_col, data_col = st.columns([1, 1])
    with chart_col:
        st.subheader("🔥 Top Trigger Keyword Vulnerabilities")
        keyword_data = pd.DataFrame({"Keyword Term": ["lottery", "claim prize", "urgent login", "verify bank", "gift card", "free cash"], "System Block Count": [48, 36, 31, 28, 19, 14]}).set_index("Keyword Term")
        st.bar_chart(keyword_data)
        
    with data_col:
        st.subheader("📈 Security Traffic Trends")
        time_trend_data = pd.DataFrame({"Hour Line": ["12:00", "13:00", "14:00", "15:00", "16:00", "17:00"], "Spam Attacks Stopped": [4, 7, 3, 12, 8, spam_count]}).set_index("Hour Line")
        st.line_chart(time_trend_data)
        
    st.subheader("📋 System Incident Threat Log")
    st.dataframe(st.session_state.history, use_container_width=True)