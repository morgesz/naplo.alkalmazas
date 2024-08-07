# app.py

from flask import Flask, render_template, redirect, url_for, flash, request, send_file, make_response
from models import db, NaploBejegyzes
from forms import NaploForm, ImportForm
import csv
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = 'titkos_kulcs'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    sort_by = request.args.get('sort_by', 'datum')
    order = request.args.get('order', 'desc')
    filter_text = request.args.get('filter', '')

    query = NaploBejegyzes.query

    if filter_text:
        query = query.filter(NaploBejegyzes.cim.contains(filter_text) | NaploBejegyzes.tartalom.contains(filter_text))

    if sort_by == 'cim':
        if order == 'asc':
            bejegyzesek = query.order_by(NaploBejegyzes.cim.asc()).all()
        else:
            bejegyzesek = query.order_by(NaploBejegyzes.cim.desc()).all()
    else:  # Default to sorting by date
        if order == 'asc':
            bejegyzesek = query.order_by(NaploBejegyzes.datum.asc()).all()
        else:
            bejegyzesek = query.order_by(NaploBejegyzes.datum.desc()).all()

    # Összegzés: bejegyzések száma
    bejegyzesek_szama = len(bejegyzesek)

    # Max elem kiválasztása: legutóbbi bejegyzés dátuma
    legutobbi_bejegyzes = max(bejegyzesek, key=lambda x: x.datum) if bejegyzesek else None

    # Átlag számítás: átlagos bejegyzés hossz
    atlagos_hossz = sum(len(b.tartalom) for b in bejegyzesek) / bejegyzesek_szama if bejegyzesek_szama > 0 else 0

    return render_template('index.html', bejegyzesek=bejegyzesek, sort_by=sort_by, order=order, filter=filter_text,
                           bejegyzesek_szama=bejegyzesek_szama, legutobbi_bejegyzes=legutobbi_bejegyzes, atlagos_hossz=atlagos_hossz)

@app.route('/new', methods=['GET', 'POST'])
def new_entry():
    form = NaploForm()
    if form.validate_on_submit():
        uj_bejegyzes = NaploBejegyzes(datum=form.datum.data, cim=form.cim.data, tartalom=form.tartalom.data)
        db.session.add(uj_bejegyzes)
        db.session.commit()
        flash('Bejegyzés hozzáadva!', 'success')
        return redirect(url_for('index'))
    return render_template('new_entry.html', form=form)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_entry(id):
    bejegyzes = NaploBejegyzes.query.get_or_404(id)
    form = NaploForm()
    if form.validate_on_submit():
        bejegyzes.datum = form.datum.data
        bejegyzes.cim = form.cim.data
        bejegyzes.tartalom = form.tartalom.data
        db.session.commit()
        flash('Bejegyzés frissítve!', 'success')
        return redirect(url_for('index'))
    elif request.method == 'GET':
        form.datum.data = bejegyzes.datum
        form.cim.data = bejegyzes.cim
        form.tartalom.data = bejegyzes.tartalom
    return render_template('edit_entry.html', form=form)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_entry(id):
    bejegyzes = NaploBejegyzes.query.get_or_404(id)
    db.session.delete(bejegyzes)
    db.session.commit()
    flash('Bejegyzés törölve!', 'success')
    return redirect(url_for('index'))

@app.route('/export', methods=['GET'])
def export_entries():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Dátum', 'Cím', 'Tartalom'])

    bejegyzesek = NaploBejegyzes.query.all()
    for bejegyzes in bejegyzesek:
        writer.writerow([bejegyzes.datum, bejegyzes.cim, bejegyzes.tartalom])

    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename=bejegyzesek.csv'
    response.headers['Content-type'] = 'text/csv'
    return response

@app.route('/import', methods=['GET', 'POST'])
def import_entries():
    form = ImportForm()
    if form.validate_on_submit():
        file = form.file.data
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.reader(stream)

        next(csv_input)  # Skip header row
        for row in csv_input:
            datum, cim, tartalom = row
            uj_bejegyzes = NaploBejegyzes(datum=datum, cim=cim, tartalom=tartalom)
            db.session.add(uj_bejegyzes)
        db.session.commit()
        flash('Bejegyzések importálva!', 'success')
        return redirect(url_for('index'))
    return render_template('import.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
