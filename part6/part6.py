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
            "Letters and memos",
            "Advertisements",
            "Instructions",
            "Articles",
            "E-mails",
            "Notices"
        ]
        self.passage_types = [
            "Business letter",
            "Email correspondence",
            "Advertisement",
            "Notice",
            "Article",
            "Instructions",
            "Memo"
        ]
        self.history_file = "part6_history.json"
        self.history = self.load_history()
        
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"passages": [], "total_correct": 0, "total_questions": 0}
        return {"passages": [], "total_correct": 0, "total_questions": 0}
    
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
    
    def generate_passage(self, topic=None):
        if not topic:
            topic = random.choice(self.topics)
        
        passage_type = random.choice(self.passage_types)
        
        prompt = f"""
        Generate a TOEIC Part 6 practice passage (Text Completion) on the topic of {topic} in the format of a {passage_type}.
        
        The passage should be a short text (4-6 sentences) with THREE incomplete sentences that have blanks indicated by "___".
        For each blank, provide four options (A, B, C, D) to fill in the blank.
        Only ONE option should be correct for each blank. Include an explanation of why each correct answer is right and why the others are wrong.
        
        Format the response as a JSON object with these fields:
        - passage_title: A title for the passage
        - passage_text: The full text with THREE blanks indicated by "___"
        - questions: An array of 3 objects, each containing:
          - blank_number: The number of the blank (1, 2, or 3)
          - options: An array of 4 options (A, B, C, D)
          - correct_answer: The letter of the correct option (A, B, C, or D)
          - explanation: A detailed explanation of the correct answer
        - passage_type: The type of passage (e.g., email, letter, notice)
        - topic: The topic of the passage
        
        Make sure the questions test these skills:
        - Vocabulary (similar words with different meanings, phrasal verbs)
        - Word forms (noun, pronoun, verb, adjective, adverb, infinitive, gerund)
        - Grammar (subject, verb, object, complement, preposition, adjective)
        - Words in context (choosing the correct word that fits the context)
        
        The difficulty should be appropriate for TOEIC test takers (intermediate to advanced English).
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
                    "passage_title": "Sample Passage",
                    "passage_text": "Could not parse the passage properly. Please try again.",
                    "questions": [
                        {
                            "blank_number": 1,
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "A",
                            "explanation": "Please try again."
                        },
                        {
                            "blank_number": 2,
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "A",
                            "explanation": "Please try again."
                        },
                        {
                            "blank_number": 3,
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "A",
                            "explanation": "Please try again."
                        }
                    ],
                    "passage_type": passage_type,
                    "topic": topic
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error generating passage: {e}")
            return None
    
    def display_passage(self, passage):
        print("\n" + "=" * 80)
        print(f"Topic: {passage['topic']} | Type: {passage['passage_type']}\n")
        print(f"Title: {passage['passage_title']}\n")
        print(passage['passage_text'])
        print("\n" + "=" * 80)
    
    def display_question(self, question):
        print(f"\nQuestion {question['blank_number']}:")
        print("Options:")
        for i, option in enumerate(['A', 'B', 'C', 'D']):
            print(f"{option}. {question['options'][i]}")
    
    def practice_session(self, num_passages=2, topic=None):
        if not self.client and not self.setup_api():
            return
        
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "passages": [],
            "correct": 0,
            "total": num_passages * 3  # Each passage has 3 questions
        }
        
        for i in range(num_passages):
            print(f"\nGenerating passage {i+1}/{num_passages}...")
            passage = self.generate_passage(topic)
            
            if not passage:
                print("Failed to generate passage. Skipping...")
                continue
            
            passage_result = {
                "passage_title": passage['passage_title'],
                "passage_type": passage['passage_type'],
                "topic": passage['topic'],
                "questions": []
            }
            
            self.display_passage(passage)
            
            for question in passage['questions']:
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
                
                passage_result['questions'].append({
                    "blank_number": question['blank_number'],
                    "user_answer": user_answer,
                    "correct_answer": question['correct_answer'],
                    "is_correct": is_correct
                })
                
                # If user quit, break out of the passage loop too
                if user_answer == 'Q':
                    break
            
            # If user quit during questions, break out of passages loop
            if user_answer == 'Q':
                break
                
            # Add passage result to session
            session['passages'].append(passage_result)
            
            # Pause between passages
            if i < num_passages - 1:
                input("\nPress Enter for the next passage...")
        
        # Update history
        self.history['passages'].append(session)
        self.history['total_correct'] += session['correct']
        self.history['total_questions'] += sum(len(p['questions']) for p in session['passages'])
        self.save_history()
        
        # Show session summary
        total_questions = sum(len(p['questions']) for p in session['passages'])
        print("\n" + "=" * 80)
        print(f"Session Summary: {session['correct']}/{total_questions} correct")
        if total_questions > 0:
            percentage = (session['correct'] / total_questions) * 100
            print(f"Accuracy: {percentage:.1f}%")
        print("=" * 80)
    
    def show_stats(self):
        print("\n" + "=" * 80)
        print("TOEIC Part 6 Practice Statistics")
        print("=" * 80)
        
        if not self.history['passages']:
            print("No practice sessions recorded yet.")
            return
        
        total_correct = self.history['total_correct']
        total_questions = self.history['total_questions']
        
        print(f"Total Sessions: {len(self.history['passages'])}")
        print(f"Total Questions Attempted: {total_questions}")
        print(f"Total Correct Answers: {total_correct}")
        
        if total_questions > 0:
            overall_accuracy = (total_correct / total_questions) * 100
            print(f"Overall Accuracy: {overall_accuracy:.1f}%")
        
        # Topic performance
        topic_stats = {}
        for session in self.history['passages']:
            for passage in session['passages']:
                topic = passage.get('topic', 'Unknown')
                if topic not in topic_stats:
                    topic_stats[topic] = {'correct': 0, 'total': 0}
                
                for q in passage['questions']:
                    topic_stats[topic]['total'] += 1
                    if q['is_correct']:
                        topic_stats[topic]['correct'] += 1
        
        if topic_stats:
            print("\nPerformance by Topic:")
            for topic, stats in topic_stats.items():
                if stats['total'] > 0:
                    accuracy = (stats['correct'] / stats['total']) * 100
                    print(f"{topic}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
        
        # Passage type performance
        type_stats = {}
        for session in self.history['passages']:
            for passage in session['passages']:
                p_type = passage.get('passage_type', 'Unknown')
                if p_type not in type_stats:
                    type_stats[p_type] = {'correct': 0, 'total': 0}
                
                for q in passage['questions']:
                    type_stats[p_type]['total'] += 1
                    if q['is_correct']:
                        type_stats[p_type]['correct'] += 1
        
        if type_stats:
            print("\nPerformance by Passage Type:")
            for p_type, stats in type_stats.items():
                if stats['total'] > 0:
                    accuracy = (stats['correct'] / stats['total']) * 100
                    print(f"{p_type}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
        
        print("=" * 80)

def main():
    print("\n" + "=" * 80)
    print("TOEIC Part 6 Practice Tool - Text Completion")
    print("=" * 80)
    print("This tool will help you practice for TOEIC Part 6 using GPT-4 to generate passages with blanks.")
    
    practice = TOEICPractice()
    
    while True:
        print("\nMenu:")
        print("1. Start a practice session")
        print("2. View statistics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            # Ask for number of passages
            while True:
                try:
                    num = int(input("\nHow many passages would you like to practice? (1-10): "))
                    if 1 <= num <= 10:
                        break
                    print("Please enter a number between 1 and 10.")
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