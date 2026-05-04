import os
import random

# List of jokes
jokes = [
    "Why don't scientists trust atoms? Because they make up everything.",
    "Why don't eggs tell jokes? They'd crack each other up!",
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "What do you call a fake noodle? An impasta.",
    "Why did the scarecrow win an award? Because he was outstanding in his field.",
    "Why don't lobsters share? Because they're shellfish.",
    "What do you call a can opener that doesn't work? A can't opener.",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "Why don't some couples go to the gym? Because some relationships don't work out.",
    "What do you call a bear with no socks on? Barefoot.",
]

# Create folder if it doesn't exist
if not os.path.exists('test_batch'):
    os.makedirs('test_batch')

# Create 5 new text files with random jokes
for i in range(5):
    filename = f'test_batch/joke_{i+1}.txt'
    with open(filename, 'w') as f:
        f.write(random.choice(jokes))