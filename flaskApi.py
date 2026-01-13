from flask import Flask , request , jsonify

app = Flask(__name__)

@app.route("/is_even/<int:n>")

def is_even(n):
    if n % 2 == 0:
        print(f"{n} is a even number.")
        result = {'Number': n ,
                  'result' : True,
                  'Author' : 'Rajat Singh', 
                  'list' : [0]}
        
    else:
        print(f"{n} is a even number.")
        result = {'Number': n ,
                  'result' : False,
                  'Author' : 'Rajat Singh'}
    
    return jsonify(result)
        


if __name__ == "__main__":
    app.run(debug=True)