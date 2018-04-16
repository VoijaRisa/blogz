from flask import Flask, request, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:launchcode@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "k4g1w4h1m1t5ud35u"

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    post_list = Blog.query.all()
    
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        
        if title == "" or body == "":
            return render_template('newpost.html', returned_title=title, returned_body=body, error="Please ensure all boxes are filled in.", page_title="Add a Post")
        
        new_post = Blog(title, body)
        db.session.add(new_post)
        db.session.commit()

        id = str(len(post_list) + 1)
                
        return redirect('blog?id=' + id)
    
    elif request.method == 'GET':
        id = str(request.args.get('id'))
        print("ID IS" + id)
        if id != "None":
            single_post = Blog.query.get(id)
            return render_template('blog.html', post_list=post_list, single_post=single_post, id=id, page_title="My Blog")
        else:
            return render_template('blog.html', post_list=post_list, id="all", page_title="My Blog")

@app.route('/newpost')
def newpost():
    return render_template('newpost.html', page_title="Add a Post")

if __name__ == '__main__':
    app.run()