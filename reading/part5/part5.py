#!/usr/bin/env python3
import os
import json
import random
import time
import openai
from getpass import getpass
from datetime import datetime

class TOEICPractice:
    def __init__(self):
        self.api_key = None
        self.client = None
        self.topics = [
            "Office issues",
            "Financial issues",
            "Sales and marketing",
            "Business transactions",
            "Transportation",
            "Tourism",
            "Entertainment and dining out",
            "Schedules"
        ]
        self.history_file = "part5_history.json"
        self.history = self.load_history()
        
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"sessions": [], "total_correct": 0, "total_questions": 0}
        return {"sessions": [], "total_correct": 0, "total_questions": 0}
    
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
    
    def generate_question(self, topic=None):
        if not topic:
            topic = random.choice(self.topics)
        
        prompt = f"""
        Generate a TOEIC Part 5 practice question (Incomplete Sentences) on the topic of {topic}.
        
        The question should be a single sentence with one blank, and provide four options (A, B, C, D) to fill in the blank.
        Only ONE option should be correct. Include an explanation of why the correct answer is right and why the others are wrong.
        
        Format the response as a JSON object with these fields:
        - sentence: The incomplete sentence with a blank indicated by "___"
        - options: An array of 4 options (A, B, C, D)
        - correct_answer: The letter of the correct option (A, B, C, or D)
        - explanation: A detailed explanation of the correct answer
        - topic: The topic of the question
        
        Make sure the question tests one of these skills:
        - Vocabulary (similar words with different meanings, phrasal verbs)
        - Word forms (noun, pronoun, verb, adjective, adverb, infinitive, gerund)
        - Grammar (subject, verb, object, complement, preposition, adjective)
        
        The difficulty should be appropriate for TOEIC test takers (intermediate to advanced English).
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}]
                # Removed response_format parameter as it might not be supported
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
                    "sentence": "Could not parse the question properly.",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "A",
                    "explanation": "Please try again.",
                    "topic": topic
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error generating question: {e}")
            return None
    
    def display_question(self, question):
        print("\n" + "=" * 80)
        print(f"Topic: {question['topic']}\n")
        print(question['sentence'])
        print("\nOptions:")
        for i, option in enumerate(['A', 'B', 'C', 'D']):
            print(f"{option}. {question['options'][i]}")
        print("=" * 80)
    
    def practice_session(self, num_questions=5, topic=None):
        if not self.client and not self.setup_api():
            return
        
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "questions": [],
            "correct": 0,
            "total": num_questions
        }
        
        for i in range(num_questions):
            print(f"\nGenerating question {i+1}/{num_questions}...")
            question = self.generate_question(topic)
            
            if not question:
                print("Failed to generate question. Skipping...")
                continue
            
            self.display_question(question)
            
            # Get user answer
            while True:
                user_answer = input("\nYour answer (A/B/C/D or 'q' to quit): ").upper()
                if user_answer in ['A', 'B', 'C', 'D', 'Q']:
                    break
                print("Invalid input. Please enter A, B, C, D, or Q.")
            
            if user_answer == 'Q':
                print("\nSession ended early.")
                break
            
            # Check answer
            is_correct = user_answer == question['correct_answer']
            result = "Correct!" if is_correct else "Incorrect!"
            
            print(f"\n{result} The correct answer is {question['correct_answer']}.")
            print(f"\nExplanation: {question['explanation']}")
            
            # Record result
            if is_correct:
                session['correct'] += 1
            
            session['questions'].append({
                "sentence": question['sentence'],
                "user_answer": user_answer,
                "correct_answer": question['correct_answer'],
                "is_correct": is_correct,
                "topic": question['topic']
            })
            
            # Pause between questions
            if i < num_questions - 1:
                input("\nPress Enter for the next question...")
        
        # Update history
        self.history['sessions'].append(session)
        self.history['total_correct'] += session['correct']
        self.history['total_questions'] += len(session['questions'])
        self.save_history()
        
        # Show session summary
        print("\n" + "=" * 80)
        print(f"Session Summary: {session['correct']}/{len(session['questions'])} correct")
        if len(session['questions']) > 0:
            percentage = (session['correct'] / len(session['questions'])) * 100
            print(f"Accuracy: {percentage:.1f}%")
        print("=" * 80)
    
    def show_stats(self):
        print("\n" + "=" * 80)
        print("TOEIC Practice Statistics")
        print("=" * 80)
        
        if not self.history['sessions']:
            print("No practice sessions recorded yet.")
            return
        
        total_correct = self.history['total_correct']
        total_questions = self.history['total_questions']
        
        print(f"Total Sessions: {len(self.history['sessions'])}")
        print(f"Total Questions Attempted: {total_questions}")
        print(f"Total Correct Answers: {total_correct}")
        
        if total_questions > 0:
            overall_accuracy = (total_correct / total_questions) * 100
            print(f"Overall Accuracy: {overall_accuracy:.1f}%")
        
        # Topic performance
        topic_stats = {}
        for session in self.history['sessions']:
            for q in session['questions']:
                topic = q.get('topic', 'Unknown')
                if topic not in topic_stats:
                    topic_stats[topic] = {'correct': 0, 'total': 0}
                
                topic_stats[topic]['total'] += 1
                if q['is_correct']:
                    topic_stats[topic]['correct'] += 1
        
        if topic_stats:
            print("\nPerformance by Topic:")
            for topic, stats in topic_stats.items():
                if stats['total'] > 0:
                    accuracy = (stats['correct'] / stats['total']) * 100
                    print(f"{topic}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
        
        print("=" * 80)

def main():
    print("\n" + "=" * 80)
    print("TOEIC Part 5 Practice Tool - Incomplete Sentences")
    print("=" * 80)
    print("This tool will help you practice for TOEIC Part 5 using GPT-4 to generate questions.")
    
    practice = TOEICPractice()
    
    while True:
        print("\nMenu:")
        print("1. Start a practice session")
        print("2. View statistics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            # Ask for number of questions
            while True:
                try:
                    num = int(input("\nHow many questions would you like to practice? (1-20): "))
                    if 1 <= num <= 20:
                        break
                    print("Please enter a number between 1 and 20.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Ask for specific topic or random
            print("\nAvailable topics:")
            for i, topic in enumerate(practice.topics, 1):
                print(f"{i}. {topic}")
            print(f"{len(practice.topics) + 1}. Random (mix of topics)")
            
            while True:
                try:
                    topic_choice = int(input(f"\nChoose a topic (1-{len(practice.topics) + 1}): "))
                    if 1 <= topic_choice <= len(practice.topics) + 1:
                        break
                    print(f"Please enter a number between 1 and {len(practice.topics) + 1}.")
                except ValueError:
                    print("Please enter a valid number.")
            
            selected_topic = None if topic_choice == len(practice.topics) + 1 else practice.topics[topic_choice - 1]
            practice.practice_session(num, selected_topic)
            
        elif choice == '2':
            practice.show_stats()
            
        elif choice == '3':
            print("\nThank you for using the TOEIC Practice Tool. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()