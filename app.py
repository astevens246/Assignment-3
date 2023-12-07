from flask import Flask, request, render_template
from PIL import Image, ImageFilter
from pprint import PrettyPrinter
from dotenv import load_dotenv
import json
import os
import random
import requests

load_dotenv()


app = Flask(__name__)

@app.route('/')
def homepage():
    """A homepage with handy links for your convenience."""
    return render_template('home.html')

################################################################################
# COMPLIMENTS ROUTES
################################################################################

list_of_compliments = [
    'awesome',
    'beatific',
    'blithesome',
    'conscientious',
    'coruscant',
    'erudite',
    'exquisite',
    'fabulous',
    'fantastic',
    'gorgeous',
    'indubitable',
    'ineffable',
    'magnificent',
    'outstanding',
    'propitioius',
    'remarkable',
    'spectacular',
    'splendiferous',
    'stupendous',
    'super',
    'upbeat',
    'wondrous',
    'zoetic'
]

@app.route('/compliments')
def compliments():
    """Shows the user a form to get compliments."""
    return render_template('compliments_form.html')

@app.route('/compliments_results', methods=['POST'])
def compliments_results():
    if request.method == 'POST':
        # Get data from the form
        user_name = request.form.get('user_name')
        want_compliments = request.form.get('want_compliments', 'no')  # Default to 'no' if not provided
        num_compliments = int(request.form.get('num_compliments'))

        # Print statements for debugging
        print(f'user_name: {user_name}, want_compliments: {want_compliments}, num_compliments: {num_compliments}')

        # Greet the user by name
        greeting = f'Hi {user_name}!'

        # Check if user wants compliments
        compliments_list = []
        if want_compliments == 'yes':
            # Choose random compliments from the list
            compliments_list = random.sample(list_of_compliments, num_compliments)

        context = {
            'greeting': greeting,
            'want_compliments': want_compliments,  # Add this line to pass want_compliments to the template
            'compliments_list': compliments_list,
        }

        return render_template('compliments_results.html', **context)


################################################################################
# ANIMAL FACTS ROUTE
################################################################################

animal_to_fact = {
    'koala': 'Koala fingerprints are so close to humans\' that they could taint crime scenes.',
    'parrot': 'Parrots will selflessly help each other out.',
    'mantis shrimp': 'The mantis shrimp has the world\'s fastest punch.',
    'lion': 'Female lions do 90 percent of the hunting.',
    'narwhal': 'Narwhal tusks are really an "inside out" tooth.'
}

@app.route('/animal_facts', methods=['GET', 'POST'])
def animal_facts():
    """Show a form to choose an animal and receive facts."""

    all_animals = list(animal_to_fact.keys())
    
    chosen_animal = None
    chosen_fact = None
    
    if request.method == 'POST':
        chosen_animal = request.form.get('animal')
        
        if chosen_animal in animal_to_fact:
            chosen_fact = animal_to_fact.get(chosen_animal)

    context = {
        'all_animals': all_animals,
        'chosen_animal': chosen_animal,
        'chosen_fact': chosen_fact
    }
    return render_template('animal_facts.html', **context)

if __name__ == '__main__':
    app.run(debug=True)


################################################################################
# IMAGE FILTER ROUTE
################################################################################

filter_types_dict = {
    'blur': ImageFilter.BLUR,
    'contour': ImageFilter.CONTOUR,
    'detail': ImageFilter.DETAIL,
    'edge enhance': ImageFilter.EDGE_ENHANCE,
    'emboss': ImageFilter.EMBOSS,
    'sharpen': ImageFilter.SHARPEN,
    'smooth': ImageFilter.SMOOTH
}

def save_image(image, filter_type):
    """Save the image, then return the full file path of the saved image."""
    # Append the filter type at the beginning (in case the user wants to 
    # apply multiple filters to 1 image, there won't be a name conflict)
    new_file_name = f"{filter_type}-{image.filename}"
    image.filename = new_file_name

    # Construct full file path
    file_path = os.path.join(app.root_path, 'static/images', new_file_name)
    
    # Save the image
    image.save(file_path)

    return file_path


def apply_filter(file_path, filter_name):
    """Apply a Pillow filter to a saved image."""
    i = Image.open(file_path)
    i.thumbnail((500, 500))
    i = i.filter(filter_types_dict.get(filter_name))
    i.save(file_path)

@app.route('/image_filter', methods=['GET', 'POST'])
def image_filter():
    """Filter an image uploaded by the user, using the Pillow library."""
    filter_types = list(filter_types_dict.keys())

    if request.method == 'POST':
        # Get the user's chosen filter type
        filter_type = request.form.get('filter_type')

        # Get the image file submitted by the user
        image = request.files.get('users_image')

        if image:
            # Save the image and get the file path
            file_path = save_image(image, filter_type)

            # Apply the selected filter to the image
            apply_filter(file_path, filter_type)

            # Construct the correct image URL for rendering
            image_url = f'/static/images/{image.filename}'

            context = {
                'filter_types': filter_types,
                'image_url': image_url,
            }

            return render_template('image_filter.html', **context)

    # If it's a GET request or there was an issue with the POST request
    context = {
        'filter_types': filter_types,
    }
    return render_template('image_filter.html', **context)

################################################################################
# GIF SEARCH ROUTE
################################################################################
# The Tenor website said that it no longer supports VI API Key registration so I just used the API key from the example

"""You'll be using the Tenor API for this next section. 
Be sure to take a look at their API. 

https://tenor.com/gifapi/documentation

Register and make an API key for yourself. 
Set up dotenv, create a .env file and define a variable 
API_KEY with a value that is the api key for your account. """

API_KEY = os.getenv('API_KEY')
print(API_KEY)

TENOR_URL = 'https://api.tenor.com/v1/search'
pp = PrettyPrinter(indent=4)

@app.route('/gif_search', methods=['GET', 'POST'])
def gif_search():
    """Show a form to search for GIFs and show resulting GIFs from Tenor API."""
    if request.method == 'POST':
        # TODO: Get the search query & number of GIFs requested by the user, store each as a 
        # variable
        search_query = request.form.get('search_query')
        quantity = int(request.form.get('quantity', 5))
        
        # make the API request to Tenor
        response = requests.get(
            TENOR_URL,
            {
                # TODO: Add in key-value pairs for:
                #'q': search_query
                #'key': the API key (defined above)
                #'limit': the number of GIFs requested
            })

        gifs = json.loads(response.content).get('results')

        context = {
            'gifs': gifs
        }

         # Uncomment me to see the result JSON!
        # Look closely at the response! It's a list
        # list of data. The media property contains a 
        # list of media objects. Get the gif and use it's 
        # url in your template to display the gif. 
        # pp.pprint(gifs)

        return render_template('gif_search.html', **context)
    else:
        return render_template('gif_search.html')

if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
