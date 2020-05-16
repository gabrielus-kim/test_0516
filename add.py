from flask import Flask, render_template

app=Flask(__name__,
        static_folder='static',
        template_folder='template')

app.config['ENV']='Development'
app.config['DEBUG']=True

@app.route('/')
def index():

    return render_template('template.html')


app.run(port='8001')