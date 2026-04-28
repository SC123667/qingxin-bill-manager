#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess
import sys
import os
import importlib.util

def install_package_with_mirrors(package):
    """使用多个镜像源尝试安装包"""
    # 国内镜像源列表（按优先级排序）
    mirrors = [
        "https://pypi.tuna.tsinghua.edu.cn/simple/",      # 清华大学镜像
        "https://mirrors.aliyun.com/pypi/simple/",        # 阿里云镜像
        "https://pypi.mirrors.ustc.edu.cn/simple/",       # 中科大镜像
        "https://pypi.douban.com/simple/",                # 豆瓣镜像
        None  # 官方源
    ]
    
    for i, mirror in enumerate(mirrors):
        try:
            print(f"\n{'='*50}")
            if mirror:
                mirror_name = mirror.split('//')[1].split('/')[0]
                print(f"📦 尝试从 {mirror_name} 安装 {package}...")
                cmd = [sys.executable, "-m", "pip", "install", package, "-i", mirror, "--trusted-host", mirror.split('//')[1].split('/')[0]]
            else:
                print(f"📦 尝试从官方源安装 {package}...")
                cmd = [sys.executable, "-m", "pip", "install", package]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"✅ {package} 安装成功！")
                return True
            else:
                print(f"❌ 从此源安装失败: {result.stderr.strip()[:100]}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ 安装 {package} 超时，尝试下一个镜像源...")
        except Exception as e:
            print(f"❌ 安装出错: {str(e)[:100]}")
    
    print(f"❌ 所有镜像源都无法安装 {package}")
    return False

def check_package_installed(package_name):
    """检查包是否已安装"""
    # 处理包名映射
    package_mapping = {
        'PySide6': 'PySide6',
        'cryptography': 'cryptography',
        'matplotlib': 'matplotlib',
        'pandas': 'pandas',
        'openpyxl': 'openpyxl'
    }
    
    # 获取实际的包名
    clean_name = package_name.split('>=')[0].split('==')[0].split('[')[0]
    module_name = package_mapping.get(clean_name, clean_name)
    
    try:
        spec = importlib.util.find_spec(module_name)
        return spec is not None
    except (ImportError, ModuleNotFoundError, ValueError):
        try:
            __import__(module_name)
            return True
        except (ImportError, ModuleNotFoundError):
            return False

def verify_installation():
    """验证关键依赖是否正确安装"""
    print("\n🔍 验证关键依赖安装...")
    
    critical_imports = [
        ("PySide6.QtWidgets", "PySide6 GUI框架"),
        ("cryptography.fernet", "数据加密库"),
        ("matplotlib.pyplot", "图表绘制库"),
        ("openpyxl", "Excel文件操作库")
    ]
    
    all_good = True
    for module, description in critical_imports:
        try:
            __import__(module)
            print(f"✅ {description}: 可正常导入")
        except ImportError as e:
            print(f"❌ {description}: 导入失败 - {e}")
            all_good = False
    
    return all_good

def main():
    print("🚀 账单管理系统 - 智能依赖安装器 v2.0")
    print("="*60)
    
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 读取requirements.txt文件（使用绝对路径）
    requirements_file = os.path.join(script_dir, "requirements.txt")
    if not os.path.exists(requirements_file):
        print(f"❌ 找不到 {requirements_file} 文件！")
        return False
    
    # 解析依赖包
    with open(requirements_file, 'r', encoding='utf-8') as f:
        packages = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    print(f"📋 检测到 {len(packages)} 个依赖包:")
    for pkg in packages:
        print(f"   • {pkg}")
    
    print("\n🔍 检查已安装的包...")
    
    # 检查哪些包需要安装
    packages_to_install = []
    for package in packages:
        package_name = package.split('>=')[0].split('==')[0]
        if check_package_installed(package_name):
            print(f"✅ {package_name} 已安装")
        else:
            print(f"❗ {package_name} 未安装")
            packages_to_install.append(package)
    
    if not packages_to_install:
        print("\n🎉 所有依赖包都已安装！")
        # 即使都安装了，也要验证一下
        if verify_installation():
            print("\n✅ 所有关键依赖验证通过！")
            print("\n🚀 现在可以运行账单管理系统了:")
            print("   python3 main.py")
            return True
        else:
            print("\n❌ 依赖验证失败，可能需要重新安装某些包")
            return False
    
    print(f"\n📦 需要安装 {len(packages_to_install)} 个包:")
    for pkg in packages_to_install:
        print(f"   • {pkg}")
    
    # 开始安装
    print("\n🚀 开始安装依赖包...")
    success_count = 0
    failed_packages = []
    
    for package in packages_to_install:
        if install_package_with_mirrors(package):
            success_count += 1
        else:
            failed_packages.append(package)
    
    # 安装结果总结
    print("\n" + "="*60)
    print("📊 安装结果总结:")
    print(f"✅ 成功安装: {success_count} 个包")
    print(f"❌ 安装失败: {len(failed_packages)} 个包")
    
    if failed_packages:
        print("\n❌ 以下包安装失败:")
        for pkg in failed_packages:
            print(f"   • {pkg}")
        print("\n💡 建议:")
        print("   1. 检查网络连接")
        print("   2. 手动安装失败的包: pip install <包名>")
        print("   3. 尝试使用conda安装: conda install <包名>")
        print("   4. 某些包可能需要系统依赖，请查看具体错误信息")
        return False
    else:
        print("\n🎉 所有依赖包安装完成！")
        
        # 验证安装
        if verify_installation():
            print("\n✅ 所有关键依赖验证通过！")
            print("\n🚀 现在可以运行账单管理系统了:")
            print("   python3 main.py")
            return True
        else:
            print("\n❌ 依赖验证失败，请检查安装是否完整")
            return False

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ 用户中断安装")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中发生错误: {e}")
        sys.exit(1)