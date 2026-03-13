SELECT
    WorkoutID AS workout_id,
    UserID AS user_id,
    WorkoutDate AS workout_date,
    Duration AS duration,
    CaloriesBurned AS calories_burned,
    Rating AS rating,
    CompletionStatus AS completion_status
FROM {{ source('fitconnect', 'workouts') }}
WHERE CompletionStatus = 'Completed'
