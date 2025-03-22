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
            "E-mails and letters",
            "Memos",
            "Advertisements",
            "Notices",
            "Articles and reports",
            "Forms",
            "Charts and tables",
            "Graphs and schedules"
        ]
        self.passage_types = [
            "Single passage",
            "Double passage"
        ]
        self.question_types = [
            "Main idea",
            "Detail",
            "Inference",
            "Vocabulary"
        ]
        self.history_file = "part7_history.json"
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
    
    def generate_passage(self, passage_type=None, topic=None):
        if not passage_type:
            passage_type = random.choice(self.passage_types)
        
        if not topic:
            topic = random.choice(self.topics)
        
        # Determine number of passages based on passage type
        num_passages = 2 if passage_type == "Double passage" else 1
        
        # Determine number of questions
        num_questions = 5 if passage_type == "Double passage" else random.randint(2, 4)
        
        prompt = f"""
        Generate a TOEIC Part 7 practice {passage_type} on the topic of {topic}.
        
        {"For the double passage, create two related passages that complement each other." if passage_type == "Double passage" else "Create a single comprehensive passage."}
        
        The passage(s) should be of appropriate length for TOEIC Part 7 (approximately 300-500 words total).
        Include {num_questions} reading comprehension questions with four options (A, B, C, D) for each question.
        
        Make sure to include a mix of these question types:
        - Main idea questions (What is the passage mainly about?)
        - Detail questions (According to the passage, what...?)
        - Inference questions (What can be inferred about...?)
        - Vocabulary questions (The word "X" in paragraph Y is closest in meaning to...)
        
        Only ONE option should be correct for each question. Include an explanation of why the correct answer is right and why the others are wrong.
        
        Format the response as a JSON object with these fields:
        - passage_title: A title for the passage or passages
        - passage_text: {"An array of two passages" if passage_type == "Double passage" else "The full text of the passage"}
        - questions: An array of {num_questions} objects, each containing:
          - question_number: The number of the question
          - question_text: The text of the question
          - question_type: The type of question (Main idea, Detail, Inference, or Vocabulary)
          - options: An array of 4 options (A, B, C, D)
          - correct_answer: The letter of the correct option (A, B, C, or D)
          - explanation: A detailed explanation of the correct answer
        - passage_type: The type of passage (Single passage or Double passage)
        - topic: The topic of the passage
        
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
                    "passage_text": ["Could not parse the passage properly. Please try again."] if passage_type == "Double passage" else "Could not parse the passage properly. Please try again.",
                    "questions": [
                        {
                            "question_number": i+1,
                            "question_text": f"Question {i+1}",
                            "question_type": random.choice(self.question_types),
                            "options": ["Option A", "Option B", "Option C", "Option D"],
                            "correct_answer": "A",
                            "explanation": "Please try again."
                        } for i in range(num_questions)
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
        
        if passage['passage_type'] == "Double passage":
            print("PASSAGE 1:")
            print(passage['passage_text'][0])
            print("\nPASSAGE 2:")
            print(passage['passage_text'][1])
        else:
            print(passage['passage_text'])
            
        print("\n" + "=" * 80)
    
    def display_question(self, question):
        print(f"\nQuestion {question['question_number']} ({question['question_type']}):")
        print(question['question_text'])
        print("Options:")
        for i, option in enumerate(['A', 'B', 'C', 'D']):
            print(f"{option}. {question['options'][i]}")
    
    def practice_session(self, num_passages=2, passage_type=None, topic=None):
        if not self.client and not self.setup_api():
            return
        
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "passages": [],
            "correct": 0,
            "total": 0  # Will be updated as we go
        }
        
        for i in range(num_passages):
            # For each iteration, randomly choose passage type if not specified
            current_passage_type = passage_type if passage_type else random.choice(self.passage_types)
            
            print(f"\nGenerating {current_passage_type} {i+1}/{num_passages}...")
            passage = self.generate_passage(current_passage_type, topic)
            
            if not passage:
                print("Failed to generate passage. Skipping...")
                continue
            
            passage_result = {
                "passage_title": passage['passage_title'],
                "passage_type": passage['passage_type'],
                "topic": passage['topic'],
                "questions": []
            }
            
            # Update total questions count
            session['total'] += len(passage['questions'])
            
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
                    "question_number": question['question_number'],
                    "question_type": question['question_type'],
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
        self.history['sessions'].append(session)
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
        print("TOEIC Part 7 Practice Statistics")
        print("=" * 80)
        
        if not self.history['sessions']:
            print("No practice sessions recorded yet.")
            return
        
        # Overall stats
        total_sessions = len(self.history['sessions'])
        total_correct = self.history['total_correct']
        total_questions = self.history['total_questions']
        
        if total_questions > 0:
            overall_accuracy = (total_correct / total_questions) * 100
            print(f"Overall Accuracy: {overall_accuracy:.1f}% ({total_correct}/{total_questions})")
        
        print(f"Total Sessions: {total_sessions}")
        
        # Stats by question type
        question_type_stats = {}
        for session in self.history['sessions']:
            for passage in session['passages']:
                for question in passage['questions']:
                    q_type = question['question_type']
                    if q_type not in question_type_stats:
                        question_type_stats[q_type] = {'correct': 0, 'total': 0}
                    
                    question_type_stats[q_type]['total'] += 1
                    if question['is_correct']:
                        question_type_stats[q_type]['correct'] += 1
        
        print("\nPerformance by Question Type:")
        for q_type, stats in question_type_stats.items():
            if stats['total'] > 0:
                accuracy = (stats['correct'] / stats['total']) * 100
                print(f"{q_type}: {accuracy:.1f}% ({stats['correct']}/{stats['total']})")
        
        # Stats by passage type
        passage_type_stats = {}
        for session in self.history['sessions']:
            for passage in session['passages']:
                p_type = passage['passage_type']
                if p_type not in passage_type_stats:
                    passage_type_stats[p_type] = {'correct': 0, 'total': 0}
                
                for question in passage['questions']:
                    passage_type_stats[p_type]['total'] += 1
                    if question['is_correct']:
                        passage_type_stats[p_type]['correct'] += 1
        
        print("\nPerformance by Passage Type:")
        for p_type, stats in passage_type_stats.items():
            if stats['total'] > 0:
                accuracy = (stats['correct'] / stats['total']) * 100
                print(f"{p_type}: {accuracy:.1f}% ({stats['correct']}/{stats['total']})")
        
        # Recent sessions
        print("\nRecent Sessions:")
        recent_sessions = self.history['sessions'][-5:] if len(self.history['sessions']) > 5 else self.history['sessions']
        recent_sessions.reverse()  # Show most recent first
        
        for i, session in enumerate(recent_sessions):
            total_questions = sum(len(p['questions']) for p in session['passages'])
            if total_questions > 0:
                accuracy = (session['correct'] / total_questions) * 100
                print(f"{i+1}. {session['date']}: {session['correct']}/{total_questions} correct ({accuracy:.1f}%)")
            else:
                print(f"{i+1}. {session['date']}: No questions answered")
        
        print("=" * 80)

def main():
    practice = TOEICPractice()
    
    while True:
        print("\n" + "=" * 80)
        print("TOEIC Part 7 Reading Comprehension Practice")
        print("=" * 80)
        print("1. Start a practice session")
        print("2. View statistics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
            # Ask for number of passages
            while True:
                try:
                    num_passages = int(input("\nHow many passages would you like to practice? (1-5, default: 2): ") or "2")
                    if 1 <= num_passages <= 5:
                        break
                    print("Please enter a number between 1 and 5.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Ask for passage type preference
            print("\nPassage type:")
            print("1. Random (default)")
            print("2. Single passages only")
            print("3. Double passages only")
            
            type_choice = input("Enter your choice (1-3): ") or "1"
            passage_type = None
            if type_choice == "2":
                passage_type = "Single passage"
            elif type_choice == "3":
                passage_type = "Double passage"
            
            # Ask for topic preference
            print("\nTopic:")
            print("1. Random (default)")
            for i, topic in enumerate(practice.topics):
                print(f"{i+2}. {topic}")
            
            topic_choice = input(f"\nEnter your choice (1-{len(practice.topics)+1}): ") or "1"
            topic = None
            if topic_choice != "1" and topic_choice.isdigit():
                topic_idx = int(topic_choice) - 2
                if 0 <= topic_idx < len(practice.topics):
                    topic = practice.topics[topic_idx]
            
            # Start practice session
            practice.practice_session(num_passages, passage_type, topic)
            
        elif choice == '2':
            practice.show_stats()
            
        elif choice == '3':
            print("\nThank you for practicing TOEIC Part 7! Goodbye.")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()