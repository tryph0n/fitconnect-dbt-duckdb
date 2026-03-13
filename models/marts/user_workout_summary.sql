-- User workout summary built on top of staging models

WITH workout_stats AS (
    SELECT
        user_id,
        MIN(workout_date) AS first_workout_date,
        MAX(workout_date) AS latest_workout_date,
        COUNT(*) AS number_of_workouts,
        COALESCE(SUM(calories_burned), 0) AS total_calories_burned,
        COALESCE(AVG(duration), 0) AS avg_workout_duration,
        COALESCE(AVG(rating), 0) AS avg_rating
    FROM {{ ref('stg_workouts') }}
    GROUP BY user_id
),

final AS (
    SELECT
        p.user_id,
        p.first_name,
        p.last_name,
        p.gender,
        p.fitness_goal,
        p.activity_level,
        COALESCE(w.first_workout_date, NULL) AS first_workout_date,
        COALESCE(w.latest_workout_date, NULL) AS latest_workout_date,
        COALESCE(w.number_of_workouts, 0) AS number_of_workouts,
        COALESCE(w.total_calories_burned, 0) AS total_calories_burned,
        COALESCE(w.avg_workout_duration, 0) AS avg_workout_duration,
        COALESCE(w.avg_rating, 0) AS avg_rating
    FROM {{ ref('stg_profiles') }} p
    LEFT JOIN workout_stats w ON p.user_id = w.user_id
)

SELECT * FROM final
