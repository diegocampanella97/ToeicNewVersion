#!/usr/bin/env python3
import os
import json
import random
import time
import openai
from getpass import getpass
from datetime import datetime

class TOEICEmailResponsePractice:
    def __init__(self):
        self.api_key = None
        self.client = None
        self.email_contexts = [
            "Office issues",
            "Job ads and applications",
            "Ads for products and services",
            "Orders and shipments",
            "Schedules",
            "Appointments"
        ]
        self.task_types = [
            "Ask questions",
            "Request information",
            "Make suggestions",
            "Provide information",
            "Explain problems"
        ]
        self.history_file = "part6_7_history.json"
        self.history = self.load_history()
        
    def load_history(self):
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"sessions": [], "total_responses": 0}
        return {"sessions": [], "total_responses": 0}
    
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
    
    def generate_email_scenario(self, context=None):
        if not context:
            context = random.choice(self.email_contexts)
        
        # Randomly determine the number of tasks (between 1 and 3)
        num_tasks = random.randint(1, 3)
        
        # Randomly select task types without repetition
        selected_task_types = random.sample(self.task_types, num_tasks)
        
        # Generate task descriptions
        tasks = []
        for task_type in selected_task_types:
            if task_type == "Ask questions":
                count = random.randint(1, 3)
                tasks.append(f"Ask {self._number_to_word(count).upper()} question{'s' if count > 1 else ''}.")
            elif task_type == "Request information":
                count = random.randint(1, 2)
                tasks.append(f"Make {self._number_to_word(count).upper()} request{'s' if count > 1 else ''} for information.")
            elif task_type == "Make suggestions":
                count = random.randint(1, 2)
                tasks.append(f"Make {self._number_to_word(count).upper()} suggestion{'s' if count > 1 else ''}.")
            elif task_type == "Provide information":
                count = random.randint(1, 3)
                tasks.append(f"Give {self._number_to_word(count).upper()} piece{'s' if count > 1 else ''} of information.")
            elif task_type == "Explain problems":
                count = random.randint(1, 2)
                tasks.append(f"Explain {self._number_to_word(count).upper()} problem{'s' if count > 1 else ''}.")
        
        prompt = f"""
        Generate a realistic email scenario for a TOEIC Writing test (Questions 6-7).
        The email should be related to: {context}
        
        The response should require the test-taker to perform the following tasks:
        {', '.join(tasks)}
        
        Format the response as a JSON object with these fields:
        - email_subject: A clear subject line for the email
        - sender_name: The name of the person sending the email
        - sender_position: The position or role of the sender
        - recipient_name: The name of the intended recipient (the test-taker)
        - recipient_position: The position or role of the recipient
        - email_body: The full content of the email (150-200 words)
        - context: The context of the email ({context})
        - tasks: An array of the specific tasks the test-taker needs to address in their response {tasks}
        - key_points: 3-5 key points that should be addressed in a good response
        - sample_response: A sample good response to the email that addresses all the tasks
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
                    "email_subject": f"Regarding {context}",
                    "sender_name": "John Smith",
                    "sender_position": "Manager",
                    "recipient_name": "Test Taker",
                    "recipient_position": "Employee",
                    "email_body": f"This is a fallback email about {context}. Please respond addressing the following tasks: {', '.join(tasks)}",
                    "context": context,
                    "tasks": tasks,
                    "key_points": ["Be professional", "Address all tasks", "Use correct grammar", "Be concise"],
                    "sample_response": "This is a sample response that would address all the required tasks."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error generating email scenario: {e}")
            return None
    
    def evaluate_response(self, response, scenario):
        evaluation_prompt = f"""
        Evaluate the following email response written for a TOEIC Writing test (Questions 6-7):
        
        Original Email Subject: {scenario['email_subject']}
        Original Email Body: {scenario['email_body']}
        
        Required Tasks: {', '.join(scenario['tasks'])}
        
        Student Response:
        {response}
        
        Please evaluate the response based on:
        1. Task Completion (whether all required tasks were addressed)
        2. Organization (structure, coherence, use of connecting words)
        3. Sentence Variety (use of different sentence types and structures)
        4. Grammar (grammatical accuracy)
        5. Vocabulary (appropriate word choice)
        
        Provide specific feedback for improvement in each area and an overall assessment.
        
        Format the response as a JSON object with these fields:
        - task_completion_score: A score from 1-5 for task completion
        - organization_score: A score from 1-5 for organization
        - sentence_variety_score: A score from 1-5 for sentence variety
        - grammar_score: A score from 1-5 for grammar
        - vocabulary_score: A score from 1-5 for vocabulary
        - overall_score: An overall score from 1-5
        - task_completion_feedback: Specific feedback on task completion
        - organization_feedback: Specific feedback on organization
        - sentence_variety_feedback: Specific feedback on sentence variety
        - grammar_feedback: Specific feedback on grammar
        - vocabulary_feedback: Specific feedback on vocabulary
        - overall_feedback: General feedback and suggestions for improvement
        - improved_response: A suggested improved response
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
                    "task_completion_score": 3,
                    "organization_score": 3,
                    "sentence_variety_score": 3,
                    "grammar_score": 3,
                    "vocabulary_score": 3,
                    "overall_score": 3,
                    "task_completion_feedback": "Unable to provide detailed feedback on task completion. Please try again.",
                    "organization_feedback": "Unable to provide detailed feedback on organization. Please try again.",
                    "sentence_variety_feedback": "Unable to provide detailed feedback on sentence variety. Please try again.",
                    "grammar_feedback": "Unable to provide detailed feedback on grammar. Please try again.",
                    "vocabulary_feedback": "Unable to provide detailed feedback on vocabulary. Please try again.",
                    "overall_feedback": "Unable to provide detailed overall feedback. Please try again.",
                    "improved_response": "Unable to provide an improved response. Please try again."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error evaluating response: {e}")
            return None
    
    def display_email_scenario(self, scenario):
        print("\n" + "=" * 80)
        print(f"From: {scenario['sender_name']} ({scenario['sender_position']})")
        print(f"To: {scenario['recipient_name']} ({scenario['recipient_position']})")
        print(f"Subject: {scenario['email_subject']}")
        print("=" * 80)
        print(scenario['email_body'])
        print("\n" + "=" * 80)
        print("Tasks:")
        for task in scenario['tasks']:
            print(f"- {task}")
        print("\n" + "=" * 80)
    
    def display_evaluation(self, evaluation):
        print("\n" + "=" * 80)
        print("Response Evaluation")
        print("=" * 80)
        
        print(f"Task Completion: {evaluation['task_completion_score']}/5")
        print(evaluation['task_completion_feedback'])
        print()
        
        print(f"Organization: {evaluation['organization_score']}/5")
        print(evaluation['organization_feedback'])
        print()
        
        print(f"Sentence Variety: {evaluation['sentence_variety_score']}/5")
        print(evaluation['sentence_variety_feedback'])
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
        
        print("Suggested Improved Response:")
        print(evaluation['improved_response'])
        print("\n" + "=" * 80)
    
    def _number_to_word(self, number):
        """Convert a number to its word representation."""
        words = {
            1: "one",
            2: "two",
            3: "three",
            4: "four",
            5: "five"
        }
        return words.get(number, str(number))

    def display_statistics(self):
        if not self.history["sessions"]:
            print("\nNo practice sessions found. Start practicing to see your statistics!")
            return
        
        print("\n" + "=" * 80)
        print("TOEIC Email Response Practice Statistics")
        print("=" * 80)
        
        total_sessions = len(self.history["sessions"])
        total_responses = self.history["total_responses"]
        
        print(f"Total Practice Sessions: {total_sessions}")
        print(f"Total Email Responses: {total_responses}")
        print()
        
        # Calculate average scores
        avg_task_completion = 0
        avg_organization = 0
        avg_sentence_variety = 0
        avg_grammar = 0
        avg_vocabulary = 0
        avg_overall = 0
        
        for session in self.history["sessions"]:
            for response in session["responses"]:
                avg_task_completion += response["scores"]["task_completion_score"]
                avg_organization += response["scores"]["organization_score"]
                avg_sentence_variety += response["scores"]["sentence_variety_score"]
                avg_grammar += response["scores"]["grammar_score"]
                avg_vocabulary += response["scores"]["vocabulary_score"]
                avg_overall += response["scores"]["overall_score"]
        
        if total_responses > 0:
            avg_task_completion /= total_responses
            avg_organization /= total_responses
            avg_sentence_variety /= total_responses
            avg_grammar /= total_responses
            avg_vocabulary /= total_responses
            avg_overall /= total_responses
            
            print("Average Scores:")
            print(f"Task Completion: {avg_task_completion:.2f}/5")
            print(f"Organization: {avg_organization:.2f}/5")
            print(f"Sentence Variety: {avg_sentence_variety:.2f}/5")
            print(f"Grammar: {avg_grammar:.2f}/5")
            print(f"Vocabulary: {avg_vocabulary:.2f}/5")
            print(f"Overall: {avg_overall:.2f}/5")
        
        print("\n" + "=" * 80)
        print("Recent Practice Sessions:")
        
        # Display the 5 most recent sessions
        recent_sessions = self.history["sessions"][-5:]
        for i, session in enumerate(reversed(recent_sessions)):
            print(f"\nSession {len(self.history['sessions']) - i}: {session['date']}")
            print(f"Email Context: {session['context']}")
            print(f"Number of Responses: {len(session['responses'])}")
            print(f"Average Score: {session['average_score']:.2f}/5")

    def run_practice_session(self, context=None):
        """Run a complete practice session with one or more email responses."""
        # Create a new session record
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "context": context if context else "Random",
            "responses": [],
            "average_score": 0
        }
        
        continue_session = True
        while continue_session:
            # Generate an email scenario
            print("\nGenerating email scenario...")
            scenario = self.generate_email_scenario(context)
            
            if not scenario:
                print("Failed to generate an email scenario. Please try again.")
                continue
            
            # Display the email scenario
            self.display_email_scenario(scenario)
            
            # Get user's response
            print("\nWrite your response to the email. Press Enter twice when finished.")
            print("You have 10 minutes to complete your response.")
            
            # Start a timer
            start_time = time.time()
            time_limit = 10 * 60  # 10 minutes in seconds
            
            # Collect user's response
            user_response = ""
            while True:
                line = input()
                if not line and user_response:  # Empty line and we already have some content
                    break
                user_response += line + "\n"
                
                # Check if time is up
                elapsed_time = time.time() - start_time
                if elapsed_time >= time_limit:
                    print("\nTime's up! Your response has been submitted.")
                    break
                
                # Show remaining time every minute
                remaining_time = time_limit - elapsed_time
                if remaining_time <= 60 and int(remaining_time) % 10 == 0:  # Every 10 seconds in the last minute
                    print(f"\nRemaining time: {int(remaining_time)} seconds")
                elif int(elapsed_time) % 60 == 0 and elapsed_time > 0:  # Every minute
                    print(f"\nRemaining time: {int(remaining_time / 60)} minutes")
            
            # Evaluate the response
            print("\nEvaluating your response...")
            evaluation = self.evaluate_response(user_response, scenario)
            
            if not evaluation:
                print("Failed to evaluate your response. Please try again.")
                continue
            
            # Display the evaluation
            self.display_evaluation(evaluation)
            
            # Record the response in the session
            response_record = {
                "scenario": scenario,
                "user_response": user_response,
                "scores": {
                    "task_completion_score": evaluation["task_completion_score"],
                    "organization_score": evaluation["organization_score"],
                    "sentence_variety_score": evaluation["sentence_variety_score"],
                    "grammar_score": evaluation["grammar_score"],
                    "vocabulary_score": evaluation["vocabulary_score"],
                    "overall_score": evaluation["overall_score"]
                },
                "feedback": evaluation["overall_feedback"]
            }
            
            session["responses"].append(response_record)
            
            # Ask if the user wants to continue
            continue_choice = input("\nWould you like to respond to another email? (y/n): ").lower()
            continue_session = continue_choice == 'y'
        
        # Calculate average score for the session
        if session["responses"]:
            total_score = sum(response["scores"]["overall_score"] for response in session["responses"])
            session["average_score"] = total_score / len(session["responses"])
        
        # Update history
        self.history["sessions"].append(session)
        self.history["total_responses"] += len(session["responses"])
        self.save_history()
        
        print("\nPractice session completed. Your progress has been saved.")

def main():
    practice = TOEICEmailResponsePractice()
    
    print("\n" + "=" * 80)
    print("TOEIC Writing Practice - Email Response (Questions 6-7)")
    print("=" * 80)
    print("This program helps you practice responding to emails for TOEIC Writing Questions 6-7.")
    print("You will be given an email and specific tasks to address in your response.")
    print("Your response will be evaluated based on task completion, organization, grammar, and more.")
    
    # Set up API connection
    if not practice.setup_api():
        print("Failed to set up API connection. Exiting.")
        return
    
    while True:
        print("\n" + "=" * 80)
        print("Main Menu")
        print("=" * 80)
        print("1. Start a practice session with random email contexts")
        print("2. Choose a specific email context for practice")
        print("3. View your practice statistics")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "1":
            practice.run_practice_session()
        elif choice == "2":
            print("\nAvailable Email Contexts:")
            for i, context in enumerate(practice.email_contexts, 1):
                print(f"{i}. {context}")
            
            context_choice = input(f"\nChoose a context (1-{len(practice.email_contexts)}): ")
            try:
                context_index = int(context_choice) - 1
                if 0 <= context_index < len(practice.email_contexts):
                    selected_context = practice.email_contexts[context_index]
                    practice.run_practice_session(selected_context)
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
        elif choice == "3":
            practice.display_statistics()
        elif choice == "4":
            print("\nThank you for using TOEIC Writing Practice. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()