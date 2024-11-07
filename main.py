from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
from docx import Document
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def init_ollama():
    return Ollama(
        model="llama3.2:1b", 
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
        temperature=0.7,
        num_ctx=2048,
        num_thread=4,
        timeout=60
    )

STORY_PROMPT = """
You are a master storyteller AI with deep knowledge of narrative structures. Create a captivating story based on the following structure. Each part should be unique and contribute to a well-rounded, engaging narrative.

Instructions:
- **Title:** A unique title representing the theme of the story.
- **Prologue:** Introduce the setting and main premise, giving readers a sense of the world and context.
- **Main Characters:** 
    - List each main character with their name, age, role, and brief description.
    - Briefly describe key traits, motivations, and relationships essential to the story arc.
- **Chapters:**
    - **Chapter 1:** Introduce the protagonist, setting, and initial situation.
    - **Chapter 2:** Present the main conflict or challenge faced by the protagonist.
    - **Chapter 3:** Show the development and complications leading up to the climax.
    - **Chapter 4:** Describe the climax with heightened tension and character decisions.
    - **Chapter 5:** Resolve the main conflict, showing the character's transformation.
    - **Chapter 6:** Epilogue that provides closure and hints at the protagonist's future.

Each paragraph should have a minimum of 5 sentences. Avoid repetition and ensure each section adds to the plot's progression.

**Additional Details:**
- Language: {language}
- Paragraphs: {num_paragraphs}
- Story Type: {story_type}
- Input Type: {input_type}
- Input Value: {input_value}
- Additional Instructions: {additional_instructions}

Focus on emotional depth, vivid imagery, and a logical narrative flow that immerses the reader in the story's journey.
"""

class StoryTellerAI:
    def __init__(self):
        self.llm = init_ollama()
        self.genres = [
            "Fantasy", "Science Fiction", "Mystery", "Romance",
            "Adventure", "Horror", "Historical Fiction", "Comedy", 
            "Thriller", "Drama", "Dystopian", "Paranormal",
            "Young Adult", "Children's Fiction", "Crime", "Superhero",
            "Western", "Slice of Life", "Fairy Tale", "Mythology",
            "Urban Fantasy", "Historical Romance", "Psychological Thriller", 
            "Dark Fantasy", "Epic Fantasy", "Space Opera", "Post-Apocalyptic",
            "Steampunk", "Cyberpunk", "Detective Fiction", "Medical Fiction",
            "Political Fiction", "Satire", "Military Fiction", "Gothic",
            "Spy Fiction", "Legal Thriller", "Biographical Fiction",
            "Coming of Age", "Family Saga", "Time Travel", "Road Trip"
        ]

    def get_user_preferences(self):
        concept = input("Enter a story concept (press Enter to skip): ").strip()
        title = "" if concept else input("Enter a story title (press Enter for genre selection): ").strip()
        
        if not concept and not title:
            print("\nAvailable genres:")
            for i, genre in enumerate(self.genres, 1):
                print(f"{i}. {genre}")
            genre_idx = int(input("\nSelect genre number: ")) - 1
            concept = f"A story in {self.genres[genre_idx]} genre"
        
        num_paragraphs = int(input("How many paragraphs do you want? (1-10): "))
        language = input("Enter preferred language (e.g., English, Spanish): ")
        
        return {
            "concept": concept,
            "title": title,
            "num_paragraphs": num_paragraphs,
            "language": language
        }
    
    def save_to_word(self, story, filename):
        doc = Document()
        doc.add_heading('AI Generated Story', 0)
        doc.add_paragraph(story)
        doc.save(f"{filename}.docx")
        print(f"\nStory saved to {filename}.docx")

    def save_to_pdf(self, story, filename):
        # Create PDF with A4 size
        c = canvas.Canvas(f"{filename}.pdf", pagesize=A4)
        
        # Add heading
        c.setFont("Helvetica-Bold", 24)
        c.drawString(50, A4[1] - 50, "AI Generated Story")
        
        # Initialize text object with margins
        text = c.beginText()
        text.setTextOrigin(50, A4[1] - 100)  # Adjusted for heading
        text.setFont("Helvetica", 12)
        text.setLeading(14)  # Line spacing
        
        # Split story into lines and handle page breaks
        lines = story.splitlines()
        for line in lines:
            # Wrap long lines
            words = line.split()
            current_line = []
            for word in words:
                current_line.append(word)
                # Check if current line width exceeds page width
                if c.stringWidth(' '.join(current_line), "Helvetica", 12) > A4[0] - 100:
                    current_line.pop()  # Remove last word
                    text.textLine(' '.join(current_line))
                    current_line = [word]  # Start new line with the word that didn't fit
                    
            # Add remaining words as a line
            if current_line:
                text.textLine(' '.join(current_line))
            
            # Check if we need a new page
            if text.getY() < 50:  # Bottom margin 50 points
                c.drawText(text)
                c.showPage()
                text = c.beginText()
                text.setTextOrigin(50, A4[1] - 50)
                text.setFont("Helvetica", 12)
                text.setLeading(14)
        
        # Draw remaining text and save
        c.drawText(text)
        c.save()
        print(f"\nStory saved to {filename}.pdf")

    def generate_story(self, preferences):
        try:
            prompt = PromptTemplate(
                template=STORY_PROMPT,
                input_variables=["input_type", "input_value", "story_type", "num_paragraphs", "language", "additional_instructions"]
            )
            
            story_prompt = prompt.format(
                input_type="concept" if preferences["concept"] else "title",
                input_value=preferences["concept"] if preferences["concept"] else preferences["title"],
                story_type="story",
                num_paragraphs=preferences["num_paragraphs"],
                language=preferences["language"],
                additional_instructions="Focus on emotional resonance and vivid storytelling"
            )
            
            story = self.llm(story_prompt)
            print("\nYour story:\n")
            print(story)

            save = input("\nWould you like to save this story? (word/pdf/no): ").lower()
            if save == "word":
                filename = input("Enter filename (without extension): ")
                self.save_to_word(story, filename)
            elif save == "pdf":
                filename = input("Enter filename (without extension): ")
                self.save_to_pdf(story, filename)
            
            return story
            
        except Exception as e:
            print(f"Error generating story: {str(e)}")
            return "Failed to generate story. Please try again."

def main():
    storyteller = StoryTellerAI()
    print("Welcome to AI Story Generator!")
    print("Welcome ke AI Story Generator!")
    print("=" * 50)
    
    while True:
        try:
            preferences = storyteller.get_user_preferences()
            print("\nGenerating your story...")
            print("\nMenghasilkan cerita Anda...")
            story = storyteller.generate_story(preferences)
            
            if input("\nGenerate another story? (y/n): ").lower() != 'y':
                break
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print(f"Terjadi kesalahan: {str(e)}")
            if input("\nTry again? (y/n): ").lower() != 'y':
                break
    
    print("\nThank you for using AI Story Generator!")
    print("\nTerima kasih telah menggunakan AI Story Generator!")

if __name__ == "__main__":
    main()
