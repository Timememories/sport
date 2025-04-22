import csv
import io

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///system_reports.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
db = SQLAlchemy(app)


class SystemReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    machine_code = db.Column(db.String(100), nullable=False)
    cpu_cores = db.Column(db.Integer, nullable=False)
    logical_cpus = db.Column(db.Integer, nullable=False)
    cpu_usage = db.Column(db.String(20), nullable=False)
    total_memory = db.Column(db.String(20), nullable=False)
    used_memory = db.Column(db.String(20), nullable=False)
    memory_usage = db.Column(db.String(20), nullable=False)
    disk_info = db.Column(db.Text, nullable=False)
    device_info = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    mac_address = db.Column(db.String(50), nullable=False)


@app.route('/')
def splash_home():
    return render_template('splash.html')


@app.route('/system_reports', methods=['GET', 'POST'])
def system_reports():
    machine_code = request.args.get('machine_code')
    # 构建查询条件
    query = SystemReport.query
    if machine_code:
        query = query.filter(SystemReport.machine_code.like(f'%{machine_code}%'))
    sort_by = request.args.get('sort_by')
    sort_order = request.args.get('sort_order', 'asc')
    if sort_by:
        if sort_order == 'asc':
            query = query.order_by(getattr(SystemReport, sort_by).asc())
        else:
            query = query.order_by(getattr(SystemReport, sort_by).desc())
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'delete':
            report_id = request.form.get('report_id')
            report = SystemReport.query.get(report_id)
            if report:
                db.session.delete(report)
                db.session.commit()
                flash('Report has been successfully deleted')
        elif action == 'sort':
            query = SystemReport.query.order_by(SystemReport.machine_code)
            reports = query.all()
            return render_template('system_reports.html', reports=reports)
        elif action == 'view_all':
            reports = SystemReport.query.all()
            return render_template('system_reports.html', reports=reports)
        elif action == 'edit':
            return redirect(url_for('system_reports'))
        return redirect(url_for('system_reports'))
    reports = query.all()
    return render_template('system_reports.html', reports=reports, sort_by=sort_by, sort_order=sort_order)


@app.route('/add_system_report', methods=['GET', 'POST'])
def add_system_report():
    if request.method == 'POST':
        new_machine_code = request.form.get('machine_code')
        new_cpu_cores = request.form.get('cpu_cores')
        new_logical_cpus = request.form.get('logical_cpus')
        new_cpu_usage = request.form.get('cpu_usage')
        new_total_memory = request.form.get('total_memory')
        new_used_memory = request.form.get('used_memory')
        new_memory_usage = request.form.get('memory_usage')
        new_disk_info = request.form.get('disk_info')
        new_device_info = request.form.get('device_info')
        new_ip_address = request.form.get('ip_address')
        new_mac_address = request.form.get('mac_address')

        new_report = SystemReport(
            machine_code=new_machine_code,
            cpu_cores=new_cpu_cores,
            logical_cpus=new_logical_cpus,
            cpu_usage=new_cpu_usage,
            total_memory=new_total_memory,
            used_memory=new_used_memory,
            memory_usage=new_memory_usage,
            disk_info=new_disk_info,
            device_info=new_device_info,
            ip_address=new_ip_address,
            mac_address=new_mac_address
        )
        db.session.add(new_report)
        db.session.commit()
        flash('Report has been successfully added')
        return redirect(url_for('system_reports'))
    return render_template('add_system_report.html')


@app.route('/edit_system_report/<int:id>', methods=['GET', 'POST'])
def edit_system_report(id):
    report = SystemReport.query.get_or_404(id)
    if request.method == 'POST':
        report.machine_code = request.form['machine_code']
        report.cpu_cores = request.form['cpu_cores']
        report.logical_cpus = request.form['logical_cpus']
        report.cpu_usage = request.form['cpu_usage']
        report.total_memory = request.form['total_memory']
        report.used_memory = request.form['used_memory']
        report.memory_usage = request.form['memory_usage']
        report.disk_info = request.form['disk_info']
        report.device_info = request.form['device_info']
        report.ip_address = request.form['ip_address']
        report.mac_address = request.form['mac_address']
        db.session.commit()
        flash('Report has been successfully modified')
        return redirect(url_for('system_reports'))
    return render_template('edit_system_report.html', report=report)


@app.route('/view_system_report_details/<int:id>', methods=['GET'])
def view_system_report_details(id):
    action = request.args.get('action')
    if action == 'add':
        return render_template('add_system_report.html')
    report = SystemReport.query.get_or_404(id)
    return render_template('system_report_details.html', report=report)


@app.route('/get_system_report/<int:id>', methods=['GET'])
def get_system_report(id):
    report = SystemReport.query.get_or_404(id)
    return jsonify({
        'machine_code': report.machine_code,
        'cpu_cores': report.cpu_cores,
        'logical_cpus': report.logical_cpus,
        'cpu_usage': report.cpu_usage,
        'total_memory': report.total_memory,
        'used_memory': report.used_memory,
        'memory_usage': report.memory_usage,
        'disk_info': report.disk_info,
        'device_info': report.device_info,
        'ip_address': report.ip_address,
        'mac_address': report.mac_address
    })


@app.route('/search_system_reports', methods=['POST'])
def search_system_reports():
    machine_code = request.form.get('machine_code')

    # 构建查询条件
    query = SystemReport.query
    if machine_code:
        query = query.filter(SystemReport.machine_code.like(f'%{machine_code}%'))

    # 执行查询
    results = query.all()

    # 将查询结果转换为字典列表
    results_list = [{
        'id': report.id,
        'machine_code': report.machine_code,
        'cpu_cores': report.cpu_cores,
        'logical_cpus': report.logical_cpus,
        'cpu_usage': report.cpu_usage,
        'total_memory': report.total_memory,
        'used_memory': report.used_memory,
        'memory_usage': report.memory_usage,
        'disk_info': report.disk_info,
        'device_info': report.device_info,
        'ip_address': report.ip_address,
        'mac_address': report.mac_address
    } for report in results]

    return jsonify(results_list)


@app.route('/search_results', methods=['POST'])
def search_results():
    machine_code = request.form.get('machine_code')

    # 构建查询条件
    query = SystemReport.query
    if machine_code:
        query = query.filter(SystemReport.machine_code.like(f'%{machine_code}%'))

    # 执行查询
    reports = query.all()

    return render_template('system_reports.html', reports=reports, sort_by=None, sort_order=None)


@app.route('/download_system_reports')
def download_system_reports():
    # 从数据库中获取所有的系统报告信息
    reports = SystemReport.query.all()
    print(f"Number of reports retrieved from database: {len(reports)}")  # 打印获取的数据数量
    for report in reports:
        print(f"Report: {report}")  # 打印每个系统报告信息

    # 创建一个 BytesIO 对象，用于存储 CSV 数据
    csv_buffer = io.BytesIO()
    # 将 BytesIO 对象包装为文本模式
    text_buffer = io.TextIOWrapper(csv_buffer, newline='')
    csv_writer = csv.writer(text_buffer)

    # 写入 CSV 文件的表头
    header = ['Machine Code', 'CPU Cores', 'Logical CPUs', 'CPU Usage', 'Total Memory', 'Used Memory', 'Memory Usage',
              'Disk Info', 'Device Info', 'IP Address', 'MAC Address']
    csv_writer.writerow(header)
    print(f"Header written: {header}")  # 打印表头是否被写入

    # 遍历所有的系统报告信息并写入 CSV 文件
    for index, report in enumerate(reports):
        print(
            f"Writing row {index + 1}: {[report.machine_code, report.cpu_cores, report.logical_cpus, report.cpu_usage, report.total_memory, report.used_memory, report.memory_usage, report.disk_info, report.device_info, report.ip_address, report.mac_address]}")  # 打印正在写入的数据
        csv_writer.writerow(
            [report.machine_code, report.cpu_cores, report.logical_cpus, report.cpu_usage, report.total_memory,
             report.used_memory, report.memory_usage, report.disk_info, report.device_info, report.ip_address,
             report.mac_address])

    # 刷新并关闭文本缓冲区，将数据刷新到 BytesIO 对象中
    text_buffer.detach()

    # 将 BytesIO 对象的指针重置到开头
    csv_buffer.seek(0)

    # 使用 send_file 函数发送文件
    return send_file(
        csv_buffer,
        mimetype='text/csv',
        as_attachment=True,
        download_name='system_reports_data.csv'
    )


# 新增接口

@app.route('/add_system_report_api', methods=['POST'])
def add_system_report_api():
    data = request.get_json()
    machine_code = data.get('machine_code')

    # 根据 machine_code 查询数据库中是否存在对应的记录
    report = SystemReport.query.filter_by(machine_code=machine_code).first()

    if report:
        # 如果记录存在，则更新该记录的信息
        report.cpu_cores = data.get('cpu_cores', report.cpu_cores)
        report.logical_cpus = data.get('logical_cpus', report.logical_cpus)
        report.cpu_usage = data.get('cpu_usage', report.cpu_usage)
        report.total_memory = data.get('total_memory', report.total_memory)
        report.used_memory = data.get('used_memory', report.used_memory)
        report.memory_usage = data.get('memory_usage', report.memory_usage)
        report.disk_info = data.get('disk_info', report.disk_info)
        report.device_info = data.get('device_info', report.device_info)
        report.ip_address = data.get('ip_address', report.ip_address)
        report.mac_address = data.get('mac_address', report.mac_address)

        db.session.commit()
        return jsonify({'message': 'Report has been successfully updated'})
    else:
        # 如果记录不存在，则添加新的记录
        new_report = SystemReport(**data)
        db.session.add(new_report)
        db.session.commit()
        return jsonify({'message': 'Report has been successfully added'})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=8000)
