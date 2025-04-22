import csv
import io

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file

from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///spots.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)


class SportsRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sport_name = db.Column(db.String(100), nullable=False)
    athlete_name = db.Column(db.String(100), nullable=False)
    event_date = db.Column(db.String(100), nullable=False)


@app.route('/')
def splash_home():
    return render_template('splash.html')


# @app.route('/home', methods=['GET', 'POST'])
# def home():
#     return render_template('home.html')


@app.route('/home', methods=['GET', 'POST'])
def scenic_spots():
    sport_name = request.args.get('sport_name')
    athlete_name = request.form.get('athlete_name')
    event_date = request.form.get('event_date')
    # 构建查询条件
    query = SportsRecord.query
    if sport_name:
        query = query.filter(SportsRecord.sport_name.like(f'%{sport_name}%'))
    if athlete_name:
        query = query.filter(SportsRecord.athlete_name.like(f'%{athlete_name}%'))
    if event_date:
        query = query.filter(SportsRecord.event_date.like(f'%{event_date}%'))
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    if sort_by:
        if sort_order == 'asc':
            query = query.order_by(getattr(SportsRecord, sort_by).asc())
        else:
            query = query.order_by(getattr(SportsRecord, sort_by).desc())
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            spot_id = request.form.get('spot_id')
            spot = SportsRecord.query.get(spot_id)
            if spot:
                db.session.delete(spot)
                db.session.commit()
                flash('景区已成功删除')
        elif action == 'sort':
            query = SportsRecord.query.order_by(SportsRecord.sport_name)
            spots = query.all()
            return render_template('scenic_sport.html', spots=spots)
        elif action == 'view_all':
            spots = SportsRecord.query.all()
            return render_template('scenic_sport.html', spots=spots)
        elif action == 'edit':
            return redirect(url_for('scenic_spots'))
        return redirect(url_for('scenic_spots'))
    spots = query.all()
    return render_template('scenic_sport.html', spots=spots, sort_by=sort_by, sort_order=sort_order)


@app.route('/add_scenic_spot', methods=['GET', 'POST'])
def add_scenic_spot():
    if request.method == 'POST':
        new_sport_name = request.form.get('sport_name')
        new_event_date = request.form.get('event_date')
        new_athlete_name = request.form.get('athlete_name')
        new_spot = SportsRecord(
            sport_name=new_sport_name,
            event_date=new_event_date,
            athlete_name=new_athlete_name
        )
        db.session.add(new_spot)
        db.session.commit()
        flash('景区已成功添加')
        return redirect(url_for('scenic_spots'))
    return render_template('add_scenic_spot.html')


@app.route('/edit/<int:spot_id>', methods=['GET', 'POST'])
def edit(spot_id):
    spot = SportsRecord.query.get(spot_id)
    if not spot:
        return jsonify({'message': '未找到该景区'}), 404
    return render_template('edit_scenic_sport.html', spot=spot)


@app.route('/edit_scenic_spot/<int:id>', methods=['GET', 'POST'])
def edit_scenic_spot(id):
    spot = SportsRecord.query.get_or_404(id)
    if request.method == 'POST':
        spot.sport_name = request.form['sport_name']
        spot.event_date = request.form['event_date']
        spot.athlete_name = request.form['athlete_name']
        db.session.commit()
        flash('景区已成功修改')
        return redirect(url_for('scenic_spots'))
    return render_template('edit_scenic_sport.html', spot=spot)


@app.route('/view_scenic_spot_details/<int:id>', methods=['GET'])
def view_scenic_spot_details(id):
    action = request.args.get('action')
    if action == 'add':
        return render_template('add_scenic_spot.html')
    spot = SportsRecord.query.get_or_404(id)
    return render_template('scenic_sport_details.html', spot=spot)


@app.route('/get_scenic_spot/<int:id>', methods=['GET'])
def get_scenic_spot(id):
    spot = SportsRecord.query.get_or_404(id)
    return jsonify({
        'sport_name': spot.sport_name,
        'event_date': spot.event_date,
        'athlete_name': spot.athlete_name
    })


@app.route('/search_scenic_spots', methods=['POST'])
def search_scenic_spots():
    sport_name = request.form.get('sport_name')
    athlete_name = request.form.get('athlete_name')
    event_date = request.form.get('event_date')

    # 构建查询条件
    query = SportsRecord.query
    if sport_name:
        query = query.filter(SportsRecord.sport_name.like(f'%{sport_name}%'))
    if athlete_name:
        query = query.filter(SportsRecord.athlete_name.like(f'%{athlete_name}%'))
    if event_date:
        query = query.filter(SportsRecord.event_date.like(f'%{event_date}%'))

    # 执行查询
    results = query.all()

    # 将查询结果转换为字典列表
    results_list = [{
        'id': spot.id,
        'sport_name': spot.sport_name,
        'event_date': spot.event_date,
        'athlete_name': spot.athlete_name
    } for spot in results]

    return jsonify(results_list)


@app.route('/search_results', methods=['POST'])
def search_results():
    sport_name = request.form.get('sport_name')
    athlete_name = request.form.get('athlete_name')
    event_date = request.form.get('event_date')

    # 构建查询条件
    query = SportsRecord.query
    if sport_name:
        query = query.filter(SportsRecord.sport_name.like(f'%{sport_name}%'))
    if athlete_name:
        query = query.filter(SportsRecord.athlete_name.like(f'%{athlete_name}%'))
    if event_date:
        query = query.filter(SportsRecord.event_date.like(f'%{event_date}%'))

    # 执行查询
    spots = query.all()

    return render_template('scenic_sport.html', spots=spots, sort_by=None, sort_order=None)


@app.route('/download_scenic_spots')
def download_scenic_spots():
    # 从数据库中获取所有的景区信息
    spots = SportsRecord.query.all()
    print(f"Number of spots retrieved from database: {len(spots)}")  # 打印获取的数据数量
    for spot in spots:
        print(f"Spot: {spot}")  # 打印每个景区信息

    # 创建一个 BytesIO 对象，用于存储 CSV 数据
    csv_buffer = io.BytesIO()
    # 将 BytesIO 对象包装为文本模式
    text_buffer = io.TextIOWrapper(csv_buffer, newline='')
    csv_writer = csv.writer(text_buffer)

    # 写入 CSV 文件的表头
    header = ['Sport Name', 'Athlete Name', 'Event Date']
    csv_writer.writerow(header)
    print(f"Header written: {header}")  # 打印表头是否被写入

    # 遍历所有的景区信息并写入 CSV 文件
    for index, spot in enumerate(spots):
        print(f"Writing row {index + 1}: {[spot.sport_name, spot.athlete_name, spot.event_date]}")  # 打印正在写入的数据
        csv_writer.writerow([spot.sport_name, spot.athlete_name, spot.event_date])

    # 刷新并关闭文本缓冲区，将数据刷新到 BytesIO 对象中
    text_buffer.detach()

    # 将 BytesIO 对象的指针重置到开头
    csv_buffer.seek(0)

    # 使用 send_file 函数发送文件
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='scenic_spots_data.csv'
    )


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8000)
