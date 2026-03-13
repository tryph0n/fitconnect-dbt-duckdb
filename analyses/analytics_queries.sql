-- FitConnect Analytics Queries
-- Run these against the analytics schema in DuckDB

-- 1. Average number of workouts per user
SELECT
    AVG(number_of_workouts) AS avg_workouts_per_user
FROM analytics.user_workout_summary;

-- 2. Distribution: how many users completed each number of workouts
SELECT
    number_of_workouts,
    COUNT(*) AS user_count
FROM analytics.user_workout_summary
GROUP BY number_of_workouts
ORDER BY number_of_workouts;

-- 3. Top users by total calories burned
SELECT
    first_name,
    last_name,
    number_of_workouts,
    ROUND(total_calories_burned, 1) AS total_calories,
    ROUND(avg_workout_duration, 1) AS avg_duration_min
FROM analytics.user_workout_summary
ORDER BY total_calories_burned DESC;

-- 4. Workout frequency by fitness goal
SELECT
    fitness_goal,
    COUNT(*) AS user_count,
    ROUND(AVG(number_of_workouts), 1) AS avg_workouts,
    ROUND(AVG(total_calories_burned), 1) AS avg_total_calories
FROM analytics.user_workout_summary
GROUP BY fitness_goal
ORDER BY avg_workouts DESC;
