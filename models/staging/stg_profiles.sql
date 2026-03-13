SELECT
    ProfileID AS profile_id,
    UserID AS user_id,
    FirstName AS first_name,
    LastName AS last_name,
    BirthDate AS birth_date,
    Gender AS gender,
    Height AS height,
    CurrentWeight AS current_weight,
    TargetWeight AS target_weight,
    FitnessGoal AS fitness_goal,
    ActivityLevel AS activity_level
FROM {{ source('fitconnect', 'profiles') }}
