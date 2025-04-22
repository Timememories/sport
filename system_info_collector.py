import tkinter as tk
from tkinter import messagebox
import platform
import psutil
import os
import subprocess
import importlib.util
import socket
import uuid
import requests  # 导入 requests 库


# 安装依赖库
def install_dependencies():
    system = platform.system()
    if system == "Windows":
        try:
            if importlib.util.find_spec("wmi") is None:
                subprocess.check_call(["pip", "install", "wmi", "pywin32"])
                print("Windows dependency libraries installed successfully")
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error occurred while installing Windows dependency libraries: {e}")
            print(f"Error occurred while installing Windows dependency libraries: {e}")
    elif system == "Darwin":
        pass
    elif system == "Linux":
        pass


# 获取系统信息
def get_system_info():
    try:
        cpu_info = {
            # CPU 核心数
            'Number of CPU cores': psutil.cpu_count(logical=False),
            # 逻辑 CPU 数
            'Number of logical CPUs': psutil.cpu_count(logical=True),
            # CPU 使用率
            'CPU usage rate': psutil.cpu_percent(interval=1)
        }

        mem = psutil.virtual_memory()
        mem_info = {
            # 总内存(GB)
            'Total memory (GB)': round(mem.total / (1024 * 1024 * 1024), 2),
            # 已用内存(GB)
            'Used memory (GB)': round(mem.used / (1024 * 1024 * 1024), 2),
            # 内存使用率
            'Memory usage rate': mem.percent
        }

        disk_info = []
        partitions = psutil.disk_partitions()
        for partition in partitions:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append(
                    f"{partition.device} - Total capacity (GB): {round(usage.total / (1024 * 1024 * 1024), 2)}, "
                    f"Used capacity (GB): {round(usage.used / (1024 * 1024 * 1024), 2)}, "
                    f"Usage rate: {usage.percent}%")
            except PermissionError:
                disk_info.append(f"{partition.device} - Unable to access this disk partition")

        system_info = {**cpu_info, **mem_info, 'Disk information': disk_info}
        print("System information collected successfully")
        return system_info
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while getting system information: {e}")
        print(f"Error occurred while getting system information: {e}")
        return None


# 获取设备信息
def get_device_info():
    system = platform.system()
    device_info = []
    try:
        if system == "Windows":
            try:
                import wmi
                c = wmi.WMI()
                for item in c.Win32_PnPEntity():
                    try:
                        device_info.append(
                            f"Device name: {item.Name}, Device type: {item.ClassName}, Model: {item.Model}")
                    except AttributeError:
                        device_info.append(f"Device name: {item.Name}, Device type: {item.ClassName}, Model: Unknown")
            except ImportError:
                device_info.append(
                    "The wmi library is not installed. Unable to get device information. Please make sure pywin32 and wmi libraries are installed.")
                print("The wmi library is not installed. Unable to get device information.")
        elif system == "Darwin":
            try:
                result = subprocess.check_output(["system_profiler", "SPHardwareDataType"]).decode('utf-8')
                lines = result.strip().split('\n')
                device_info = [line.strip() for line in lines if line.strip()]
            except subprocess.CalledProcessError as e:
                device_info.append(f"Error occurred while getting macOS device information: {e}")
                print(f"Error occurred while getting macOS device information: {e}")
        elif system == "Linux":
            try:
                result = subprocess.check_output(["dmidecode"]).decode('utf-8')
                lines = result.strip().split('\n')
                device_info = [line.strip() for line in lines if line.strip()]
            except subprocess.CalledProcessError as e:
                device_info.append(f"Error occurred while getting Linux device information: {e}")
                print(f"Error occurred while getting Linux device information: {e}")
        else:
            device_info.append("Unsupported operating system. Unable to get device information.")
            print("Unsupported operating system. Unable to get device information.")
        print("Device information collected successfully")
        return device_info
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while getting device information: {e}")
        print(f"Error occurred while getting device information: {e}")
        return None


# 获取机器编码
def get_machine_code():
    system = platform.system()
    if system == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            for system in c.Win32_ComputerSystemProduct():
                machine_code = system.UUID
                print(f"Machine code: {machine_code}")
                return machine_code
        except Exception as e:
            messagebox.showerror("Error", f"Error occurred while getting machine code: {e}")
            print(f"Error occurred while getting machine code: {e}")
    elif system == "Darwin":
        try:
            result = subprocess.check_output(
                ["system_profiler", "SPHardwareDataType", "|", "grep", "Serial Number (system):"]).decode('utf-8')
            lines = result.splitlines()
            for line in lines:
                if "Hardware UUID:" in line:
                    uuid = line.split(": ")[1].strip()
                    print(f"Machine code: {uuid}")
                    return uuid

        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error occurred while getting macOS machine code: {e}")
            print(f"Error occurred while getting macOS machine code: {e}")
    else:
        messagebox.showinfo("Prompt", "Currently only Windows and macOS systems support getting machine code.")
        print("Currently only Windows and macOS systems support getting machine code.")
    return None


# 获取局域网信息
def get_local_network_info():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()

        mac = ':'.join(("%012X" % uuid.getnode())[i:i + 2] for i in range(0, 12, 2))
        return {
            # IP 地址
            'IP address': ip_address,
            # MAC 地址
            'MAC address': mac
        }
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while getting local network information: {e}")
        print(f"Error occurred while getting local network information: {e}")
        return None


# 生成报告
def generate_report(system_info, device_info, machine_code, network_info):
    try:
        report = "System Information Report\n\n"
        if machine_code:
            report += f"Machine code: {machine_code}\n\n"
        for key, value in system_info.items():
            if isinstance(value, list):
                report += f"{key}:\n"
                for sub_value in value:
                    report += f"  - {sub_value}\n"
            else:
                report += f"{key}: {value}\n"

        report += "\nInstalled Device Information\n\n"
        for device in device_info:
            report += f" - {device}\n"

        if network_info:
            report += "\nLocal Network Information\n\n"
            for key, value in network_info.items():
                report += f"{key}: {value}\n"

        report_path = os.path.join(os.getcwd(), "system_report.txt")
        with open(report_path, 'w', encoding='utf-8') as file:
            file.write(report)
        print("Report generated successfully")
        return report_path
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while generating the report: {e}")
        print(f"Error occurred while generating the report: {e}")
        return None


# 显示报告
def show_report():
    try:
        install_dependencies()
        system_info = get_system_info()
        if system_info is None:
            return
        device_info = get_device_info()
        if device_info is None:
            return
        machine_code = get_machine_code()
        network_info = get_local_network_info()
        report_path = generate_report(system_info, device_info, machine_code, network_info)
        if report_path:
            messagebox.showinfo("Report Generated Successfully",
                                f"The system information report has been generated. Path: {report_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Error occurred while executing the report generation process: {e}")
        print(f"Error occurred while executing the report generation process: {e}")


# 显示系统信息并调用接口
def show_system_info():
    system_info = get_system_info()
    machine_code = get_machine_code()
    device_info = get_device_info()
    network_info = get_local_network_info()

    if system_info and device_info:
        info_text = ""
        if machine_code:
            info_text += f"Machine code: {machine_code}\n\n"

        info_text += "System Information:\n"
        for key, value in system_info.items():
            if isinstance(value, list):
                info_text += f"{key}:\n"
                for sub_value in value:
                    info_text += f"  - {sub_value}\n"
            else:
                info_text += f"{key}: {value}\n"

        info_text += "\nDevice Information:\n"
        for device in device_info:
            info_text += f" - {device}\n"

        if network_info:
            info_text += "\nLocal Network Information:\n"
            for key, value in network_info.items():
                info_text += f"{key}: {value}\n"

        messagebox.showinfo("System Information", info_text)

        # 调用接口
        url = "http://127.0.0.1:8000/add_system_report_api"
        payload = {
            "machine_code": machine_code,
            "cpu_cores": system_info['Number of CPU cores'],
            "logical_cpus": system_info['Number of logical CPUs'],
            "cpu_usage": system_info['CPU usage rate'],
            "total_memory": system_info['Total memory (GB)'],
            "used_memory": system_info['Used memory (GB)'],
            "memory_usage": system_info['Memory usage rate'],
            "disk_info": "\n".join(system_info['Disk information']),
            "device_info": "\n".join(device_info),
            "ip_address": network_info['IP address'],
            "mac_address": network_info['MAC address']
        }
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "User-Agent": "Python-Requests",
            "Connection": "keep-alive",
            "Content-Type": "application/json"
        }
        print("System information sent to API successfully")
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            print("System information sent to API successfully")
            print(response.text)
        except requests.RequestException as e:
            messagebox.showerror("Error", f"Error occurred while sending system information to API: {e}")
            print(f"Error occurred while sending system information to API: {e}")


root = tk.Tk()
root.title("System Information Collection Tool")

# 初始窗口大小
window_width = 400
window_height = 300

# 获取屏幕尺寸
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 计算窗口居中位置
x_coordinate = int((screen_width / 2) - (window_width / 2))
y_coordinate = int((screen_height / 2) - (window_height / 2))

# 设置窗口位置
root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")


# 鼠标进入按钮事件
def on_enter(event):
    collect_button.config(bg="#808080", fg="white")


# 鼠标离开按钮事件
def on_leave(event):
    collect_button.config(bg=root.cget('bg'), fg="black")


# 设置按钮为透明，文字颜色为黑色，鼠标悬停时箭头变为小手形状，增大按钮尺寸
collect_button = tk.Button(root, text="Collect information and generate report", command=show_report,
                           bg=root.cget('bg'), bd=0, highlightthickness=0,
                           activebackground=root.cget('bg'), fg="black", cursor="hand2", width=30, height=3)
collect_button.pack(pady=10)

show_info_button = tk.Button(root, text="Show system information", command=show_system_info,
                             bg=root.cget('bg'), bd=0, highlightthickness=0,
                             activebackground=root.cget('bg'), fg="black", cursor="hand2", width=30, height=3)
show_info_button.pack(pady=10)

root.mainloop()
