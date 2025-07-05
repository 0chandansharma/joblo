import asyncio
from typing import Optional
from .job_agent import JobAgent
import logging
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
console = Console()


class JobAssistantCLI:
    def __init__(self):
        self.agent = None
        self.console = console
        
    def initialize(self):
        """Initialize the job agent"""
        self.console.print("[yellow]Initializing JobLo Assistant...[/yellow]")
        try:
            self.agent = JobAgent()
            self.console.print("[green]✓ JobLo Assistant initialized successfully![/green]")
            return True
        except Exception as e:
            self.console.print(f"[red]Error initializing agent: {e}[/red]")
            return False
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
# Welcome to JobLo Assistant! 🚀

I'm your intelligent job search assistant. I can help you:
- Search for jobs based on your criteria
- Find remote jobs in specific locations
- Match jobs to your skills and experience
- Answer questions about the job market

## Sample queries:
- "Find remote data scientist jobs in Bangalore"
- "Show me software engineer positions requiring Python"
- "What jobs are available for freshers?"
- "Find jobs at top tech companies"

Type 'help' for more commands or 'exit' to quit.
        """
        self.console.print(Panel(Markdown(welcome_text), title="JobLo Assistant", border_style="blue"))
    
    def display_help(self):
        """Display help information"""
        help_text = """
## Available Commands:
- **search <query>**: Search for jobs (e.g., 'search python developer bangalore')
- **count**: Get total number of jobs in database
- **clear**: Clear the conversation history
- **help**: Show this help message
- **exit/quit**: Exit the assistant

## Query Examples:
- Natural language: "Find remote jobs for data scientists"
- Skill-based: "Jobs requiring React and Node.js"
- Experience-based: "Entry level software engineer positions"
- Location-based: "Jobs in Mumbai for backend developers"
        """
        self.console.print(Panel(Markdown(help_text), title="Help", border_style="green"))
    
    def run(self):
        """Run the CLI interface"""
        if not self.initialize():
            return
        
        self.display_welcome()
        
        while True:
            try:
                user_input = Prompt.ask("\n[cyan]You[/cyan]")
                
                if not user_input.strip():
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self.console.print("[yellow]Thank you for using JobLo Assistant! Goodbye! 👋[/yellow]")
                    break
                
                if user_input.lower() == 'help':
                    self.display_help()
                    continue
                
                if user_input.lower() == 'clear':
                    self.console.clear()
                    self.display_welcome()
                    continue
                
                if user_input.lower() == 'count':
                    response = self.agent.chat("How many jobs are in the database?")
                else:
                    response = self.agent.chat(user_input)
                
                self.console.print(Panel(
                    Markdown(response),
                    title="JobLo Assistant",
                    border_style="green",
                    padding=(1, 2)
                ))
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Use 'exit' to quit properly.[/yellow]")
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                logger.error(f"Error in CLI: {e}")


def main():
    """Main entry point for CLI"""
    cli = JobAssistantCLI()
    cli.run()


if __name__ == "__main__":
    main()