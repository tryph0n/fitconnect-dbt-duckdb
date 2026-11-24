-- Connection check: read a few rows from the PostgreSQL source, without e-mail or password columns
SELECT UserID, Username, JoinDate
FROM {{ source('fitconnect', 'users') }}
LIMIT 5
