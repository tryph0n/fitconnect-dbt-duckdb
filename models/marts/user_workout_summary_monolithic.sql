-- Monolithic fact table for analyzing user workout sessions

WITH profiles AS (
    SELECT
        ProfileID AS profile_id,
        UserID AS user_id,
        FirstName AS first_name,
        LastName AS last_name,
        Gender AS gender,
        FitnessGoal AS fitness_goal,
        ActivityLevel AS activity_level
    FROM {{ source('fitconnect', 'profiles') }}
),

workouts AS (
    SELECT
        WorkoutID AS workout_id,
        UserID AS user_id,
        WorkoutDate AS workout_date,
        Duration AS duration,
        CaloriesBurned AS calories_burned,
        Rating AS rating
    FROM {{ source('fitconnect', 'workouts') }}
    WHERE CompletionStatus = 'Completed'
),

user_workout_summary AS (
    SELECT
        user_id,
        MIN(workout_date) AS first_workout_date,
        MAX(workout_date) AS latest_workout_date,
        COUNT(*) AS number_of_workouts,
        COALESCE(SUM(calories_burned), 0) AS total_calories_burned,
        COALESCE(AVG(duration), 0) AS avg_workout_duration,
        COALESCE(AVG(rating), 0) AS avg_rating
    FROM workouts
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
        COALESCE(s.first_workout_date, NULL) AS first_workout_date,
        COALESCE(s.latest_workout_date, NULL) AS latest_workout_date,
        COALESCE(s.number_of_workouts, 0) AS number_of_workouts,
        COALESCE(s.total_calories_burned, 0) AS total_calories_burned,
        COALESCE(s.avg_workout_duration, 0) AS avg_workout_duration,
        COALESCE(s.avg_rating, 0) AS avg_rating
    FROM profiles p
    LEFT JOIN user_workout_summary s ON p.user_id = s.user_id
)

SELECT * FROM final
