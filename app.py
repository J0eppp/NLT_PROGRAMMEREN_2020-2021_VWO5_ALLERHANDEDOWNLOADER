import requests
from bs4 import BeautifulSoup
import json
import mysql.connector

f = open('./recipes.txt', 'r')
urls = [url.replace('\n', '') for url in f.readlines()]

recipes = []
blacklisted = ['g', 'el', 'tl', 'ml']

for url in urls:
	req = requests.get(url)
	soup = BeautifulSoup(req.text, 'html.parser')
	name = url.split('/')[-1]
	recipe = {
		'url': url,
		'name': name,
		'imageUrl': '',
		'ingredients': []
	}
	for img in soup.find_all('img', class_='print-only recipe-image'):
		recipe['imageUrl'] = img.get('src')
	for li in soup.find_all('li'):
		if li.get('itemprop') == 'ingredients':
			ingredient = li.getText().replace('\n', '')
			ingredient = ingredient.replace(''.join(filter(str.isdigit, ingredient)), '')
			if ingredient[0] == ' ':
				ingredient = ingredient[1:]
			for e in ingredient.split(' '):
				if e in blacklisted:
					ingredient = ingredient.replace(e, '')
					if ingredient[0] == ' ':
						ingredient = ingredient[1:]
			recipe['ingredients'].append(ingredient)
	recipes.append(recipe)

with open('./recipes.json', 'w+') as fo:
	json.dump(recipes, fo, indent=4, ensure_ascii=False)

db = mysql.connector.connect(host = 'localhost', user = 'ahRecipeFinder', password = 'Test123', database = 'ahRecipeFinder')
for recipe in recipes:
	cursor = db.cursor()
	sql = "INSERT INTO recipes (URL, imageURL, name, ingredients) VALUES (%s, %s, %s, %s)"
	ingredients = recipe['ingredients']
	i = ''
	for ingredient in ingredients:
		i += ingredient + ', '
	val = (recipe['url'], recipe['imageUrl'], recipe['name'], i)
	cursor.execute(sql, val)
	db.commit()