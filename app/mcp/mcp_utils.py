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

