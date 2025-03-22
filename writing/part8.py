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
        self.topics = [
            "Business",
            "Technology",
            "Education",
            "Environment",
            "Health",
            "Travel",
            "Entertainment",
            "Food",
            "Work-life balance",
            "Social media"
        ]
        self.essay_types = [
            "Opinion",
            "Agree/Disagree",
            "Problem/Solution",
            "Advantages/Disadvantages"
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
            topic = random.choice(self.topics)
        
        if not essay_type:
            essay_type = random.choice(self.essay_types)
        
        prompt = f"""
        Generate a TOEIC Writing test essay prompt on the topic of {topic}.
        The essay should be of type: {essay_type}.
        
        Format the response as a JSON object with these fields:
        - essay_title: A clear title for the essay prompt
        - essay_prompt: The full essay prompt (150-200 words)
        - topic: The topic of the essay ({topic})
        - essay_type: The type of essay ({essay_type})
        - word_count: The suggested word count (between 175-300 words)
        - time_limit: The suggested time limit in minutes (between 20-30 minutes)
        - key_points: 3-5 key points that should be addressed in a good response
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
                    "essay_title": f"{essay_type} Essay on {topic}",
                    "essay_prompt": f"Write an {essay_type.lower()} essay about {topic.lower()}. Provide your perspective and support it with examples.",
                    "topic": topic,
                    "essay_type": essay_type,
                    "word_count": 250,
                    "time_limit": 25,
                    "key_points": ["Introduction with clear thesis", "Supporting arguments", "Examples", "Conclusion"]
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error generating essay prompt: {e}")
            return None
    
    def evaluate_essay(self, essay, prompt):
        evaluation_prompt = f"""
        Evaluate the following essay written for a TOEIC Writing test:
        
        Essay Prompt: {prompt['essay_prompt']}
        
        Student Essay:
        {essay}
        
        Please evaluate the essay based on:
        1. Content and Development (relevance to the topic, development of ideas)
        2. Organization (structure, coherence, transitions)
        3. Language Use (grammar, vocabulary, sentence variety)
        4. Mechanics (spelling, punctuation, capitalization)
        
        Provide specific feedback for improvement in each area and an overall assessment.
        
        Format the response as a JSON object with these fields:
        - content_score: A score from 1-5 for content and development
        - organization_score: A score from 1-5 for organization
        - language_score: A score from 1-5 for language use
        - mechanics_score: A score from 1-5 for mechanics
        - overall_score: An overall score from 1-5
        - content_feedback: Specific feedback on content and development
        - organization_feedback: Specific feedback on organization
        - language_feedback: Specific feedback on language use
        - mechanics_feedback: Specific feedback on mechanics
        - overall_feedback: General feedback and suggestions for improvement
        - improved_introduction: A suggested improved introduction
        - improved_conclusion: A suggested improved conclusion
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": evaluation_prompt}]
            )
            
            # Parse the response content as JSON
            try:
                result = json.loads(response.choices[0].message.content)
                return result
            except json.JSONDecodeError:
                # If JSON parsing fails, create a fallback
                fallback_result = {
                    "content_score": 3,
                    "organization_score": 3,
                    "language_score": 3,
                    "mechanics_score": 3,
                    "overall_score": 3,
                    "content_feedback": "Unable to provide detailed feedback on content. Please try again.",
                    "organization_feedback": "Unable to provide detailed feedback on organization. Please try again.",
                    "language_feedback": "Unable to provide detailed feedback on language use. Please try again.",
                    "mechanics_feedback": "Unable to provide detailed feedback on mechanics. Please try again.",
                    "overall_feedback": "Unable to provide detailed overall feedback. Please try again.",
                    "improved_introduction": "Unable to provide an improved introduction. Please try again.",
                    "improved_conclusion": "Unable to provide an improved conclusion. Please try again."
                }
                
                return fallback_result
        except Exception as e:
            print(f"Error evaluating essay: {e}")
            return None
    
    def display_prompt(self, prompt):
        print("\n" + "=" * 80)
        print(f"Essay Type: {prompt['essay_type']} | Topic: {prompt['topic']}\n")
        print(f"Title: {prompt['essay_title']}\n")
        print("Essay Prompt:")
        print(prompt['essay_prompt'])
        print(f"\nWord Count: {prompt['word_count']} words | Time Limit: {prompt['time_limit']} minutes")
        print("\nKey Points to Address:")
        for i, point in enumerate(prompt['key_points']):
            print(f"{i+1}. {point}")
        print("\n" + "=" * 80)
    
    def display_evaluation(self, evaluation):
        print("\n" + "=" * 80)
        print("Essay Evaluation")
        print("=" * 80)
        
        print(f"Content & Development: {evaluation['content_score']}/5")
        print(evaluation['content_feedback'])
        print()
        
        print(f"Organization: {evaluation['organization_score']}/5")
        print(evaluation['organization_feedback'])
        print()
        
        print(f"Language Use: {evaluation['language_score']}/5")
        print(evaluation['language_feedback'])
        print()
        
        print(f"Mechanics: {evaluation['mechanics_score']}/5")
        print(evaluation['mechanics_feedback'])
        print()
        
        print(f"Overall Score: {evaluation['overall_score']}/5")
        print(evaluation['overall_feedback'])
        print()
        
        print("Suggested Improvements:")
        print("\nImproved Introduction:")
        print(evaluation['improved_introduction'])
        print("\nImproved Conclusion:")
        print(evaluation['improved_conclusion'])
        
        print("\n" + "=" * 80)
        print()
        
        print(f"Organization: {evaluation['organization_score']}/5")
        print(evaluation['organization_feedback'])
        print()
        
        print(f"Language Use: {evaluation['language_score']}/5")
        print(evaluation['language_feedback'])
        print()
        
        print(f"Mechanics: {evaluation['mechanics_score']}/5")
        print(evaluation['mechanics_feedback'])
        print()
        
        print(f"Overall Score: {evaluation['overall_score']}/5")
        print(evaluation['overall_feedback'])
        print()
        
        print("Suggested Improvements:")
        print("\nImproved Introduction:")
        print(evaluation['improved_introduction'])
        print("\nImproved Conclusion:")
        print(evaluation['improved_conclusion'])
        
        print("\n" + "=" * 80)
    
    def practice_session(self, topic=None, essay_type=None):
        if not self.client and not self.setup_api():
            return
        
        session = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "essay": None,
            "scores": None
        }
        
        print(f"\nGenerating essay prompt...")
        prompt = self.generate_essay_prompt(topic, essay_type)
        
        if not prompt:
            print("Failed to generate essay prompt. Exiting session.")
            return
        
        self.display_prompt(prompt)
        
        # Record start time
        start_time = time.time()
        
        # Get user essay
        print("\nWrite your essay below. Press Enter twice when you're finished.")
        print("(To exit without submitting, type 'q' on a new line and press Enter)")
        print("\n" + "-" * 40)
        
        lines = []
        while True:
            line = input()
            if line.lower() == 'q' and not lines:
                print("\nSession ended without submission.")
                return
            if not line and lines and not lines[-1]:
                break
            lines.append(line)
        
        essay = "\n".join(lines)
        
        # Record end time and calculate duration
        end_time = time.time()
        duration_minutes = (end_time - start_time) / 60
        
        if not essay.strip():
            print("No essay provided. Exiting session.")
            return
        
        # Word count
        word_count = len(essay.split())
        
        print(f"\nEssay submitted! Word count: {word_count} words")
        print(f"Time taken: {duration_minutes:.1f} minutes")
        
        # Evaluate the essay
        print("\nEvaluating your essay...")
        evaluation = self.evaluate_essay(essay, prompt)
        
        if not evaluation:
            print("Failed to evaluate essay. Exiting session.")
            return
        
        self.display_evaluation(evaluation)
        
        # Record result
        session["essay"] = {
            "prompt": prompt,
            "text": essay,
            "word_count": word_count,
            "duration_minutes": duration_minutes
        }
        
        session["scores"] = {
            "content_score": evaluation['content_score'],
            "organization_score": evaluation['organization_score'],
            "language_score": evaluation['language_score'],
            "mechanics_score": evaluation['mechanics_score'],
            "overall_score": evaluation['overall_score']
        }
        
        # Update history
        self.history['sessions'].append(session)
        self.history['total_essays'] += 1
        self.save_history()
        
        # Show session summary
        print("\n" + "=" * 80)
        print(f"Session Summary:")
        print(f"Topic: {prompt['topic']} | Essay Type: {prompt['essay_type']}")
        print(f"Word Count: {word_count}/{prompt['word_count']} words")
        print(f"Time Taken: {duration_minutes:.1f}/{prompt['time_limit']} minutes")
        print(f"Overall Score: {evaluation['overall_score']}/5")
        print("=" * 80)
    
    def show_stats(self):
        print("\n" + "=" * 80)
        print("TOEIC Essay Practice Statistics")
        print("=" * 80)
        
        if not self.history['sessions']:
            print("No practice sessions recorded yet.")
            return
        
        # Overall stats
        total_sessions = len(self.history['sessions'])
        total_essays = self.history['total_essays']
        
        print(f"Total Sessions: {total_sessions}")
        print(f"Total Essays Written: {total_essays}")
        
        # Calculate average scores
        avg_content = sum(session['scores']['content_score'] for session in self.history['sessions']) / total_sessions
        avg_organization = sum(session['scores']['organization_score'] for session in self.history['sessions']) / total_sessions
        avg_language = sum(session['scores']['language_score'] for session in self.history['sessions']) / total_sessions
        avg_mechanics = sum(session['scores']['mechanics_score'] for session in self.history['sessions']) / total_sessions
        avg_overall = sum(session['scores']['overall_score'] for session in self.history['sessions']) / total_sessions
        
        print("\nAverage Scores:")
        print(f"Content & Development: {avg_content:.1f}/5")
        print(f"Organization: {avg_organization:.1f}/5")
        print(f"Language Use: {avg_language:.1f}/5")
        print(f"Mechanics: {avg_mechanics:.1f}/5")
        print(f"Overall: {avg_overall:.1f}/5")
        
        # Stats by topic
        topic_stats = {}
        for session in self.history['sessions']:
            topic = session['essay']['prompt']['topic']
            if topic not in topic_stats:
                topic_stats[topic] = {'total_score': 0, 'count': 0}
            
            topic_stats[topic]['total_score'] += session['scores']['overall_score']
            topic_stats[topic]['count'] += 1
        
        print("\nPerformance by Topic:")
        for topic, stats in topic_stats.items():
            if stats['count'] > 0:
                avg_score = stats['total_score'] / stats['count']
                print(f"{topic}: {avg_score:.1f}/5 ({stats['count']} essays)")
        
        # Stats by essay type
        type_stats = {}
        for session in self.history['sessions']:
            essay_type = session['essay']['prompt']['essay_type']
            if essay_type not in type_stats:
                type_stats[essay_type] = {'total_score': 0, 'count': 0}
            
            type_stats[essay_type]['total_score'] += session['scores']['overall_score']
            type_stats[essay_type]['count'] += 1
        
        print("\nPerformance by Essay Type:")
        for essay_type, stats in type_stats.items():
            if stats['count'] > 0:
                avg_score = stats['total_score'] / stats['count']
                print(f"{essay_type}: {avg_score:.1f}/5 ({stats['count']} essays)")
        
        # Recent sessions
        print("\nRecent Sessions:")
        recent_sessions = self.history['sessions'][-5:] if len(self.history['sessions']) > 5 else self.history['sessions']
        recent_sessions.reverse()  # Show most recent first
        
        for i, session in enumerate(recent_sessions):
            if session['essay']:
                topic = session['essay']['prompt']['topic']
                essay_type = session['essay']['prompt']['essay_type']
                word_count = session['essay']['word_count']
                overall_score = session['scores']['overall_score']
                print(f"{i+1}. {session['date']}: {essay_type} essay on {topic}, {word_count} words, Score: {overall_score}/5")
            else:
                print(f"{i+1}. {session['date']}: No essay completed")
        
        print("=" * 80)


def main():
    practice = TOEICEssayPractice()
    
    while True:
        print("\n" + "=" * 80)
        print("TOEIC Essay Writing Practice (Question 8)")
        print("=" * 80)
        print("1. Start a practice session")
        print("2. View statistics")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == '1':
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
            
            # Ask for essay type preference
            print("\nEssay Type:")
            print("1. Random (default)")
            for i, essay_type in enumerate(practice.essay_types):
                print(f"{i+2}. {essay_type}")
            
            type_choice = input(f"\nEnter your choice (1-{len(practice.essay_types)+1}): ") or "1"
            essay_type = None
            if type_choice != "1" and type_choice.isdigit():
                type_idx = int(type_choice) - 2
                if 0 <= type_idx < len(practice.essay_types):
                    essay_type = practice.essay_types[type_idx]
            
            # Start practice session
            practice.practice_session(topic, essay_type)
            
        elif choice == '2':
            practice.show_stats()
            
        elif choice == '3':
            print("\nThank you for practicing TOEIC Essay Writing!")
            break
            
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()