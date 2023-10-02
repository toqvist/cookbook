from flask import Flask, request
from recipe_scrapers import scrape_me
import dotenv
import os
from git import Repo
import subprocess

app = Flask(__name__)
recipe_directory = '../cookbook/src/recipes'

dotenv.load_dotenv()

API_KEY = os.getenv("API_KEY")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

@app.route('/', methods=['GET'])
def home():
    return 'Hello', 200


@app.route('/scrape', methods=['POST'])
def scrape():
    request_body = request.get_json()

    if request_body['key'] != API_KEY:
        return 'Invalid API key', 400
    
    scraper = scrape_me(request_body['url'], wild_mode=True)

    host = scraper.host()
    title = scraper.title()
    total_time = scraper.total_time()
    image = scraper.image()
    ingredients = scraper.ingredients()
    instructions_list = scraper.instructions_list()
    yields = scraper.yields()
    sourceURL = request_body['url']
    sourceLabel = host

    md_header = (
        f"---\n"
        f"title: {title}\n"
        f"image: {image}\n"
        f"tags:\n"
        f"time: {total_time} min\n"
        f"servings: {yields}\n"
        f"sourceLabel: {sourceLabel}\n"
        f"sourceURL: {sourceURL}\n"
        f"ingredients:\n"
    )
    md_ingredients = "\n".join(
        f"  - {ingredient}" for ingredient in ingredients)

    md_content = md_header + md_ingredients + "\n---\n"

    # Numbering and appending instructions to the markdown content
    instructions_str = "\n\n".join(
        f"{idx}. {instruction}" for idx, instruction in enumerate(instructions_list, 1))
    md_content += instructions_str + "\n\n"

    filename = title.lower().replace(" ", "-").split("(")[0].strip("-") + ".md"


    repo = Repo('..')
    repository_url = f"https://{GITHUB_ACCESS_TOKEN}@github.com/toqvist/cookbook.git"

    try:
        repo.create_remote('origin', repository_url)
        origin = repo.remote(name="origin")
    except  Exception as e:
        print(f"Remote creation failed. {str(e)}")
    
    try:
        origin.pull()
    except Exception as e:
        # Log the error message
        print(f"Git pull error: {str(e)}")
        return str(e), 50

    
    # Saving to a markdown file
    with open(f"{recipe_directory}/{filename}", "w") as file:
        file.write(md_content)

    try:
        repo.git.add(".")

        # Commit the changes with a descriptive message
        commit_message = f"Add recipe: {title}"
        repo.git.commit("-m", commit_message)

        # Push the changes to the remote repository (assuming origin and main branch)
        origin.push()

    except Exception as e:
        return str(e), 500  # Return an error message and status code 500 in case of an error
    
    return scraper.to_json(), 200

if __name__ == '__main__':
    app.run(debug=True)
