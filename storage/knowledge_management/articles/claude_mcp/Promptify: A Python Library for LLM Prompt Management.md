About a year ago, I was knee-deep in a project, trying to extract medical terms from patient records for a healthcare startup.

As a tech content writer, I’ve seen my fair share of coding tools, but wrangling NLP tasks with raw LLMs like GPT was a headache —Until I discovered Promptify.

This Python library, with its prompter, LLM integration, and pipeline, turned hours of prompt tweaking into a few lines of code.

In this article, I’ll share why Promptify feels like a breath of fresh air for anyone tackling NLP, explained simply with code examples.



What’s Promptify, Anyway?
You’ve got a chunk of text, say a medical report or a story snippet, and you need to pull out key details, classify topics, or generate questions. Normally, you’d spend ages crafting the perfect prompt for an LLM like GPT or PaLM.

Promptify changes that.

It’s a Python library that pairs a prompter (for crafting prompts), an LLM (like OpenAI’s models), and a pipeline to streamline NLP tasks.

From diagnosing medical conditions to generating quiz questions based on Alice in Wonderland, Promptify makes it feel effortless — not because you’re cheating, but because it’s smart coding.

Why I love it:

Dead Simple: Pre-built templates (or custom ones) mean you don’t need to be a prompt wizard.

Flexible: Handles tasks like named entity recognition (NER), classification, or question generation.

Works with What You’ve Got: Supports Python 3.7+, OpenAI 0.25+, and multiple LLMs.

Let’s get it set up and dive into some examples that sold me on it.

Setting Up Promptify
Installing Promptify is as easy as it gets. I ran this on my trusty Python 3.8 setup:

pip3 install promptify
Want the bleeding-edge version? Grab it from GitHub:

pip3 install git+https://github.com/promptslab/Promptify.git
With that done, you’re ready to play. You’ll need an API key for your LLM (I used OpenAI’s), but more on that later.

My Promptify Experiments
When I first tried Promptify, I was skeptical — could it really simplify my NLP struggles? I tested it with three tasks: extracting entities from a medical record, classifying health conditions, and generating questions from a story. Here’s what happened.

Example 1: Pulling Medical Entities (NER)
Back at that healthcare startup, I had a messy patient record to parse:

The patient is a 93-year-old female with a medical history of chronic right hip pain, osteoporosis, hypertension, depression, and chronic atrial fibrillation admitted for evaluation and management of severe nausea and vomiting and urinary tract infection.

I needed to extract ages, conditions, and symptoms. Here’s how Promptify nailed it:

from promptify import Prompter, OpenAI, Pipeline

# The patient record
sentence = """The patient is a 93-year-old female with a medical history of chronic right hip pain, osteoporosis, hypertension, depression, and chronic atrial fibrillation admitted for evaluation and management of severe nausea and vomiting and urinary tract infection"""
# Set up OpenAI (swap in your API key)
model = OpenAI("your_api_key_here")
# Pick the NER template
prompter = Prompter('ner.jinja')
# Create the pipeline
pipe = Pipeline(prompter, model)
# Run it
result = pipe.fit(sentence, domain="medical", labels=None)
# Check the results
print(result)
What I Got:

[
    {"E": "93-year-old", "T": "Age"},
    {"E": "chronic right hip pain", "T": "Medical Condition"},
    {"E": "osteoporosis", "T": "Medical Condition"},
    {"E": "hypertension", "T": "Medical Condition"},
    {"E": "depression", "T": "Medical Condition"},
    {"E": "chronic atrial fibrillation", "T": "Medical Condition"},
    {"E": "severe nausea and vomiting", "T": "Symptom"},
    {"E": "urinary tract infection", "T": "Medical Condition"},
    {"Branch": "Internal Medicine", "Group": "Geriatrics"}
]
This blew my mind. In minutes, I had a clean list of entities, plus the bonus of categorizing the case under Internal Medicine and Geriatrics. It saved me hours of manual tagging for the startup’s database.

Example 2: Classifying Medical Conditions
Next, I wanted to label the conditions in that same record and group them by medical domain. Here’s the code I used:

from promptify import OpenAI, Prompter

# Same patient record
sentence = """The patient is a 93-year-old female with a medical history of chronic right hip pain, osteoporosis, hypertension, depression, and chronic atrial fibrillation admitted for evaluation and management of severe nausea and vomiting and urinary tract infection"""
# Initialize the model
model = OpenAI("your_api_key_here")
# Set up the prompter
nlp_prompter = Prompter(model)
# Run multilabel classification
result = nlp_prompter.fit('multilabel_classification.jinja', domain='medical', text_input=sentence)
# See what came out
print(result)4
Output:

[
    {
        '1': 'Medicine',
        '2': 'Osteoporosis',
        '3': 'Hypertension',
        '4': 'Depression',
        '5': 'Atrial fibrillation',
        '6': 'Nausea and vomiting',
        '7': 'Urinary tract infection',
        'branch': 'Health',
        'group': 'Clinical medicine',
        'main class': 'Health'
    }
]
This was a lifesaver for organizing data. Each condition got a clear label, and the broader “Health” and “Clinical medicine” tags helped the team sort records for analysis. Honestly, I was grinning like a kid when I saw how clean this output was.

Example 3: Generating Story Questions
To mix things up, I tried Promptify on a creative task. I’m a bit of a book nerd, so I fed it a line from Alice in Wonderland:

The rabbit-hole went straight on like a tunnel for some way, and then dipped suddenly down, so suddenly that Alice had not a moment to think about stopping herself before she found herself falling down a very deep well.

I wanted questions for a book club quiz. Here’s what I ran:

from promptify import OpenAI, Prompter
# The story snippet
sentence = """The rabbit-hole went straight on like a tunnel for some way, and then dipped suddenly down, so suddenly that Alice had not a moment to think about stopping herself before she found herself falling down a very deep well."""
# Set up the model
model = OpenAI("your_api_key_here")
# Pick the question-answer template
nlp_prompter = Prompter(model)
# Generate questions
result = nlp_prompter.fit('qa_gen.jinja', domain='story_writing', text_input=sentence)
# Check the output
print(result)
Output:

[
    {'A': 'Alice found herself falling down a very deep well.', 'Q': 'What happened when Alice went down the rabbit-hole?'},
    {'A': 'Very deep.', 'Q': 'How deep was the well?'},
    {'A': 'No, she did not have a moment to think.', 'Q': 'Did Alice have time to think about stopping herself?'},
    {'A': 'It went straight on like a tunnel.', 'Q': 'What direction did the rabbit-hole go?'},
    {'A': 'No, she did not expect it.', 'Q': 'Did Alice expect to fall down a well?'}
]
I used these questions for a local book club, and they sparked a great discussion! Promptify turned a single sentence into a mini-quiz without me breaking a sweat.

Why Promptify Won Me Over
Look, I’ve written about tech tools for years, and I’m picky. Promptify hooked me because it’s like having a smart assistant who handles the boring stuff. Here’s why it’s worth your time:

Saves Brainpower: A few lines of code replace hours of prompt engineering.

Adapts to You: Use built-in templates or tweak your own for niche tasks.

Versatile as Heck: Medical data? Creative writing? It’s got you covered.

Plays Nice with LLMs: Swap between OpenAI, Hugging Face, or others without a fuss.

My only hiccup was grabbing an API key — OpenAI’s signup was quick, but don’t forget to check your LLM provider’s docs for that.

How to Jump In
Ready to try Promptify? Here’s my quick-and-dirty guide:

Install it with pip3 install promptify.

Get an API key (OpenAI’s a solid start).

Pick a template like ner.jinja or write your own.

Use the Pipeline or Prompter to process your text.

Mess around with the output — it’s super flexible.
