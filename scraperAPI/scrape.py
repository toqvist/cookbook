from recipe_scrapers import scrape_me
import os
import logging
from git import Repo
import subprocess
import sys

arguments = sys.argv

request_body = {
    'url': arguments[0],
    'push_to_repo': 'true'
}

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
  repo.git.add(f"{recipe_path}/{filename}")

  commit_message = f"Add recipe: {title}"
  repo.git.commit("-m", commit_message)

  origin.push(force=True)