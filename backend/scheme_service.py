# Government schemes database for Indian agriculture
SCHEMES_DATABASE = [
    {
        "id": "pm-kisan",
        "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
        "type": "Central Government Direct Benefit Transfer",
        "eligible_crops": ["All Crops"],
        "benefit": "₹6,000 per year directly transferred into farmer bank accounts in 3 equal installments of ₹2,000.",
        "eligibility": "All landholding farmers families across India holding cultivable land.",
        "documents": "Aadhaar card, Bank Account linked with Aadhaar, Land ownership records / Khasra Khatoni.",
        "link": "https://pmkisan.gov.in"
    },
    {
        "id": "pmfby",
        "name": "PMFBY (Pradhan Mantri Fasal Bima Yojana)",
        "type": "Crop Insurance & Financial Support",
        "eligible_crops": ["Rice", "Wheat", "Maize", "Cotton", "Chickpea", "Sugarcane", "Pigeonpeas", "Mungbean", "Blackgram", "Jute"],
        "benefit": "Comprehensive crop insurance cover against yield loss due to non-preventable natural risks (drought, flood, pest attack). Maximum premium paid by farmer is only 1.5% for Rabi, 2% for Kharif crops, and 5% for commercial crops.",
        "eligibility": "All farmers including sharecroppers and tenant farmers growing notified crops in notified areas.",
        "documents": "Land possession certificate / tenancy agreement, Proposal form, Bank account details, Sowing certificate.",
        "link": "https://pmfby.gov.in"
    },
    {
        "id": "pdmc",
        "name": "Per Drop More Crop (Micro Irrigation Scheme - PMKSY)",
        "type": "Subsidy on Drip & Sprinkler Systems",
        "eligible_crops": ["Sugarcane", "Banana", "Pomegranate", "Papaya", "Cotton", "Maize", "Watermelon", "Muskmelon", "Orange / Citrus", "Coffee"],
        "benefit": "Up to 55% subsidy for Small & Marginal farmers and 45% for Other farmers for installing Drip Irrigation and Sprinkler systems.",
        "eligibility": "Farmers owning land with an assured water source.",
        "documents": "Land registration document, Aadhaar card, Bank passbook, Soil & Water test report.",
        "link": "https://pmksy.gov.in"
    },
    {
        "id": "shc",
        "name": "Soil Health Card Scheme",
        "type": "Free Soil Testing & Advisory",
        "eligible_crops": ["All Crops"],
        "benefit": "Free soil test analysis and custom recommendation card for 12 key parameters (N, P, K, S, Zn, Fe, Cu, Mn, Bo, pH, EC, OC) issued every 2 years.",
        "eligibility": "All farmers across India.",
        "documents": "Farmer registration ID or Aadhaar number.",
        "link": "https://soilhealth.dac.gov.in"
    },
    {
        "id": "smam",
        "name": "Sub-Mission on Agricultural Mechanization (SMAM)",
        "type": "Farm Machinery & Equipment Subsidy",
        "eligible_crops": ["Wheat", "Rice", "Maize", "Sugarcane", "Cotton", "Chickpea"],
        "benefit": "40% to 50% subsidy on purchase of agricultural machinery (Tractors, Rotavators, Power Tillers, Seed Drills, Combine Harvesters) or hiring via Custom Hiring Centres (CHC).",
        "eligibility": "Individual farmers, Farmer Producer Organizations (FPOs), Cooperatives.",
        "documents": "Aadhaar card, Bank passbook, Land records, Passport photo.",
        "link": "https://agrimachinery.nic.in"
    },
    {
        "id": "nfsm",
        "name": "National Food Security Mission (NFSM - Pulses & Coarse Cereals)",
        "type": "Demonstration & High-Yield Seed Subsidy",
        "eligible_crops": ["Chickpea", "Pigeonpeas (Arhar)", "Mungbean", "Blackgram (Urad)", "Lentil (Masoor)", "Maize (Corn)", "Wheat", "Rice"],
        "benefit": "Free distribution of High Yielding Variety (HYV) seed minikits, 50% subsidy on bio-fertilizers, micronutrients, and plant protection equipment.",
        "eligibility": "Farmers cultivating pulse and cereal crops in identified NFSM districts.",
        "documents": "Aadhaar card, Land record / Khasra number.",
        "link": "https://nfsm.gov.in"
    },
    {
        "id": "nhm",
        "name": "Mission for Integrated Development of Horticulture (MIDH / NHM)",
        "type": "Horticulture Plantation Subsidy",
        "eligible_crops": ["Mango", "Banana", "Pomegranate", "Apple", "Orange / Citrus", "Papaya", "Coconut"],
        "benefit": "40% to 50% financial assistance for establishing new orchards, protected cultivation (polyhouses/shade nets), and post-harvest cold storage.",
        "eligibility": "Individual horticulturists, SHGs, FPOs.",
        "documents": "Land ownership proof, Project report for orchard establishment.",
        "link": "https://midh.gov.in"
    }
]

def get_matching_schemes(crop_name: str, location_state: str = None) -> list:
    """
    Returns list of government schemes relevant to the recommended crop.
    """
    matched = []
    crop_clean = crop_name.strip()
    
    for scheme in SCHEMES_DATABASE:
        crops = scheme["eligible_crops"]
        if "All Crops" in crops or any(crop_clean.lower() in c.lower() for c in crops):
            matched.append(scheme)
            
    return matched
