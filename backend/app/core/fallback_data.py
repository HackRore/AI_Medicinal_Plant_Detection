# Comprehensive Plant Fallback Data for PlantoAI Production
# Unified mapping for ML predictions and API details

PLANT_FALLBACK = [
    {
        "id": 1, 
        "common_name": "Aloevera", 
        "species_name": "Aloevera", # Matches ML class name
        "common_names": {"en": "Aloevera", "hi": "Kumari", "ta": "Kattralai", "te": "Kalabanda", "bn": "Ghritakumari"},
        "scientific_classification": "Kingdom: Plantae, Family: Asphodelaceae, Genus: Aloe, Species: A. vera",
        "description": "Succulent plant with powerful healing gel used worldwide in medicine and cosmetics.", 
        "image_url": "https://images.unsplash.com/photo-1596541223130-5d31a57dd071?q=80&w=800&auto=format&fit=crop",
        "medicinal_properties": [{"ailment": "Skin Burns", "usage": "Apply fresh gel directly", "preparation": "Fresh gel", "dosage": "As needed", "precautions": "None"}]
    },
    {
        "id": 2, 
        "common_name": "Neem", 
        "species_name": "Neem", # Matches ML class name
        "common_names": {"en": "Neem", "hi": "Nimba", "ta": "Veppa", "te": "Vepa", "bn": "Nim"},
        "scientific_classification": "Kingdom: Plantae, Family: Meliaceae, Genus: Azadirachta, Species: A. indica",
        "description": "The village pharmacy of India — every part has documented medicinal value.", 
        "image_url": "https://images.unsplash.com/photo-1628102431508-32f228cb61ed?q=80&w=800&auto=format&fit=crop",
        "medicinal_properties": [{"ailment": "Infections", "usage": "Apply leaf paste", "preparation": "Crushed leaves", "dosage": "Twice daily", "precautions": "Avoid pregnancy"}]
    },
    {
        "id": 3, 
        "common_name": "Tulsi", 
        "species_name": "Tulsi", # Matches ML class name
        "common_names": {"en": "Tulsi", "hi": "Tulasi", "ta": "Thulasi", "te": "Tulasi", "bn": "Tulsi"},
        "scientific_classification": "Kingdom: Plantae, Family: Lamiaceae, Genus: Ocimum, Species: O. tenuiflorum",
        "description": "Queen of herbs in Ayurveda — sacred, aromatic, and clinically proven adaptogen.", 
        "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?q=80&w=800&auto=format&fit=crop",
        "medicinal_properties": [{"ailment": "Cough & Cold", "usage": "Drink as tea", "preparation": "Boiled leaves", "dosage": "1 cup", "precautions": "None"}]
    },
    {"id": 4, "common_name": "Amla", "species_name": "Amla", "common_names": {"en": "Amla", "hi": "Amalaki"}, "description": "High Vitamin C fruit used for immunity and hair health.", "image_url": "https://images.unsplash.com/photo-1606830732731-97b5e4344449?q=80&w=800&auto=format&fit=crop"},
    {"id": 5, "common_name": "Ashwagandha", "species_name": "Ashwagandha", "common_names": {"en": "Ashwagandha", "hi": "Ashwagandha"}, "description": "Powerful adaptogen for stress and stamina.", "image_url": "https://images.unsplash.com/photo-1611073114324-4c1bb38053f3?q=80&w=800&auto=format&fit=crop"},
    {"id": 6, "common_name": "Giloy", "species_name": "Amruthaballi", "common_names": {"en": "Giloy", "hi": "Guduchi"}, "description": "Immune booster and fever treatment.", "image_url": "https://images.unsplash.com/photo-1601641772186-538be2383861?q=80&w=800&auto=format&fit=crop"},
    {"id": 7, "common_name": "Turmeric", "species_name": "Turmeric", "common_names": {"en": "Turmeric", "hi": "Haridra"}, "description": "Anti-inflammatory and antioxidant powerhouse.", "image_url": "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?q=80&w=800&auto=format&fit=crop"},
    {"id": 8, "common_name": "Brahmi", "species_name": "Bhrami", "common_names": {"en": "Brahmi", "hi": "Brahmi"}, "description": "Cognitive booster and memory enhancer.", "image_url": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?q=80&w=800&auto=format&fit=crop"},
    {"id": 9, "common_name": "Moringa", "species_name": "Drumstick", "common_names": {"en": "Moringa", "hi": "Shigru"}, "description": "The miracle tree, highly nutrient-dense.", "image_url": "https://images.unsplash.com/photo-1596461404969-9ae70f2830c1?q=80&w=800&auto=format&fit=crop"},
    {"id": 10, "common_name": "Ginger", "species_name": "Ginger", "common_names": {"en": "Ginger", "hi": "Shunthi"}, "description": "Nausea, cold, and digestion aid.", "image_url": "https://images.unsplash.com/photo-1615485500704-8e990f9900f7?q=80&w=800&auto=format&fit=crop"},
    {"id": 11, "common_name": "Hibiscus", "species_name": "Hibiscus", "common_names": {"en": "Hibiscus", "hi": "Japa"}, "description": "Hair growth and blood pressure support.", "image_url": "https://images.unsplash.com/photo-1596541223130-5d31a57dd071?q=80&w=800&auto=format&fit=crop"},
    {"id": 12, "common_name": "Fenugreek", "species_name": "Trigonella_foenum-graecum", "common_names": {"en": "Fenugreek", "hi": "Methi"}, "description": "Diabetes and cholesterol management.", "image_url": "https://images.unsplash.com/photo-1628102431508-32f228cb61ed?q=80&w=800&auto=format&fit=crop"},
    {"id": 13, "common_name": "Curry Leaves", "species_name": "Curry", "common_names": {"en": "Curry Leaves", "hi": "Meetha Neem"}, "description": "Digestive aid and hair health support.", "image_url": "https://images.unsplash.com/photo-1628102431508-32f228cb61ed?q=80&w=800&auto=format&fit=crop"},
    {"id": 14, "common_name": "Lemongrass", "species_name": "Lemongrass", "common_names": {"en": "Lemongrass", "hi": "Bhustrina"}, "description": "Calming tea for anxiety and fever.", "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?q=80&w=800&auto=format&fit=crop"},
    {"id": 15, "common_name": "Peppermint", "species_name": "Mint", "common_names": {"en": "Peppermint", "hi": "Pudina"}, "description": "IBS and headache relief.", "image_url": "https://images.unsplash.com/photo-1615485290382-441e4d049cb5?q=80&w=800&auto=format&fit=crop"},
]
