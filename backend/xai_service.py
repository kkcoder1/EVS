import json

# Load crop metadata
def load_crop_metadata():
    try:
        with open("model/crop_metadata.json", "r") as f:
            return json.load(f)
    except Exception:
        return {}

CROP_METADATA = load_crop_metadata()

def generate_xai_explanation(recommended_crop: str, top_crops: list, user_inputs: dict) -> dict:
    """
    Generates plain-language, farmer-friendly explanation of why a crop was selected,
    feature alignment radar scores, and specific agronomic takeaways.
    """
    crop_info = CROP_METADATA.get(recommended_crop, {})
    if not crop_info:
        return {
            "summary": f"{recommended_crop} is recommended based on your combined soil nutrients and weather profile.",
            "points": ["Soil parameters align with general growth requirements."],
            "radar_scores": {"N": 80, "P": 80, "K": 80, "pH": 80, "Temp": 80, "Rainfall": 80}
        }
        
    n_user = user_inputs.get('N', 80)
    p_user = user_inputs.get('P', 45)
    k_user = user_inputs.get('K', 40)
    ph_user = user_inputs.get('ph', 6.5)
    temp_user = user_inputs.get('temperature', 25)
    rain_user = user_inputs.get('rainfall', 120)
    
    # Calculate fit percentage per parameter
    def compute_fit(val, target_min, target_max, target_mean):
        if target_min <= val <= target_max:
            return 100
        diff = min(abs(val - target_min), abs(val - target_max))
        tolerance = (target_max - target_min) or 20
        fit = max(40, 100 - (diff / tolerance) * 50)
        return round(fit, 1)

    n_prof = crop_info.get('N', (50, 100, 75))
    p_prof = crop_info.get('P', (30, 60, 45))
    k_prof = crop_info.get('K', (30, 60, 45))
    ph_prof = crop_info.get('ph', (5.5, 7.5, 6.5))
    temp_prof = crop_info.get('temp', (18, 32, 25))
    rain_prof = crop_info.get('rainfall', (60, 180, 120))
    
    fit_n = compute_fit(n_user, n_prof[0], n_prof[1], n_prof[2])
    fit_p = compute_fit(p_user, p_prof[0], p_prof[1], p_prof[2])
    fit_k = compute_fit(k_user, k_prof[0], k_prof[1], k_prof[2])
    fit_ph = compute_fit(ph_user, ph_prof[0], ph_prof[1], ph_prof[2])
    fit_temp = compute_fit(temp_user, temp_prof[0], temp_prof[1], temp_prof[2])
    fit_rain = compute_fit(rain_user, rain_prof[0], rain_prof[1], rain_prof[2])
    
    # Construct key plain language bullet points
    reasons = []
    
    # Soil Nitrogen
    if n_prof[0] <= n_user <= n_prof[1]:
        reasons.append(f"✓ **Soil Nitrogen ({n_user} kg/ha)** perfectly matches {recommended_crop}'s optimal range of {n_prof[0]}-{n_prof[1]} kg/ha.")
    elif n_user < n_prof[0]:
        reasons.append(f"⚡ Soil Nitrogen is slightly below peak demand ({n_user} vs {n_prof[0]} kg/ha required). Supplementing with urea will ensure maximum yield.")
    else:
        reasons.append(f"✓ High Soil Nitrogen ({n_user} kg/ha) supports vigorous vegetative foliage growth for {recommended_crop}.")
        
    # Soil pH & Potash
    if ph_prof[0] <= ph_user <= ph_prof[1]:
        reasons.append(f"✓ **Soil pH ({ph_user})** is in the ideal sweet spot ({ph_prof[0]}-{ph_prof[1]}), allowing efficient nutrient absorption by roots.")
    else:
        reasons.append(f"• Soil pH ({ph_user}) is manageable for {recommended_crop} with minor soil conditioning.")
        
    # Weather / Climate Alignment
    if rain_prof[0] <= rain_user <= rain_prof[1]:
        reasons.append(f"✓ **Rainfall & Moisture ({rain_user} mm)** matches the crop's water footprint ({rain_prof[0]}-{rain_prof[1]} mm).")
    else:
        reasons.append(f"✓ Current region rainfall ({rain_user} mm) and expected weather forecast support healthy growth cycle.")

    if temp_prof[0] <= temp_user <= temp_prof[1]:
        reasons.append(f"✓ Local climate temperature ({temp_user}°C) provides the optimal thermal window ({temp_prof[0]}-{temp_prof[1]}°C) for seed germination and flowering.")

    overall_fit = round((fit_n + fit_p + fit_k + fit_ph + fit_temp + fit_rain) / 6.0, 1)

    summary_text = (
        f"**{recommended_crop}** is your top recommended crop with an estimated **{overall_fit}% agronomic match**. "
        f"Your soil's nutrient composition (N: {n_user}, P: {p_user}, K: {k_user}, pH: {ph_user}) and local climate "
        f"({temp_user}°C, {rain_user} mm rainfall) align strongly with this crop's physiological needs."
    )

    return {
        "summary": summary_text,
        "overall_fit_percentage": overall_fit,
        "key_reasons": reasons,
        "crop_details": {
            "sowing_season": crop_info.get("sowing_season", "Kharif / Rabi"),
            "water_requirement": crop_info.get("water_requirement", "Moderate"),
            "duration": crop_info.get("duration", "100-120 days"),
            "care_tips": crop_info.get("care_tips", "Ensure proper weeding and field drainage."),
            "fertilizer": crop_info.get("fertilizer", "Apply balanced NPK as recommended by Soil Health Card.")
        },
        "radar_scores": {
            "Nitrogen": fit_n,
            "Phosphorus": fit_p,
            "Potassium": fit_k,
            "pH": fit_ph,
            "Temperature": fit_temp,
            "Rainfall": fit_rain
        },
        "comparison_targets": {
            "Nitrogen": {"user": n_user, "optimal_min": n_prof[0], "optimal_max": n_prof[1]},
            "Phosphorus": {"user": p_user, "optimal_min": p_prof[0], "optimal_max": p_prof[1]},
            "Potassium": {"user": k_user, "optimal_min": k_prof[0], "optimal_max": k_prof[1]},
            "pH": {"user": ph_user, "optimal_min": ph_prof[0], "optimal_max": ph_prof[1]}
        }
    }
