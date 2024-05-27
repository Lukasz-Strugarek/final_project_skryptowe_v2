import os
import pickle


def load_profiles():
    if os.path.exists('profiles.pkl'):
        try:
            with open('profiles.pkl', 'rb') as file:
                return pickle.load(file)
        except EOFError:
            return {}
    return {}

def save_profiles(profiles):
    with open('profiles.pkl', 'wb') as file:
        pickle.dump(profiles, file)