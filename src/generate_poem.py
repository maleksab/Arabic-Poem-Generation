
# ============================================
# Project 9: Arabic Poem Generation
# File: generate_poem.py
# Task 2: Generate poems using Llama 3
# ============================================

import ollama
from prompts import poem_prompt


def generate_poem(theme, style, length):
    """
    Generate an Arabic poem using Llama 3.
    """

    # Create the prompt
    prompt = poem_prompt(theme, style, length)

    # Send the prompt to Llama 3
    response = ollama.generate(
        model="llama3",
        prompt=prompt
    )

    # Extract the generated poem
    poem = response["response"]

    return poem


# ============================================
# Main program
# ============================================

if __name__ == "__main__":

    print("=== Arabic Poem Generator ===")

    # Get information from the user
    theme = input("Enter the poem theme: ")
    style = input("Enter the poem style: ")
    length = input("Enter the number of verses: ")

    # Generate the poem
    result = generate_poem(theme, style, length)

    # Display the result
    print("\n=== Generated Poem ===\n")
    print(result)
