-- Snowflake DDL & example patterns for AI-assisted inspection workspace
-- NOTE: The AI SQL/Cortex examples below are illustrative. They assume your Snowflake account
-- has Cortex/AI SQL enabled and you have the appropriate privileges.

-- 1) Create a staging table for findings
CREATE OR REPLACE TABLE INSPECTION_FINDINGS (
  property_id NUMBER,
  property_name STRING,
  room_id NUMBER,
  room_name STRING,
  image_filename STRING,
  label STRING,
  score FLOAT,
  notes STRING,
  evaluated_at TIMESTAMP_LTZ DEFAULT current_timestamp()
);

-- 2) Example: Aggregate risk per property
CREATE OR REPLACE VIEW PROPERTY_RISK_SUMMARY AS
SELECT
  property_id,
  property_name,
  COUNT(*) AS total_findings,
  AVG(score) AS avg_score,
  SUM(score) AS total_score,
  MAX(evaluated_at) AS last_evaluated
FROM INSPECTION_FINDINGS
GROUP BY property_id, property_name;

-- 3) Example AI-SQL (illustrative): using a hypothetical AI_CLASSIFY_IMAGE function
-- If your account supports Snowflake Cortex/AI SQL, you might call a built-in UDF like this:
-- SELECT
--   image_filename,
--   AI_CLASSIFY_IMAGE(IMAGE_COLUMN, 'vision-model-id') AS predicted_label
-- FROM IMAGE_TABLE;

-- 4) Example: use embeddings/semantic search to identify similar defects (illustrative)
-- CREATE TABLE IMAGE_EMBEDDINGS AS
-- SELECT
--   image_id,
--   VECTOR_GEN(IMAGE_BYTES) AS embedding
-- FROM IMAGE_TABLE;

-- 5) Streams & Tasks (optional): example to keep PROPERTY_RISK_SUMMARY up-to-date
-- CREATE OR REPLACE TASK REFRESH_PROPERTY_RISK
-- WAREHOUSE = MY_WH
-- SCHEDULE = 'USING CRON 0 * * * * UTC'
-- AS
-- INSERT INTO PROPERTY_RISK_LOG
-- SELECT CURRENT_TIMESTAMP(), * FROM PROPERTY_RISK_SUMMARY;

-- 6) Dynamic Tables (optional): a dynamic table could continuously compute scores
-- CREATE OR REPLACE DYNAMIC TABLE DYN_PROPERTY_RISK AS
-- SELECT property_id, property_name, SUM(score) AS total_score
-- FROM INSPECTION_FINDINGS
-- GROUP BY property_id, property_name;

-- IMPORTANT: Replace the illustrative AI_* function calls with concrete functions provided
-- by Snowflake Cortex in your account. The exact function names and usage may vary and may
-- require enabling feature flags and roles. See your Snowflake account docs for details.
