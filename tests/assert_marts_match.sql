-- Both user workout marts must return the same rows.
-- The average columns are rounded on both sides to remove floating-point noise.

WITH monolithic AS (
    SELECT
        user_id,
        first_name,
        last_name,
        gender,
        fitness_goal,
        activity_level,
        first_workout_date,
        latest_workout_date,
        number_of_workouts,
        total_calories_burned,
        ROUND(avg_workout_duration, 6) AS avg_workout_duration,
        ROUND(avg_rating, 6) AS avg_rating
    FROM {{ ref('user_workout_summary_monolithic') }}
),

modular AS (
    SELECT
        user_id,
        first_name,
        last_name,
        gender,
        fitness_goal,
        activity_level,
        first_workout_date,
        latest_workout_date,
        number_of_workouts,
        total_calories_burned,
        ROUND(avg_workout_duration, 6) AS avg_workout_duration,
        ROUND(avg_rating, 6) AS avg_rating
    FROM {{ ref('user_workout_summary') }}
),

only_in_monolithic AS (
    SELECT * FROM monolithic
    EXCEPT
    SELECT * FROM modular
),

only_in_modular AS (
    SELECT * FROM modular
    EXCEPT
    SELECT * FROM monolithic
)

SELECT 'only_in_monolithic' AS found_in, * FROM only_in_monolithic
UNION ALL
SELECT 'only_in_modular' AS found_in, * FROM only_in_modular
