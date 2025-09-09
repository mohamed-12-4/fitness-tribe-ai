import json
import firebase_admin
from firebase_admin import credentials, firestore
import os

def _load_data(file_path):
    """
    Load the exercise data from the JSON file path.
    """
    with open(file_path, "r") as file:
        data = json.load(file)
    return data

EXERCISES = _load_data("app/data/exercises.json")
EXERCISE_MAP = {exercise["exerciseId"]: exercise for exercise in EXERCISES}


def initialize_firebase():
    """Initialize Firebase Admin SDK if not already initialized"""
    if not firebase_admin._apps:
        # Try to get Firebase credentials from environment or service account file
        try:
            cred_path = 'app/ghiras-454ed-firebase-adminsdk-fbsvc-88ab2174dc.json'
        
            cred = credentials.Certificate(cred_path)

            firebase_admin.initialize_app(cred)
        except:
            cred_path = '/etc/secrets/ghiras-454ed-firebase-adminsdk-fbsvc-88ab2174dc.json'
        
            cred = credentials.Certificate(cred_path)

            firebase_admin.initialize_app(cred)

    
    return firestore.client()

def get_user_profile(user_id: str):
    """
    Retrieve user profile information from Firestore.
    
    Args:
        user_id: The ID of the user
        
    Returns:
        Dict containing user profile data or None if not found
        
    Raises:
        Exception: If there's an error accessing Firestore
    """
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get the profile document
        profile_ref = (db.collection('users')
                      .document(user_id)
                      .collection('profile')
                      .document('data')
                      .collection('personal_info')
                      .document('current'))
        
        profile_doc = profile_ref.get()
        
        if profile_doc.exists:
            profile_data = profile_doc.to_dict()
            
            # Add metadata
            profile_data['user_id'] = user_id
            profile_data['last_updated'] = profile_doc.update_time.isoformat() if profile_doc.update_time else None
            
            return profile_data
        else:
            return None
            
    except Exception as e:
        raise Exception(f"Error retrieving profile for user {user_id}: {str(e)}")

def list_facts():
    target_muscles = set()
    equipment = set()
    body_parts = set()
    for exercise in EXERCISES:
        target_muscles.update([tnm.lower() for tnm in exercise["targetMuscles"]])
        equipment.update([eq.lower() for eq in exercise["equipments"]])
        body_parts.update([bp.lower() for bp in exercise["bodyParts"]])
    return {
        "targetMuscles": target_muscles,
        "equipment": equipment,
        "bodyParts": body_parts,
    }

def get_exercise_by_id(exercise_id):
    return EXERCISE_MAP.get(exercise_id)

def get_exercises_by_target_muscle(target_muscle):
    target_muscle = target_muscle.lower()
    return [ex for ex in EXERCISES if target_muscle in [tm.lower() for tm in ex["targetMuscles"]]][:20]

def get_user_recent_workouts(user_id: str, limit: int = 10):
    """
    Retrieve user's most recent completed workouts from Firestore.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of workouts to retrieve (default: 10)
        
    Returns:
        List of workout documents ordered from newest to oldest
        
    Raises:
        Exception: If there's an error accessing Firestore
    """
    try:
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get the completed workouts collection reference
        workouts_ref = (db.collection('users')
                       .document(user_id)
                       .collection('exercise')
                       .document('data')
                       .collection('completed_workouts'))
        
        # Query workouts ordered by endTime (newest first)
        # endTime format: "2025-09-07T21:46:08.859144"
        query = workouts_ref.order_by('endTime', direction=firestore.Query.DESCENDING).limit(limit)
        
        # Execute the query
        workout_docs = query.get()
        
        workouts = []
        for doc in workout_docs:
            workout_data = doc.to_dict()
            workout_data['workout_id'] = doc.id
            workout_data['document_path'] = doc.reference.path
            
            # Add formatted timestamps if they exist
            if 'endTime' in workout_data and workout_data['endTime']:
                workout_data['endTime_formatted'] = workout_data['endTime']
                # Also add a more readable format
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(workout_data['endTime'].replace('Z', '+00:00'))
                    workout_data['endTime_readable'] = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    workout_data['endTime_readable'] = workout_data['endTime']
            
            workouts.append(workout_data)
        
        return workouts
    
            
    except Exception:
        raise Exception(f"Error retrieving workouts for user {user_id}:")

def get_user_sleep_sessions(user_id: str, limit: int = 10):
    """
    Retrieve user's sleep logging data from Firestore, ordered by creation time.
    
    Args:
        user_id: The ID of the user
        limit: Maximum number of sleep sessions to retrieve (default: 10)
        
    Returns:
        List of sleep session documents ordered from newest to oldest
        
    Raises:
        Exception: If there's an error accessing Firestore
    """
    try:
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get the sleep sessions collection reference
        sleep_sessions_ref = (db.collection('users')
                             .document(user_id)
                             .collection('sleep')
                             .document('data')
                             .collection('sleep_sessions'))
        
        # Query sleep sessions ordered by createdAt (newest first)
        query = sleep_sessions_ref.order_by('createdAt', direction=firestore.Query.DESCENDING).limit(limit)
        
        # Execute the query
        session_docs = query.get()
        
        sleep_sessions = []
        for doc in session_docs:
            session_data = doc.to_dict()
            
            # Only include specified fields
            filtered_session = {
                'session_id': doc.id,
                'mood': session_data.get('mood'),
                'sleepQuality': session_data.get('sleepQuality'),
                'totalDuration_hours': None
            }
            
            # Convert totalDuration from milliseconds to hours
            total_duration_ms = session_data.get('totalDuration')
            if total_duration_ms is not None:
                try:
                    # Convert milliseconds to hours (1 hour = 3,600,000 ms)
                    filtered_session['totalDuration_hours'] = round(total_duration_ms / 3600000, 2)
                except (ValueError, TypeError):
                    filtered_session['totalDuration_hours'] = None
            
            # Add formatted timestamps if they exist
            if 'createdAt' in session_data and session_data['createdAt']:
                try:
                    from datetime import datetime
                    if hasattr(session_data['createdAt'], 'isoformat'):
                        # If it's a Firestore timestamp
                        filtered_session['createdAt_formatted'] = session_data['createdAt'].isoformat()
                        filtered_session['createdAt_readable'] = session_data['createdAt'].strftime("%B %d, %Y at %I:%M %p")
                    else:
                        # If it's a string timestamp
                        dt = datetime.fromisoformat(str(session_data['createdAt']).replace('Z', '+00:00'))
                        filtered_session['createdAt_formatted'] = session_data['createdAt']
                        filtered_session['createdAt_readable'] = dt.strftime("%B %d, %Y at %I:%M %p")
                except Exception as e:
                    filtered_session['createdAt_formatted'] = str(session_data['createdAt'])
                    filtered_session['createdAt_readable'] = str(session_data['createdAt'])
            
            sleep_sessions.append(filtered_session)
        
        return sleep_sessions
        
            
    except Exception as e:
        raise Exception(f"Error retrieving sleep sessions for user {user_id}: {str(e)}.")

def get_user_food_log_by_days(user_id: str, limit_days: int = 7):
    """
    Retrieve user's logged food data from Firestore, grouped by days using createdAt field.
    
    Args:
        user_id: The ID of the user
        limit_days: Maximum number of days to retrieve (default: 7)
        
    Returns:
        Dict with dates as keys and list of food entries as values, ordered from newest to oldest
        
    Raises:
        Exception: If there's an error accessing Firestore
    """
    try:
        if not user_id or not user_id.strip():
            raise ValueError("User ID cannot be empty")
        
        # Initialize Firebase
        db = initialize_firebase()
        
        # Get the food log entries collection reference
        food_log_ref = (db.collection('users')
                       .document(user_id)
                       .collection('nutrition')
                       .document('data')
                       .collection('food_log_entries'))
        
        # Query food entries ordered by createdAt (newest first)
        # Get more entries to ensure we have enough for the requested days
        query = food_log_ref.order_by('createdAt', direction=firestore.Query.DESCENDING).limit(limit_days * 10)
        
        # Execute the query
        food_docs = query.get()
        
        # Group food entries by date
        food_by_days = {}
        from datetime import datetime
        
        for doc in food_docs:
            food_data = doc.to_dict()
            
            # Extract date from createdAt
            created_at = food_data.get('createdAt')
            if not created_at:
                continue
                
            try:
                # Handle different timestamp formats
                if hasattr(created_at, 'date'):
                    # Firestore timestamp
                    date_key = created_at.date().isoformat()
                else:
                    # String timestamp
                    dt = datetime.fromisoformat(str(created_at).replace('Z', '+00:00'))
                    date_key = dt.date().isoformat()
                
                # Initialize date group if not exists
                if date_key not in food_by_days:
                    food_by_days[date_key] = []
                
                # Add essential food entry data
                nutrition_info = food_data.get('nutritionInfo', {})
                
                food_entry = {
                    'entry_id': doc.id,
                    'food_name': food_data.get('foodName'),
                    'type': food_data.get('mealType'),
                    'quantity': food_data.get('servingSize'),
                    'calories': nutrition_info.get('calories', 0),
                    'protein': nutrition_info.get('protein', 0),
                    'carbohydrates': nutrition_info.get('carbohydrates', 0),
                    'fat': nutrition_info.get('fat', 0),
                    'createdAt': str(created_at)
                }
                
                food_by_days[date_key].append(food_entry)
                
            except Exception as e:
                # Skip entries with invalid timestamps
                continue
        
        # Sort dates (newest first) and limit to requested days
        sorted_dates = sorted(food_by_days.keys(), reverse=True)[:limit_days]
        limited_food_by_days = {date: food_by_days[date] for date in sorted_dates}
        return limited_food_by_days        
    except Exception as e:
        raise Exception(f"Error retrieving food log for user {user_id}: {str(e)}")
