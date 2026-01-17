-- Migration: Add xai_explanation JSONB columns for xAI-style explanations
-- Date: 2025-01-18
-- Description: Adds dedicated xai_explanation columns to user_segments and personalization_rules
--              tables to store structured xAI explanations (what/why/so_what/recommendation)

-- Add xai_explanation to user_segments
ALTER TABLE user_segments 
ADD COLUMN xai_explanation JSONB DEFAULT NULL;

-- Update comment for reasoning to clarify its purpose
COMMENT ON COLUMN user_segments.reasoning IS 'Brief text summary of segmentation';
COMMENT ON COLUMN user_segments.xai_explanation IS 'Full xAI explanation structure: {what, why, so_what, recommendation}';

-- Add xai_explanation to personalization_rules
ALTER TABLE personalization_rules 
ADD COLUMN xai_explanation JSONB DEFAULT NULL;

-- Update comment for reasoning to clarify its purpose
COMMENT ON COLUMN personalization_rules.reasoning IS 'Brief text summary of rule generation';
COMMENT ON COLUMN personalization_rules.xai_explanation IS 'Full xAI explanation structure: {what, why, so_what, recommendation}';

-- Add GIN index for efficient JSONB queries on xai_explanation
CREATE INDEX idx_user_segments_xai_explanation ON user_segments USING GIN (xai_explanation);
CREATE INDEX idx_personalization_rules_xai_explanation ON personalization_rules USING GIN (xai_explanation);
