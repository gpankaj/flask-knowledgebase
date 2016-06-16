from flask import jsonify, request, url_for
from . import api
import jsonpickle,json

from flask.ext.jsontools import jsonapi


@api.route('/blogs',methods=['POST'])
def set_blog():
    from ..model import Blog
    blog = Blog().from_json(request.json)
    from src.model import db
    db.session.add(blog)
    db.session.commit()
    response = jsonify({})
    response.status_code = 201
    response.headers['Location'] = blog.get_url()
    return response

@api.route('/blog/<int:blog_id>',methods=['GET'])
@jsonapi
def get_blog(blog_id):

    #print "Checking for " + blog_id
    from ..model import Blog
    blog = Blog.query.get_or_404(blog_id)
    #return jsonpickle.encode(blog)
    #return json.dumps(blog, default=lambda o: o.__dict__)
    #return json.dumps({'answer': blog.answer})

    return blog






"""
    for property in object.__dict__.keys():
        #import re
        #matchObj = re.match(r'^_$', property)
        print property
        props= property.split('_')

        if(props[0]):
            convert_to_dict[property] = Blog.__dict__[property]
    return convert_to_dict
"""
