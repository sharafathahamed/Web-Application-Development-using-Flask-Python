from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import uuid
from models import init_db, get_db_connection

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

init_db()
@app.route('/')
def index():
    return redirect(url_for('products'))

@app.route('/products')
def products():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM Product ORDER BY product_id').fetchall()
    conn.close()
    return render_template('products.html', products=products)

@app.route('/add_product', methods=['POST'])
def add_product():
    product_id = request.form['product_id']
    name = request.form['name']
    
    if not product_id or not name:
        flash('Product ID and Name are required!', 'error')
        return redirect(url_for('products'))
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Product (product_id, name) VALUES (?, ?)', 
                    (product_id, name))
        conn.commit()
        flash('Product added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Product ID already exists!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('products'))

@app.route('/edit_product/<product_id>', methods=['POST'])
def edit_product(product_id):
    new_name = request.form['name']
    
    if not new_name:
        flash('Product name is required!', 'error')
        return redirect(url_for('products'))
    
    conn = get_db_connection()
    conn.execute('UPDATE Product SET name = ? WHERE product_id = ?', 
                (new_name, product_id))
    conn.commit()
    conn.close()
    
    flash('Product updated successfully!', 'success')
    return redirect(url_for('products'))

@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Product WHERE product_id = ?', (product_id,))
    conn.commit()
    conn.close()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('products'))

@app.route('/locations')
def locations():
    conn = get_db_connection()
    locations = conn.execute('SELECT * FROM Location ORDER BY location_id').fetchall()
    conn.close()
    return render_template('locations.html', locations=locations)

@app.route('/add_location', methods=['POST'])
def add_location():
    location_id = request.form['location_id']
    name = request.form['name']
    
    if not location_id or not name:
        flash('Location ID and Name are required!', 'error')
        return redirect(url_for('locations'))
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT INTO Location (location_id, name) VALUES (?, ?)', 
                    (location_id, name))
        conn.commit()
        flash('Location added successfully!', 'success')
    except sqlite3.IntegrityError:
        flash('Location ID already exists!', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('locations'))

@app.route('/edit_location/<location_id>', methods=['POST'])
def edit_location(location_id):
    new_name = request.form['name']
    
    if not new_name:
        flash('Location name is required!', 'error')
        return redirect(url_for('locations'))
    
    conn = get_db_connection()
    conn.execute('UPDATE Location SET name = ? WHERE location_id = ?', 
                (new_name, location_id))
    conn.commit()
    conn.close()
    
    flash('Location updated successfully!', 'success')
    return redirect(url_for('locations'))

@app.route('/delete_location/<location_id>')
def delete_location(location_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM Location WHERE location_id = ?', (location_id,))
    conn.commit()
    conn.close()
    
    flash('Location deleted successfully!', 'success')
    return redirect(url_for('locations'))

@app.route('/movements')
def movements():
    conn = get_db_connection()
    movements = conn.execute('''
        SELECT pm.*, p.name as product_name, 
               fl.name as from_location_name, 
               tl.name as to_location_name
        FROM ProductMovement pm
        LEFT JOIN Product p ON pm.product_id = p.product_id
        LEFT JOIN Location fl ON pm.from_location = fl.location_id
        LEFT JOIN Location tl ON pm.to_location = tl.location_id
        ORDER BY pm.timestamp DESC
    ''').fetchall()
    
    products = conn.execute('SELECT * FROM Product').fetchall()
    locations = conn.execute('SELECT * FROM Location').fetchall()
    conn.close()
    
    return render_template('movements.html', 
                         movements=movements, 
                         products=products, 
                         locations=locations)

@app.route('/add_movement', methods=['POST'])
def add_movement():
    movement_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    from_location = request.form['from_location'] or None
    to_location = request.form['to_location'] or None
    product_id = request.form['product_id']
    qty = int(request.form['qty'])
    
    if not product_id or not qty or qty <= 0:
        flash('Product and valid quantity are required!', 'error')
        return redirect(url_for('movements'))
    
    if not from_location and not to_location:
        flash('Either From Location or To Location must be specified!', 'error')
        return redirect(url_for('movements'))
    
    conn = get_db_connection()
    try:
        conn.execute('''
            INSERT INTO ProductMovement 
            (movement_id, timestamp, from_location, to_location, product_id, qty) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (movement_id, timestamp, from_location, to_location, product_id, qty))
        conn.commit()
        flash('Movement added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding movement: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('movements'))

@app.route('/edit_movement/<movement_id>')
def edit_movement(movement_id):
    conn = get_db_connection()
    movement = conn.execute('''
        SELECT * FROM ProductMovement WHERE movement_id = ?
    ''', (movement_id,)).fetchone()
    
    products = conn.execute('SELECT * FROM Product').fetchall()
    locations = conn.execute('SELECT * FROM Location').fetchall()
    conn.close()
    
    return render_template('edit_movement.html', 
                         movement=movement, 
                         products=products, 
                         locations=locations)

@app.route('/update_movement/<movement_id>', methods=['POST'])
def update_movement(movement_id):
    from_location = request.form['from_location'] or None
    to_location = request.form['to_location'] or None
    product_id = request.form['product_id']
    qty = int(request.form['qty'])
    
    if not product_id or not qty or qty <= 0:
        flash('Product and valid quantity are required!', 'error')
        return redirect(url_for('edit_movement', movement_id=movement_id))
    
    if not from_location and not to_location:
        flash('Either From Location or To Location must be specified!', 'error')
        return redirect(url_for('edit_movement', movement_id=movement_id))
    
    conn = get_db_connection()
    try:
        conn.execute('''
            UPDATE ProductMovement 
            SET from_location = ?, to_location = ?, product_id = ?, qty = ?
            WHERE movement_id = ?
        ''', (from_location, to_location, product_id, qty, movement_id))
        conn.commit()
        flash('Movement updated successfully!', 'success')
    except Exception as e:
        flash(f'Error updating movement: {str(e)}', 'error')
    finally:
        conn.close()
    
    return redirect(url_for('movements'))

@app.route('/delete_movement/<movement_id>')
def delete_movement(movement_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM ProductMovement WHERE movement_id = ?', (movement_id,))
    conn.commit()
    conn.close()
    
    flash('Movement deleted successfully!', 'success')
    return redirect(url_for('movements'))

@app.route('/balance')
def balance():
    conn = get_db_connection()
    
    balance_data = conn.execute('''
        WITH movements AS (
            SELECT 
                product_id,
                to_location as location,
                qty as positive_qty,
                0 as negative_qty
            FROM ProductMovement
            WHERE to_location IS NOT NULL
            
            UNION ALL
            
            SELECT 
                product_id,
                from_location as location,
                0 as positive_qty,
                qty as negative_qty
            FROM ProductMovement
            WHERE from_location IS NOT NULL
        )
        SELECT 
            p.product_id,
            p.name as product_name,
            l.location_id,
            l.name as location_name,
            COALESCE(SUM(m.positive_qty), 0) - COALESCE(SUM(m.negative_qty), 0) as balance
        FROM Product p
        CROSS JOIN Location l
        LEFT JOIN movements m ON p.product_id = m.product_id AND l.location_id = m.location
        GROUP BY p.product_id, l.location_id
        HAVING balance > 0
        ORDER BY p.name, l.name
    ''').fetchall()
    
    conn.close()
    
    return render_template('balance.html', balance_data=balance_data)

if __name__ == '__main__':

    app.run(debug=True)
