SELECT *
FROM {{ source('fitconnect', 'users') }}
LIMIT 5
