import subprocess
import shutil
import os

def build():
    # 1. 清理之前的构建
    for path in ['build', 'dist']:
        if os.path.exists(path):
            shutil.rmtree(path)

    # 2. 执行 PyInstaller
    print("正在打包中，请稍候...")
    cmd = [
        'pyinstaller',
        '--onefile',
        '--console',
        '--name=multiTelnet',
        'manager.py'
    ]
    subprocess.run(cmd)

    # 3. 准备分发包
    release_dir = 'release'
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir)

    # 拷贝 exe
    shutil.copy('dist/multiTelnet.exe', f'{release_dir}/multiTelnet.exe')
    
    # 拷贝必要的目录结构
    shutil.copytree('inventory', f'{release_dir}/inventory')
    
    # 创建空日志目录
    os.makedirs(f'{release_dir}/logs', exist_ok=True)

    print(f"打包完成！请查看 '{release_dir}' 文件夹。")
    print("你可以直接把整个 'release' 文件夹拷贝到任何电脑上运行。")

if __name__ == "__main__":
    build()
