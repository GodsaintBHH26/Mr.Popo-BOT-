
MEMBERS_TABLE = "member-scores"

USER_ID = "id"
CREATED_AT = "created_at"
SCORE = "score"
ROLE = "role"

# Query to create a new user entry to the database
CREATE_USER_QUERY = f"""
INSERT INTO "{MEMBERS_TABLE}" ({USER_ID}, {CREATED_AT}, {SCORE}, {ROLE})
VALUES ($1, NOW(), $2, $3)
"""

# Query to fetch the user scores from the database
GET_USER_QUERY = f"""
SELECT * FROM "{MEMBERS_TABLE}" WHERE {USER_ID}=$1
"""

# Query to update the user scores
UPDATE_SCORE_QUERY = f"""
UPDATE "{MEMBERS_TABLE}" 
SET {SCORE}=$1, {ROLE}=$2
WHERE {USER_ID}=$3
"""
