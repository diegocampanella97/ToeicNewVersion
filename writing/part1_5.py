#!/usr/bin/env python3
import os
import json
import random
import time
import openai
import requests
from getpass import getpass
from datetime import datetime

# PIL is optional - will be used if available
try:
    from PIL import Image
except ImportError:
    pass

class TOEICWritingPractice:
    def __init__(self):
        self.api_key = None
        self.client = None
        self.scenes = [
            "Store",
            "Park",
            "Office",
            "Bank",
            "Restaurant",
            "Airport",
            "Library",
            "School",
            "Hospital",
            "Train station"
        ]
        self.word_types = [
            "Noun",
            "Preposition",
            "Verb",
            "Coordinating conjunction",
            "Adjective",
            "Subordinating conjunction",
            "Adverb"
        ]
        self.history_file = "part1_5_history.json"
        self.images_dir = "toeic_images"
        self.history = self.load_history()
        
        # Create images directory if it doesn't exist
        if not os.path.exists(self.images_dir):
            os.makedirs(self.images_dir)
        
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"sessions": [], "total_exercises": 0}
        return {"sessions": [], "total_exercises": 0}
    
    def save_history(self):
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def setup_api(self):
        # Check if API key is already set in environment
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
        if not self.api_key:
            print("\nOpenAI API key not found in environment variables.")
            self.api_key = getpass("Please enter your OpenAI API key: ")
            # Ask if user wants to save the API key to environment
            save_key = input("Would you like to save this API key for future sessions? (y/n): ").lower()
            if save_key == 'y':
                with open(os.path.expanduser("~/.bashrc"), "a") as f:
                    f.write(f'\nexport OPENAI_API_KEY="{self.api_key}"\n')
                print("API key saved to ~/.bashrc. Please restart your terminal or run 'source ~/.bashrc' to apply.")
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            print("API connection established successfully!")
            return True
        except Exception as e:
            print(f"Error setting up OpenAI API: {e}")
            return False
    
    def generate_image_description(self, scene=None):
        if not scene:
            scene = random.choice(self.scenes)
        
        prompt = f"""
        Generate a detailed description of a scene in a {scene} for a TOEIC Writing practice exercise.
        The description should be vivid and include people, objects, and actions that would be visible in a photograph.
        The scene should be suitable for a TOEIC Writing test where students need to write a sentence about the image.
        
        Format the response as a JSON object with these fields:
        - scene_title: A brief title for the scene
        - scene_description: A detailed description of what would be visible in the photograph (150-200 words)
        - scene_type: The type of scene (e.g., {scene})
        - suggested_sentence: An example of a good sentence that describes the scene
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response content as JSON
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, try to extract information manually
                content = response.choices[0].message.content
                print("Warning: Could not parse response as JSON. Using fallback method.")
                
                # Create a basic structure for the result
                fallback_result = {
                    "scene_title": f"Scene at a {scene}",
                    "scene_description": "Could not generate a proper scene description. Please try again.",
                    "scene_type": scene,
                    "suggested_sentence": "This is an example sentence about the scene."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error generating scene description: {e}")
            return None
            
    def generate_image(self, scene_description):
        """
        Generate an image using OpenAI's DALL-E based on the scene description.
        Returns the path to the saved image file.
        """
        # Create a simplified prompt for DALL-E that focuses on realism
        prompt = f"A realistic photograph of {scene_description['scene_title']}. The scene shows {scene_description['scene_description'][:200]}..."
        
        try:
            # Generate timestamp for unique filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_filename = f"{timestamp}_{scene_description['scene_type'].lower().replace(' ', '_')}.png"
            image_path = os.path.join(self.images_dir, image_filename)
            
            print("Generating image... This may take a moment.")
            
            # Call DALL-E API to generate the image
            response = self.client.images.generate(
                model="dall-e-3",  # Using DALL-E 3 for more realistic images
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )
            
            # Get the image URL from the response
            image_url = response.data[0].url
            
            # Download and save the image
            import requests
            image_data = requests.get(image_url).content
            with open(image_path, 'wb') as f:
                f.write(image_data)
                
            print(f"Image saved to {image_path}")
            return image_path
            
        except Exception as e:
            print(f"Error generating image: {e}")
            print("Continuing without image...")
            return None
    
    def generate_word_pair(self):
        # Select two different word types
        word_types = random.sample(self.word_types, 2)
        
        prompt = f"""
        Generate a pair of words for a TOEIC Writing practice exercise.
        The words should be:
        1. A {word_types[0]}
        2. A {word_types[1]}
        
        The words should be common English words that could be used to describe a scene in a {random.choice(self.scenes)}.
        If providing a noun, use the singular form.
        If providing a verb, use the base form.
        
        Format the response as a JSON object with these fields:
        - word1: The first word
        - word1_type: The type of the first word ({word_types[0]})
        - word2: The second word
        - word2_type: The type of the second word ({word_types[1]})
        - example_usage: A brief example of how these words might be used in a sentence
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response content as JSON
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, create a fallback
                fallback_result = {
                    "word1": "customer" if word_types[0] == "Noun" else "happy" if word_types[0] == "Adjective" else "quickly",
                    "word1_type": word_types[0],
                    "word2": "purchase" if word_types[1] == "Verb" else "in" if word_types[1] == "Preposition" else "store",
                    "word2_type": word_types[1],
                    "example_usage": "The customer made a purchase in the store."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error generating word pair: {e}")
            return None
    
    def evaluate_sentence(self, sentence, word1, word2, scene_description):
        prompt = f"""
        Evaluate the following sentence written for a TOEIC Writing practice exercise:
        
        Sentence: "{sentence}"
        
        The sentence should use these two words correctly: "{word1}" and "{word2}"
        
        The sentence should describe this scene:
        {scene_description}
        
        Please evaluate the sentence based on:
        1. Grammar and structure
        2. Correct usage of the provided words
        3. Relevance to the scene
        4. Overall clarity and effectiveness
        
        Provide specific suggestions for improvement and an improved version of the sentence.
        
        Format the response as a JSON object with these fields:
        - grammar_score: A score from 1-5 for grammar correctness
        - word_usage_score: A score from 1-5 for correct usage of the provided words
        - relevance_score: A score from 1-5 for relevance to the scene
        - overall_score: An overall score from 1-5
        - feedback: Specific feedback on the sentence
        - improved_sentence: An improved version of the sentence
        - explanation: An explanation of the improvements made
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse the response content as JSON
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, create a fallback
                fallback_result = {
                    "grammar_score": 3,
                    "word_usage_score": 3,
                    "relevance_score": 3,
                    "overall_score": 3,
                    "feedback": "Unable to provide detailed feedback. Please try again.",
                    "improved_sentence": sentence,
                    "explanation": "Unable to provide an explanation. Please try again."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error evaluating sentence: {e}")
            return None
    
    def display_scene(self, scene):
        print("\n" + "=" * 80)
        print(f"Scene Type: {scene['scene_type']}\n")
        print(f"Title: {scene['scene_title']}\n")
        print("Scene Description:")
        print(scene['scene_description'])
        
        # Check if the scene has an associated image path
        if 'image_path' in scene and scene['image_path']:
            print(f"\nImage generated and saved to: {scene['image_path']}")
            
            # Try to display the image if running in a compatible environment
            try:
                # Try to use PIL to display the image if available
                from PIL import Image
                print("\nAttempting to open the image...")
                Image.open(scene['image_path']).show()
            except (ImportError, Exception) as e:
                print(f"\nTo view the image, open the file at: {scene['image_path']}")
        
        print("\n" + "=" * 80)
    
    def display_word_pair(self, word_pair):
        print(f"\nWord 1: {word_pair['word1']} ({word_pair['word1_type']})")
        print(f"Word 2: {word_pair['word2']} ({word_pair['word2_type']})")
        print("\nWrite a sentence about the scene using BOTH words.")
    
    def display_evaluation(self, evaluation):
        print("\n" + "-" * 40)
        print("Evaluation:")
        print(f"Grammar: {evaluation['grammar_score']}/5")
        print(f"Word Usage: {evaluation['word_usage_score']}/5")
        print(f"Relevance: {evaluation['relevance_score']}/5")
        print(f"Overall: {evaluation['overall_score']}/5")
        print("\nFeedback:")
        print(evaluation['feedback'])
        print("\nImproved Sentence:")
        print(evaluation['improved_sentence'])
        print("\nExplanation:")
        print(evaluation['explanation'])
        print("-" * 40)
    
    def practice_session(self, num_exercises=5, scene_type=None):
        if not self.client and not self.setup_api():
            return
        
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "exercises": [],
            "average_score": 0
        }
        
        total_score = 0
        completed_exercises = 0
        
        for i in range(num_exercises):
            # For each iteration, randomly choose scene type if not specified
            current_scene_type = scene_type if scene_type else random.choice(self.scenes)
            
            print(f"\nGenerating exercise {i+1}/{num_exercises}...")
            scene = self.generate_image_description(current_scene_type)
            
            if not scene:
                print("Failed to generate scene. Skipping...")
                continue
                
            # Generate image for the scene
            print("Generating an image for this scene...")
            image_path = self.generate_image(scene)
            if image_path:
                scene['image_path'] = image_path
            
            word_pair = self.generate_word_pair()
            
            if not word_pair:
                print("Failed to generate word pair. Skipping...")
                continue
            
            exercise_result = {
                "scene_title": scene['scene_title'],
                "scene_type": scene['scene_type'],
                "word1": word_pair['word1'],
                "word1_type": word_pair['word1_type'],
                "word2": word_pair['word2'],
                "word2_type": word_pair['word2_type']
            }
            
            # Add image path to exercise result if available
            if 'image_path' in scene:
                exercise_result['image_path'] = scene['image_path']
            
            self.display_scene(scene)
            self.display_word_pair(word_pair)
            
            # Get user sentence
            user_sentence = input("\nYour sentence: ")
            
            if user_sentence.lower() == 'q':
                print("\nSession ended early.")
                break
            
            if not user_sentence.strip():
                print("No sentence provided. Skipping evaluation.")
                continue
            
            # Evaluate the sentence
            evaluation = self.evaluate_sentence(user_sentence, word_pair['word1'], word_pair['word2'], scene['scene_description'])
            
            if not evaluation:
                print("Failed to evaluate sentence. Skipping...")
                continue
            
            self.display_evaluation(evaluation)
            
            # Record result
            exercise_result.update({
                "user_sentence": user_sentence,
                "grammar_score": evaluation['grammar_score'],
                "word_usage_score": evaluation['word_usage_score'],
                "relevance_score": evaluation['relevance_score'],
                "overall_score": evaluation['overall_score'],
                "improved_sentence": evaluation['improved_sentence']
            })
            
            # Add exercise result to session
            session['exercises'].append(exercise_result)
            
            # Update total score
            total_score += evaluation['overall_score']
            completed_exercises += 1
            
            # Pause between exercises
            if i < num_exercises - 1:
                input("\nPress Enter for the next exercise...")
        
        # Calculate average score
        if completed_exercises > 0:
            session['average_score'] = total_score / completed_exercises
        
        # Update history
        self.history['sessions'].append(session)
        self.history['total_exercises'] += completed_exercises
        self.save_history()
        
        # Show session summary
        print("\n" + "=" * 80)
        print(f"Session Summary: {completed_exercises} exercises completed")
        if completed_exercises > 0:
            print(f"Average Score: {session['average_score']:.1f}/5")
        print("=" * 80)
    
    def show_stats(self):
        print("\n" + "=" * 80)
        print("TOEIC Writing Practice Statistics")
        print("=" * 80)
        
        if not self.history['sessions']:
            print("No practice sessions recorded yet.")
            return
        
        # Overall stats
        total_sessions = len(self.history['sessions'])
        total_exercises = self.history['total_exercises']
        
        if total_exercises > 0:
            # Calculate overall average score
            overall_score = sum(session['average_score'] * len(session['exercises']) for session in self.history['sessions']) / total_exercises
            print(f"Overall Average Score: {overall_score:.1f}/5")
        
        print(f"Total Sessions: {total_sessions}")
        print(f"Total Exercises Completed: {total_exercises}")
        
        # Stats by scene type
        scene_type_stats = {}
        for session in self.history['sessions']:
            for exercise in session['exercises']:
                s_type = exercise['scene_type']
                if s_type not in scene_type_stats:
                    scene_type_stats[s_type] = {'total_score': 0, 'count': 0}
                
                scene_type_stats[s_type]['total_score'] += exercise['overall_score']
                scene_type_stats[s_type]['count'] += 1
        
        print("\nPerformance by Scene Type:")
        for s_type, stats in scene_type_stats.items():
            if stats['count'] > 0:
                avg_score = stats['total_score'] / stats['count']
                print(f"{s_type}: {avg_score:.1f}/5 ({stats['count']} exercises)")
        
        # Stats by word types
        word_type_stats = {}
        for session in self.history['sessions']:
            for exercise in session['exercises']:
                word1_type = exercise['word1_type']
                word2_type = exercise['word2_type']
                
                for w_type in [word1_type, word2_type]:
                    if w_type not in word_type_stats:
                        word_type_stats[w_type] = {'total_score': 0, 'count': 0}
                    
                    word_type_stats[w_type]['total_score'] += exercise['word_usage_score']
                    word_type_stats[w_type]['count'] += 1
        
        print("\nPerformance by Word Type:")
        for w_type, stats in word_type_stats.items():
            if stats['count'] > 0:
                avg_score = stats['total_score'] / stats['count']
                print(f"{w_type}: {avg_score:.1f}/5 ({stats['count']} occurrences)")
        
        # Recent sessions
        print("\nRecent Sessions:")
        recent_sessions = self.history['sessions'][-5:] if len(self.history['sessions']) > 5 else self.history['sessions']
        recent_sessions.reverse()  # Show most recent first
        
        for i, session in enumerate(recent_sessions):
            exercises_count = len(session['exercises'])
            if exercises_count > 0:
                print(f"{i+1}. {session['date']}: {exercises_count} exercises, Average Score: {session['average_score']:.1f}/5")
            else:
                print(f"{i+1}. {session['date']}: No exercises completed")
        
        print("=" * 80)


def main():
    practice = TOEICWritingPractice()
    
    while True:
        print("\n" + "=" * 80)
        print("TOEIC Writing Practice (Questions 1-5)")
        print("=" * 80)
        print("1. Start a practice session")
        print("2. View statistics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            # Ask for number of exercises
            while True:
                try:
                    num_exercises = int(input("\nHow many exercises would you like to practice? (1-10, default: 5): ") or "5")
                    if 1 <= num_exercises <= 10:
                        break
                    print("Please enter a number between 1 and 10.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Ask for scene type preference
            print("\nScene type:")
            print("1. Random (default)")
            for i, scene in enumerate(practice.scenes):
                print(f"{i+2}. {scene}")
            
            scene_choice = input(f"\nEnter your choice (1-{len(practice.scenes)+1}): ") or "1"
            scene_type = None
            if scene_choice != "1" and scene_choice.isdigit():
                scene_idx = int(scene_choice) - 2
                if 0 <= scene_idx < len(practice.scenes):
                    scene_type = practice.scenes[scene_idx]
            
            # Start practice session
            practice.practice_session(num_exercises, scene_type)
            
        elif choice == '2':
            practice.show_stats()
            
        elif choice == '3':
            print("\nThank you for practicing TOEIC Writing!")
            break
            
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()