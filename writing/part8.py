#!/usr/bin/env python3
import os
import json
import random
import time
import openai
from getpass import getpass
from datetime import datetime

class TOEICEssayPractice:
    def __init__(self):
        self.api_key = None
        self.client = None
        self.essay_topics = [
            "Work issues",
            "Travel and transportation choices",
            "Friendships and family",
            "Shopping practices",
            "Leisure time activities",
            "Education and learning",
            "Technology and society",
            "Health and wellness",
            "Environment and sustainability",
            "Cultural experiences"
        ]
        self.essay_types = [
            "Express a general opinion",
            "Agree or disagree with a statement",
            "Discuss the advantages and disadvantages",
            "Explain your preference",
            "Explain the importance"
        ]
        self.history_file = "part8_history.json"
        self.history = self.load_history()
        
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"sessions": [], "total_essays": 0}
        return {"sessions": [], "total_essays": 0}
    
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
    
    def generate_essay_prompt(self, topic=None, essay_type=None):
        if not topic:
            topic = random.choice(self.essay_topics)
        
        if not essay_type:
            essay_type = random.choice(self.essay_types)
        
        prompt = f"""
        Generate a realistic essay prompt for a TOEIC Writing test (Question 8).
        The essay should be related to: {topic}
        The essay type should be: {essay_type}
        
        Format the response as a JSON object with these fields:
        - essay_prompt: The full text of the essay prompt (50-100 words)
        - topic: The topic of the essay ({topic})
        - essay_type: The type of essay ({essay_type})
        - key_points: 3-5 key points that should be addressed in a good essay
        - suggested_structure: A brief outline of how a good essay should be structured
        - sample_essay: A sample good essay that responds to the prompt (about 300 words)
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
                    "essay_prompt": f"Write an essay about {topic}. {self._get_instruction_by_type(essay_type)}",
                    "topic": topic,
                    "essay_type": essay_type,
                    "key_points": ["Be clear and concise", "Use specific examples", "Organize your ideas logically", "Use appropriate grammar and vocabulary"],
                    "suggested_structure": "Introduction with thesis statement, 2-3 body paragraphs with supporting ideas, conclusion that restates your opinion.",
                    "sample_essay": f"This is a sample essay about {topic}. It would normally be about 300 words long and demonstrate good organization, grammar, and vocabulary."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error generating essay prompt: {e}")
            return None
    
    def _get_instruction_by_type(self, essay_type):
        """Helper method to generate instructions based on essay type."""
        if essay_type == "Express a general opinion":
            return "Express your opinion on this topic and support it with specific reasons and examples."
        elif essay_type == "Agree or disagree with a statement":
            return "State whether you agree or disagree with this statement and support your position with specific reasons and examples."
        elif essay_type == "Discuss the advantages and disadvantages":
            return "Discuss the advantages and disadvantages of this topic, providing specific examples to support your points."
        elif essay_type == "Explain your preference":
            return "Explain your preference regarding this topic and support it with specific reasons and examples."
        elif essay_type == "Explain the importance":
            return "Explain why this topic is important and support your explanation with specific reasons and examples."
        else:
            return "Write a well-organized essay with a clear thesis statement, supporting paragraphs, and a conclusion."
    
    def evaluate_essay(self, essay, prompt):
        evaluation_prompt = f"""
        Evaluate the following essay written for a TOEIC Writing test (Question 8):
        
        Original Essay Prompt: {prompt['essay_prompt']}
        
        Student Essay:
        {essay}
        
        Please evaluate the essay based on:
        1. Organization (clear thesis statement, logical structure, effective conclusion)
        2. Development (supporting ideas with specific details and examples)
        3. Coherence and Cohesion (use of transition words and logical flow)
        4. Grammar (grammatical accuracy and sentence structure)
        5. Vocabulary (appropriate word choice and variety)
        
        Provide specific feedback for improvement in each area and an overall assessment.
        
        Format the response as a JSON object with these fields:
        - organization_score: A score from 1-5 for organization
        - development_score: A score from 1-5 for development
        - coherence_score: A score from 1-5 for coherence and cohesion
        - grammar_score: A score from 1-5 for grammar
        - vocabulary_score: A score from 1-5 for vocabulary
        - overall_score: An overall score from 1-5
        - organization_feedback: Specific feedback on organization
        - development_feedback: Specific feedback on development
        - coherence_feedback: Specific feedback on coherence and cohesion
        - grammar_feedback: Specific feedback on grammar
        - vocabulary_feedback: Specific feedback on vocabulary
        - overall_feedback: General feedback and suggestions for improvement
        - improved_essay: A suggested improved version of the essay
        """
        
        try:
            response_eval = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": evaluation_prompt}]
            )
            
            # Parse the response content as JSON
            try:
                result = json.loads(response_eval.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, create a fallback
                fallback_result = {
                    "organization_score": 3,
                    "development_score": 3,
                    "coherence_score": 3,
                    "grammar_score": 3,
                    "vocabulary_score": 3,
                    "overall_score": 3,
                    "organization_feedback": "Unable to provide detailed feedback on organization. Please try again.",
                    "development_feedback": "Unable to provide detailed feedback on development. Please try again.",
                    "coherence_feedback": "Unable to provide detailed feedback on coherence. Please try again.",
                    "grammar_feedback": "Unable to provide detailed feedback on grammar. Please try again.",
                    "vocabulary_feedback": "Unable to provide detailed feedback on vocabulary. Please try again.",
                    "overall_feedback": "Unable to provide detailed overall feedback. Please try again.",
                    "improved_essay": "Unable to provide an improved essay. Please try again."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error evaluating essay: {e}")
            return None
    
    def display_essay_prompt(self, prompt):
        print("\n" + "=" * 80)
        print("TOEIC Writing Test - Question 8")
        print("=" * 80)
        print(f"Topic: {prompt['topic']}")
        print(f"Essay Type: {prompt['essay_type']}")
        print("=" * 80)
        print(prompt['essay_prompt'])
        print("\n" + "=" * 80)
        print("Key Points to Address:")
        for point in prompt['key_points']:
            print(f"- {point}")
        print("\n" + "=" * 80)
        print("Suggested Structure:")
        print(prompt['suggested_structure'])
        print("\n" + "=" * 80)
    
    def display_evaluation(self, evaluation):
        print("\n" + "=" * 80)
        print("Essay Evaluation")
        print("=" * 80)
        
        print(f"Organization: {evaluation['organization_score']}/5")
        print(evaluation['organization_feedback'])
        print()
        
        print(f"Development: {evaluation['development_score']}/5")
        print(evaluation['development_feedback'])
        print()
        
        print(f"Coherence and Cohesion: {evaluation['coherence_score']}/5")
        print(evaluation['coherence_feedback'])
        print()
        
        print(f"Grammar: {evaluation['grammar_score']}/5")
        print(evaluation['grammar_feedback'])
        print()
        
        print(f"Vocabulary: {evaluation['vocabulary_score']}/5")
        print(evaluation['vocabulary_feedback'])
        print()
        
        print("=" * 80)
        print(f"Overall Score: {evaluation['overall_score']}/5")
        print(evaluation['overall_feedback'])
        print("\n" + "=" * 80)
        
        print("Suggested Improved Essay:")
        print(evaluation['improved_essay'])
        print("\n" + "=" * 80)
    
    def display_statistics(self):
        if not self.history["sessions"]:
            print("\nNo practice sessions found. Start practicing to see your statistics!")
            return
        
        print("\n" + "=" * 80)
        print("TOEIC Essay Practice Statistics")
        print("=" * 80)
        
        total_sessions = len(self.history["sessions"])
        total_essays = self.history["total_essays"]
        
        print(f"Total Practice Sessions: {total_sessions}")
        print(f"Total Essays Written: {total_essays}")
        print()
        
        # Calculate average scores
        avg_organization = 0
        avg_development = 0
        avg_coherence = 0
        avg_grammar = 0
        avg_vocabulary = 0
        avg_overall = 0
        
        for session in self.history["sessions"]:
            for essay in session["essays"]:
                avg_organization += essay["scores"]["organization_score"]
                avg_development += essay["scores"]["development_score"]
                avg_coherence += essay["scores"]["coherence_score"]
                avg_grammar += essay["scores"]["grammar_score"]
                avg_vocabulary += essay["scores"]["vocabulary_score"]
                avg_overall += essay["scores"]["overall_score"]
        
        if total_essays > 0:
            avg_organization /= total_essays
            avg_development /= total_essays
            avg_coherence /= total_essays
            avg_grammar /= total_essays
            avg_vocabulary /= total_essays
            avg_overall /= total_essays
            
            print("Average Scores:")
            print(f"Organization: {avg_organization:.2f}/5")
            print(f"Development: {avg_development:.2f}/5")
            print(f"Coherence and Cohesion: {avg_coherence:.2f}/5")
            print(f"Grammar: {avg_grammar:.2f}/5")
            print(f"Vocabulary: {avg_vocabulary:.2f}/5")
            print(f"Overall: {avg_overall:.2f}/5")
        
        print("\n" + "=" * 80)
        print("Recent Practice Sessions:")
        
        # Display the 5 most recent sessions
        recent_sessions = self.history["sessions"][-5:]
        for i, session in enumerate(reversed(recent_sessions)):
            print(f"\nSession {len(self.history['sessions']) - i}: {session['date']}")
            print(f"Essay Topic: {session['topic']}")
            print(f"Essay Type: {session['essay_type']}")
            print(f"Number of Essays: {len(session['essays'])}")
            print(f"Average Score: {session['average_score']:.2f}/5")

    def run_practice_session(self, topic=None, essay_type=None):
        """Run a complete practice session with one essay."""
        # Create a new session record
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "topic": topic if topic else "Random",
            "essay_type": essay_type if essay_type else "Random",
            "essays": [],
            "average_score": 0
        }
        
        # Generate an essay prompt
        print("\nGenerating essay prompt...")
        prompt = self.generate_essay_prompt(topic, essay_type)
        
        if not prompt:
            print("Failed to generate an essay prompt. Please try again.")
            return
        
        # Display the essay prompt
        self.display_essay_prompt(prompt)
        
        # Get user's essay
        print("\nWrite your essay. Press Enter twice when finished.")
        print("You have 30 minutes to complete your essay.")
        
        # Start a timer
        start_time = time.time()
        time_limit = 30 * 60  # 30 minutes in seconds
        
        # Collect user's essay
        user_essay = ""
        while True:
            line = input()
            if not line and user_essay:  # Empty line and we already have some content
                break
            user_essay += line + "\n"
            
            # Check if time is up
            elapsed_time = time.time() - start_time
            if elapsed_time >= time_limit:
                print("\nTime's up! Your essay has been submitted.")
                break
            
            # Show remaining time every 5 minutes
            remaining_time = time_limit - elapsed_time
            if remaining_time <= 60 and int(remaining_time) % 10 == 0:  # Every 10 seconds in the last minute
                print(f"\nRemaining time: {int(remaining_time)} seconds")
            elif int(elapsed_time) % 300 == 0 and elapsed_time > 0:  # Every 5 minutes
                print(f"\nRemaining time: {int(remaining_time / 60)} minutes")
        
        # Evaluate the essay
        print("\nEvaluating your essay...")
        evaluation = self.evaluate_essay(user_essay, prompt)
        
        if not evaluation:
            print("Failed to evaluate your essay. Please try again.")
            return
        
        # Display the evaluation
        self.display_evaluation(evaluation)
        
        # Record the essay in the session
        essay_record = {
            "prompt": prompt,
            "user_essay": user_essay,
            "scores": {
                "organization_score": evaluation["organization_score"],
                "development_score": evaluation["development_score"],
                "coherence_score": evaluation["coherence_score"],
                "grammar_score": evaluation["grammar_score"],
                "vocabulary_score": evaluation["vocabulary_score"],
                "overall_score": evaluation["overall_score"]
            },
            "feedback": evaluation["overall_feedback"]
        }
        
        session["essays"].append(essay_record)
        
        # Calculate average score for the session
        if session["essays"]:
            total_score = sum(essay["scores"]["overall_score"] for essay in session["essays"])
            session["average_score"] = total_score / len(session["essays"])
        
        # Update history
        self.history["sessions"].append(session)
        self.history["total_essays"] += len(session["essays"])
        self.save_history()
        
        print("\nPractice session completed. Your progress has been saved.")

def main():
    practice = TOEICEssayPractice()
    
    print("\n" + "=" * 80)
    print("TOEIC Writing Practice - Essay Writing (Question 8)")
    print("=" * 80)
    print("This program helps you practice writing essays for TOEIC Writing Question 8.")
    print("You will be given an essay prompt and asked to write an opinion essay.")
    print("Your essay will be evaluated based on organization, development, coherence, grammar, and vocabulary.")
    
    # Set up API connection
    if not practice.setup_api():
        print("Failed to set up API connection. Exiting.")
        return
    
    while True:
        print("\n" + "=" * 80)
        print("Main Menu")
        print("=" * 80)
        print("1. Start a practice session with random topic and essay type")
        print("2. Choose a specific topic for practice")
        print("3. Choose a specific essay type for practice")
        print("4. Choose both topic and essay type for practice")
        print("5. View your practice statistics")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")
        
        if choice == "1":
            practice.run_practice_session()
        elif choice == "2":
            print("\nAvailable Essay Topics:")
            for i, topic in enumerate(practice.essay_topics, 1):
                print(f"{i}. {topic}")
            
            topic_choice = input(f"\nChoose a topic (1-{len(practice.essay_topics)}): ")
            try:
                topic_index = int(topic_choice) - 1
                if 0 <= topic_index < len(practice.essay_topics):
                    selected_topic = practice.essay_topics[topic_index]
                    practice.run_practice_session(selected_topic)
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "3":
            print("\nAvailable Essay Types:")
            for i, essay_type in enumerate(practice.essay_types, 1):
                print(f"{i}. {essay_type}")
            
            type_choice = input(f"\nChoose an essay type (1-{len(practice.essay_types)}): ")
            try:
                type_index = int(type_choice) - 1
                if 0 <= type_index < len(practice.essay_types):
                    selected_type = practice.essay_types[type_index]
                    practice.run_practice_session(None, selected_type)
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "4":
            # Choose topic
            print("\nAvailable Essay Topics:")
            for i, topic in enumerate(practice.essay_topics, 1):
                print(f"{i}. {topic}")
            
            topic_choice = input(f"\nChoose a topic (1-{len(practice.essay_topics)}): ")
            try:
                topic_index = int(topic_choice) - 1
                if 0 <= topic_index < len(practice.essay_topics):
                    selected_topic = practice.essay_topics[topic_index]
                    
                    # Choose essay type
                    print("\nAvailable Essay Types:")
                    for i, essay_type in enumerate(practice.essay_types, 1):
                        print(f"{i}. {essay_type}")
                    
                    type_choice = input(f"\nChoose an essay type (1-{len(practice.essay_types)}): ")
                    try:
                        type_index = int(type_choice) - 1
                        if 0 <= type_index < len(practice.essay_types):
                            selected_type = practice.essay_types[type_index]
                            practice.run_practice_session(selected_topic, selected_type)
                        else:
                            print("Invalid essay type choice. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    print("Invalid topic choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "5":
            practice.display_statistics()
        elif choice == "6":
            print("\nThank you for using TOEIC Writing Practice. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()