from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import errorcode

app = Flask(__name__)

# Set up your MySQL connection
def get_db_connection():
    return mysql.connector.connect(
            host='localhost',
            user="root",
            password="eaaw6N+}",
            database="junaid_jamshed"
    )
    
@app.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('query', '')

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("use junaid_jamshed;")
    query = """
    SELECT link, code,
    MATCH(link, `Fabric Type`, Neckline, Collection, Trouser, Sleeves, Embellishment, Color, Shirt, Dupatta)
    AGAINST(%s IN NATURAL LANGUAGE MODE) AS relevance
    FROM products
    ORDER BY relevance DESC
    LIMIT 10;
    """
    print("Query: ", search_query)
    cursor.execute(query, (search_query,))
    results = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return jsonify(results)


if __name__ == '__main__':
    print("Starting Flask app...")
    app.run(debug=True)
    print("Flask app started.")


