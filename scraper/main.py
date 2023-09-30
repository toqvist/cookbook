from flask import Flask, request
from recipe_scrapers import scrape_me
import dotenv
import os

app = Flask(__name__)
recipe_directory = '../cookbook/src/recipes'

dotenv.load_dotenv()  # Load environment variables from .env

API_KEY = os.getenv("API_KEY")

@app.route('/', methods=['POST'])
def home():
    request_body = request.get_json()
    scraper = scrape_me(
        request_body['url'], wild_mode=True)

    scraper.host()
    scraper.title()
    scraper.total_time()
    scraper.image()
    scraper.ingredients()
    scraper.ingredient_groups()
    scraper.instructions()
    scraper.instructions_list()
    scraper.yields()
    scraper.to_json()
    scraper.links()
    scraper.nutrients()  # if available

    return scraper.to_json()


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
        f"time: {total_time}\n"
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

    # Saving to a markdown file
    with open(f"{recipe_directory}/{filename}", "w") as file:
        file.write(md_content)

    return scraper.to_json()

if __name__ == '__main__':
    app.run(debug=True)
