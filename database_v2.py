# database_v2.py — backward-compatible re-exports (use database.py directly)
from database import get_connection, init_database, generate_learner_id, DB_NAME

# Legacy alias
generate_school_id = generate_learner_id
