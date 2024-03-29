from flask import Flask, request
from recipe_scrapers import scrape_me
import dotenv
import os
import logging
from git import Repo
import subprocess

app = Flask(__name__)
recipe_directory = '../cookbook/src/recipes'
recipe_path = 'cookbook/src/recipes'
git_directory = '..'

dotenv.load_dotenv()

SERVICE_MODE = os.getenv("SERVICE_MODE")
API_KEY = os.getenv("API_KEY")
GITHUB_ACCESS_TOKEN = os.getenv("GITHUB_ACCESS_TOKEN")

@app.route('/', methods=['GET'])
def home():
    return 'Hello', 200



@app.route('/dirs', methods=['POST'])
def log_directory_contents():
    
    request_body = request.get_json()
    directory_path = request_body['path']
    
    def print_item(item_name, indent=0):
        print("  " * indent + item_name)

    def traverse_directory(directory, indent=0):
        for item_name in os.listdir(directory):
            item_path = os.path.join(directory, item_name)
            print_item(item_name, indent)
            """ if os.path.isdir(item_path):
                traverse_directory(item_path, indent + 1) """

    print_item(f"[{os.path.basename(directory_path)}]")
    traverse_directory(directory_path)
    return 'Hello', 200

""" @app.route('/touch', methods=['GET'])
def touch():
    with open('touch.txt', 'w') as f:
        f.write('Touchy')
    if os.path.exists('touch.txt'):
        return 'File saved', 200
    else:
        return 'File not saved', 200
    
@app.route('/cat', methods=['POST'])
def cat():
    request_body = request.get_json()
    file_path = request_body['path']
    with open(file_path, 'r') as f:
        return f.read(), 200
        
 """

@app.route('/scrape', methods=['POST'])
def scrape():
    request_body = request.get_json()


    if SERVICE_MODE != 'development':
        if request_body['key'] != API_KEY:
            return f'Invalid API key: {request_body["key"]}', 400
        
    scraper = scrape_me(request_body['url'], wild_mode=True)

    host = scraper.host()
    title = scraper.title()
    total_time = scraper.total_time()
    image = scraper.image()
    ingredients = scraper.ingredients()
    instructions_list = scraper.instructions_list()

    yields = scraper.yields()
    if yields.endswith("servings"):
        yields = yields.replace("servings", "").strip()
    
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


    repo = Repo(git_directory)
    repository_url = f"https://{GITHUB_ACCESS_TOKEN}@github.com/toqvist/cookbook.git"
    
    if SERVICE_MODE != 'development':
        email = "tobias.ahlqvist@protonmail.com"
        username = "Tobias' Bot"

        os.environ["GIT_AUTHOR_NAME"] = username
        os.environ["GIT_AUTHOR_EMAIL"] = email
        os.environ["GIT_COMMITTER_NAME"] = username
        os.environ["GIT_COMMITTER_EMAIL"] = email
    
    origin = None
    for remote in repo.remotes:
        if remote.name == 'origin':
            origin = remote
            break

    if origin:
        origin.set_url(repository_url)
    else:
        origin = repo.create_remote('origin', repository_url)

    try:
        origin.pull()
    except Exception as e:
        print(f"Git pull error: {str(e)}")
        return str(f"Git pull error: {str(e)}"), 500 
    
    repo.git.checkout('main')
    
    # Saving to a markdown file
    try:
        with open(f"{recipe_directory}/{filename}", "w") as file:
            file.write(md_content)
            print(recipe_directory)
            if os.path.exists(f"{recipe_directory}/{filename}"):
                print("File saved")
            else:
                print("File not saved")
    except Exception as e:
        print(f"Error writing file: {str(e)}")

    if request_body['push_to_repo'] == 'true':
        try:
            repo.git.add(f"{recipe_path}/{filename}")

            commit_message = f"Add recipe: {title}"
            repo.git.commit("-m", commit_message)

            origin.push(force=True)

        except Exception as e:
            return str(e), 500
        
    return scraper.to_json(), 200


if __name__ == '__main__':
    app.run(debug=True)
