-- PlantoAI Persistent Memory Schema
-- Phase 4: Feedback Loop

-- Table for storing all neural predictions
CREATE TABLE IF NOT EXISTS predictions (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    image_hash text,
    predicted_species text,
    confidence float,
    gate_score float,
    meta jsonb,
    created_at timestamptz DEFAULT now()
);

-- Table for storing user-submitted corrections
CREATE TABLE IF NOT EXISTS corrections (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id uuid REFERENCES predictions(id) ON DELETE CASCADE,
    correct_species text,
    user_reported boolean DEFAULT true,
    created_at timestamptz DEFAULT now()
);

-- Index for fast lookup and stats
CREATE INDEX IF NOT EXISTS idx_predictions_species ON predictions(predicted_species);
CREATE INDEX IF NOT EXISTS idx_corrections_prediction_id ON corrections(prediction_id);
