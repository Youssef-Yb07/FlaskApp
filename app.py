# import libraries
from flask import Flask, flash, request, redirect, url_for

# add the cors library so that the server can accept requests from the frontend
from flask_cors import CORS, cross_origin

# create the flask app
app = Flask(__name__)

# os library is used to save the file 
import os

# import the resume_parser file to extract the data from the resume
import resume_parser

# add the cors headers
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# create a route to test the server is working
@app.route('/hello')
@cross_origin()
def hello():
    return 'Hello, World!'


# create a route to upload the file and extract the data from the resume 
@app.route('/upload',methods=['POST'])
# annotate the function with the cross_origin decorator to allow the frontend to make requests to the server
@cross_origin()

# define the function to upload the file and extract the data from the resume
def upload_file():
    # check if the request method is POST
    if request.method == 'POST':
        # if if a post request, get the file from the request
        file = request.files['file']
        # print the file to check if the file is uploaded
        print(file)
        # save the file to the current directory
        new_path = os.path.join('./', file.filename)
        file.save(new_path)
        # call the extract_all_data function from the resume_parser file to extract the data from the resume
        # and give the path of the file as an argument
        return resume_parser.extract_all_data(new_path)
    
    # else return a message to upload the file
    return 'Please upload your file'


